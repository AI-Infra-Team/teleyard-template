import os
import hashlib
import time
import subprocess
import yaml
import sys

DEBUG_LOCAL=False

# 定义你的图片目录
if DEBUG_LOCAL:
    image_dir="../../container_image"
else:
    image_dir = "/app/image_dir"

# 存储上一次扫描时所有文件的哈希值
last_hashes = {}

if DEBUG_LOCAL:
    conf_yaml="../../../nodes.yml"
else:
    conf_yaml='/app/nodes_conf/nodes.yml'


REPO_HOST=''
REPO_NAMESPACE=''
with open(conf_yaml, 'r') as f:
    conf = yaml.safe_load(f)
    REPO_HOST = conf['imageRepositoryHostIp']
    REPO_NAMESPACE = conf['imageRepository'].split('/')[1]

ssh_user='teleinfra'
ssh_ip=conf['nodes'][0]['ip']
if not DEBUG_LOCAL:
    ssh_secret=conf['sshSecret']


# overwrite print() with flush
# same args as print(), but also flushes the buffer
sysprint=print
f=open("./upload_log.txt", "a")
def print(*args, **kwargs):
    global f
    sysprint(*args, **kwargs)
    sys.stdout.flush()
    # write to file
    if f.closed:
        f=open("./upload_log.txt", "a")
    # f.write(' '.join(args)+"\n")
    for arg in args:
        f.write(str(arg))
        f.write(' ')
    f.write("\n")
    f.flush()

def get_file_hash(file_path):
    """ 计算给定文件的MD5哈希值 """
    print(f"hashing file: {file_path}")
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            break
    return hash_md5.hexdigest()

last_hashes={}
def check_files():
    """ 检查文件是否有变更 """
    global last_hashes
    current_hashes = {}
    changes_detected = False
    
    image_tag__arch__path ={}
    
    # 遍历目录中的所有文件
    print("checking files")
    if not os.path.exists(image_dir):
        os.system("mkdir -p "+image_dir)
        
    # map arch -> files
    for root, dirs, files in os.walk(image_dir):
        for name in files:
            if not name.endswith(".tar"):
                continue
            name_parts= name.split(".tar")[0].split("_")

            # prepare empty arch->packpath map
            
            if len(name_parts) != 3 or name_parts[1] not in ['amd64', 'arm64']:
                image_tag__arch__path[name+"_unknown_arch"]=os.path.join(root, name)
            else:
                if name_parts[0]+"_"+name_parts[2] not in image_tag__arch__path:
                    image_tag__arch__path[name_parts[0]+"_"+name_parts[2]]={}
                image_tag__arch__path[name_parts[0]+"_"+name_parts[2]][name_parts[1]]=os.path.join(root, name)

    # collect changed images
    changed_images={}
    for image_tag in image_tag__arch__path:
        if image_tag.find("_unknown_arch")>-1:
            # {filename}_unknown_arch -> file_path
            file_path=image_tag__arch__path[image_tag]
            current_hash = get_file_hash(file_path)
            current_hashes[file_path] = current_hash
            # # 如果文件不存在于上次记录中，或者哈希值不同，则认为文件已更改
            if file_path not in last_hashes or last_hashes[file_path] != current_hash:
                changes_detected = True
                print(f"Detected change in {file_path}")
                changed_images[image_tag]=image_tag__arch__path[image_tag]
        else:
            # image_tag -> {'amd64': 'path1', 'arm64': 'path2'}
            if len(image_tag__arch__path[image_tag]) !=2:
                continue
            
            for arch in image_tag__arch__path[image_tag]:
                file_path=image_tag__arch__path[image_tag][arch]
                current_hash = get_file_hash(file_path)
                current_hashes[file_path] = current_hash
                # # 如果文件不存在于上次记录中，或者哈希值不同，则认为文件已更改
                if file_path not in last_hashes or last_hashes[file_path] != current_hash:
                    changes_detected = True
                    print(f"Detected change in {file_path}")
                    changed_images[image_tag]=image_tag__arch__path[image_tag]
    
    print(changed_images)
    # 如果检测到任何变更，更新哈希值并执行上传操作
    if changes_detected:
        for changed_image_key in changed_images:
            
            if changed_image_key.find("_unknown_arch")>-1:
                # {filename}_unknown_arch -> file_path
                status_fdir=changed_images[changed_image_key]
                create_upload_status_file(status_fdir, "uploading")
                
                success, imagename = upload_unknown_arch_image(status_fdir)

                if success:
                    [imagename,tag]=imagename.split(':')
                    create_upload_status_file(status_fdir, f"success_{imagename}_{tag}")
                else:
                    create_upload_status_file(status_fdir, "fail")
            else:
                changed_image=changed_images[changed_image_key]
                status_fdir=os.path.dirname(changed_image['amd64'])+"/"+changed_image_key
                create_upload_status_file(status_fdir, "uploading")
                
                success, imagename = upload_image(changed_image['amd64'],changed_image['arm64'])
                
                if success:
                    [imagename,tag]=imagename.split(':')
                    create_upload_status_file(status_fdir, f"success_{imagename}_{tag}")
                else:
                    create_upload_status_file(status_fdir, "fail")
        last_hashes = current_hashes


def run_command(command,allow_fail=False):
    """
    Run a shell command and ensure it completes successfully.
    """
    result = subprocess.run(f"ssh {ssh_user}@{ssh_ip} '{command}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        return False
    else:
        print(result.stdout)
        if 'reported.' in result.stdout.decode('utf-8'):
            return result.stdout.decode('utf-8').split('reported.\n')[-1]
        return result.stdout.decode('utf-8')

def upload_unknown_arch_image(image_path):
    image_path=image_path.replace("/app/image_dir","${image_dir}")
    img_name=run_command(f"sudo docker load -i {image_path}")
    if img_name is False: return False,""
    img_name=img_name.split("Loaded image: ")[-1].strip()
    
    def get_id(img_name): # 获取刚load的特定架构的镜像id，用于后续打tag
        res= run_command(f"sudo docker image list -q {img_name}")
        if not res: return False
        return res.strip()
    imgid=get_id(img_name)
    
    img_key_no_prefix=img_name.split("/")[-1]
    # 给对应id 打上带架构的tag
    if run_command(f"sudo docker tag {imgid} {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_unknown_arch") is False: return False,""
    # 推送到远程仓库，后续创建manifest需要远程仓库有这两个镜像
    if run_command(f"sudo docker push {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_unknown_arch") is False: return False,""

    return True, img_key_no_prefix+"_unknown_arch"    
    

def upload_image(image_amd64, image_arm64):
    if DEBUG_LOCAL:
        time.sleep(5)
    # else:
        # f=open("testdebug","a")
    # f.write(f"{image_amd64} {image_arm64}\n")
    # f.close()
    
    def push_image(image_amd64, image_arm64):
        
            

        # 加载镜像，两个镜像的包名和tag名一样，所以我们去拿他的id
        img_name=run_command(f"sudo docker load -i {image_amd64}")
        if img_name is False: return False,""
        img_name=img_name.split("Loaded image: ")[-1].strip()

        def get_id(img_name): # 获取刚load的特定架构的镜像id，用于后续打tag
            res= run_command(f"sudo docker image list -q {img_name}")
            if not res: return False
            return res.strip()
        amdid=get_id(img_name)
        if amdid is False: return False,""
        
        run_command(f"sudo docker load -i {image_arm64}")
        armid=get_id(img_name)
        if armid is False: return False,""

        img_key_no_prefix=img_name.split("/")[-1]
        # 给对应id 打上带架构的tag
        if run_command(f"sudo docker tag {amdid} {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_amd64") is False: return False, ""
        if run_command(f"sudo docker tag {armid} {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_arm64") is False: return False, ""
        # 推送到远程仓库，后续创建manifest需要远程仓库有这两个镜像
        if run_command(f"sudo docker push {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_amd64") is False: return False, ""
        if run_command(f"sudo docker push {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_arm64") is False: return False, ""
        # 创建manifest，以将 通用镜像名称 映射到 具体架构的镜像（manifest 指令需要加 --insecure）
        run_command(f"sudo docker manifest rm {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}",allow_fail=True)
        if run_command(f"sudo docker manifest create {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix} {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_amd64 {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_arm64 --insecure", allow_fail=True) is False: return False
        if run_command(f"sudo docker manifest annotate {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix} "
                    f"--arch amd64 {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_amd64") is False: return False, ""
        if run_command(f"sudo docker manifest annotate {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix} "
                    f"--arch arm64 {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix}_arm64") is False: return False, ""
        # 推送manifest（manifest 指令需要加 --insecure）
        if run_command(f"sudo docker manifest push {REPO_HOST}/{REPO_NAMESPACE}/{img_key_no_prefix} --insecure") is False: return False, ""
        return True, img_key_no_prefix
    # print(image_amd64,image_arm64)
    # dir=os.path.dirname(image_amd64)
    # imagename="_".join(image_amd64.split("/")[-1].split("_")[:-2])
    # cur_dir=os.getcwd()
    # os.chdir(dir)
    image_amd64=image_amd64.replace("/app/image_dir","${image_dir}")
    image_arm64=image_arm64.replace("/app/image_dir","${image_dir}")
    
    if not DEBUG_LOCAL:
        return push_image(image_amd64, image_arm64)
    # os.chdir(cur_dir)
    return True

def create_upload_status_file(file_path, status):

    # find old same prefix, remove it
    file_dir=os.path.dirname(file_path)
    filename=os.path.basename(file_path)
    statuss=[
        'success',
        'fail',
        'uploading'
    ]
    
    for st in statuss:
        dirlist=os.listdir(file_dir)
        for d in dirlist:
            if d.find(f"{filename}_{st}")!=-1:
                os.system(f"rm -f {file_dir}/{d}")
            # os.remove(f"{file_dir}/{filename}_{st}")
            
    status_file_name = f"{file_path}_{status}"
    with open(status_file_name, "w") as f:
        f.write(f"Upload {status} for {file_path}\n")
    print(f"Created {status_file_name}")

if __name__ == "__main__":
    # add ssh_secret into authority
    
    print(f"\nsetup ssh to main node {ssh_ip}\n")
    
    if not DEBUG_LOCAL:
        os.system(f"mkdir -p ~/.ssh")
        os.system(f"ssh-keyscan -H {ssh_ip} >> ~/.ssh/known_hosts")
        os.system(f"echo '{ssh_secret}' > ~/.ssh/id_ed25519")
        os.system(f"chmod 600 ~/.ssh/id_ed25519")
    
    print(f"\nssh is setuped")

    while True:
        check_files()
        time.sleep(30)  # 每30秒执行一次检查
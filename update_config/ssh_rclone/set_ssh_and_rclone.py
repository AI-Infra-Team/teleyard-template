import os,sys,getpass,yaml,subprocess
CUR_FDIR = os.path.dirname(os.path.abspath(__file__)); cur_scan=CUR_FDIR; scan=[["pylib.py" in os.listdir(cur_scan),cur_scan,exec('global cur_scan;cur_scan=os.path.join(cur_scan, "..")')] for _ in range(10)]; found_pylib=[x[0] for x in scan]; pylib_dir_idx=found_pylib.index(True); assert pylib_dir_idx>=0, "pylib.py not found"; print(scan[pylib_dir_idx][1]); ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, scan[pylib_dir_idx][1])); sys.path.append(ROOT_DIR)
os.chdir(CUR_FDIR)
import pylib



print("\ntype in your ssh password:")
# wait for user input password
password=getpass.getpass()
def encrypt_password(password):
    try:
        # 调用 rclone obscure 命令来加密密码
        result = subprocess.run(['rclone', 'obscure', password], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"加密密码时出错: {e}")
        exit(1)
password_enc=encrypt_password(password)


print("\nconfiguring ssh no pass")
main_node=pylib.ConfReader().get_main_node()
main_node_ip=main_node['ip']
ssh_secret= yaml.safe_load(pylib.get_secret_data(key='nodes_conf'))['sshSecret']
# pylib.os_system_sure(f"ssh-keyscan -H {main_node_ip} >> ~/.ssh/known_hosts")
ssh_dir=os.path.join(pylib.current_user_dir(),".ssh")
pylib.mkdir(ssh_dir)

need_add_secret=False
try:
    with open(os.path.join(ssh_dir,"id_ed25519"),"r") as f:
        content=f.read()
        if content.find(ssh_secret)==-1:
            need_add_secret
except:
    need_add_secret=True

if need_add_secret:
    with open(os.path.join(ssh_dir,"id_ed25519"),"a") as f2:
        f2.write(ssh_secret)
        
if os.name != 'nt':
    pylib.os_system_sure(f"chmod 600 ~/.ssh/id_ed25519")


print("\nconfiguring rclone")
config=f"""[remote]
type = sftp
host = {main_node_ip}
user = teleinfra
pass = {password_enc}
shell type = unix
md5sum_command = md5sum
sha1sum_command = sha1sum"""
rclone_conf_path=os.path.join(pylib.current_user_dir(),"rclone_main_node.conf")
with open(rclone_conf_path,"w") as f:
    f.write(config)
pylib.os_system_sure(f"rclone config import {rclone_conf_path}")
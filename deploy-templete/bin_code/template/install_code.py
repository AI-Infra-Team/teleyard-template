import os, sys, subprocess
import urllib.request
import tempfile
import zipfile
def cmd_color(string,color):
    color_dict={"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37}
    return f"\033[{color_dict[color]}m{string}\033[0m"

def os_system_sure(command):
    BEFORE_RUN_TITLE=cmd_color("执行命令：","blue")
    RUN_FAIL_TITLE=cmd_color(">","blue")+"\n"+cmd_color("命令执行失败：","red")
    RUN_SUCCESS_TITLE=cmd_color(">","blue")+"\n"+cmd_color("命令执行成功：","green")
    print(f"{BEFORE_RUN_TITLE}{command}")
    code=os.system(command)
    # result, code = run_command2(command,allow_fail=True)
    # code=os.system(command)
    if code != 0:
        print(f"{RUN_FAIL_TITLE}{command}")
        exit(1)
    print(f"{RUN_SUCCESS_TITLE}{command}\n")
def os_system(command):
    BEFORE_RUN_TITLE=cmd_color("执行命令：","blue")
    RUN_FAIL_TITLE=cmd_color("\n命令执行失败：","red")
    RUN_SUCCESS_TITLE=cmd_color("\n命令执行成功：","green")
    print(f"{BEFORE_RUN_TITLE}{command}")
    code=os.system(command)
    # result =run_command2(command,allow_fail=True)
    if code != 0:
        print(f"{RUN_FAIL_TITLE}{command}")
    else:
        print(f"{RUN_SUCCESS_TITLE}{command}\n")
    return code

def download_file(url, destination):
    print(f"downloading file {url} to {destination}")
    urllib.request.urlretrieve(url, destination)

def create_shortcut(target_path, shortcut_path, description="", icon_path=""):
    target_path=os.path.abspath(target_path)
    shortcut_path=os.path.abspath(shortcut_path)
    # PowerShell 脚本创建快捷方式
    powershell_command = f'''
    $WScriptShell = New-Object -ComObject WScript.Shell;
    $Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}");
    $Shortcut.TargetPath = "{target_path}";
    $Shortcut.Description = "{description}";
    $Shortcut.Save();
    '''
    temp_file = tempfile.NamedTemporaryFile(suffix=".ps1",delete=False)
    temp_file.write(powershell_command.encode())
    temp_file.close()    
    os_system(f"C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe -Command \"Set-ExecutionPolicy RemoteSigned -Force\"")
    os_system(f"C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe -File {temp_file.name}")
    os.remove(temp_file.name)
    # subprocess.run(["powershell", "-Command", powershell_command], check=True)

MAIN_NODE_IP="${MAIN_NODE_IP}"
TMP_DIR=tempfile.gettempdir()    
if os.name=="nt":
    CODE_URL=f"http://{MAIN_NODE_IP}:8003/bin_code/code_win.zip"
else:
    ARCH=""
    if os.uname().machine == "aarch64":
        ARCH="arm64"
    if os.uname().machine == "x86_64":
        ARCH="amd64"
    if os.uname().machine == "arm64":
        ARCH="arm64"
    CODE_URL=f"http://{MAIN_NODE_IP}:8003/bin_code/code_{ARCH}.deb"
    

os.chdir(TMP_DIR)
if not os.path.exists(os.path.basename(CODE_URL)):
    download_file(CODE_URL,os.path.basename(CODE_URL))
if os.name=="nt":
    zippath=os.path.abspath(os.path.basename(CODE_URL))
    try:
        os.makedirs("C://teledeploy/code")
    except:
        pass
    assert os.path.exists("C://teledeploy/code"), "mkdir C://teledeploy/code failed"
        # print("install failed")
    os.chdir("C://teledeploy/code")
    with zipfile.ZipFile(zippath, "r") as zip_ref:
        zip_ref.extractall()
    # os_system_sure("unzip code_win.zip")
    userdir=os.path.abspath(os.path.expanduser("~"))
    create_shortcut("Code.exe",os.path.join(userdir,"Desktop/code.lnk"))
    print("unzip at:",os.getcwd())
    
else:
    os_system_sure(f"sudo dpkg -i code_{ARCH}.deb")
    # os_system_sure(f"tar -zxvf code_{ARCH}.tar.gz")
    # dirname="VSCode-linux-x64"
    # if ARCH=="arm64":
    #     dirname="VSCode-linux-arm64"
    # curuser=os.getlogin()
    # os_system_sure(f"sudo mkdir -p /teledeploy/code")
    # os_system_sure(f"sudo mv {dirname}/* /teledeploy/code/")
    # os_system_sure(f"sudo chown -R {curuser} /teledeploy/code")
    # os_system_sure(f"sudo chmod -R 777 /teledeploy/code")
    # os_system_sure(f"sudo ln -s /teledeploy/code/code /usr/bin/code")
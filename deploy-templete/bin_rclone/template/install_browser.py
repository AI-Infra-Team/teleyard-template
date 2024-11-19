import os, sys, subprocess
import urllib.request
import tempfile
import zipfile

# ${MAIN_NODE_IP} is embedded local_value
MAIN_NODE_IP="${MAIN_NODE_IP}"

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

TMP_DIR=tempfile.gettempdir()    
if os.name=="nt":
    # CODE_URL=f"http://{MAIN_NODE_IP}:8003/bin_rclone/rclone-browser.exe"
    raise "run `Invoke-WebRequest -Uri 'http://10.127.20.218:8003/bin_rclone/rclone-browser.exe' -OutFile rclone-browser.exe; .\\rclone-browser.exe`"
else:
    ARCH=""
    if os.uname().machine == "aarch64":
        ARCH="arm64"
    if os.uname().machine == "x86_64":
        ARCH="amd64"
    if os.uname().machine == "arm64":
        raise "arm64 not supported"
    CODE_URL=f"http://{MAIN_NODE_IP}:8003/bin_rclone/rclone-browser.AppImage"
    

os.chdir(TMP_DIR)
if not os.path.exists(os.path.basename(CODE_URL)):
    download_file(CODE_URL,os.path.basename(CODE_URL))
os_system_sure("sudo cp rclone-browser.AppImage /usr/bin/rclone-browser")
os_system_sure("sudo chmod 777 /usr/bin/rclone-browser")

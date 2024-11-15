import os
import urllib.request

def cmd_color(string,color):
    color_dict={"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37}
    return f"\033[{color_dict[color]}m{string}\033[0m"

if os.name == 'nt':
    print(cmd_color("this script is only for centos/ctyunos","red"))
    exit(1)


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

os_system("""python3 -c 'import urllib.request, os; script = urllib.request.urlopen("http://10.127.20.218:8003/bin_easy_config/add_tele_host.py").read(); print(script.decode())' | python3""")

print("setting up rpm source")

os_system("rm -rf /etc/yum.repos.d")
os_system("mkdir /etc/yum.repos.d")


# use url lib to download, very independent
script = urllib.request.urlopen("http://download.chinatelecom.ai/CentOS8-ChinaTelecom.repo").read().decode()
with open("/etc/yum.repos.d/CentOS8-ChinaTelecom.repo","w") as f:
    f.write(script)

os_system("yum update -y")
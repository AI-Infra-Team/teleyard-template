import os
import urllib.request

def cmd_color(string,color):
    color_dict={"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37}
    return f"\033[{color_dict[color]}m{string}\033[0m"

# if windows
if os.name == 'nt':
    print(cmd_color("this script is only for ubuntu18.04 ","red"))
    exit(1)

# get ubuntu version
def get_ubuntu_version():
    with open('/etc/os-release') as f:
        os_info = f.read()
    
    for line in os_info.splitlines():
        if line.startswith("VERSION="):
            return line.split("=")[1].strip('"')
    
    return "Ubuntu version not found"
if get_ubuntu_version().find("18.04")==-1:
    print(cmd_color("this script is only for ubuntu18.04 ","red"))
    exit(1)

os.system("""python3 -c 'import urllib.request, os; script = urllib.request.urlopen("http://10.127.20.218:8003/bin_easy_config/add_tele_host.py").read(); print(script.decode())' | python3""")

print("setting up apt source")


# use url lib to download, very independent
apt_source_content = urllib.request.urlopen("http://download.chinatelecom.ai/Bionic-ChinaTelecom.list").read().decode()
# with open("/etc/yum.repos.d/CentOS8-ChinaTelecom.repo","w") as f:
#     f.write(script)

# 将APT源列表写入到/etc/apt/sources.list.d/目录下的文件中
with open("/etc/apt/sources.list.d/ChinaTelecom.list", "w") as f:
    f.write(apt_source_content)

# 更新APT包索引
os.system("apt-get update")
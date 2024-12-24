import os
CUR_FDIR = os.path.dirname(os.path.abspath(__file__))

if os.name != 'nt' and os.getuid() != 0:
    # print("Please run as root to add hosts")
    os.system(f"sudo python3 {__file__}")
    exit(0)

print("setting up hosts")
def add_hosts(hosts: list):
    # verify hosts format
    for host in hosts:
        if not host.find(" ") > 0:
            print("Error: hosts format error 1")
            exit(1)
        if len(host.split(" "))!=2:
            print("Error: hosts format error 2")
            exit(1)

    if os.name == 'nt':
        hostfile=r"C:\Windows\System32\drivers\etc\hosts"
    else:
        hostfile="/etc/hosts"
    # sudo open
    with open(hostfile) as f:
        content=f.read()
    lines=content.split("\n")

    updated_hosts={}
    for i in range(len(lines)):
        # find hosts
        for host in hosts:
            if host==lines[i]:
                print(f"host no update needed: {host}")
                updated_hosts[host]=i
                break
            host_name=host.split(" ")[1]
            # if start with host_ip, updata the line with new config
            if lines[i].replace("\n","").endswith(host_name):
                print(f"host update: {lines[i]} -> {host}")
                lines[i]=host
                updated_hosts[host]=i
                break
    for host in hosts:
        if host not in updated_hosts:
            print(f"host add: {host}")
            lines.append(host)
            updated_hosts[host]=len(lines)-1
    with open(hostfile, "w") as f:
        f.write("\n".join(lines))

add_hosts([
    "172.16.135.1 centos.chinatelecom.ai",
    "172.16.135.1 download.chinatelecom.ai",
    "10.30.254.254 pypi.chinatelecom.ai",
    "10.30.254.254 ubuntu.chinatelecom.ai",
    "10.37.86.30 harbor.telecomai.com.cn",
    "10.127.23.106 harbor.telecom-ai.com.cn"
])
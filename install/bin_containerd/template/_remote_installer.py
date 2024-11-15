# https://github.com/kinvolk/containerd-cri/blob/master/docs/installation.md#step-2-install-containerd

import os, subprocess


ARCH=""
if os.uname().machine == "aarch64":
    ARCH="arm64"
if os.uname().machine == "x86_64":
    ARCH="amd64"
if os.uname().machine == "arm64":
    ARCH="arm64"

def cmd_color(string,color):
    color_dict={"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37}
    return f"\033[{color_dict[color]}m{string}\033[0m"
def run_command2(command, allow_fail=False, prefix=cmd_color("   > ","blue")):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        print(f"{prefix}{line.decode().strip()}")
    process.stdout.close()
    return_code = process.wait()
    if not allow_fail and return_code:
        raise subprocess.CalledProcessError(return_code, command)
    return process.stdout, return_code
BEFORE_RUN_TITLE=cmd_color("执行命令：","blue")
RUN_FAIL_TITLE=cmd_color("命令执行失败：","red")
RUN_SUCCESS_TITLE=cmd_color("命令执行成功：","green")
def os_system_sure(command):
    print(f"{BEFORE_RUN_TITLE}{command}")
    result, code = run_command2(command)
    if code != 0:
        print(f"{RUN_FAIL_TITLE}{command}")
        exit(1)
    print(f"{RUN_SUCCESS_TITLE}{command}\n\n")
def os_system(command):
    print(f"{BEFORE_RUN_TITLE}{command}")
    result =run_command2(command,allow_fail=True)
    if result != 0:
        print(f"{RUN_FAIL_TITLE}{command}")
    print(f"{RUN_SUCCESS_TITLE}{command}\n\n")
    
def cmd_with_result(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result

# check containerd installed
if cmd_with_result("sudo containerd --version").returncode == 0:
    print("containerd 已安装")
    exit(0)

os_system_sure("mkdir -p /tmp/install_containerd")
os.chdir("/tmp/install_containerd")
os_system(f"wget http://${MAIN_NODE_IP}:8003/bin_containerd/cri-containerd-1.7.0-linux-{ARCH}.tar.gz ")

os_system(f"sudo tar --no-overwrite-dir -C / -xzf cri-containerd-1.7.0-linux-{ARCH}.tar.gz")
# copy to global bin 
flist=[
    "bin/containerd",
    "bin/containerd-shim",
    "bin/containerd-shim-runc-v1",
    "bin/containerd-shim-runc-v2",
    "bin/containerd-stress",
    "bin/crictl",
    "bin/critest",
    "bin/ctd-decoder",
    "bin/ctr",
    "sbin/runc",
]
for f in flist:
    os_system(f"sudo cp /usr/local/{f} /usr/{f}")
# sudo systemctl start containerd
os_system_sure("sudo systemctl start containerd")


import os,platform, subprocess
CUR_FPATH = os.path.abspath(__file__)
CUR_FDIR = os.path.dirname(CUR_FPATH)
# chdir to the directory of this script
os.chdir(CUR_FDIR)


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
    else:
        print(f"{RUN_SUCCESS_TITLE}{command}\n\n")

INSTALLERS=[
    "cri-tools",
    "kubernetes-cni",
    "kubectl",
    'socat',
    'libnetfilter_cthelper',
    'libnetfilter_cttimeout',
    'libnetfilter_queue',
    'conntrack',
    "kubelet",
    "kubeadm",
]

ARCH=""
# is arm
if platform.machine()=="aarch64":
    ARCH="aarch64"
elif platform.machine()=="x86_64":
    ARCH="x86_64"
elif platform.machine()=="arm64":
    ARCH="aarch64"

FILE_SERVER="http://${MAIN_NODE_IP}:8003/bin_k8s_3_brother"
os_system_sure("mkdir -p /tmp/install_k8s_3_brother")
os.chdir("/tmp/install_k8s_3_brother")
def download(path):
    file=path.split("/")[-1]
    if not os.path.exists(file):
        os_system_sure(f"wget {path}")
download(f"{FILE_SERVER}/k8s_127_{ARCH}.zip")
download(f"{FILE_SERVER}/conntrack-tools-1.4.4-11.el8.{ARCH}.rpm")
download(f"{FILE_SERVER}/socat-1.7.4.1-1.el8.{ARCH}.rpm")
download(f"{FILE_SERVER}/libnetfilter_cthelper-1.0.0-15.el8.{ARCH}.rpm")
download(f"{FILE_SERVER}/libnetfilter_cttimeout-1.0.0-11.el8.{ARCH}.rpm")
download(f"{FILE_SERVER}/libnetfilter_queue-1.0.4-3.el8.{ARCH}.rpm")
os_system_sure(f"unzip k8s_127_{ARCH}.zip")


flist=os.listdir(".")
flist_match=[]
# check completion
for installer_prefix in INSTALLERS:
    if not any([f.startswith(installer_prefix) for f in flist]):
        print(f"Error: {installer_prefix} not found in ../installers/k8s")
        print("Please run 1.download.py first")
        exit(1)
    else:
        installers=[f for f in flist if f.startswith(installer_prefix)]
        installers=[f for f in installers if f.find(ARCH)!=-1]
        flist_match.append(installers[0])

for f in flist_match:
    os_system(f"sudo rpm -ivh {f}")

# Create the systemd drop-in file /etc/systemd/system/kubelet.service.d/0-containerd.conf:
# [Service]                                                 
# Environment="KUBELET_EXTRA_ARGS=--container-runtime=remote --runtime-request-timeout=15m --container-runtime-endpoint=unix:///run/containerd/containerd.sock"
os_system_sure("sudo mkdir -p /etc/systemd/system/kubelet.service.d")
with open("/etc/systemd/system/kubelet.service.d/0-containerd.conf", "w") as f:
    f.write("[Service]\n")
    f.write("Environment=\"KUBELET_EXTRA_ARGS=--container-runtime=remote --runtime-request-timeout=15m --container-runtime-endpoint=unix:///run/containerd/containerd.sock\"\n")

# sudo systemctl daemon-reload
os_system_sure("sudo systemctl daemon-reload")
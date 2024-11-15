import os, sys
CUR_FDIR = os.path.dirname(os.path.abspath(__file__)); cur_scan=CUR_FDIR; scan=[["pylib.py" in os.listdir(cur_scan),cur_scan,exec('global cur_scan;cur_scan=os.path.join(cur_scan, "..")')] for _ in range(10)]; found_pylib=[x[0] for x in scan]; pylib_dir_idx=found_pylib.index(True); assert pylib_dir_idx>=0, "pylib.py not found"; print(scan[pylib_dir_idx][1]); ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, scan[pylib_dir_idx][1])); sys.path.append(ROOT_DIR)
os.chdir(CUR_FDIR)
import pylib

pylib.python_sure("../../as_conf_prepare.py")


# # https://github.com/containerd/containerd/blob/main/docs/getting-started.md
# pylib.allow_fail(os.mkdir,"../../installers/containerd")
# os.chdir("../../installers/containerd")
# URLS=[
#     "https://github.com/containerd/containerd/releases/download/v1.7.0/cri-containerd-1.7.0-linux-amd64.tar.gz",
#     "https://github.com/containerd/containerd/releases/download/v1.7.0/cri-containerd-1.7.0-linux-arm64.tar.gz"
# ]
# for url in URLS:
#     if not os.path.exists(url.split("/")[-1]):
#         pylib.allow_fail(os.system,f"wget {url}")

# os.chdir(CUR_FDIR)
# pylib.copy("_remote_installer.py", "../../installers/containerd/")

# if not os.path.exists("cri-containerd-1.3.4.linux-amd64.tar.gz"):
    # os.system("wget https://github.com/containerd/containerd/releases/download/v1.7.0/cri-containerd-1.7.0-linux-amd64.tar.gz")

# 暂时没有arm的 https://github.com/kinvolk/containerd-cri/blob/master/docs/installation.md
# 不过我们目前新机子都是x86，暂时不用下载arm的
# if not os.path.exists("cri-containerd-1.2.4.linux-arm.tar.gz"):
#     os.system("wget https://storage.googleapis.com/cri-containerd-release/cri-containerd-1.2.4.linux-arm64.tar.gz")
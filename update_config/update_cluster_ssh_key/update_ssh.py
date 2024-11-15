import os, sys
CUR_FDIR = os.path.dirname(os.path.abspath(__file__)); cur_scan=CUR_FDIR; scan=[["pylib.py" in os.listdir(cur_scan),cur_scan,exec('global cur_scan;cur_scan=os.path.join(cur_scan, "..")')] for _ in range(10)]; found_pylib=[x[0] for x in scan]; pylib_dir_idx=found_pylib.index(True); assert pylib_dir_idx>=0, "pylib.py not found"; print(scan[pylib_dir_idx][1]); ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, scan[pylib_dir_idx][1])); sys.path.append(ROOT_DIR)
os.chdir(CUR_FDIR)
import pylib, yaml, base64

# configs
NODES_CONF="nodes_jd.yml"

# logics
with open(os.path.join(ROOT_DIR,NODES_CONF),encoding='utf-8') as f:
    conf=yaml.safe_load(f)

ssh_private=conf['ssh_private']
ssh_private_base64=base64.b64encode(ssh_private.encode()).decode()
for node in conf['nodes']:
    ip=node["ip"]
    user=node["user"]
    remote_run_script=os.path.join(CUR_FDIR,"template/remote_update_ssh.py")
    print(f"updating ssh on node {ip} for user {user}")
    pylib.os_system(f"scp {remote_run_script} {user}@{ip}:~/remote_update_ssh.py")
    pylib.os_system(f'ssh {user}@{ip} "python3 ~/remote_update_ssh.py {ssh_private_base64}"')

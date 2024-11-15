import os, sys
CUR_FDIR = os.path.dirname(os.path.abspath(__file__)); cur_scan=CUR_FDIR; scan=[["pylib.py" in os.listdir(cur_scan),cur_scan,exec('global cur_scan;cur_scan=os.path.join(cur_scan, "..")')] for _ in range(10)]; found_pylib=[x[0] for x in scan]; pylib_dir_idx=found_pylib.index(True); assert pylib_dir_idx>=0, "pylib.py not found"; print(scan[pylib_dir_idx][1]); ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, scan[pylib_dir_idx][1])); sys.path.append(ROOT_DIR)
os.chdir(CUR_FDIR)
import pylib
import yaml

APPNAME="k8s_kubepi"


pylib.python_sure(f"../dispatch_to_main_node.py /home/teleinfra/tmp/{APPNAME} config.yml")


# apply
with open("../../nodes.yml","r") as f:
    conf=yaml.safe_load(f)
conf=pylib.ConfReader(conf)
main_node=conf.get_main_node()
main_node_ip=main_node["ip"]
pylib.os_system_sure(f'ssh teleinfra@{main_node_ip} "sudo chmod -R 555 /home/teleinfra/tmp/ && kubectl apply -f /home/teleinfra/tmp/{APPNAME}/config.yml"')
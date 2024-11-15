import os,sys
CUR_FDIR = os.path.dirname(os.path.abspath(__file__)); cur_scan=CUR_FDIR; scan=[["pylib.py" in os.listdir(cur_scan),cur_scan,exec('global cur_scan;cur_scan=os.path.join(cur_scan, "..")')] for _ in range(10)]; found_pylib=[x[0] for x in scan]; pylib_dir_idx=found_pylib.index(True); assert pylib_dir_idx>=0, "pylib.py not found"; print(scan[pylib_dir_idx][1]); ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, scan[pylib_dir_idx][1])); sys.path.append(ROOT_DIR)
os.chdir(CUR_FDIR)
import pylib

conf=pylib.ConfReader()
main_node=conf.get_main_node()
main_node_ip=main_node['ip']
main_node_rclone=conf.get_main_node_rclone()
pylib.os_system_sure(f'rclone sync _update_k8s_config.py {main_node_rclone}:/tmp')
pylib.os_system_sure(f'ssh teleinfra@{main_node_ip} "sudo python3 /tmp/_update_k8s_config.py"')
pylib.os_system_sure(f'ssh teleinfra@{main_node_ip} "rm -f /tmp/_update_k8s_config.py"')
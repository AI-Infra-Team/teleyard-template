import os, sys
CUR_FDIR = os.path.dirname(os.path.abspath(__file__)); cur_scan=CUR_FDIR; scan=[["pylib.py" in os.listdir(cur_scan),cur_scan,exec('global cur_scan;cur_scan=os.path.join(cur_scan, "..")')] for _ in range(10)]; found_pylib=[x[0] for x in scan]; pylib_dir_idx=found_pylib.index(True); assert pylib_dir_idx>=0, "pylib.py not found"; print(scan[pylib_dir_idx][1]); ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, scan[pylib_dir_idx][1])); sys.path.append(ROOT_DIR)
os.chdir(CUR_FDIR)
import pylib


pylib.python_sure("../../as_conf_upload.py")
# images=[
#     'prom/alertmanager:v0.26.0',
#     'quay.io/prometheus-operator/prometheus-config-reloader:v0.67.1',
#     'prom/prometheus:v2.46.0',
#     'grafana/grafana:9.5.3',
#     'bats/bats:v1.4.1',
#     'curlimages/curl:7.85.0',
#     'library/busybox:1.31.1',
#     'quay.io/kiwigrid/k8s-sidecar:1.27.4',
#     'grafana/grafana-image-renderer:lastet',
#     'registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.9.2',
#     'quay.io/brancz/kube-rbac-proxy:v0.14.2',
#     'quay.io/prometheus/node-exporter:v1.6.1',
#     'quay.io/prometheus/pushgateway:latest'
# ]

# for image in images:
#     pylib.python_sure(f"../container_image/upload.py {image}")
# pylib.python_sure(f"../container_image/upload.py {' '.join(images)}")
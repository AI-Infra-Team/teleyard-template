import os, sys
CUR_FDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CUR_FDIR)
ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, "../.."))
sys.path.append(ROOT_DIR)
import pylib

pylib.python_sure(f"../../as_conf_upload.py")

# APP_NAME="bottom"

# pylib.python_sure(f"../dispatch_to_main_node.py /tele_data_share/public/install/ ../../installers/{APP_NAME}")
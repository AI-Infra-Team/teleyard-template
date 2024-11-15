# import os

# os.system("""python3 -c 'import urllib.request, os; script = urllib.request.urlopen("http://10.127.20.218:8003/bin_easy_config/add_tele_host.py").read(); print(script.decode())' | python3""")

# print("setting up pip source")

# source="""
# [global]
# index-url = http://pypi.chinatelecom.ai/simple/
# [install]
# trusted-host=pypi.chinatelecom.ai
# """

# with open("/etc/pip.conf","w") as f:
#     f.write(source)

import os
import urllib.request

# Download the script from the URL
script_url = "http://10.127.20.218:8003/bin_easy_config/add_tele_host.py"
script = urllib.request.urlopen(script_url).read()

# Print the script's content
exec(script.decode())

# Setting up pip source
print("Setting up pip source")

# Windows uses pip.ini, typically located in the user’s AppData directory
pip_config_path = os.path.join(os.getenv('APPDATA'), 'pip', 'pip.ini')

# Source configuration for pip
source = """
[global]
index-url = http://pypi.chinatelecom.ai/simple/
[install]
trusted-host=pypi.chinatelecom.ai
"""

# Ensure the pip directory exists
pip_dir = os.path.dirname(pip_config_path)
if not os.path.exists(pip_dir):
    os.makedirs(pip_dir)

# Write the configuration to pip.ini
with open(pip_config_path, "w") as f:
    f.write(source)

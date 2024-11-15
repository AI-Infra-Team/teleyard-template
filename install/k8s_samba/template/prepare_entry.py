import os
import yaml

with open("/app/s3_conf/storage.yml") as f:
    conf=yaml.safe_load(f)

entry_sh=""
dir_2_users={}
admin_users=[]
for user in conf:
    user_passwd=conf[user]['password']
    # add user
    entry_sh+=f'useradd -m {user}\n'
    entry_sh+=f"usermod -aG root {user}\n"
    entry_sh+=f'echo -e "{user_passwd}\\n{user_passwd}" | smbpasswd -a {user}\n'
    
    if '*' in conf[user]['dir']:
        admin_users.append(user)
    else:
        for dir in conf[user]['dir']:
            if dir not in dir_2_users:
                dir_2_users[dir]=set()
            dir_2_users[dir].add(user)

# '*' should have access to all dirs
for admin in admin_users:
    for dir in dir_2_users:
        dir_2_users[dir].add(admin)

smb_conf="""
[global]
   workgroup = WORKGROUP
   server string = Samba Server Version %v
   netbios name = SAMBA
   force user = root
   force group = root
   security = user
   map to guest = bad user
"""
for dir in dir_2_users:
    if not os.path.exists(f"/share/{dir}"):
        entry_sh+=f"""
mkdir -p /share/{dir}
chown root:root /share/{dir}
chmod 775 /share/{dir}
"""
        # os.makedirs(f"/share/{dir}")
        # os.system(f"chown -R root:root /share/{dir}")
        # os.system(f"chmod 775 /share/{dir}")
    users=dir_2_users[dir]
    users_conn=', '.join(users)
    smb_conf+=f"""

[{dir}]
   path = /share/{dir}
   browsable = yes
   read only = no
   valid users = {users_conn}
   create mask = 0777
   force create mode = 0777
   directory mask = 0777
   force directory mode = 0777
"""
entry_sh+=f"""
cat > /etc/samba/smb.conf <<EOF
{smb_conf}
EOF
"""

entry_sh+="""
/bin/bash /usr/bin/samba.sh
"""

with open("/app/prepare_entry/entry.sh","w") as f:
    f.write(entry_sh)

print("==== entry.sh ===")

print(entry_sh)

print("=================")
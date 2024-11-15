import os, sys, base64

def os_system(command):
    print("RUN CMD:",command)
    os.system(command)

if len(sys.argv)!=2:
    print("Usage: python3 remote_update_ssh.py [ssh secret]")
    exit(1)

ssh_secret=sys.argv[1]
ssh_secret=base64.b64decode(ssh_secret).decode()

sshpath=os.path.expanduser("~/.ssh")
sshauthpath=os.path.join(sshpath,"authorized_keys")
# verify user .ssh/authorized_keys exists
if not os.path.exists(sshauthpath):
    os_system(f"mkdir -p {sshpath}")
    # os_system("touch ~/.ssh/authorized_keys")
    with open(sshauthpath,"w") as f:
        f.write("")

with open(sshauthpath) as f:
    content=f.read()
    if ssh_secret not in content:
        new_auth=content+"\n"+ssh_secret
    else:
        new_auth=None

if new_auth:
    with open(sshauthpath,"w") as f:
        f.write(new_auth)
else:
    print("SSH key already exists, skip adding")

os_system(f"chmod 600 {sshauthpath}")

def delete_self():
    self=os.path.abspath(__file__)
    os.remove(self)
    print("Removed self, update finished")
delete_self()
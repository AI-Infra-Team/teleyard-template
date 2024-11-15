import os
import yaml
import json
import sys
import requests
import urllib.parse as urlparse
import time
import socket    

with open("/app/s3_conf/juice.yml") as f:
    conf=yaml.safe_load(f)


dir_2_users={}
ROOT_DIR="/var/lib/sftpgo"
prev_init_script=""


def generate_links():
    global prev_init_script
    global dir_2_users
    global ROOT_DIR
    
    for user in conf:
        prev_init_script+=f"mkdir -p {ROOT_DIR}/{user}\n"
    with open("/app/prepare_entry/init.sh","w") as f:
        f.write(prev_init_script)
generate_links()


def wait_for_port(host, port):
    """
    Wait for a specific port to become available.

    :param host: The host to check.
    :param port: The port to check.
    :param timeout: Maximum time to wait in seconds.
    :return: True if the port becomes available within the timeout, False otherwise.
    """
    print("Waiting for SFTPGo to be ready...")
    while True:
        try:
            # Create a socket object
            with socket.create_connection((host, port), timeout=1):
                print(f"Port {port} on {host} is open!")
                return True
        except (socket.timeout, ConnectionRefusedError):
            pass
        time.sleep(1)  # Wait for 1 second before trying again
wait_for_port("127.0.0.1",2022) 
time.sleep(5)





# change base_url to point to your SFTPGo installation
base_url = "http://127.0.0.1:8080"
# set to False if you want to skip TLS certificate validation
verify_tls_cert = False
# set the credentials for a valid admin here
admin_user = os.environ['SFTPGO_DEFAULT_ADMIN_USERNAME']
admin_password = os.environ['SFTPGO_DEFAULT_ADMIN_PASSWORD']


# get a JWT token
auth = requests.auth.HTTPBasicAuth(admin_user, admin_password)
r = requests.get(urlparse.urljoin(base_url, "api/v2/token"), auth=auth, verify=verify_tls_cert, timeout=10)
if r.status_code != 200:
    print("error getting access token: {}".format(r.text))
    sys.exit(1)
access_token = r.json()["access_token"]
auth_header = {"Authorization": "Bearer " + access_token}




# os.system("ls /share")
# os.system(f"ls {ROOT_DIR}")

# collect all of the dirs for *
for user in conf:
    if '*' in conf[user]['dir']:
        pass
    else:
        for dir in conf[user]['dir']:
            if dir not in dir_2_users:
                dir_2_users[dir]=set()
            dir_2_users[dir].add(user)
            # all_dirs[dir]=1

for user in conf:
    if '*' in conf[user]['dir']:
        for dir in dir_2_users:
            dir_2_users[dir].add(user)

for dir in dir_2_users:
    dir_users=dir_2_users[dir]

    # https://github.com/drakkan/sftpgo/blob/c69fbe6bf9333d3f0081f5ac0e7f0e458831c469/internal/vfs/folder.go#L29
    # type BaseVirtualFolder struct {
    #     ID            int64  `json:"id"`
    #     Name          string `json:"name"`
    #     MappedPath    string `json:"mapped_path,omitempty"`
    #     Description   string `json:"description,omitempty"`
    #     UsedQuotaSize int64  `json:"used_quota_size"`
    #     // Used quota as number of files
    #     UsedQuotaFiles int `json:"used_quota_files"`
    #     // Last quota update as unix timestamp in milliseconds
    #     LastQuotaUpdate int64 `json:"last_quota_update"`
    #     // list of usernames associated with this virtual folder
    #     Users []string `json:"users,omitempty"`
    #     // list of group names associated with this virtual folder
    #     Groups []string `json:"groups,omitempty"`
    #     // Filesystem configuration details
    #     FsConfig Filesystem `json:"filesystem"`
    # }

    folder_req={
        "id":0,
        "name": dir,
        "mapped_path": f"/share/{dir}",
        "description": "",
        "used_quota_size": 0,
        "used_quota_files": 0,
        "last_quota_update": 0,
        "users": [user for user in dir_users],
        "groups": [],
        "filesystem": {
            "redacted-secret": "",
            "provider": 0 # https://github.com/sftpgo/sdk/blob/64fc18a344f9c87be4f028ffb7a851fad50976f0/filesystem.go#L20
                          # 0: local
        },
    }
    print("creating folder",folder_req)
    r = requests.post(os.path.join(base_url, os.path.join("api/v2/folders")),
                      headers=auth_header, verify=verify_tls_cert, json=folder_req, timeout=10)
    if r.status_code == 201:
        print("folder {} updated".format(dir))
        print(r.text)
    else:
        print("error updating folder {}, response code: {} response text: {}".format(dir,r.status_code,r.text))


for user in conf:
    # https://github.com/sftpgo/sdk/blob/64fc18a344f9c87be4f028ffb7a851fad50976f0/user.go#L316    
    # // BaseUser defines the shared user fields
    # type BaseUser struct {
    #     // Data provider unique identifier
    #     ID int64 `json:"id"`
    #     // 1 enabled, 0 disabled (login is not allowed)
    #     Status int `json:"status"`
    #     // Username
    #     Username string `json:"username"`
    #     // Password used for password authentication.
    #     // For users created using SFTPGo REST API the password is be stored using bcrypt or argon2id hashing algo.
    #     // Checking passwords stored with pbkdf2, md5crypt and sha512crypt is supported too.
    #     Password string `json:"password,omitempty"`
    #     // Indicates whether the password is set
    #     HasPassword bool `json:"has_password,omitempty"`
    #     // The user cannot upload or download files outside this directory. Must be an absolute path
    #     HomeDir string `json:"home_dir"`
    #     // If SFTPGo runs as root system user then the created files and directories will be assigned to this system UID
    #     UID int `json:"uid"`
    #     // If SFTPGo runs as root system user then the created files and directories will be assigned to this system GID
    #     GID int `json:"gid"`
    #     // Maximum concurrent sessions. 0 means unlimited
    #     MaxSessions int `json:"max_sessions"`
    #     // Maximum size allowed as bytes. 0 means unlimited
    #     QuotaSize int64 `json:"quota_size"`
    #     // Maximum number of files allowed. 0 means unlimited
    #     QuotaFiles int `json:"quota_files"`

    #     // List of permissions granted per-directory
    #     Permissions map[string][]string `json:"permissions"`
    #     // Maximum data transfer allowed for uploads as MB. 0 means no limit.
    #     // You can periodically reset the data related transfer fields for example
    #     // each month
    #     UploadDataTransfer int64 `json:"upload_data_transfer"`
    #     // Maximum data transfer allowed for downloads as MB. 0 means no limit.
    #     DownloadDataTransfer int64 `json:"download_data_transfer"`
    #     // Maximum total data transfer as MB. 0 means unlimited.
    #     // You can set a total data transfer instead of the individual values
    #     // for uploads and downloads
    #     TotalDataTransfer int64 `json:"total_data_transfer"`
    #     
    #     // Creation time as unix timestamp in milliseconds. It will be 0 for admins created before v2.2.0
    #     CreatedAt int64 `json:"created_at"`
    #     // last update time as unix timestamp in milliseconds
    #     UpdatedAt int64 `json:"updated_at"`
    #     
    # }
    # https://github.com/drakkan/sftpgo/blob/c69fbe6bf9333d3f0081f5ac0e7f0e458831c469/internal/dataprovider/user.go#L138
    # type User struct {
    #     sdk.BaseUser
    #     // Additional restrictions
    #     Filters UserFilters `json:"filters"`
    #     // Mapping between virtual paths and virtual folders
    #     VirtualFolders []vfs.VirtualFolder `json:"virtual_folders,omitempty"`
    #     // Filesystem configuration details
    #     FsConfig vfs.Filesystem `json:"filesystem"`
    #     // groups associated with this user
    #     Groups []sdk.GroupMapping `json:"groups,omitempty"`
    #     // we store the filesystem here using the base path as key.
    #     fsCache map[string]vfs.Fs `json:"-"`
    #     // true if group settings are already applied for this user
    #     groupSettingsApplied bool `json:"-"`
    #     // in multi node setups we mark the user as deleted to be able to update the webdav cache
    #     DeletedAt int64 `json:"-"`
    # }
    # // Filesystem defines filesystem details
    # type Filesystem struct {
    #     RedactedSecret string                 `json:"-"`
    #     Provider       sdk.FilesystemProvider `json:"provider"`
    #     OSConfig       sdk.OSFsConfig         `json:"osconfig,omitempty"`
    #     S3Config       S3FsConfig             `json:"s3config,omitempty"`
    #     GCSConfig      GCSFsConfig            `json:"gcsconfig,omitempty"`
    #     AzBlobConfig   AzBlobFsConfig         `json:"azblobconfig,omitempty"`
    #     CryptConfig    CryptFsConfig          `json:"cryptconfig,omitempty"`
    #     SFTPConfig     SFTPFsConfig           `json:"sftpconfig,omitempty"`
    #     HTTPConfig     HTTPFsConfig           `json:"httpconfig,omitempty"`
    # }
    def new_dir_req(dir):
        dir_users=dir_2_users[dir]
        return {
            "id":0,
            "name": dir,
            "mapped_path": f"/share/{dir}",
            "description": "",
            "used_quota_size": 0,
            "used_quota_files": 0,
            "last_quota_update": 0,
            "users": [user for user in dir_users],
            "groups": [],
            "filesystem": {
                "redacted-secret": "",
                "provider": 0 # https://github.com/sftpgo/sdk/blob/64fc18a344f9c87be4f028ffb7a851fad50976f0/filesystem.go#L20
                            # 0: local
            },
            "virtual_path": f"/{dir}"
        }
    
    
    if '*' in conf[user]['dir']:
        user_folders=[new_dir_req(dir) for dir in dir_2_users.keys()]
    else:
        user_folders=[new_dir_req(dir) for dir in conf[user]['dir']]
        
    user_req={
        "id":0,
        "status": 1,
        "username": user,
        "password": conf[user]['password'],
        "has_password": True,
        "home_dir": f"{ROOT_DIR}/{user}",
        "uid": 0,
        "gid": 0,
        "max_sessions": 0,
        "quota_size": 0,
        "quota_files": 0,
        "permissions": {
            "/":["*"]
        },
        "upload_data_transfer":0,
        "download_data_transfer":0,
        "total_data_transfer":0,
        "created_at":0,
        "updated_at":0,
        "filters": {},
        "virtual_folders": user_folders,
        "filesystem": {
            "redacted-secret": "",
            "provider": 0 # https://github.com/sftpgo/sdk/blob/64fc18a344f9c87be4f028ffb7a851fad50976f0/filesystem.go#L20
                          # 0: local
        },
        "fs-cache": {},
        "group-settings-applied": False,
        "deleted-at": 0
    }

    r = requests.post(os.path.join(base_url, os.path.join("api/v2/users")),
			headers=auth_header, verify=verify_tls_cert, json=user_req, timeout=10)
    if r.status_code == 201:
        print("user {} updated".format(user))
    else:
        print("error updating user {}, response code: {} response text: {}".format(user,r.status_code,r.text))
        

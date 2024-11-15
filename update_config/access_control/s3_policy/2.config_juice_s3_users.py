
import os, sys, yaml, json, time
CUR_FDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CUR_FDIR)
ROOT_DIR=os.path.abspath(os.path.join(CUR_FDIR, "../../.."))
sys.path.append(ROOT_DIR)
import pylib

USERS=pylib.get_secret_data(key='juice_s3_policy_conf')
USERS=yaml.safe_load(USERS)

FSNAME='telejfs'

for user in USERS:
    pw=USERS[user]['password']
    pylib.os_system(f"mc admin user add {FSNAME} {user} {pw}")
    time.sleep(5)
    
    # generate dirs content
    #  like:
    #  [
    #      "arn:aws:s3:::telejfs/public/*",
    #      "arn:aws:s3:::telejfs/{user}/*"
    #  ]
    dirs=[]
    if '*' in USERS[user]['dir']:
        dirs.append("arn:aws:s3:::telejfs/*")
    else:
        for dir in USERS[user]['dir']:
            dirs.append(f"arn:aws:s3:::telejfs/{dir}/*")
    
    # rw access to telejfs/public & telejfs/{user}
    policy_name = user.split('_')[-1]
    policy_name += '-policy'
    
    policy={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListBucketVersions",
                        "s3:ListMultipartUploadParts",
                        "s3:AbortMultipartUpload",
                        "s3:DeleteObject",
                        "s3:GetObject",
                        "s3:ListMultipartUploadParts",
                        "s3:PutObject",
                        "s3:CreateBucket",
                        "s3:DeleteBucket",
                    ],
                    "Resource": dirs
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListBucketVersions",
                        "s3:ListMultipartUploadParts"
                    ],
                    "Resource": [
                        "arn:aws:s3:::telejfs"
                    ]
                }
            ]
        }
    
    tmpdir=os.path.join(pylib.current_user_dir(),"tmp")
    pylib.mkdir(tmpdir)
    with open(f'{tmpdir}/{policy_name}.json','w') as f:
        f.write(json.dumps(policy))
        
    pylib.os_system(f"mc admin policy unset {FSNAME} {policy_name} user={user}")
    pylib.os_system(f"mc admin policy remove {FSNAME} {policy_name}")
    pylib.os_system(f"mc admin policy add {FSNAME} {policy_name} {tmpdir}/{policy_name}.json")
    time.sleep(5)
    pylib.os_system(f"mc admin policy set {FSNAME} {policy_name} user={user}")

pylib.os_system(f"mc admin user list {FSNAME}")
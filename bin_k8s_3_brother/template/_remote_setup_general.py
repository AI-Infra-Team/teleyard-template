import os, subprocess, yaml, time, socket


def os_system_sure(command):
    print(f"执行命令：{command}")
    result = os.system(command)
    if result != 0:
        print(f"命令执行失败：{command}")
        exit(1)
    print(f"命令执行成功：{command}\n\n") 

os_system_sure("mkdir -p /tmp/k8s_setup")
os.chdir("/tmp/k8s_setup")

os_system_sure("scp teleinfra@${MAIN_NODE_IP}:/teledeploy_secret/bin_k8s_3_brother/nodes.yml ./nodes.yml")

# match pattern xxx{}xxx  any word in {} will be replaced by replace_with
import re
def update_or_replace_line_in_file(file_path, match, replace_with):
    assert match.find("\n") == -1
    assert match.find("{}") != -1

    with open(file_path, "r") as f:
        content=f.read()
        oldines=content.split("\n")
        newline=match.replace("{}",replace_with)
        need_add=True

        # match any word in {}
        match=match.replace("{}",".*")
        for (i,l) in enumerate(oldines):
            result = re.search(match, l)
            if result:
                # replace old line, dont use copy line
                print("update line ",l,"to",newline)
                oldines[i]=newline
                need_add=False
                break
        if need_add:
            oldines.append(newline)
            print("add line",newline)
        newcontent="\n".join(oldines)
    with open(file_path, "w") as f:
        f.write(newcontent)

def cgroup_driver_systemd():
    # /etc/sysconfig/kubelet
    # KUBELET_EXTRA_ARGS="--cgroup-driver=systemd" 
    CGROUP_DRIVER_CONF_PATH={
        'p':"/etc/sysconfig/kubelet"
    }
    def cgroup_driver_systemd():
        # global CGROUP_DRIVER_CONF_PATH
        with open(CGROUP_DRIVER_CONF_PATH['p'], "r") as f:
            content=f.read()
            line="""KUBELET_EXTRA_ARGS="--cgroup-driver=systemd"
        """
            oldines=content.split("\n")
            need_add=True
            for (i,l) in enumerate(oldines):
                if l.find("KUBELET_EXTRA_ARGS") != -1:
                    # replace old line, dont use copy line
                    oldines[i]=line
                    need_add=False
                    break
            if need_add:
                oldines.append(line)
            newcontent="\n".join(oldines)
        with open(CGROUP_DRIVER_CONF_PATH['p'], "w") as f:
            # print("write to",CGROUP_DRIVER_CONF_PATH['p'])
            # print(" with",newcontent)
            f.write(newcontent)
    cgroup_driver_systemd()

    def test_cgroup_driver_systemd():
        # global CGROUP_DRIVER_CONF_PATH
        def test(content):
            CGROUP_DRIVER_CONF_PATH['p']="tempfile"
            with open(CGROUP_DRIVER_CONF_PATH['p'], "w") as f:
                f.write(content)
            cgroup_driver_systemd()
            with open(CGROUP_DRIVER_CONF_PATH['p'], "r") as f:
                print("read from ",CGROUP_DRIVER_CONF_PATH['p'])
                newcontent=f.read()
                assert newcontent.count("KUBELET_EXTRA_ARGS") == 1
                assert newcontent.find('KUBELET_EXTRA_ARGS="--cgroup-driver=systemd"') !=-1
            # remove tempfile
            os.remove(CGROUP_DRIVER_CONF_PATH['p'])
        test('KUBELET_EXTRA_ARGS="--cgroup-driver=systemd"\n')
        test('KUBELET_EXTRA_ARGS=')
        print("test_cgroup_driver_systemd passed")
    # test_cgroup_driver_systemd()
cgroup_driver_systemd()    
# exit(0)

    
# master side
def containerd_and_img_repo_config():
    setup_conf=yaml.safe_load(open("nodes.yml"))

    print(f'mapping img repository host {setup_conf["imageRepository"]} to {setup_conf["imageRepositoryHost"]} in /etc/hosts')
    hostname=setup_conf['imageRepository']
    if hostname.find("http://") != -1:
        hostname=hostname[len("http://"):]
    if hostname.find("https://") != -1:
        hostname=hostname[len("https://"):]
    if hostname.find("/") != -1:
        hostname=hostname[:hostname.find("/")]
    # insert nameserver 127.0.0.1 to first line
    with open("/etc/hosts", "r") as f:
        content=f.read()
        lines=content.split("\n")
        # self ip to self hostname
        self_host=socket.gethostname()
        img_repo_host=setup_conf['imageRepositoryHost']
        img_repo_ip=setup_conf['imageRepositoryHostIp']
        with open("nodes.yml") as f:
            nodes_conf=yaml.safe_load(f)["nodes"]
        self_ips=socket.gethostbyname_ex(self_host)[2]
        self_ip=[node['ip'] for node in nodes_conf if node['ip'] in self_ips][0]
        # remove old self host
        lines=[l for l in lines if l.find(self_host) == -1]
        lines=[l for l in lines if l.find(img_repo_host) == -1]
        # add new self host
        lines.insert(0,f"{self_ip} {self_host}")
        lines.insert(0,f"{img_repo_ip} {img_repo_host}")
        with open("/etc/hosts", "w") as f:
            f.write("\n".join(lines))

        # remove_old_127_0_0_1
        # lines=[l for l in lines if l.find("127.0.0.1") == -1]
        # lines.insert(0,"nameserver 127.0.0.1")
        # with open("/etc/hosts", "w") as f:
        #     f.write("\n".join(lines))

    print("generate /etc/containerd/certs.d/{镜像源host}/hosts.toml")
    REPO_HOST=setup_conf['imageRepositoryHost']
    os_system_sure(f"mkdir -p /etc/containerd/certs.d/{REPO_HOST}")
    with open(f"/etc/containerd/certs.d/{REPO_HOST}/hosts.toml", "w") as f:
        f.write(f"""server = "http://{REPO_HOST}"

[host."http://{REPO_HOST}"]
  capabilities = ["pull", "resolve", "push"]
  skip_verify = true
""")
        # 644, 6：rw, 4：r
        os_system_sure(f"chmod 644 /etc/containerd/certs.d/{REPO_HOST}/hosts.toml")


    print(f"update image registry passwd in /etc/containerd/config.toml")
    ##################
    # no config case #
    ##################
    REPO_PW=setup_conf['imageRepositoryPw']
    REPO_HOST=setup_conf['imageRepositoryHost']
    if not os.path.exists("/etc/containerd/config.toml"):
        os_system_sure("mkdir -p /etc/containerd")
        os_system_sure("chmod 777 /etc/containerd")
        os_system_sure("containerd config default > /etc/containerd/config.toml")
        with open ("/etc/containerd/config.toml", "r") as f:
            content=f.read()
        # registry configs
        content=content.replace('[plugins."io.containerd.grpc.v1.cri".registry.configs]',f"""[plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.vl.cri".registry.configs."{REPO_HOST}".tls]
          insecure_skip_verify = true
          ca_file = "/etc/harbor/ssl/ca.pem"
          cert_file = "/etc/harbor/ssl/harbor.pem"
          key_file = "/etc/harbor/ssl/harbor-key.pem"
        [plugins."io.containerd.grpc.vl.cri".registry.configs."{REPO_HOST}".auth]
          username = "admin"
          password = "{REPO_PW}" """)
        content=content.replace('[plugins."io.containerd.grpc.v1.cri".registry.mirrors]',f"""[plugins."io.containerd.grpc.v1.cri".registry.mirrors]
        [plugins."io.containerd.grpc.vl.cri".registry.mirrors."{REPO_HOST}"]
          endpoint = ["http://{REPO_HOST}"] """)

        with open("/etc/containerd/config.toml", "w") as f:
            f.write(content)
        os_system_sure("chmod 644 -R /etc/containerd")
    ###################
    #   with config   #
    ###################
    else:
        with open ("/etc/containerd/config.toml", "r") as f:
            content=f.read()
            hostname=setup_conf['imageRepositoryHost']
            newpw=setup_conf['imageRepositoryPw']
            oldines=content.split("\n")
            match_registry_auth='[plugins."io.containerd.grpc.vl.cri".registry.configs."{}".auth]'
            re_match_registry_auth=match_registry_auth.replace(".", "\.").replace("[", "\[").replace("]", "\]").replace('"', '\\"').replace("{}", "(.*)")
            print(re_match_registry_auth)
            # find line with `match_registry_auth`
            for (i,l) in enumerate(oldines):
                result = re.search(re_match_registry_auth, l)
                if result:
                    # replace old line match with hostname
                    new_line = re.sub(re_match_registry_auth, match_registry_auth.replace("{}",hostname), l)
                    
                    # print("update line ",l,"to",new_line)
                    oldines[i]=new_line

                    # find password in next 2 line
                    if oldines[i+2].find("password"):
                        oldines[i+2]=oldines[i+2].split('=')[0]+f'= "{newpw}"'
                    break
            newcontent="\n".join(oldines)
            with open("/etc/containerd/config.toml", "w") as f:
                f.write(newcontent)
    ####################
    #   general case   #
    ####################
    with open ("/etc/containerd/config.toml", "r") as f:
        content=f.read()
        # systemc cgroup
        content=content.replace('SystemdCgroup = false','SystemdCgroup = true')
        
        # pause version 3.9
        REPO_ADDR=setup_conf['imageRepository']
        content=re.sub(r'sandbox_image\s*=\s*"(\S+)"',f'sandbox_image = "{REPO_ADDR}/pause:3.9"',content)

        # certs.d
        content=re.sub(r'\[plugins\."io\.containerd\.grpc\.v1\.cri"\.registry\]\s*config_path = ".*"',
                       """[plugins."io.containerd.grpc.v1.cri".registry]
      config_path = "/etc/containerd/certs.d/\"""", content)

        with open("/etc/containerd/config.toml", "w") as f:
            f.write(content)
            
    os_system_sure("systemctl restart containerd")
    os_system_sure("systemctl enable kubelet")
    time.sleep(5)
    

containerd_and_img_repo_config()

def netfilter():
    os_system_sure("sudo modprobe br_netfilter")
    os_system_sure("sudo sysctl net.bridge.bridge-nf-call-iptables=1")
    os_system_sure("sudo sysctl net.bridge.bridge-nf-call-ip6tables=1")
    os_system_sure("sudo sysctl --system")
    # /etc/sysctl.conf
    with open("/etc/sysctl.conf", "r") as f:
        lines=f.readlines()
    lines=[l for l in lines if l.find("net.bridge.bridge-nf-call-iptables") == -1]
    lines=[l for l in lines if l.find("net.bridge.bridge-nf-call-ip6tables") == -1]
    lines.append("net.bridge.bridge-nf-call-iptables = 1\n")
    lines.append("net.bridge.bridge-nf-call-ip6tables = 1\n")
    with open("/etc/sysctl.conf", "w") as f:
        f.writelines(lines)
netfilter()


def flannel_link_resolv():
    # sudo mkdir -p /run/systemd/resolve
    # sudo ln -s /etc/resolv.conf /run/systemd/resolve/resolv.conf
    os_system_sure("systemctl enable systemd-resolved")
    os_system_sure("systemctl start systemd-resolved")
    if not os.path.exists("/run/systemd/resolve/resolv.conf"):
        os_system_sure("mkdir -p /run/systemd/resolve")
        os_system_sure("ln -s /etc/resolv.conf /run/systemd/resolve/resolv.conf")
flannel_link_resolv()
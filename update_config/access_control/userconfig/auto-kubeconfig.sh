#!/bin/bash
set -e

echo "input new username: "
read username
namespace=$username

echo "input cluster api-server: https://<ip>:<port>"
# A100 集群 KUBE_APISERVER="https://10.127.20.218:6443"
# H100 集群 KUBE_APISERVER="https://10.127.16.3:6443"

read KUBE_APISERVER
if [[ ! $KUBE_APISERVER =~ ^https://([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}$ ]]; then
    echo "URL 格式不正确"
    exit 1
fi

if [ -d "/etc/kubernetes/pki" ]; then 
    # K8S 使用 kubeadm 部署，证书在 /etc/kubernetes/pki
    workpath="/etc/kubernetes/pki"
    cacrt="../ca.crt"
    cakey="../ca.key"
else if [ -d "/opt/kubernetes/ssl" ]
    # K8S 使用其他方式部署，证书在 /opt/kubernetes/ssl
    workpath="/opt/kubernetes/ssl"
    cacrt="../ca.pem"
    cakey="../ca-key.pem"
else
    echo "CA 证书未找到"
    exit 1
fi

cd $workpath

if [ ! -d "users" ]; then
    mkdir -p users
fi
cd users

# 覆盖式写入 openssl.cnf
cat > "openssl.cnf" <<EOL
[ req ]
default_bits = 2048
default_md = sha256
distinguished_name = req_distinguished_name
 
[ req_distinguished_name ]
 
[ v3_ca ]
basicConstraints = critical, CA:TRUE
keyUsage = critical, digitalSignature, keyEncipherment, keyCertSign
 
[ v3_req_server ]
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
 
[ v3_req_client ]
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
EOL

key="${username}.key"
csr="${username}.csr"
crt="${username}.crt"
configfile="${username}.kubeconfig"
context="${username}.context"

cacrt="../ca.pem"
cakey="../ca-key.pem"

openssl genrsa -out "$key" 2048

openssl req -new -key "$key" -subj "/CN=$username/O=teleai" -out "$csr"

openssl x509 -req -in "$csr" -CA $cacrt -CAkey $cakey -CAcreateserial -extensions v3_req_client -extfile openssl.cnf -out "$crt" -days 3650

kubectl config set-cluster kubernetes \
--certificate-authority="$cacrt" \
--server=${KUBE_APISERVER} \
--embed-certs=true \
--kubeconfig="$configfile"

kubectl config set-credentials "$username" \
--client-certificate="$crt" \
--client-key="$key" \
--embed-certs=true \
--kubeconfig="$configfile"

kubectl config set-context "$context" \
--cluster=kubernetes \
--namespace="$namespace" \
--user="$username" \
--kubeconfig="$configfile"

kubectl config use-context "$context" --kubeconfig="$configfile"

echo "kubeconfig 文件生成于 $workpath/user/$username.kubeconfig"

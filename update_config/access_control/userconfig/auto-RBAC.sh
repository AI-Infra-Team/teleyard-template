#!/bin/bash
set -e

echo "input new user name:"
read username
namespace=$username

if ! kubectl get namespace "$namespace" &> /dev/null; then
    kubectl create namespace "$namespace"
    echo "Namespace $namespace created."
fi

cat << EOF > ~/${username}-RBAC.yml
# user-global-readonly-role
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: global-readonly-role
rules:
- apiGroups: ["*"]  # 通配符，表示所有 API 组
  resources: ["*"]  # 通配符，表示所有资源类型
  verbs: ["get", "list", "describe"]
---
# user-global-readonly-rolebinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ${username}-global-readonly-binding
subjects:
- kind: User
  name: ${username}
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: global-readonly-role
  apiGroup: rbac.authorization.k8s.io
---
# user-modify-role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: ${username}
  name: ${username}-modify-role
rules:
- apiGroups: ["*"]
  resources: ["*"]  # 根据需要添加其他资源
  verbs: ["*"]
---
# user-modify-rolebinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: ${username}
  name: ${username}-modify-binding
subjects:
- kind: User
  name: ${username}
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: ${username}-modify-role
  apiGroup: rbac.authorization.k8s.io
EOF

kubectl apply -f "/home/teleinfra/$username-RBAC.yml"
rm "/home/teleinfra/$username-RBAC.yml"

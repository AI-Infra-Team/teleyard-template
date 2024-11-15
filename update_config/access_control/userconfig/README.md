# 用户命名空间隔离 (Access Control) 实现

## v1 版本(使用 RBAC 硬编码实现)

### 1 功能
每个研究组具有自己的用户和 namespace，如 sora 组用户名为 sora，分发的 namespace 也名为 sora(这个 namespace 是每个用户默认的命名空间)。

sora 用户权限:

对所有 namespace 下的所有对象有 list, get, describe 权限；

对 sora namespace 下的对象有所有权限。

### 2 使用

### 2.1 user.kubeconfig 创建
```shell
sudo bash auto-kubeconfig.sh
```

### 2.2 权限绑定
```shell
bash auto-RBAC.sh
```

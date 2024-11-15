#!/bin/bash

# 检查是否以root身份运行
if [ "$(id -u)" -ne 0 ]; then
    echo "此脚本必须以 root 用户身份运行" >&2
    exit 1
fi

# 检查是否提供了正确的参数数量
if [ "$#" -ne 2 ]; then
    echo "用法: $0 <username> <password>"
    exit 1
fi

# 获取新用户名和密码
new_username=$1
initial_password=$2

# 创建新用户
adduser --disabled-password --gecos "" $new_username

# 检查用户创建是否成功
if [ $? -eq 0 ]; then
    echo "用户 $new_username 已成功创建。"

    # 设置初始密码
    echo "$new_username:$initial_password" | chpasswd

    # 检查密码设置是否成功
    if [ $? -eq 0 ]; then
        echo "初始密码已设置。"
    else
        echo "无法设置初始密码，请检查错误。"
        exit 1
    fi
else
    echo "用户创建失败，请检查错误并重试。"
    exit 1
fi

# 将新用户添加到 sudo 组
usermod -aG sudo $new_username

# 检查是否成功添加到 sudo 组
if [ $? -eq 0 ]; then
    echo "用户 $new_username 已被添加到 sudo 组。"
else
    echo "无法将用户添加到 sudo 组，请检查错误。"
    exit 1
fi

echo "完成！"
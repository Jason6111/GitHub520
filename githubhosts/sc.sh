#!/bin/bash

# 设置相关变量
PYTHON_VERSION="3.7"
SAVE_DIR="/www/wwwroot/tv.jason888.eu.org/githubhosts"

# 确保保存目录存在
echo "Ensuring save directory exists..."
sudo mkdir -p "$SAVE_DIR"

# 更新系统包和安装必要工具
echo "Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip

# 检查 Python 版本
echo "Checking Python version..."
if ! python3 --version | grep -q "$PYTHON_VERSION"; then
    echo "Python version $PYTHON_VERSION is not installed!"
    exit 1
fi

# 升级 pip
echo "Upgrading pip..."
sudo python3 -m pip install --upgrade pip

# 安装项目依赖
REQ_FILE="$SAVE_DIR/requirements.txt"
if [ -f "$REQ_FILE" ]; then
    echo "Installing dependencies from $REQ_FILE..."
    sudo pip3 install -r "$REQ_FILE"
else
    echo "No requirements.txt found in $SAVE_DIR, skipping dependency installation."
fi

# 运行 Python 脚本，将生成的文件保存到指定目录
echo "Running fetch_ips.py..."
sudo python3 "$SAVE_DIR/fetch_ips.py" > "$SAVE_DIR/output.txt"

echo "Script completed successfully. Output saved to $SAVE_DIR/output.txt."

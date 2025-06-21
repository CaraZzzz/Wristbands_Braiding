#!/usr/bin/env python3
"""
手绳编织助手后端服务启动脚本
"""

import os
import sys
import subprocess
import time

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误：需要Python 3.7或更高版本")
        sys.exit(1)
    print(f"Python版本: {sys.version}")

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "server/requirements.txt"
        ])
        print("依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        sys.exit(1)

def start_server():
    """启动Flask服务器"""
    print("正在启动Flask服务器...")
    try:
        # 切换到server目录
        os.chdir("server")
        
        # 启动服务器
        subprocess.run([
            sys.executable, "app.py"
        ])
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("=" * 50)
    print("手绳编织助手后端服务")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    install_requirements()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 
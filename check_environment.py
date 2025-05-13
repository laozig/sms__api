#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境检查脚本
检查项目环境和API服务是否正常运行
"""

import os
import sys
import socket
import requests
import importlib
import time

def check_python_version():
    """检查Python版本"""
    print(f"Python版本: {sys.version}")
    return True

def check_required_modules():
    """检查必要的模块是否存在"""
    required_modules = ['flask', 'flask_cors', 'sqlalchemy', 'jwt']
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"模块 {module} 已安装")
        except ImportError:
            missing_modules.append(module)
            print(f"模块 {module} 未安装")
    
    if missing_modules:
        print(f"缺少必要模块: {', '.join(missing_modules)}")
        return False
    
    return True

def check_database_file():
    """检查数据库文件是否存在"""
    db_path = 'sms_api.db'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"数据库文件存在: {db_path} (大小: {size} 字节)")
        return True
    else:
        print(f"数据库文件不存在: {db_path}")
        return False

def check_port_available(port=5000):
    """检查端口是否可用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        print(f"端口 {port} 已被占用 (可能是API服务正在运行)")
        return True
    else:
        print(f"端口 {port} 未被占用 (API服务可能未运行)")
        return False
    sock.close()

def check_api_connection():
    """测试API连接"""
    api_url = "http://localhost:5000/api/test"
    try:
        response = requests.get(api_url, timeout=2)
        if response.status_code == 200:
            print(f"API连接成功: {response.json()}")
            return True
        else:
            print(f"API连接失败: 状态码 {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("API连接失败: 无法连接到服务器")
        return False
    except Exception as e:
        print(f"API连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("\n=== 环境检查 ===\n")
    
    # 检查Python版本
    check_python_version()
    
    # 检查必要模块
    check_required_modules()
    
    # 检查数据库文件
    check_database_file()
    
    # 检查端口占用情况
    is_port_used = check_port_available()
    
    # 检查API连接
    if is_port_used:
        api_connected = check_api_connection()
        if not api_connected:
            print("\n端口被占用但API连接失败，可能是其他服务占用了该端口。")
    else:
        print("\nAPI服务未运行，无法测试API连接。")
        print("请运行 'python app.py' 启动服务。")
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    main() 
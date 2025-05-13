#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gunicorn配置文件
用于在生产环境中运行Flask应用
"""

import multiprocessing
import os

# 绑定的IP和端口
bind = "0.0.0.0:5000"

# 工作进程数 - 一般设置为 (2 x $num_cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式 - 使用异步工作模式以提高并发能力
worker_class = "gevent"

# 每个工作进程的最大并发请求数
worker_connections = 1000

# 请求超时时间（秒）
timeout = 120

# 重启超时工作进程，而不是杀死它们
graceful_timeout = 60

# 每个工作进程处理的最大请求数 - 超过后会重启工作进程，避免内存泄漏
max_requests = 1000
max_requests_jitter = 50  # 添加抖动避免所有工作进程同时重启

# 日志配置
accesslog = os.path.join(os.getcwd(), "logs/gunicorn_access.log")
errorlog = os.path.join(os.getcwd(), "logs/gunicorn_error.log")
loglevel = "info"

# 守护进程模式 - 生产环境设置为True
daemon = False

# 进程ID文件
pidfile = "gunicorn.pid"

# 预加载应用 - 在工作进程fork之前加载应用，节省内存
preload_app = True

# 使用gevent时设置为False
# 当使用fork()创建子进程时，子进程会继承父进程的打开文件描述符
# 这可能会导致多个进程共享文件描述符，从而导致不可预知的问题
forwarded_allow_ips = '*'

# 在使用代理的情况下，从Header获取真实的客户端IP
secure_scheme_headers = {
    'X-FORWARDED-PROTO': 'https',
}

# 限制请求行的大小
limit_request_line = 4094

# 启动前运行的钩子函数
def on_starting(server):
    """
    服务器启动前运行的钩子函数
    """
    print("Gunicorn server is starting...")
    
    # 确保日志目录存在
    if not os.path.exists("logs"):
        os.makedirs("logs")

# 工作进程启动前运行的钩子函数
def pre_fork(server, worker):
    """
    工作进程fork前运行的钩子函数
    """
    print(f"Worker {worker.pid} is about to be spawned")

# 工作进程启动后运行的钩子函数
def post_fork(server, worker):
    """
    工作进程fork后运行的钩子函数
    """
    print(f"Worker {worker.pid} has been spawned")

# 工作进程重启前运行的钩子函数
def worker_abort(worker):
    """
    工作进程异常终止前运行的钩子函数
    """
    print(f"Worker {worker.pid} is aborting") 
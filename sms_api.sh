#!/bin/bash

# SMS API服务管理脚本
# 用法: ./sms_api.sh {start|stop|restart|status}

# 配置项
APP_DIR="$(pwd)"
VENV_DIR="${APP_DIR}/venv"
GUNICORN_WORKERS=4
PORT=5000
BIND_ADDRESS="0.0.0.0:${PORT}"
LOG_DIR="${APP_DIR}/logs"
PID_FILE="${APP_DIR}/sms_api.pid"
LOG_FILE="${LOG_DIR}/sms_api.log"
GUNICORN_LOG="${LOG_DIR}/gunicorn.log"

# 创建日志目录
mkdir -p ${LOG_DIR}

# 检查虚拟环境
check_venv() {
    if [ ! -d "${VENV_DIR}" ]; then
        echo "错误: 虚拟环境不存在，请先创建虚拟环境并安装依赖"
        echo "创建命令: python3 -m venv venv"
        echo "激活命令: source venv/bin/activate"
        echo "安装依赖: pip install -r requirements.txt"
        exit 1
    fi
}

# 启动服务
start() {
    echo "正在启动SMS API服务..."
    
    # 检查服务是否已经运行
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat "${PID_FILE}")
        if ps -p ${PID} > /dev/null; then
            echo "服务已经在运行中，PID: ${PID}"
            exit 1
        else
            # PID文件存在但进程不存在，删除PID文件
            rm "${PID_FILE}"
        fi
    fi
    
    # 检查虚拟环境
    check_venv
    
    # 启动服务
    cd "${APP_DIR}"
    source "${VENV_DIR}/bin/activate"
    
    # 设置环境变量
    export FLASK_CONFIG=production
    
    # 使用nohup在后台启动Gunicorn
    nohup ${VENV_DIR}/bin/gunicorn -w ${GUNICORN_WORKERS} -b ${BIND_ADDRESS} \
        --timeout 120 --preload \
        --log-file="${GUNICORN_LOG}" \
        --pid="${PID_FILE}" \
        "app:create_app('production')" > "${LOG_FILE}" 2>&1 &
    
    # 检查启动是否成功
    sleep 2
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat "${PID_FILE}")
        if ps -p ${PID} > /dev/null; then
            echo "SMS API服务已成功启动，PID: ${PID}"
            echo "服务地址: http://${BIND_ADDRESS}"
            echo "日志文件: ${LOG_FILE}"
            echo "Gunicorn日志: ${GUNICORN_LOG}"
            exit 0
        fi
    fi
    
    echo "服务启动失败，请检查日志文件获取详细信息"
    exit 1
}

# 停止服务
stop() {
    echo "正在停止SMS API服务..."
    
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat "${PID_FILE}")
        
        if ps -p ${PID} > /dev/null; then
            echo "正在终止进程 ${PID}..."
            kill -15 ${PID}
            
            # 等待进程终止
            TIMEOUT=30
            while ps -p ${PID} > /dev/null && [ ${TIMEOUT} -gt 0 ]; do
                sleep 1
                TIMEOUT=$((TIMEOUT-1))
            done
            
            if ps -p ${PID} > /dev/null; then
                echo "进程未在规定时间内终止，强制结束进程..."
                kill -9 ${PID}
                sleep 1
            fi
            
            if ps -p ${PID} > /dev/null; then
                echo "无法终止进程 ${PID}"
                exit 1
            else
                echo "服务已停止"
                rm -f "${PID_FILE}"
            fi
        else
            echo "服务未运行，但PID文件存在，正在删除..."
            rm -f "${PID_FILE}"
        fi
    else
        echo "未找到PID文件，服务可能未运行"
        
        # 检查是否有gunicorn进程在运行
        GUNICORN_PID=$(pgrep -f "gunicorn.*app:create_app")
        if [ -n "${GUNICORN_PID}" ]; then
            echo "发现遗留的Gunicorn进程，正在终止..."
            kill -15 ${GUNICORN_PID}
            sleep 2
            if pgrep -f "gunicorn.*app:create_app" > /dev/null; then
                kill -9 $(pgrep -f "gunicorn.*app:create_app")
            fi
            echo "遗留进程已终止"
        fi
    fi
}

# 重启服务
restart() {
    stop
    sleep 2
    start
}

# 检查服务状态
status() {
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat "${PID_FILE}")
        if ps -p ${PID} > /dev/null; then
            echo "SMS API服务正在运行，PID: ${PID}"
            echo "服务地址: http://${BIND_ADDRESS}"
            echo "运行时间: $(ps -o etime= -p ${PID})"
            echo "内存使用: $(ps -o %mem= -p ${PID})%"
            echo "CPU使用: $(ps -o %cpu= -p ${PID})%"
            exit 0
        else
            echo "服务未运行，但PID文件存在"
            exit 1
        fi
    else
        # 检查是否有gunicorn进程在运行但没有PID文件
        GUNICORN_PID=$(pgrep -f "gunicorn.*app:create_app")
        if [ -n "${GUNICORN_PID}" ]; then
            echo "发现Gunicorn进程正在运行，但没有PID文件"
            echo "PID: ${GUNICORN_PID}"
            exit 2
        else
            echo "SMS API服务未运行"
            exit 3
        fi
    fi
}

# 主命令处理
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 
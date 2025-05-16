#!/bin/bash

APP_NAME="sms_flask_app"
APP_PATH="/sms/sms__api/app.py"
PROJECT_DIR="/sms/sms__api"
VENV_PATH="/sms/sms__api/venv"  # ← 修改为你的虚拟环境路径
LOG_FILE="$PROJECT_DIR/output.log"

start() {
    if pgrep -f "$APP_PATH" > /dev/null; then
        echo "$APP_NAME is already running."
    else
        echo "Starting $APP_NAME..."
        cd "$PROJECT_DIR"
        source "$VENV_PATH/bin/activate"
        nohup python "$APP_PATH" > "$LOG_FILE" 2>&1 &
        echo "$APP_NAME started. Logs: $LOG_FILE"
    fi
}

stop() {
    if pgrep -f "$APP_PATH" > /dev/null; then
        echo "Stopping $APP_NAME..."
        pkill -f "$APP_PATH"
        echo "$APP_NAME stopped."
    else
        echo "$APP_NAME is not running."
    fi
}

restart() {
    echo "Restarting $APP_NAME..."
    stop
    sleep 1
    start
}

status() {
    if pgrep -f "$APP_PATH" > /dev/null; then
        echo "$APP_NAME is running. PID(s):"
        pgrep -af "$APP_PATH"
    else
        echo "$APP_NAME is not running."
    fi
}

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
        echo "Usage: $0 {start|stop|restart|status}"
        ;;
esac

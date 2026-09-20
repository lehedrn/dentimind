#!/bin/bash

# 口腔医院AI客服系统 - 服务管理脚本
# 用法：./service.sh [start|stop|restart|status|logs]

# 配置
PROJECT_DIR="/home/workspaces/com/ztq/dentimind"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
VENV_PIP="$PROJECT_DIR/venv/bin/pip"
UVICORN="$PROJECT_DIR/venv/bin/uvicorn"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/server.log"
PID_FILE="$PROJECT_DIR/.server.pid"
HOST="0.0.0.0"
PORT="8000"

# 加载 .env 读取 SSL 配置
if [ -f "$PROJECT_DIR/.env" ]; then
    SSL_CERT_FILE=$(grep "^SSL_CERT_FILE=" "$PROJECT_DIR/.env" | cut -d'=' -f2-)
    SSL_KEY_FILE=$(grep "^SSL_KEY_FILE=" "$PROJECT_DIR/.env" | cut -d'=' -f2-)
fi

# 构造 SSL 参数（如果证书存在）
SSL_ARGS=""
if [ -n "$SSL_CERT_FILE" ] && [ -n "$SSL_KEY_FILE" ]; then
    # 将相对路径转换为绝对路径（相对于 PROJECT_DIR）
    case "$SSL_CERT_FILE" in
        /*) ABS_CERT="$SSL_CERT_FILE" ;;
        *)  ABS_CERT="$PROJECT_DIR/$SSL_CERT_FILE" ;;
    esac
    case "$SSL_KEY_FILE" in
        /*) ABS_KEY="$SSL_KEY_FILE" ;;
        *)  ABS_KEY="$PROJECT_DIR/$SSL_KEY_FILE" ;;
    esac

    if [ -f "$ABS_CERT" ] && [ -f "$ABS_KEY" ]; then
        SSL_ARGS="--ssl-certfile $ABS_CERT --ssl-keyfile $ABS_KEY"
        PROTOCOL="https"
    else
        PROTOCOL="http"
    fi
else
    PROTOCOL="http"
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：显示信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查虚拟环境
check_venv() {
    if [ ! -f "$UVICORN" ]; then
        error "虚拟环境不存在: $UVICORN"
        info "请先运行: python3 -m venv $PROJECT_DIR/venv && source $PROJECT_DIR/venv/bin/activate && pip install -r $BACKEND_DIR/requirements.txt"
        exit 1
    fi
}

# 函数：启动服务
start() {
    info "检查服务状态..."

    if is_running; then
        warn "服务已在运行中 (PID: $(cat $PID_FILE))"
        return 1
    fi

    info "创建日志目录..."
    mkdir -p "$LOG_DIR"

    info "启动服务..."
    cd "$BACKEND_DIR"
    # shellcheck disable=SC2086
    nohup "$UVICORN" main:app --host "$HOST" --port "$PORT" $SSL_ARGS > "$LOG_FILE" 2>&1 &
    PID=$!

    echo "$PID" > "$PID_FILE"

    sleep 3

    if is_running; then
        success "服务已启动 (PID: $PID)"
        info "访问地址: ${PROTOCOL}://localhost:$PORT"
        info "API文档: ${PROTOCOL}://localhost:$PORT/docs"
        if [ -n "$SSL_ARGS" ]; then
            info "SSL: ✓ 已启用 HTTPS"
        else
            warn "SSL: 未启用（仅 HTTP）"
        fi
        info "日志文件: $LOG_FILE"
        return 0
    else
        error "服务启动失败，请查看日志: $LOG_FILE"
        return 1
    fi
}

# 函数：停止服务
stop() {
    info "停止服务..."

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            sleep 2

            if ! ps -p "$PID" > /dev/null 2>&1; then
                success "服务已停止 (PID: $PID)"
                rm -f "$PID_FILE"
                return 0
            else
                warn "强制停止服务..."
                kill -9 "$PID"
                sleep 1
                rm -f "$PID_FILE"
                success "服务已强制停止"
                return 0
            fi
        else
            warn "进程不存在: $PID"
            rm -f "$PID_FILE"
            return 0
        fi
    else
        # 尝试通过端口查找进程
        PID=$(lsof -ti:$PORT 2>/dev/null | head -1)
        if [ -n "$PID" ]; then
            warn "通过端口找到进程: $PID"
            kill "$PID"
            sleep 2
            success "服务已停止 (PID: $PID)"
            return 0
        else
            warn "服务未运行"
            return 0
        fi
    fi
}

# 函数：重启服务
restart() {
    info "重启服务..."
    stop
    sleep 1
    start
}

# 函数：检查服务状态
status() {
    if is_running; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        success "服务运行中 (PID: $PID)"

        # 显示最近的日志
        echo ""
        info "最近日志:"
        tail -5 "$LOG_FILE" 2>/dev/null || echo "日志文件不存在"

        return 0
    else
        warn "服务未运行"
        return 1
    fi
}

# 函数：查看日志
logs() {
    if [ -f "$LOG_FILE" ]; then
        info "实时日志 (Ctrl+C 退出):"
        echo ""
        tail -f "$LOG_FILE"
    else
        error "日志文件不存在: $LOG_FILE"
        return 1
    fi
}

# 函数：查看错误日志
errors() {
    if [ -f "$LOG_FILE" ]; then
        info "错误日志:"
        echo ""
        grep -E "ERROR|Exception|Traceback" "$LOG_FILE" | tail -20
    else
        error "日志文件不存在: $LOG_FILE"
        return 1
    fi
}

# 函数：检查服务是否运行
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi

    # 检查端口是否被占用
    if lsof -ti:$PORT > /dev/null 2>&1; then
        return 0
    fi

    return 1
}

# 函数：安装依赖
install() {
    info "安装依赖..."
    check_venv

    cd "$BACKEND_DIR"
    "$VENV_PIP" install -r requirements.txt

    if [ $? -eq 0 ]; then
        success "依赖安装完成"
    else
        error "依赖安装失败"
        return 1
    fi
}

# 函数：显示帮助
help() {
    echo ""
    echo "口腔医院AI客服系统 - 服务管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      查看服务状态"
    echo "  logs        查看实时日志"
    echo "  errors      查看错误日志"
    echo "  install     安装依赖"
    echo "  help        显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 start        # 启动服务"
    echo "  $0 restart      # 重启服务"
    echo "  $0 logs         # 查看日志"
    echo ""
    echo "访问地址:"
    echo "  首页: ${PROTOCOL:-http}://localhost:$PORT/"
    echo "  文本客服: ${PROTOCOL:-http}://localhost:$PORT/chat"
    echo "  外呼管理: ${PROTOCOL:-http}://localhost:$PORT/outbound"
    echo "  客户管理: ${PROTOCOL:-http}://localhost:$PORT/customers"
    echo "  软电话: ${PROTOCOL:-http}://localhost:$PORT/softphone"
    echo "  API文档: ${PROTOCOL:-http}://localhost:$PORT/docs"
    echo ""
}

# 主逻辑
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
    logs)
        logs
        ;;
    errors)
        errors
        ;;
    install)
        install
        ;;
    help|--help|-h)
        help
        ;;
    *)
        if [ -z "$1" ]; then
            # 默认显示状态
            status
        else
            error "未知命令: $1"
            help
            exit 1
        fi
        ;;
esac

exit $?

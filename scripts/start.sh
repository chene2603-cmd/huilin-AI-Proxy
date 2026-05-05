#!/bin/bash
# AI中转站选型系统 - 启动脚本
# 使用方法: ./scripts/start.sh [环境]

set -e

ENV=${1:-"development"}

echo "🚀 启动AI中转站选型系统..."
echo "环境: $ENV"
echo "时间: $(date)"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: ./scripts/install.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "🔍 检查依赖..."
pip list | grep -E "(yaml|requests)" || {
    echo "📦 安装缺失依赖..."
    pip install -r requirements.txt
}

# 设置环境变量
export PYTHONPATH="$PWD:$PYTHONPATH"
export AI_PROXY_ENV="$ENV"

if [ "$ENV" = "production" ]; then
    export AI_PROXY_DEBUG="false"
    export AI_PROXY_LOG_LEVEL="WARNING"
else
    export AI_PROXY_DEBUG="true"
    export AI_PROXY_LOG_LEVEL="INFO"
fi

# 检查端口是否被占用
PORT=8080
if [ "$ENV" = "production" ]; then
    PORT=80
fi

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 $PORT 已被占用"
    read -p "是否尝试其他端口? (y/n): " choice
    if [ "$choice" = "y" ]; then
        for p in {8081..8090}; do
            if ! lsof -Pi :$p -sTCP:LISTEN -t >/dev/null ; then
                PORT=$p
                echo "✅ 使用端口: $PORT"
                break
            fi
        done
    fi
fi

# 创建运行目录
mkdir -p runs
PID_FILE="runs/ai_proxy.pid"
LOG_FILE="logs/startup_$(date +%Y%m%d_%H%M%S).log"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  系统已在运行 (PID: $PID)"
        read -p "是否重启? (y/n): " choice
        if [ "$choice" = "y" ]; then
            echo "🔄 停止当前进程..."
            kill $PID
            sleep 2
        else
            echo "👋 退出"
            exit 0
        fi
    fi
fi

# 启动系统
echo "🚀 启动主程序..."
nohup python3 main.py > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

echo "✅ 系统启动成功！"
echo "📝 PID: $PID"
echo "📁 日志文件: $LOG_FILE"
echo "🌐 Web界面: http://localhost:$PORT (如果启用)"
echo ""
echo "管理命令:"
echo "  🔍 查看状态: tail -f $LOG_FILE"
echo "  🛑 停止系统: kill $PID"
echo "  📊 查看进程: ps aux | grep python3"
echo ""
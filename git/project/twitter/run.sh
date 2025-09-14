#!/bin/bash
# Twitter自动发布系统控制脚本

PROJECT_DIR="/Users/siying/git/project/twitter"
VENV_PATH="$PROJECT_DIR/.venv"

cd "$PROJECT_DIR"

# 激活虚拟环境（如果存在）
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    echo "✅ 虚拟环境已激活"
fi

case "$1" in
    start)
        echo "🚀 启动Twitter自动发布系统..."
        python3 start_auto_publisher.py
        ;;
    test)
        echo "🧪 运行系统测试..."
        python3 manage_publisher.py test-all
        ;;
    status)
        echo "📊 检查发布状态..."
        python3 manage_publisher.py status
        ;;
    test-content)
        echo "📝 生成测试内容..."
        python3 manage_publisher.py content
        ;;
    test-headlines)
        echo "🌅 测试今日头条..."
        python3 manage_publisher.py test headlines
        ;;
    test-thread)
        echo "🧠 测试AI线程..."
        python3 manage_publisher.py test thread
        ;;
    test-tcm)
        echo "🏥 测试中医科技..."
        python3 manage_publisher.py test tcm
        ;;
    install-service)
        echo "📦 安装系统服务..."
        sudo cp service_files/twitter-auto-publisher.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable twitter-auto-publisher
        echo "✅ 服务安装完成，使用 'sudo systemctl start twitter-auto-publisher' 启动"
        ;;
    *)
        echo "🔧 Twitter自动发布系统控制脚本"
        echo ""
        echo "📋 使用方法: ./run.sh <命令>"
        echo ""
        echo "🛠️ 可用命令:"
        echo "  start           - 启动自动发布系统"
        echo "  test            - 运行完整系统测试"  
        echo "  status          - 检查今日发布状态"
        echo "  test-content    - 生成测试内容(不发布)"
        echo "  test-headlines  - 仅测试今日头条发布"
        echo "  test-thread     - 仅测试AI线程发布"
        echo "  test-tcm        - 仅测试中医科技发布"
        echo "  install-service - 安装为系统服务(需要sudo)"
        echo ""
        echo "💡 发布时间表 (UTC时间):"
        echo "  • 08:00 - 🌅 今日科技头条 (带智能配图)"
        echo "  • 12:00 - 🧠 AI+传统智慧线程"  
        echo "  • 14:00 - 🏥 中医科技专题 (带智能配图)"
        echo "  • 16:00 - 🔄 精选转发评论"
        echo "  • 20:00 - 📊 本周趋势回顾 (仅周日)"
        echo "  • 每小时30分 - 📋 检查已审核内容"
        echo ""
        echo "📝 示例:"
        echo "  ./run.sh start           # 启动系统"
        echo "  ./run.sh test-headlines  # 测试头条发布"
        echo "  ./run.sh status          # 查看状态"
        ;;
esac
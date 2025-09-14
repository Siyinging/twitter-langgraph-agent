#!/bin/bash
# Twitter智能自动发布系统启动脚本

echo "🚀 启动Twitter智能自动发布系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未找到，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import sys; sys.path.insert(0, 'src'); from react_agent.authentic_content_generator import AuthenticContentGenerator; print('✅ 依赖检查通过')" 2>/dev/null || {
    echo "❌ 缺少必要依赖，请运行以下命令安装："
    echo "pip install plotly Pillow numpy langchain-tavily apscheduler langchain-mcp-adapters pandas matplotlib seaborn"
    exit 1
}

# 创建必要目录
mkdir -p logs data

echo "🎯 选择启动模式:"
echo "1. 智能自动发布系统 (推荐)"
echo "2. 简单定时发布系统"
echo "3. 手动测试发布"

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo "🧠 启动智能自动发布系统..."
        python3 intelligent_auto_publisher.py
        ;;
    2)
        echo "⏰ 启动简单定时发布系统..."
        python3 ultra_simple_publisher.py
        ;;
    3)
        echo "🧪 手动测试发布..."
        echo "选择测试类型:"
        echo "  headlines - 科技头条"
        echo "  tcm - 中医科技"
        echo "  test - 系统测试"
        read -p "请输入: " test_type
        python3 ultra_simple_publisher.py "$test_type"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
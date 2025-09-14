#!/usr/bin/env python3
"""Twitter自动发布系统启动脚本"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auto_publisher_scheduler import main

if __name__ == "__main__":
    print("🚀 启动Twitter智能自动发布系统...")
    print("🕰️ 发布时间表:")
    print("  • 08:00 UTC - 🌅 今日科技头条 (带智能配图)")
    print("  • 12:00 UTC - 🧠 AI+传统智慧线程")
    print("  • 14:00 UTC - 🏥 中医科技专题 (带智能配图)")
    print("  • 16:00 UTC - 🔄 精选转发评论")
    print("  • 20:00 UTC - 📊 本周趋势回顾 (仅周日)")
    print("  • 每小时30分 - 📋 检查已审核内容")
    print()
    print("📝 按 Ctrl+C 停止系统")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户主动停止系统")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
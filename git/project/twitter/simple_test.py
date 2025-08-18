#!/usr/bin/env python3
"""简单测试调度器功能"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.tools import search


async def test_simple_tool():
    """测试简单工具调用"""
    try:
        print("🧪 测试工具调用...")
        
        # 测试搜索工具
        result = await search("AI trends 2024")
        print(f"✅ 工具调用成功!")
        print(f"📤 搜索结果: {str(result)[:200]}...")
        
    except Exception as e:
        print(f"❌ 工具调用失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple_tool())
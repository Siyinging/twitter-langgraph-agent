#!/usr/bin/env python3
"""测试graph直接调用"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.context import Context
from react_agent.graph import graph
from react_agent.state import InputState
from langchain_core.messages import HumanMessage


async def test_direct_graph_call():
    """直接测试graph调用"""
    try:
        print("🧪 测试直接调用graph...")
        
        # 创建简单的输入
        input_state = InputState(
            messages=[HumanMessage(content="Hello, can you search for AI trends?")]
        )
        
        print(f"📝 输入状态: {input_state}")
        
        # 创建context配置
        context = Context()
        print(f"🔧 Context创建: model={context.model}")
        
        # 直接调用graph
        result = await graph.ainvoke(
            input_state,
            config={
                "recursion_limit": 10,
                "configurable": {
                    "model": context.model,
                    "system_prompt": context.system_prompt,
                    "max_search_results": context.max_search_results,
                    "twitter_user_id": context.twitter_user_id
                }
            }
        )
        
        print(f"✅ 调用成功!")
        print(f"📤 结果: {result}")
        
        if result and result.get("messages"):
            last_message = result["messages"][-1]
            print(f"🎯 最后消息: {last_message.content[:200]}...")
        
    except Exception as e:
        print(f"❌ 调用失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_graph_call())
#!/usr/bin/env python3
"""使用LangGraph发布AI头条推文"""

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


async def publish_ai_tweet_via_graph():
    """通过LangGraph发布AI头条推文"""
    try:
        print("🚀 开始使用LangGraph发布AI头条推文...")
        
        # 用户指定的推文内容
        tweet_content = """📊 今日AI头条 #AI新闻 #科技前沿

1. OpenAI新模型突破语言理解瓶颈
2. 自动驾驶AI在复杂路况测试中表现优异
3. AI辅助癌症诊断准确率提升15%
4. 伦理AI: 新框架解决偏见问题
5. AI创作音乐登上Billboard榜单

点击查看详细信息图表👇
想深入了解哪个话题？"""
        
        # 用户指定的图片路径
        image_path = "/Users/siying/git/project/twitter/images/chart_market_summary_20250818_215704_watermarked_twitter.jpg"
        
        print(f"📝 推文内容:\n{tweet_content}")
        print(f"🖼️ 配图: {image_path}")
        
        # 创建让AI agent发布推文的指令
        instruction = f"""请发布以下推文到Twitter，并附上指定的图片：

推文内容:
{tweet_content}

图片路径: {image_path}

请使用post_tweet工具发布这条推文。"""
        
        # 创建输入状态
        input_state = InputState(
            messages=[HumanMessage(content=instruction)]
        )
        
        print(f"📤 AI指令: {instruction[:100]}...")
        
        # 创建context配置
        context = Context()
        print(f"🔧 Context配置: model={context.model}")
        
        print("\n🤖 正在通过AI agent发布推文...")
        
        # 调用graph让AI agent执行发布
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
        
        print("✅ AI agent处理完成!")
        
        if result and result.get("messages"):
            last_message = result["messages"][-1]
            print(f"🎯 AI响应: {last_message.content}")
            
            # 检查是否成功发布
            if "成功" in last_message.content or "successfully" in last_message.content.lower():
                print("🎉 推文发布成功！")
                return True
            else:
                print("⚠️  推文发布状态需要确认")
        
        return False
        
    except Exception as e:
        print(f"❌ 发布失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(publish_ai_tweet_via_graph())
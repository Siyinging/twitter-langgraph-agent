#!/usr/bin/env python3
"""发布纯文字推文测试"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from langchain_mcp_adapters.client import MultiServerMCPClient


async def publish_text_tweet():
    """发布纯文字推文"""
    try:
        print("🚀 开始发布纯文字AI头条推文...")
        
        # 用户指定的推文内容
        tweet_content = """📊 今日AI头条 #AI新闻 #科技前沿

1. OpenAI新模型突破语言理解瓶颈
2. 自动驾驶AI在复杂路况测试中表现优异
3. AI辅助癌症诊断准确率提升15%
4. 伦理AI: 新框架解决偏见问题
5. AI创作音乐登上Billboard榜单

点击查看详细信息图表👇
想深入了解哪个话题？"""
        
        # Twitter用户ID (从context.py获取的默认值)
        twitter_user_id = "e634c89a-a63a-40fe-af3b-b9d96de0b97a"
        
        print(f"📝 推文内容:\n{tweet_content}")
        print(f"🆔 用户ID: {twitter_user_id}")
        
        # 初始化MCP客户端
        print("\n🔧 初始化Twitter MCP客户端...")
        
        # 配置Twitter MCP服务器
        mcp_client = MultiServerMCPClient({
            "twitter": {
                "url": "http://103.149.46.64:8000/protocol/mcp/",
                "transport": "streamable_http"
            }
        })
        
        # 获取可用工具
        print("📋 获取MCP工具...")
        tools = await mcp_client.get_tools()
        
        # 查找post_tweet工具
        post_tweet_tool = None
        for tool in tools:
            if tool.name == "post_tweet":
                post_tweet_tool = tool
                break
        
        if not post_tweet_tool:
            print("❌ 未找到post_tweet工具")
            available_tools = [tool.name for tool in tools]
            print(f"可用工具: {available_tools}")
            return False
        
        print(f"✅ 找到post_tweet工具: {post_tweet_tool.name}")
        
        # 发布纯文字推文（不带图片）
        print("\n🐦 正在发布纯文字推文...")
        
        result = await post_tweet_tool.ainvoke({
            "text": tweet_content,
            "user_id": twitter_user_id,
            "media_inputs": []  # 空的媒体列表
        })
        
        print("🎉 推文发布完成！")
        print(f"✅ 发布结果: {result}")
        
        # 检查发布是否成功
        if isinstance(result, dict) and result.get("success", False):
            print("🎊 推文发布成功！")
            if "tweet_id" in result:
                print(f"🔗 推文ID: {result['tweet_id']}")
            return True
        else:
            print("⚠️  推文发布可能有问题，请检查结果")
            return False
        
    except Exception as e:
        print(f"❌ 推文发布失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 确保关闭MCP客户端
        try:
            if 'mcp_client' in locals():
                await mcp_client.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(publish_text_tweet())
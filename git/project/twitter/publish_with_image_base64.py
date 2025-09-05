#!/usr/bin/env python3
"""发布带图片的推文（使用base64编码）"""

import asyncio
import base64
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from langchain_mcp_adapters.client import MultiServerMCPClient


async def publish_tweet_with_image():
    """发布带图片的推文"""
    try:
        print("🚀 开始发布带图片的AI头条推文...")
        
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
        
        # Twitter用户ID
        twitter_user_id = "e634c89a-a63a-40fe-af3b-b9d96de0b97a"
        
        print(f"📝 推文内容:\n{tweet_content}")
        print(f"🖼️ 配图: {image_path}")
        
        # 读取图片文件并转换为base64
        print("📷 读取图片文件...")
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                print(f"✅ 图片读取成功，大小: {len(image_data)} 字节")
        except Exception as e:
            print(f"❌ 读取图片失败: {e}")
            return False
        
        # 初始化MCP客户端
        print("\n🔧 初始化Twitter MCP客户端...")
        
        mcp_client = MultiServerMCPClient({
            "twitter": {
                "url": "http://103.149.46.64:8000/protocol/mcp/",
                "transport": "streamable_http"
            }
        })
        
        # 获取可用工具
        tools = await mcp_client.get_tools()
        
        # 查找post_tweet工具
        post_tweet_tool = None
        for tool in tools:
            if tool.name == "post_tweet":
                post_tweet_tool = tool
                break
        
        if not post_tweet_tool:
            print("❌ 未找到post_tweet工具")
            return False
        
        print("✅ 找到post_tweet工具")
        
        # 尝试不同的图片格式
        media_formats = [
            # 格式1: 直接传递文件路径
            [image_path],
            # 格式2: base64数据
            [f"data:image/jpeg;base64,{image_base64}"],
            # 格式3: base64数据（简化）
            [image_base64],
            # 格式4: 包含媒体类型的字典
            [{"type": "image", "data": image_base64}],
            # 格式5: 文件内容
            [{"path": image_path, "content": image_base64}]
        ]
        
        for i, media_input in enumerate(media_formats, 1):
            print(f"\n🐦 尝试格式{i}发布带图片推文...")
            
            try:
                result = await post_tweet_tool.ainvoke({
                    "text": tweet_content,
                    "user_id": twitter_user_id,
                    "media_inputs": media_input
                })
                
                print(f"📤 格式{i}结果: {result}")
                
                # 检查是否成功
                if isinstance(result, dict) and result.get("success", False):
                    print(f"🎉 格式{i}发布成功！")
                    print(f"🔗 推文ID: {result.get('tweet_id')}")
                    print(f"🌐 推文链接: {result.get('url')}")
                    return True
                    
            except Exception as e:
                print(f"❌ 格式{i}失败: {str(e)}")
                continue
        
        print("❌ 所有图片格式都失败了")
        return False
        
    except Exception as e:
        print(f"❌ 发布失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            if 'mcp_client' in locals():
                await mcp_client.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(publish_tweet_with_image())
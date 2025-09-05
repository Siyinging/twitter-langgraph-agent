#!/usr/bin/env python3
"""发布用户指定的AI头条推文"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.tools import post_tweet


async def publish_user_tweet():
    """发布用户指定的AI头条推文"""
    try:
        print("🚀 开始发布AI头条推文...")
        
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
        print("\n🐦 正在发布到Twitter...")
        
        # 使用Twitter MCP工具发布推文
        result = await post_tweet(text=tweet_content, media_inputs=[image_path])
        
        print("🎉 推文发布成功！")
        print(f"✅ 发布结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 推文发布失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(publish_user_tweet())
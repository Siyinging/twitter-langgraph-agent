#!/usr/bin/env python3
"""使用直接Twitter API发布AI头条推文（支持图片）"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.twitter_api_client import TwitterAPIClient

async def publish_ai_headlines_with_image():
    """发布带图片的AI头条推文"""
    try:
        print("🚀 使用直接Twitter API发布AI头条推文...")
        
        # 推文内容
        tweet_content = """📊 今日AI头条 #AI新闻 #科技前沿

1. OpenAI新模型突破语言理解瓶颈
2. 自动驾驶AI在复杂路况测试中表现优异
3. AI辅助癌症诊断准确率提升15%
4. 伦理AI: 新框架解决偏见问题
5. AI创作音乐登上Billboard榜单

点击查看详细信息图表👇
想深入了解哪个话题？"""
        
        # 图片路径
        image_path = "/Users/siying/git/project/twitter/images/chart_market_summary_20250818_215704_watermarked_twitter.jpg"
        
        print(f"📝 推文内容:\n{tweet_content}")
        print(f"🖼️ 配图: {image_path}")
        
        # 初始化Twitter API客户端
        print("\n🔧 初始化Twitter API客户端...")
        client = TwitterAPIClient()
        
        # 检查认证状态
        if not client.is_authenticated():
            print("❌ Twitter API未正确配置")
            print("💡 请运行以下命令配置Twitter API:")
            print("   python3 setup_twitter_api.py")
            return False
        
        # 获取用户信息
        user_info = client.get_user_info()
        if user_info:
            print(f"✅ 已认证用户: @{user_info['username']}")
        
        # 发布带图片的推文
        print("\n🐦 正在发布推文...")
        result = client.post_tweet_with_media(tweet_content, [image_path])
        
        if result and result.get("success"):
            print("🎉 推文发布成功!")
            print(f"🔗 推文链接: {result['url']}")
            print(f"🆔 推文ID: {result['tweet_id']}")
            print(f"📊 媒体数量: {result['media_count']}")
            return True
        else:
            print("❌ 推文发布失败")
            
            # 尝试发布纯文本推文
            print("\n🔄 尝试发布纯文本推文...")
            text_result = client.post_tweet(tweet_content)
            
            if text_result and text_result.get("success"):
                print("✅ 纯文本推文发布成功!")
                print(f"🔗 推文链接: {text_result['url']}")
                return True
            else:
                print("❌ 纯文本推文也发布失败")
                return False
        
    except Exception as e:
        print(f"❌ 发布过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(publish_ai_headlines_with_image())
    
    if not success:
        print("\n" + "="*50)
        print("🛠️ 故障排除建议:")
        print("1. 运行 'python3 setup_twitter_api.py' 配置API凭据")
        print("2. 检查图片文件是否存在且小于5MB")  
        print("3. 验证Twitter开发者账户权限")
        print("4. 确认API密钥具有写入权限")
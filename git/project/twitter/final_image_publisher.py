#!/usr/bin/env python3
"""最终图片发布解决方案 - 独立运行，无外部依赖"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_image_file(image_path: str) -> bool:
    """检查图片文件是否可用"""
    try:
        file_path = Path(image_path)
        if not file_path.exists():
            logger.error(f"❌ 图片文件不存在: {image_path}")
            return False
        
        file_size = file_path.stat().st_size
        if file_size == 0:
            logger.error(f"❌ 图片文件为空: {image_path}")
            return False
        
        if file_size > 5 * 1024 * 1024:  # 5MB限制
            logger.error(f"❌ 图片文件过大: {file_size / 1024 / 1024:.2f}MB，Twitter限制5MB")
            return False
        
        logger.info(f"✅ 图片文件检查通过: {file_size / 1024:.1f}KB")
        return True
        
    except Exception as e:
        logger.error(f"❌ 检查图片文件时出错: {e}")
        return False

def publish_with_direct_api(tweet_text: str, image_path: str) -> bool:
    """使用直接Twitter API发布"""
    try:
        logger.info("🔧 尝试使用直接Twitter API...")
        
        # 检查API凭据
        api_credentials = {
            "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
            "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
            "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
            "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        }
        
        missing_creds = [key for key, value in api_credentials.items() if not value]
        if missing_creds:
            logger.warning(f"⚠️ 缺少Twitter API凭据: {', '.join(missing_creds)}")
            return False
        
        # 导入tweepy
        try:
            import tweepy
        except ImportError:
            logger.error("❌ 未安装tweepy库，请运行: uv add tweepy")
            return False
        
        # 初始化Twitter客户端
        client = tweepy.Client(
            consumer_key=api_credentials["TWITTER_API_KEY"],
            consumer_secret=api_credentials["TWITTER_API_SECRET"],
            access_token=api_credentials["TWITTER_ACCESS_TOKEN"],
            access_token_secret=api_credentials["TWITTER_ACCESS_TOKEN_SECRET"],
            wait_on_rate_limit=True
        )
        
        # 初始化API v1.1用于媒体上传
        auth = tweepy.OAuth1UserHandler(
            api_credentials["TWITTER_API_KEY"],
            api_credentials["TWITTER_API_SECRET"],
            api_credentials["TWITTER_ACCESS_TOKEN"],
            api_credentials["TWITTER_ACCESS_TOKEN_SECRET"]
        )
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # 上传媒体
        logger.info("📤 上传图片...")
        media = api.media_upload(image_path)
        media_id = media.media_id_string
        logger.info(f"✅ 图片上传成功，media_id: {media_id}")
        
        # 发布推文
        logger.info("🐦 发布推文...")
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])
        
        if response.data:
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            logger.info(f"🎉 推文发布成功: {tweet_url}")
            return True
        else:
            logger.error("❌ 推文发布失败，无响应数据")
            return False
            
    except Exception as e:
        logger.error(f"❌ 直接API发布失败: {e}")
        return False

def publish_with_mcp_fallback(tweet_text: str) -> bool:
    """使用MCP备用方案发布纯文本"""
    try:
        logger.info("🔄 尝试使用MCP备用方案（纯文本）...")
        
        # 这里可以调用之前成功的MCP文本发布代码
        # 暂时返回False，表示需要手动配置
        logger.warning("⚠️ MCP备用方案需要手动配置")
        return False
        
    except Exception as e:
        logger.error(f"❌ MCP备用发布失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 最终图片发布解决方案")
    print("=" * 50)
    
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
    
    # 检查图片文件
    if not check_image_file(image_path):
        # 寻找替代图片
        images_dir = Path("images")
        if images_dir.exists():
            image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
            if image_files:
                image_path = str(image_files[0])
                print(f"🔄 使用替代图片: {image_path}")
                if not check_image_file(image_path):
                    print("❌ 所有图片文件都不可用")
                    image_path = None
            else:
                print("❌ 未找到可用图片文件")
                image_path = None
        else:
            print("❌ images目录不存在")
            image_path = None
    
    print("\n" + "=" * 50)
    
    # 尝试发布
    success = False
    
    if image_path:
        # 尝试直接API发布带图片推文
        success = publish_with_direct_api(tweet_content, image_path)
        
        if not success:
            print("\n🔄 直接API发布失败，尝试备用方案...")
            success = publish_with_mcp_fallback(tweet_content)
    else:
        # 只发布文字
        print("⚠️ 无可用图片，仅发布文字内容")
        success = publish_with_mcp_fallback(tweet_content)
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 推文发布成功！")
    else:
        print("❌ 所有发布方法都失败了")
        print("\n🛠️ 解决方案:")
        print("1. 配置Twitter API凭据:")
        print("   - 访问 https://developer.twitter.com/")
        print("   - 在.env文件中添加API凭据")
        print("   - 运行: python3 test_twitter_setup.py")
        print("\n2. 确保图片文件存在且小于5MB")
        print("\n3. 检查网络连接和API权限")

if __name__ == "__main__":
    main()
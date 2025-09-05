#!/usr/bin/env python3
"""智能AI头条发布器 - 自动选择最佳发布方式"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.enhanced_twitter_publisher import EnhancedTwitterPublisher

async def publish_ai_headlines_smart():
    """智能发布AI头条推文"""
    try:
        print("🚀 智能AI头条发布器启动...")
        
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
        
        # 检查图片文件是否存在
        if not Path(image_path).exists():
            print(f"⚠️ 图片文件不存在: {image_path}")
            print("🔍 寻找替代图片...")
            
            # 寻找images目录下的其他图片
            images_dir = Path(project_root / "images")
            if images_dir.exists():
                image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
                if image_files:
                    image_path = str(image_files[0])
                    print(f"✅ 使用替代图片: {image_path}")
                else:
                    print("❌ 未找到可用图片")
                    image_path = None
            else:
                print("❌ images目录不存在")
                image_path = None
        
        # 初始化智能发布器
        print("\n🧠 初始化智能Twitter发布器...")
        publisher = EnhancedTwitterPublisher()
        
        # 检查可用方法
        available_methods = publisher.get_available_methods()
        print(f"📋 可用发布方法: {available_methods}")
        
        if not available_methods:
            print("❌ 没有可用的Twitter发布方法")
            print("\n🛠️ 设置说明:")
            
            setup_instructions = publisher.get_setup_instructions()
            for method, instruction in setup_instructions.items():
                print(f"\n{method.upper()}方法:")
                print(instruction)
            
            return False
        
        # 发布推文
        print("\n🐦 正在智能发布推文...")
        
        media_paths = [image_path] if image_path else []
        result = await publisher.post_tweet_with_media(tweet_content, media_paths)
        
        if result.get("success"):
            print("🎉 推文发布成功!")
            print(f"🔧 使用方法: {result.get('method', '未知')}")
            
            if result.get("tweet_id"):
                print(f"🆔 推文ID: {result['tweet_id']}")
            if result.get("url"):
                print(f"🔗 推文链接: {result['url']}")
            if result.get("media_count"):
                print(f"📊 媒体数量: {result['media_count']}")
            if result.get("warning"):
                print(f"⚠️ 警告: {result['warning']}")
            
            return True
        else:
            print("❌ 推文发布失败")
            print(f"❌ 错误: {result.get('error', '未知错误')}")
            if result.get("suggestion"):
                print(f"💡 建议: {result['suggestion']}")
            if result.get("methods_tried"):
                print(f"🔄 尝试的方法: {result['methods_tried']}")
            
            return False
        
    except Exception as e:
        print(f"❌ 发布过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_status_summary():
    """打印状态摘要"""
    print("\n" + "=" * 60)
    print("📊 Twitter图片发布解决方案状态")
    print("=" * 60)
    
    print("\n✅ 已完成:")
    print("  • 安装了tweepy库支持直接Twitter API调用")
    print("  • 创建了完整的媒体上传功能")
    print("  • 实现了智能发布器（API + MCP双重备份）")
    print("  • 提供了详细的配置指导")
    
    print("\n🔧 需要配置:")
    print("  • Twitter API凭据（API Key, Secret, Access Token等）")
    print("  • 访问 https://developer.twitter.com/ 获取凭据")
    
    print("\n🎯 使用方法:")
    print("  1. 配置Twitter API: python3 test_twitter_setup.py")
    print("  2. 发布推文: python3 publish_ai_news_smart.py")
    
    print("\n📋 技术优势:")
    print("  • 支持完整的Twitter媒体上传流程")
    print("  • 智能方法选择（API优先，MCP备用）")
    print("  • 详细的错误诊断和解决建议")
    print("  • 文件大小检查和格式验证")

if __name__ == "__main__":
    success = asyncio.run(publish_ai_headlines_smart())
    
    print_status_summary()
    
    if not success:
        print("\n🚨 发布失败，但解决方案已就绪!")
        print("💡 请按照上述步骤配置Twitter API凭据后重试")
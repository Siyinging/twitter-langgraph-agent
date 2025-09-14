#!/usr/bin/env python3
"""超简单Twitter自动发布器 - 无外部依赖"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class UltraSimplePublisher:
    """超简单自动发布器"""
    
    def __init__(self):
        self.is_running = False
        Path("logs").mkdir(exist_ok=True)
    
    async def test_publish(self):
        """测试发布功能 - 使用增强版生成器"""
        try:
            logger.info("🧪 开始测试发布功能（增强版内容）...")
            
            # 直接导入和测试 - 使用真实化生成器
            from react_agent.direct_publisher import direct_post_tweet
            from react_agent.authentic_content_generator import AuthenticContentGenerator
            
            # 生成真实化测试内容
            generator = AuthenticContentGenerator()
            headlines = await generator.generate_authentic_headlines()
            
            logger.info(f"📝 生成的有深度内容: {headlines[:100]}...")
            
            # 尝试发布
            result = await direct_post_tweet(headlines)
            
            if result and result.get('success'):
                tweet_id = result.get('tweet_id') or result.get('data', {}).get('tweet_id')
                logger.info(f"✅ 测试发布成功: {tweet_id}")
                return True
            else:
                error = result.get('error') if result else '发布失败'
                logger.error(f"❌ 测试发布失败: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 测试发布异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def publish_at_time(self, hour, content_type):
        """在指定时间发布内容 - 使用增强版生成器"""
        try:
            from react_agent.direct_publisher import direct_post_tweet, direct_post_with_media
            from react_agent.authentic_content_generator import AuthenticContentGenerator
            from react_agent.smart_media_manager import check_and_generate_image
            
            generator = AuthenticContentGenerator()
            
            # 根据类型生成不同内容 - 使用真实化生成器
            if content_type == "headlines":
                content = await generator.generate_authentic_headlines()
                logger.info("🌅 发布真实化的今日科技头条...")
            elif content_type == "tcm":
                content = await generator.generate_authentic_tcm_content()
                logger.info("🏥 发布真实化的中医科技专题...")
            else:
                content = await generator.generate_authentic_headlines()
                logger.info(f"📝 发布{content_type}真实化内容...")
            
            # 检查是否需要配图
            image_path = await check_and_generate_image(content, content_type)
            
            # 发布内容
            if image_path:
                logger.info(f"📸 配图: {image_path}")
                result = await direct_post_with_media(content, [image_path])
            else:
                result = await direct_post_tweet(content)
            
            if result and result.get('success'):
                tweet_id = result.get('tweet_id') or result.get('data', {}).get('tweet_id')
                logger.info(f"✅ {content_type}发布成功: {tweet_id}")
                return True
            else:
                error = result.get('error') if result else '发布失败'
                logger.error(f"❌ {content_type}发布失败: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {content_type}发布异常: {e}")
            return False
    
    async def run_schedule(self):
        """运行简单的定时任务"""
        logger.info("🚀 启动简单定时发布系统...")
        logger.info("📅 发布时间表:")
        logger.info("  • 08:00 - 🌅 今日科技头条")
        logger.info("  • 14:00 - 🏥 中医科技专题")
        
        self.is_running = True
        
        try:
            while self.is_running:
                current_time = datetime.now(timezone.utc)
                hour = current_time.hour
                minute = current_time.minute
                
                # 每天8点发布头条
                if hour == 8 and minute == 0:
                    await self.publish_at_time(8, "headlines")
                    # 避免重复发布
                    await asyncio.sleep(60)
                    
                # 每天14点发布中医科技
                elif hour == 14 and minute == 0:
                    await self.publish_at_time(14, "tcm")
                    # 避免重复发布
                    await asyncio.sleep(60)
                
                # 每分钟检查一次
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("🛑 用户停止系统")
            self.is_running = False
        except Exception as e:
            logger.error(f"❌ 系统运行异常: {e}")

def main():
    """主函数"""
    publisher = UltraSimplePublisher()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            print("🧪 运行系统测试...")
            result = asyncio.run(publisher.test_publish())
            if result:
                print("✅ 系统测试通过！")
                print("🚀 启动系统: python3 ultra_simple_publisher.py")
            else:
                print("❌ 系统测试失败，请检查配置")
            return
            
        elif command == "headlines":
            print("🌅 手动发布今日头条...")
            result = asyncio.run(publisher.publish_at_time(0, "headlines"))
            if result:
                print("✅ 头条发布成功！")
            else:
                print("❌ 头条发布失败")
            return
            
        elif command == "tcm":
            print("🏥 手动发布中医科技专题...")
            result = asyncio.run(publisher.publish_at_time(0, "tcm"))
            if result:
                print("✅ 中医科技发布成功！")
            else:
                print("❌ 中医科技发布失败")
            return
    
    print("🎯 Twitter超简单自动发布系统")
    print("=" * 50)
    print("📅 发布时间表 (UTC时间):")
    print("  • 08:00 - 🌅 今日科技头条 (带智能配图)")
    print("  • 14:00 - 🏥 中医科技专题 (带智能配图)")
    print()
    print("🛠️ 可用命令:")
    print("  • python3 ultra_simple_publisher.py test      - 测试系统")
    print("  • python3 ultra_simple_publisher.py headlines - 手动发布头条")
    print("  • python3 ultra_simple_publisher.py tcm       - 手动发布中医科技")
    print("  • python3 ultra_simple_publisher.py           - 启动定时发布")
    print()
    print("📝 按 Ctrl+C 停止系统")
    print("=" * 50)
    
    try:
        asyncio.run(publisher.run_schedule())
    except KeyboardInterrupt:
        print("\n👋 用户主动停止系统")
    except Exception as e:
        print(f"❌ 系统异常: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""快速启动Twitter自动发布系统 - 独立版本"""

import asyncio
import logging
import sys
import os
import signal
from datetime import datetime, timezone, time
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# 设置项目路径
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/quick_auto_publisher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class QuickAutoPublisher:
    """快速自动发布器 - 避免复杂导入问题"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone='UTC')
        self.is_running = False
        
        # 创建日志目录
        Path("logs").mkdir(exist_ok=True)
    
    async def publish_headlines(self):
        """发布今日头条"""
        try:
            logger.info("🌅 开始发布今日科技头条...")
            
            # 直接导入并执行 - 使用真实化生成器
            sys.path.insert(0, str(project_root / 'src'))
            from react_agent.direct_publisher import direct_post_tweet
            from react_agent.authentic_content_generator import AuthenticContentGenerator
            from react_agent.smart_media_manager import check_and_generate_image
            
            # 生成真实化的内容
            generator = AuthenticContentGenerator()
            headlines = await generator.generate_authentic_headlines()
            
            # 检查是否需要配图
            image_path = await check_and_generate_image(headlines, "morning_headlines")
            
            # 发布推文
            if image_path:
                logger.info(f"📸 为头条配图: {image_path}")
                from react_agent.direct_publisher import direct_post_with_media
                result = await direct_post_with_media(headlines, [image_path])
            else:
                result = await direct_post_tweet(headlines)
            
            if result and result.get('success'):
                tweet_id = result.get('tweet_id') or result.get('data', {}).get('tweet_id')
                logger.info(f"✅ 今日头条发布成功: {tweet_id}")
                return True
            else:
                error = result.get('error') if result else '发布失败'
                logger.error(f"❌ 今日头条发布失败: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 今日头条发布异常: {e}")
            return False
    
    async def publish_ai_thread(self):
        """发布AI线程"""
        try:
            logger.info("🧠 开始发布AI+传统智慧线程...")
            
            sys.path.insert(0, str(project_root / 'src'))
            from react_agent.authentic_content_generator import AuthenticContentGenerator
            from react_agent.direct_publisher import direct_post_thread
            
            # 生成真实化的线程内容
            generator = AuthenticContentGenerator()
            thread_content = await generator.generate_authentic_ai_thread()
            
            # 发布线程
            result = await direct_post_thread(thread_content)
            
            if result and result.get('success'):
                tweet_count = len(result.get('tweet_ids', []))
                logger.info(f"✅ AI线程发布成功: {tweet_count}条推文")
                return True
            else:
                error = result.get('error') if result else '发布失败'
                logger.error(f"❌ AI线程发布失败: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI线程发布异常: {e}")
            return False
    
    async def publish_tcm_focus(self):
        """发布中医科技专题"""
        try:
            logger.info("🏥 开始发布中医科技专题...")
            
            sys.path.insert(0, str(project_root / 'src'))
            from react_agent.authentic_content_generator import AuthenticContentGenerator
            from react_agent.direct_publisher import direct_post_tweet, direct_post_with_media
            from react_agent.smart_media_manager import check_and_generate_image
            
            # 生成真实化的内容
            generator = AuthenticContentGenerator()
            tcm_content = await generator.generate_authentic_tcm_content()
            
            # 检查是否需要配图
            image_path = await check_and_generate_image(tcm_content, "tcm_tech_focus")
            
            # 发布推文
            if image_path:
                logger.info(f"📸 为中医科技专题配图: {image_path}")
                result = await direct_post_with_media(tcm_content, [image_path])
            else:
                result = await direct_post_tweet(tcm_content)
            
            if result and result.get('success'):
                tweet_id = result.get('tweet_id') or result.get('data', {}).get('tweet_id')
                logger.info(f"✅ 中医科技专题发布成功: {tweet_id}")
                return True
            else:
                error = result.get('error') if result else '发布失败'
                logger.error(f"❌ 中医科技专题发布失败: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 中医科技专题发布异常: {e}")
            return False
    
    def setup_schedule(self):
        """设置发布时间表"""
        logger.info("🔧 设置发布时间表...")
        
        # 08:00 UTC - 今日科技头条
        self.scheduler.add_job(
            self.publish_headlines,
            CronTrigger(hour=8, minute=0),
            id='headlines',
            name='今日科技头条',
            replace_existing=True
        )
        
        # 12:00 UTC - AI+传统智慧线程
        self.scheduler.add_job(
            self.publish_ai_thread,
            CronTrigger(hour=12, minute=0),
            id='ai_thread',
            name='AI+传统智慧线程',
            replace_existing=True
        )
        
        # 14:00 UTC - 中医科技专题
        self.scheduler.add_job(
            self.publish_tcm_focus,
            CronTrigger(hour=14, minute=0),
            id='tcm_focus',
            name='中医科技专题',
            replace_existing=True
        )
        
        logger.info("✅ 发布时间表设置完成")
    
    async def test_system(self):
        """测试系统功能"""
        logger.info("🧪 开始系统测试...")
        
        try:
            # 测试头条发布
            result = await self.publish_headlines()
            if result:
                logger.info("✅ 系统测试通过")
                return True
            else:
                logger.error("❌ 系统测试失败")
                return False
        except Exception as e:
            logger.error(f"❌ 系统测试异常: {e}")
            return False
    
    async def start(self):
        """启动系统"""
        logger.info("🚀 启动Twitter自动发布系统...")
        
        self.setup_schedule()
        self.scheduler.start()
        self.is_running = True
        
        # 显示下次任务
        jobs = self.scheduler.get_jobs()
        logger.info("📅 下次发布计划:")
        for job in sorted(jobs, key=lambda x: x.next_run_time):
            if job.next_run_time:
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S UTC")
                logger.info(f"  • {job.name}: {next_run}")
        
        logger.info("✅ 自动发布系统启动成功")
        
        # 保持运行
        try:
            while self.is_running:
                await asyncio.sleep(30)
        except KeyboardInterrupt:
            logger.info("🛑 用户中断，停止系统...")
            await self.stop()
    
    async def stop(self):
        """停止系统"""
        logger.info("🛑 停止自动发布系统...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("✅ 系统已停止")

def signal_handler(signum, frame):
    """处理信号"""
    logger.info(f"🛑 收到信号 {signum}，准备停止...")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    publisher = QuickAutoPublisher()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 运行系统测试...")
        result = asyncio.run(publisher.test_system())
        if result:
            print("✅ 系统测试通过，可以正常使用！")
            print("\n🚀 启动系统: python3 quick_start_auto_publisher.py")
        else:
            print("❌ 系统测试失败，请检查配置")
        return
    
    print("🎯 Twitter智能自动发布系统 - 快速版")
    print("=" * 50)
    print("📅 发布时间表 (UTC时间):")
    print("  • 08:00 - 🌅 今日科技头条 (带智能配图)")
    print("  • 12:00 - 🧠 AI+传统智慧线程")
    print("  • 14:00 - 🏥 中医科技专题 (带智能配图)")
    print()
    print("📝 按 Ctrl+C 停止系统")
    print("💡 使用 'python3 quick_start_auto_publisher.py test' 运行测试")
    print("=" * 50)
    
    try:
        asyncio.run(publisher.start())
    except KeyboardInterrupt:
        print("\n👋 用户主动停止系统")
    except Exception as e:
        print(f"❌ 系统异常: {e}")

if __name__ == "__main__":
    main()
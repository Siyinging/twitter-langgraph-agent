#!/usr/bin/env python3
"""智能Twitter自动发布调度器
每天定时发布高质量科技内容，支持实时新闻和智能配图

发布时间表:
08:00 - 🌅 今日科技头条 (带智能配图)
12:00 - 🧠 AI+传统智慧线程
14:00 - 🏥 中医科技专题 (带智能配图)
16:00 - 🔄 精选转发评论  
20:00 - 📊 本周趋势回顾 (仅周日)
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timezone, time
from pathlib import Path
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor

from src.react_agent.daily_publisher import DailyTechPublisher
from src.react_agent.enhanced_content_reviewer import EnhancedContentReviewSystem

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_publisher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TwitterAutoPublisher:
    """Twitter自动发布调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            executors={'default': AsyncIOExecutor()},
            timezone='UTC'
        )
        self.publisher = DailyTechPublisher(use_review_system=True)
        self.review_system = EnhancedContentReviewSystem()
        self.is_running = False
        
        # 创建日志目录
        Path("logs").mkdir(exist_ok=True)
        
    async def setup_scheduler(self):
        """设置发布时间表"""
        logger.info("🔧 设置每日发布时间表...")
        
        # 08:00 UTC - 今日科技头条
        self.scheduler.add_job(
            self.publish_morning_headlines,
            CronTrigger(hour=8, minute=0),
            id='morning_headlines',
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
            self.publish_tcm_tech_focus,
            CronTrigger(hour=14, minute=0),
            id='tcm_tech_focus',
            name='中医科技专题', 
            replace_existing=True
        )
        
        # 16:00 UTC - 精选转发
        self.scheduler.add_job(
            self.publish_curated_retweet,
            CronTrigger(hour=16, minute=0),
            id='curated_retweet',
            name='精选转发',
            replace_existing=True
        )
        
        # 20:00 UTC - 本周回顾 (仅周日)
        self.scheduler.add_job(
            self.publish_weekly_recap,
            CronTrigger(hour=20, minute=0, day_of_week=6),  # 6 = Sunday
            id='weekly_recap',
            name='本周趋势回顾',
            replace_existing=True
        )
        
        # 每2小时检查是否有待审核内容
        self.scheduler.add_job(
            self.check_approved_content,
            CronTrigger(minute=30),  # 每小时30分检查
            id='check_approved',
            name='检查已审核内容',
            replace_existing=True
        )
        
        logger.info("✅ 发布时间表设置完成")
        
    async def publish_morning_headlines(self):
        """08:00 - 发布今日科技头条"""
        try:
            logger.info("🌅 开始发布今日科技头条...")
            result = await self.publisher.publish_morning_headlines()
            
            if result.get('success'):
                logger.info(f"✅ 今日头条发布成功: {result.get('tweet_id')}")
            else:
                logger.error(f"❌ 今日头条发布失败: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ 今日头条发布异常: {e}")
            
    async def publish_ai_thread(self):
        """12:00 - 发布AI+传统智慧线程"""
        try:
            logger.info("🧠 开始发布AI+传统智慧线程...")
            result = await self.publisher.publish_ai_thread()
            
            if result.get('success'):
                tweet_count = len(result.get('tweet_ids', []))
                logger.info(f"✅ AI线程发布成功: {tweet_count}条推文")
            else:
                logger.error(f"❌ AI线程发布失败: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ AI线程发布异常: {e}")
            
    async def publish_tcm_tech_focus(self):
        """14:00 - 发布中医科技专题"""
        try:
            logger.info("🏥 开始发布中医科技专题...")
            result = await self.publisher.publish_tcm_tech_focus()
            
            if result.get('success'):
                logger.info(f"✅ 中医科技专题发布成功: {result.get('tweet_id')}")
            else:
                logger.error(f"❌ 中医科技专题发布失败: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ 中医科技专题发布异常: {e}")
            
    async def publish_curated_retweet(self):
        """16:00 - 发布精选转发"""
        try:
            logger.info("🔄 开始发布精选转发...")
            result = await self.publisher.publish_curated_retweet()
            
            if result.get('success'):
                logger.info(f"✅ 精选转发发布成功: {result.get('quote_tweet_id')}")
            else:
                logger.error(f"❌ 精选转发失败: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ 精选转发异常: {e}")
            
    async def publish_weekly_recap(self):
        """20:00 - 发布本周回顾 (仅周日)"""
        try:
            logger.info("📊 开始发布本周回顾...")
            result = await self.publisher.publish_weekly_recap()
            
            if result.get('success') and not result.get('skipped'):
                logger.info(f"✅ 本周回顾发布成功: {result.get('tweet_id')}")
            elif result.get('skipped'):
                logger.info("⏭️ 今天不是周日，跳过周报发布")
            else:
                logger.error(f"❌ 本周回顾发布失败: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ 本周回顾发布异常: {e}")
            
    async def check_approved_content(self):
        """检查并发布已审核通过的内容"""
        try:
            result = await self.publisher.publish_approved_content()
            if result and not result.get('error'):
                if result.get('published_count', 0) > 0:
                    logger.info(f"📋 发布了 {result['published_count']} 条已审核内容")
                # else:
                #     logger.debug("📋 没有待发布的已审核内容")
        except Exception as e:
            logger.error(f"❌ 检查已审核内容异常: {e}")
            
    async def get_next_jobs_info(self) -> str:
        """获取下次任务信息"""
        jobs = self.scheduler.get_jobs()
        if not jobs:
            return "没有计划的任务"
            
        info_lines = ["📅 下次发布计划:"]
        for job in sorted(jobs, key=lambda x: x.next_run_time or datetime.max.replace(tzinfo=timezone.utc)):
            if job.next_run_time:
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S UTC")
                info_lines.append(f"  • {job.name}: {next_run}")
                
        return "\n".join(info_lines)
        
    async def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("⚠️ 调度器已在运行中")
            return
            
        logger.info("🚀 启动Twitter自动发布调度器...")
        
        await self.setup_scheduler()
        self.scheduler.start()
        self.is_running = True
        
        # 显示下次任务信息
        jobs_info = await self.get_next_jobs_info()
        logger.info(jobs_info)
        
        logger.info("✅ 自动发布调度器启动成功")
        logger.info("📱 系统将按时间表自动发布内容...")
        
    async def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
            
        logger.info("🛑 停止自动发布调度器...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("✅ 调度器已停止")
        
    async def get_status(self) -> dict:
        """获取系统状态"""
        jobs = self.scheduler.get_jobs()
        return {
            "is_running": self.is_running,
            "total_jobs": len(jobs),
            "next_jobs": [
                {
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in sorted(jobs, key=lambda x: x.next_run_time or datetime.max.replace(tzinfo=timezone.utc))[:3]
            ]
        }

# 全局调度器实例
scheduler_instance: Optional[TwitterAutoPublisher] = None

def signal_handler(signum, frame):
    """处理系统信号"""
    global scheduler_instance
    logger.info(f"🛑 收到信号 {signum}，准备停止服务...")
    
    if scheduler_instance and scheduler_instance.is_running:
        asyncio.create_task(scheduler_instance.stop())
    
    sys.exit(0)

async def main():
    """主函数"""
    global scheduler_instance
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 终止信号
    
    logger.info("🎯 Twitter智能自动发布系统启动")
    logger.info("=" * 50)
    
    scheduler_instance = TwitterAutoPublisher()
    
    try:
        await scheduler_instance.start()
        
        # 保持运行
        while scheduler_instance.is_running:
            await asyncio.sleep(30)  # 每30秒检查一次
            
    except KeyboardInterrupt:
        logger.info("🛑 用户中断，停止服务...")
    except Exception as e:
        logger.error(f"❌ 系统运行异常: {e}")
    finally:
        if scheduler_instance:
            await scheduler_instance.stop()
            
    logger.info("👋 系统已退出")

if __name__ == "__main__":
    asyncio.run(main())
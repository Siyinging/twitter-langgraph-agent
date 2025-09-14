#!/usr/bin/env python3
"""简单的Twitter自动发布系统启动脚本"""

import asyncio
import logging
import sys
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_system():
    """测试系统是否正常工作"""
    try:
        logger.info("🧪 开始系统测试...")
        
        # 测试发布功能
        from src.react_agent.daily_publisher import DailyTechPublisher
        publisher = DailyTechPublisher()
        
        # 测试今日头条发布
        logger.info("📰 测试今日头条发布...")
        result = await publisher.publish_morning_headlines()
        
        if result.get('success'):
            logger.info(f"✅ 头条发布成功: {result.get('tweet_id')}")
        else:
            logger.error(f"❌ 头条发布失败: {result.get('error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        logger.error(f"❌ 系统测试失败: {e}")
        return False

async def run_scheduler():
    """运行简化版调度器"""
    logger.info("🚀 启动Twitter自动发布系统...")
    logger.info("⚠️  这是简化版本，如需完整功能请修复导入路径问题")
    
    try:
        from src.react_agent.daily_publisher import DailyTechPublisher
        publisher = DailyTechPublisher()
        
        # 简单的发布循环
        while True:
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute
            
            # 每天8点发布头条
            if current_hour == 8 and current_minute == 0:
                logger.info("🌅 开始发布今日头条...")
                await publisher.publish_morning_headlines()
                
            # 每天12点发布AI线程
            elif current_hour == 12 and current_minute == 0:
                logger.info("🧠 开始发布AI线程...")
                await publisher.publish_ai_thread()
                
            # 每天14点发布中医科技
            elif current_hour == 14 and current_minute == 0:
                logger.info("🏥 开始发布中医科技...")
                await publisher.publish_tcm_tech_focus()
                
            # 每天16点发布转发
            elif current_hour == 16 and current_minute == 0:
                logger.info("🔄 开始发布转发...")
                await publisher.publish_curated_retweet()
                
            # 每天20点发布周报(仅周日)
            elif current_hour == 20 and current_minute == 0:
                logger.info("📊 开始发布周报...")
                await publisher.publish_weekly_recap()
            
            # 每分钟检查一次
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("🛑 用户停止系统")
    except Exception as e:
        logger.error(f"❌ 系统运行异常: {e}")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 运行系统测试...")
        result = asyncio.run(test_system())
        if result:
            print("✅ 系统测试通过，可以正常使用")
        else:
            print("❌ 系统测试失败，请检查配置")
        return
    
    print("🎯 Twitter智能自动发布系统")
    print("=" * 50)
    print("📅 发布时间表:")
    print("  • 08:00 - 🌅 今日科技头条")
    print("  • 12:00 - 🧠 AI+传统智慧线程") 
    print("  • 14:00 - 🏥 中医科技专题")
    print("  • 16:00 - 🔄 精选转发评论")
    print("  • 20:00 - 📊 本周趋势回顾 (仅周日)")
    print()
    print("📝 按 Ctrl+C 停止系统")
    print("💡 使用 'python3 simple_start.py test' 运行测试")
    print("=" * 50)
    
    asyncio.run(run_scheduler())

if __name__ == "__main__":
    main()
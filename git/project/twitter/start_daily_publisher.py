#!/usr/bin/env python3
"""启动每日科技内容发布器

这个脚本启动完整的每日科技内容发布系统，包括：
- 08:00 今日科技头条
- 12:00 可持续AI原创线程 
- 16:00 精选转发内容
- 20:00 本周趋势回顾（周日）
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv
from manual_scheduler import ManualTwitterScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_publisher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def check_environment():
    """检查环境配置"""
    load_dotenv()
    
    required_vars = [
        "ANTHROPIC_API_KEY",
        "TAVILY_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请在.env文件中配置这些变量")
        return False
    
    return True


async def run_single_task(task_name: str):
    """运行单个测试任务"""
    publisher = ManualTwitterScheduler().daily_publisher
    
    tasks = {
        "headlines": publisher.publish_morning_headlines,
        "tcm-headlines": lambda: publisher.content_generator.generate_tcm_tech_headlines(),
        "ai-thread": publisher.publish_ai_thread,
        "tcm-focus": publisher.publish_tcm_tech_focus,
        "retweet": publisher.publish_curated_retweet,
        "weekly": publisher.publish_weekly_recap
    }
    
    if task_name not in tasks:
        print(f"❌ 未知任务: {task_name}")
        print(f"可用任务: {', '.join(tasks.keys())}")
        return False
    
    print(f"🚀 执行单个任务: {task_name}")
    result = await tasks[task_name]()
    
    if result.get('success'):
        print(f"✅ 任务执行成功!")
        if 'tweet_id' in result:
            print(f"   推文ID: {result['tweet_id']}")
        if 'tweet_ids' in result:
            print(f"   线程推文数: {len(result['tweet_ids'])}")
    else:
        print(f"❌ 任务执行失败: {result.get('error', '未知错误')}")
        return False
    
    return True


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="每日科技内容发布器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python start_daily_publisher.py                    # 启动完整调度器
  python start_daily_publisher.py --test headlines   # 测试今日头条
  python start_daily_publisher.py --test ai-thread   # 测试AI线程
  python start_daily_publisher.py --test retweet     # 测试精选转发
  python start_daily_publisher.py --test weekly      # 测试周报
        """
    )
    
    parser.add_argument(
        "--test",
        help="运行单个测试任务 (headlines/tcm-headlines/ai-thread/tcm-focus/retweet/weekly)"
    )
    parser.add_argument(
        "--review-mode",
        action="store_true", 
        help="启用内容复查模式（需要人工审核）"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3,
        help="旧任务执行间隔（小时），默认3小时"
    )
    
    args = parser.parse_args()
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    try:
        if args.test:
            # 运行单个测试任务
            success = await run_single_task(args.test)
            sys.exit(0 if success else 1)
        else:
            # 启动完整调度器
            print("🚀 启动增强版科技内容发布系统")
            print()
            if args.review_mode:
                print("📋 复查模式已启用")
                print("📅 每日发布计划（复查模式）:")
                print("  06:30 - 创建内容草稿")
                print("  07:00-07:45 - 人工审核时间窗口")
                print("  07:45 - 发布已审核内容")
            else:
                print("📅 每日发布计划（直接模式）:")
            print("  08:00 - 今日科技头条（含中医科技）")
            print("  12:00 - AI+传统智慧线程")
            print("  14:00 - 中医科技专题")
            print("  16:00 - 精选转发内容") 
            print("  20:00 - 本周趋势回顾（周日）")
            print()
            
            # 创建并启动调度器
            scheduler = ManualTwitterScheduler(interval_hours=args.interval)
            
            await scheduler.start()
            
            print("🔄 调度器正在运行... 按 Ctrl+C 停止")
            try:
                while True:
                    await asyncio.sleep(60)
            except KeyboardInterrupt:
                print("\n👋 收到停止信号...")
            finally:
                await scheduler.stop()
            
    except Exception as e:
        logger.error(f"❌ 程序出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
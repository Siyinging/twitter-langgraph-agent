#!/usr/bin/env python3
"""Twitter Agent调度器启动脚本

使用方法:
  python run_scheduler.py --interval 3 --test-run
  python run_scheduler.py --interval 6 --daemon
  python run_scheduler.py --list-jobs

选项:
  --interval HOURS    设置执行间隔（小时），默认3小时
  --test-run         执行一次测试任务然后退出
  --daemon           后台运行模式
  --list-jobs        列出所有定时任务
  --help             显示帮助信息
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.scheduler import TwitterAgentScheduler, run_scheduler
from react_agent.context import Context


async def test_single_run():
    """执行单次测试任务"""
    print("🧪 执行单次测试任务...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        context = Context()
        print(f"🔧 Context创建成功: model={context.model}")
        
        scheduler = TwitterAgentScheduler(context, interval_hours=1)
        
        # 执行一次趋势分析任务
        await scheduler.execute_scheduled_task("trend_analysis")
        print("✅ 测试任务完成！")
    except Exception as e:
        print(f"❌ 测试任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def list_scheduled_jobs():
    """列出所有定时任务"""
    print("📋 当前定时任务列表:")
    
    context = Context()
    scheduler = TwitterAgentScheduler(context, interval_hours=3)
    
    # 添加任务但不启动调度器
    scheduler.add_scheduled_jobs()
    scheduler.list_jobs()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Twitter Agent定时调度器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run_scheduler.py --interval 3      # 每3小时执行一次
  python run_scheduler.py --test-run        # 执行单次测试
  python run_scheduler.py --list-jobs       # 列出定时任务
        """
    )
    
    parser.add_argument(
        "--interval", 
        type=int, 
        default=3,
        help="执行间隔（小时），默认3小时"
    )
    parser.add_argument(
        "--test-run", 
        action="store_true",
        help="执行一次测试任务然后退出"
    )
    parser.add_argument(
        "--daemon", 
        action="store_true",
        help="后台运行模式（持续运行）"
    )
    parser.add_argument(
        "--list-jobs", 
        action="store_true",
        help="列出所有定时任务"
    )
    
    args = parser.parse_args()
    
    # 检查环境变量
    required_env_vars = ["ANTHROPIC_API_KEY", "TAVILY_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请确保在.env文件中配置了这些变量")
        sys.exit(1)
    
    try:
        if args.list_jobs:
            # 列出定时任务
            asyncio.run(list_scheduled_jobs())
            
        elif args.test_run:
            # 执行测试任务
            success = asyncio.run(test_single_run())
            sys.exit(0 if success else 1)
            
        else:
            # 启动调度器
            print(f"🚀 启动Twitter Agent调度器（间隔: {args.interval}小时）")
            
            if args.daemon:
                print("💽 后台运行模式")
            
            asyncio.run(run_scheduler(
                interval_hours=args.interval,
                run_forever=True
            ))
    
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
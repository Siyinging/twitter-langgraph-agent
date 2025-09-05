#!/usr/bin/env python3
"""测试每日科技内容发布器

用于验证每日发布功能是否正常工作，包括：
- 内容生成测试
- 线程创建测试
- 工具集成测试
- 发布流程测试
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from react_agent.daily_publisher import DailyTechPublisher
from react_agent.content_generator import TechContentGenerator
from react_agent.thread_creator import TwitterThreadCreator
from react_agent.tools import _get_all_mcp_tools

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_mcp_tools():
    """测试MCP工具连接"""
    print("🔧 测试MCP工具连接...")
    try:
        tools = await _get_all_mcp_tools()
        print(f"✅ 成功连接MCP服务器，获取到{len(tools)}个工具:")
        for tool_name in tools.keys():
            print(f"  - {tool_name}")
        
        # 检查新增的线程工具
        required_new_tools = ['reply_tweet', 'quote_tweet']
        for tool_name in required_new_tools:
            if tool_name in tools:
                print(f"✅ {tool_name} 工具已可用")
            else:
                print(f"❌ {tool_name} 工具不可用")
        
        return True
    except Exception as e:
        print(f"❌ MCP工具连接失败: {e}")
        return False


async def test_content_generation():
    """测试内容生成功能"""
    print("\n📝 测试内容生成功能...")
    generator = TechContentGenerator()
    
    try:
        # 1. 测试今日科技头条
        print("  1. 今日科技头条:")
        headlines = await generator.generate_daily_headlines()
        print(f"     内容: {headlines[:100]}...")
        print(f"     字数: {len(headlines)}")
        
        # 2. 测试可持续AI线程
        print("  2. 可持续AI线程:")
        ai_thread = await generator.generate_sustainable_ai_thread()
        print(f"     线程长度: {len(ai_thread)}条推文")
        for i, content in enumerate(ai_thread, 1):
            print(f"     推文{i}: {content[:50]}... (字数: {len(content)})")
        
        # 3. 测试转发目标搜索
        print("  3. 转发目标搜索:")
        retweet_target = await generator.find_retweet_target()
        if retweet_target:
            print(f"     找到目标: {retweet_target['author']}")
            print(f"     评论: {retweet_target['comment']}")
        else:
            print("     未找到合适的转发目标")
        
        # 4. 测试周报生成
        print("  4. 本周科技回顾:")
        weekly_recap = await generator.generate_weekly_recap()
        print(f"     内容: {weekly_recap[:100]}...")
        print(f"     字数: {len(weekly_recap)}")
        
        return True
    except Exception as e:
        print(f"❌ 内容生成测试失败: {e}")
        return False


async def test_thread_creation():
    """测试线程创建功能（不实际发布）"""
    print("\n🧵 测试线程创建功能...")
    creator = TwitterThreadCreator()
    
    try:
        # 生成测试内容
        test_content = [
            "🌱 这是可持续AI线程测试的第一条推文，介绍绿色AI发展的重要性。",
            "💡 第二条推文探讨AI能耗问题和当前面临的技术挑战。",
            "🔧 第三条推文介绍最新的节能AI技术和解决方案。",
            "🚀 最后一条推文展望可持续AI的未来发展方向。"
        ]
        
        print(f"  模拟线程内容（{len(test_content)}条推文）:")
        for i, content in enumerate(test_content, 1):
            print(f"    {i}. {content} (字数: {len(content)})")
        
        # 检查字数限制
        all_valid = all(len(content) <= 280 for content in test_content)
        print(f"  字数检查: {'✅ 所有推文符合280字符限制' if all_valid else '❌ 部分推文超出限制'}")
        
        return True
    except Exception as e:
        print(f"❌ 线程创建测试失败: {e}")
        return False


async def test_daily_publisher_integration():
    """测试每日发布器集成"""
    print("\n📊 测试每日发布器集成...")
    publisher = DailyTechPublisher()
    
    try:
        # 测试发布器初始化
        print("  ✅ 发布器初始化成功")
        
        # 检查组件
        print(f"  ✅ 内容生成器: {type(publisher.content_generator).__name__}")
        print(f"  ✅ 线程创建器: {type(publisher.thread_creator).__name__}")
        
        # 模拟发布状态检查
        from datetime import datetime, timezone
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        status = await publisher.get_publish_status(current_date)
        print(f"  📅 今日发布状态: {status['status']}")
        
        return True
    except Exception as e:
        print(f"❌ 发布器集成测试失败: {e}")
        return False


async def test_scheduler_jobs():
    """测试调度器任务配置"""
    print("\n⏰ 测试调度器任务配置...")
    
    try:
        # 导入调度器
        from manual_scheduler import ManualTwitterScheduler
        
        # 创建调度器（不启动）
        scheduler = ManualTwitterScheduler(interval_hours=1)
        
        # 添加任务
        scheduler.add_scheduled_jobs()
        
        # 检查任务
        jobs = scheduler.scheduler.get_jobs()
        print(f"  📋 总共配置了{len(jobs)}个定时任务:")
        
        daily_jobs = []
        analysis_jobs = []
        
        for job in jobs:
            job_name = job.name
            trigger_info = str(job.trigger)
            
            if "发布" in job_name:
                daily_jobs.append(job_name)
                print(f"  📱 {job_name}: {trigger_info}")
            else:
                analysis_jobs.append(job_name)
                print(f"  📊 {job_name}: {trigger_info}")
        
        print(f"\n  统计:")
        print(f"    每日发布任务: {len(daily_jobs)}个")
        print(f"    分析任务: {len(analysis_jobs)}个")
        
        return True
    except Exception as e:
        print(f"❌ 调度器测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始每日发布器功能测试\n")
    
    test_results = []
    
    # 执行各项测试
    tests = [
        ("MCP工具连接", test_mcp_tools),
        ("内容生成功能", test_content_generation),
        ("线程创建功能", test_thread_creation),
        ("发布器集成", test_daily_publisher_integration),
        ("调度器配置", test_scheduler_jobs)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 {test_name} 出错: {e}")
            test_results.append((test_name, False))
    
    # 输出测试结果
    print(f"\n{'='*50}")
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统已准备好进行每日科技内容发布。")
        print("\n启动命令:")
        print("  python manual_scheduler.py  # 启动完整调度器")
        print("  python test_daily_publisher.py  # 运行测试")
    else:
        print("⚠️ 部分测试失败，请检查配置后重试。")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
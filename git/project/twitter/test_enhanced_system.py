#!/usr/bin/env python3
"""测试增强版Twitter发布系统

包含以下新功能测试：
- 中医科技融合内容生成
- 内容复查和审核系统
- 新的发布时间表
- CLI工具功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv
load_dotenv()

from react_agent.content_generator import TechContentGenerator
from react_agent.content_reviewer import ContentReviewSystem
from react_agent.daily_publisher import DailyTechPublisher
from manual_scheduler import ManualTwitterScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_tcm_content_generation():
    """测试中医科技内容生成"""
    print("🏥 测试中医科技内容生成...")
    generator = TechContentGenerator()
    
    try:
        # 1. 测试中医科技头条
        print("  1. 中医科技头条:")
        tcm_headlines = await generator.generate_tcm_tech_headlines()
        print(f"     内容: {tcm_headlines[:100]}...")
        print(f"     字数: {len(tcm_headlines)}")
        
        # 2. 测试AI+传统智慧线程
        print("  2. AI+传统智慧线程:")
        wisdom_thread = await generator.generate_wisdom_ai_thread()
        print(f"     线程长度: {len(wisdom_thread)}条推文")
        for i, content in enumerate(wisdom_thread[:3], 1):
            print(f"     推文{i}: {content[:60]}... (字数: {len(content)})")
        
        # 3. 测试每日中医科技专题
        print("  3. 每日中医科技专题:")
        tcm_daily = await generator.generate_daily_tcm_tech_content()
        print(f"     内容: {tcm_daily[:100]}...")
        print(f"     字数: {len(tcm_daily)}")
        
        return True
    except Exception as e:
        print(f"❌ 中医科技内容生成测试失败: {e}")
        return False


async def test_review_system():
    """测试内容复查系统"""
    print("\n📋 测试内容复查系统...")
    review_system = ContentReviewSystem()
    
    try:
        # 1. 创建测试草稿
        print("  1. 创建测试草稿:")
        test_content = "🏥 这是一条测试中医科技推文，用于验证复查系统功能。 #中医科技 #测试"
        draft_id = await review_system.create_draft(
            "test_tcm", 
            test_content, 
            {"test": True, "content_type": "tcm_tech"}
        )
        print(f"     草稿ID: {draft_id}")
        
        # 2. 预览内容
        print("  2. 预览内容:")
        preview = await review_system.preview_content(draft_id)
        print(f"     类型: {preview['content_type']}")
        print(f"     字数: {preview['char_count']}")
        print(f"     字数检查: {'✅' if preview['char_check'] else '❌'}")
        
        # 3. 审核流程
        print("  3. 审核流程:")
        await review_system.submit_for_review(draft_id)
        print("     已提交审核")
        
        review_id = await review_system.approve_content(draft_id, "自动测试审核通过")
        print(f"     审核ID: {review_id}")
        
        # 4. 获取已批准内容
        print("  4. 获取已批准内容:")
        approved = await review_system.get_approved_content()
        print(f"     已批准内容数量: {len(approved)}")
        
        # 5. 统计信息
        print("  5. 统计信息:")
        stats = await review_system.get_stats()
        print(f"     总草稿: {stats['total_drafts']}")
        print(f"     待审核: {stats['pending_reviews']}")
        print(f"     已批准: {stats['approved_content']}")
        
        return True
    except Exception as e:
        print(f"❌ 复查系统测试失败: {e}")
        return False


async def test_enhanced_publisher():
    """测试增强版发布器"""
    print("\n📱 测试增强版发布器...")
    publisher = DailyTechPublisher(use_review_system=True)
    
    try:
        # 1. 创建内容草稿
        print("  1. 创建内容草稿:")
        draft_result = await publisher.create_content_drafts_for_review()
        print(f"     结果: {draft_result['message']}")
        
        # 2. 测试发布已审核内容（不实际发布，仅测试逻辑）
        print("  2. 发布已审核内容:")
        # 先批准一些内容
        if publisher.review_system:
            pending = await publisher.review_system.get_pending_reviews()
            if pending:
                # 批准第一个内容用于测试
                first_draft = pending[0]
                await publisher.review_system.approve_content(first_draft.draft_id, "测试批准")
                print(f"     已批准测试内容: {first_draft.draft_id}")
        
        # 注意：这里不实际调用publish_approved_content以避免真实发布
        print("     发布功能已实现（跳过实际发布避免spam）")
        
        return True
    except Exception as e:
        print(f"❌ 增强版发布器测试失败: {e}")
        return False


async def test_scheduler_configuration():
    """测试调度器配置"""
    print("\n⏰ 测试调度器配置...")
    
    try:
        scheduler = ManualTwitterScheduler(interval_hours=1)
        scheduler.add_scheduled_jobs()
        
        jobs = scheduler.scheduler.get_jobs()
        print(f"  总任务数: {len(jobs)}")
        
        # 分类统计
        draft_jobs = []
        publish_jobs = []
        analysis_jobs = []
        
        for job in jobs:
            job_name = job.name
            if "草稿" in job_name:
                draft_jobs.append(job_name)
            elif "发布" in job_name:
                publish_jobs.append(job_name)
            else:
                analysis_jobs.append(job_name)
        
        print(f"  草稿创建任务: {len(draft_jobs)}个")
        for job_name in draft_jobs:
            print(f"    - {job_name}")
            
        print(f"  发布任务: {len(publish_jobs)}个")
        for job_name in publish_jobs:
            print(f"    - {job_name}")
            
        print(f"  分析任务: {len(analysis_jobs)}个")
        
        return True
    except Exception as e:
        print(f"❌ 调度器配置测试失败: {e}")
        return False


async def test_content_quality():
    """测试内容质量"""
    print("\n✅ 测试内容质量...")
    generator = TechContentGenerator()
    
    try:
        # 测试各种内容的字数限制
        content_types = [
            ("传统科技头条", generator.generate_daily_headlines()),
            ("中医科技头条", generator.generate_tcm_tech_headlines()),
            ("每日中医专题", generator.generate_daily_tcm_tech_content()),
            ("周报内容", generator.generate_weekly_recap()),
        ]
        
        all_valid = True
        
        for content_name, content_coro in content_types:
            content = await content_coro
            char_count = len(content)
            is_valid = char_count <= 280
            
            print(f"  {content_name}: {char_count}字 {'✅' if is_valid else '❌'}")
            if not is_valid:
                all_valid = False
                print(f"    内容: {content[:100]}...")
        
        # 测试线程内容
        thread_content = await generator.generate_wisdom_ai_thread()
        thread_valid = all(len(tweet) <= 280 for tweet in thread_content)
        print(f"  智慧线程: {len(thread_content)}条, 字数检查 {'✅' if thread_valid else '❌'}")
        
        if not thread_valid:
            all_valid = False
            for i, tweet in enumerate(thread_content, 1):
                if len(tweet) > 280:
                    print(f"    推文{i}: {len(tweet)}字 ❌")
        
        return all_valid
    except Exception as e:
        print(f"❌ 内容质量测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始增强版Twitter发布系统测试\n")
    
    test_results = []
    
    # 执行各项测试
    tests = [
        ("中医科技内容生成", test_tcm_content_generation),
        ("内容复查系统", test_review_system),
        ("增强版发布器", test_enhanced_publisher),
        ("调度器配置", test_scheduler_configuration),
        ("内容质量检查", test_content_quality),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"🔄 运行测试: {test_name}")
            result = await test_func()
            test_results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name} 测试完成\n")
        except Exception as e:
            logger.error(f"测试 {test_name} 出错: {e}")
            test_results.append((test_name, False))
            print(f"❌ {test_name} 测试出错\n")
    
    # 输出测试结果
    print(f"{'='*60}")
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
        print("🎉 所有测试通过！增强版系统已准备就绪。")
        print("\n📋 新功能使用方式:")
        print("1. 启动系统:")
        print("   python start_daily_publisher.py")
        print("\n2. 内容复查:")
        print("   python content_review_cli.py --interactive")
        print("   python content_review_cli.py --generate tcm-headlines")
        print("   python content_review_cli.py --batch-approve")
        print("\n3. 发布计划:")
        print("   06:30 - 创建内容草稿")
        print("   07:00-07:45 - 人工审核时间窗口") 
        print("   07:45 - 发布已审核内容")
        print("   08:00 - 头条发布")
        print("   12:00 - AI+传统智慧线程")
        print("   14:00 - 中医科技专题")
        print("   16:00 - 精选转发")
        print("   20:00 - 周报（周日）")
    else:
        print("⚠️ 部分测试失败，请检查配置后重试。")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""内容复查CLI工具

命令行工具用于管理内容复查流程：
- 预生成内容草稿
- 交互式审核
- 批量操作
- 历史查询
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.content_reviewer import ContentReviewSystem, interactive_review_session
from react_agent.content_generator import TechContentGenerator
from react_agent.daily_publisher import DailyTechPublisher
from dotenv import load_dotenv

load_dotenv()


async def generate_preview_content(content_type: str):
    """预生成内容用于预览"""
    generator = TechContentGenerator()
    review_system = ContentReviewSystem()
    
    print(f"🔄 生成 {content_type} 内容...")
    
    try:
        if content_type == "headlines":
            content = await generator.generate_daily_headlines()
            metadata = {"type": "regular_tech", "generated_at": "now"}
            
        elif content_type == "tcm-headlines":
            content = await generator.generate_tcm_tech_headlines()
            metadata = {"type": "tcm_tech", "generated_at": "now"}
            
        elif content_type == "ai-thread":
            content = await generator.generate_wisdom_ai_thread()
            metadata = {"type": "ai_wisdom", "thread_length": len(content)}
            
        elif content_type == "tcm-focus":
            content = await generator.generate_daily_tcm_tech_content()
            metadata = {"type": "tcm_daily", "generated_at": "now"}
            
        elif content_type == "weekly":
            content = await generator.generate_weekly_recap()
            metadata = {"type": "weekly_recap", "generated_at": "now"}
            
        else:
            print(f"❌ 不支持的内容类型: {content_type}")
            return None
        
        # 创建草稿
        draft_id = await review_system.create_draft(content_type, content, metadata)
        print(f"✅ 内容草稿已生成: {draft_id}")
        
        # 显示预览
        preview = await review_system.preview_content(draft_id)
        print(f"\n📖 内容预览:")
        print(f"类型: {preview['content_type']}")
        
        if isinstance(content, list):
            print(f"线程内容 ({len(content)}条):")
            for i, tweet in enumerate(content, 1):
                print(f"  {i}. {tweet[:60]}... (字数: {len(tweet)})")
        else:
            print(f"内容: {content[:100]}...")
            print(f"字数: {len(content)}")
        
        return draft_id
        
    except Exception as e:
        print(f"❌ 生成内容失败: {e}")
        return None


async def batch_approve_safe():
    """批量审核安全内容"""
    review_system = ContentReviewSystem()
    
    pending = await review_system.get_pending_reviews()
    if not pending:
        print("✅ 没有待审核内容")
        return
    
    approved_count = 0
    
    for draft in pending:
        # 简单的安全检查
        safe = True
        
        if isinstance(draft.content, list):
            # 检查线程
            for tweet in draft.content:
                if len(tweet) > 280:
                    safe = False
                    break
        else:
            # 检查单条推文
            if len(draft.content) > 280:
                safe = False
        
        if safe:
            try:
                await review_system.approve_content(draft.draft_id, "自动批准：通过安全检查")
                print(f"✅ 自动批准: {draft.draft_id}")
                approved_count += 1
            except Exception as e:
                print(f"❌ 批准失败 {draft.draft_id}: {e}")
        else:
            print(f"⚠️ 跳过 {draft.draft_id}: 未通过安全检查")
    
    print(f"\n📊 批量审核完成: 批准了 {approved_count} 个内容")


async def show_stats():
    """显示统计信息"""
    review_system = ContentReviewSystem()
    
    stats = await review_system.get_stats()
    print("📊 内容复查系统统计")
    print("=" * 30)
    print(f"总草稿数:   {stats['total_drafts']}")
    print(f"待审核:     {stats['pending_reviews']}")
    print(f"已批准:     {stats['approved_content']}")  
    print(f"已发布:     {stats['published_content']}")
    print(f"总审核数:   {stats['total_reviews']}")
    print(f"通过率:     {stats['approval_rate']}%")
    

async def show_history(days: int = 7):
    """显示审核历史"""
    review_system = ContentReviewSystem()
    
    history = await review_system.get_review_history(days)
    if not history:
        print(f"📚 最近{days}天没有审核记录")
        return
    
    print(f"📚 最近{days}天审核历史 ({len(history)}条)")
    print("=" * 50)
    
    for review in history[:20]:  # 显示最近20条
        decision_emoji = "✅" if review['decision'] == 'approved' else "❌"
        print(f"{decision_emoji} [{review['draft_content_type']}] {review['draft_id']}")
        print(f"   决定: {review['decision']}")
        print(f"   时间: {review['reviewed_at'][:19]}")
        if review['reviewer_notes']:
            print(f"   备注: {review['reviewer_notes'][:50]}...")
        print()


async def show_pending():
    """显示待审核内容"""
    review_system = ContentReviewSystem()
    
    pending = await review_system.get_pending_reviews()
    if not pending:
        print("✅ 没有待审核内容")
        return
    
    print(f"📋 待审核内容 ({len(pending)}条)")
    print("=" * 40)
    
    for i, draft in enumerate(pending, 1):
        print(f"{i}. [{draft.content_type}] {draft.draft_id}")
        print(f"   状态: {draft.status.value}")
        print(f"   创建: {draft.created_at[:19]}")
        
        if isinstance(draft.content, list):
            print(f"   类型: 线程 ({len(draft.content)}条)")
            print(f"   预览: {draft.content[0][:40]}...")
        else:
            print(f"   类型: 单条推文")
            print(f"   预览: {draft.content[:40]}...")
        print()


async def main():
    parser = argparse.ArgumentParser(
        description="内容复查CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python content_review_cli.py --generate headlines        # 生成头条草稿
  python content_review_cli.py --generate tcm-headlines    # 生成中医科技头条
  python content_review_cli.py --generate ai-thread        # 生成AI线程
  python content_review_cli.py --generate tcm-focus        # 生成中医专题
  
  python content_review_cli.py --interactive               # 交互式审核
  python content_review_cli.py --list-pending              # 查看待审核内容
  python content_review_cli.py --batch-approve             # 批量审核
  python content_review_cli.py --stats                     # 查看统计信息
  python content_review_cli.py --history 3                 # 查看3天历史
        """
    )
    
    parser.add_argument(
        "--generate", 
        choices=["headlines", "tcm-headlines", "ai-thread", "tcm-focus", "weekly"],
        help="生成指定类型的内容草稿"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="启动交互式审核会话"
    )
    parser.add_argument(
        "--list-pending", 
        action="store_true",
        help="列出待审核内容"
    )
    parser.add_argument(
        "--batch-approve", 
        action="store_true",
        help="批量审核安全内容"
    )
    parser.add_argument(
        "--stats", 
        action="store_true",
        help="显示统计信息"
    )
    parser.add_argument(
        "--history", 
        type=int, 
        metavar="DAYS",
        help="显示N天内的审核历史"
    )
    
    args = parser.parse_args()
    
    try:
        if args.generate:
            await generate_preview_content(args.generate)
            
        elif args.interactive:
            await interactive_review_session()
            
        elif args.list_pending:
            await show_pending()
            
        elif args.batch_approve:
            await batch_approve_safe()
            
        elif args.stats:
            await show_stats()
            
        elif args.history:
            await show_history(args.history)
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"❌ 出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
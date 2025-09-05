#!/usr/bin/env python3
"""内容复查和审核系统

提供内容发布前的审核工作流：
- 内容预生成和草稿保存
- 交互式内容审核
- 批准/拒绝决定
- 历史内容查询
- 发布计划管理
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ContentStatus(Enum):
    DRAFT = "draft"
    REVIEWING = "reviewing" 
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"


class ReviewDecision(Enum):
    APPROVE = "approved"
    REJECT = "rejected"
    PENDING = "pending"


@dataclass
class ContentDraft:
    """内容草稿"""
    draft_id: str
    content_type: str  # headlines, ai_thread, tcm_focus, retweet, weekly
    content: Union[str, List[str]]  # 单条推文或线程
    metadata: Dict[str, Any]
    status: ContentStatus
    created_at: str
    scheduled_time: Optional[str] = None


@dataclass
class ReviewSession:
    """审核会话"""
    review_id: str
    draft_id: str
    reviewer_notes: str
    decision: ReviewDecision
    reviewed_at: str
    modifications: Optional[Dict[str, Any]] = None


@dataclass
class PublishRecord:
    """发布记录"""
    publish_id: str
    draft_id: str
    tweet_ids: List[str]
    published_at: str
    performance: Optional[Dict[str, Any]] = None


class ContentReviewSystem:
    """内容复查和审核系统"""
    
    def __init__(self, data_dir: str = "data/review"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据文件
        self.drafts_file = self.data_dir / "drafts.json"
        self.reviews_file = self.data_dir / "reviews.json"
        self.publications_file = self.data_dir / "publications.json"
        
        # 初始化存储
        self._init_storage()
        
    def _init_storage(self):
        """初始化存储文件"""
        for file_path in [self.drafts_file, self.reviews_file, self.publications_file]:
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_data(self, file_path: Path) -> Dict[str, Any]:
        """加载数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: Path, data: Dict[str, Any]):
        """保存数据文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def create_draft(self, content_type: str, content: Union[str, List[str]], 
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建内容草稿"""
        try:
            # 生成草稿ID
            draft_id = f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 创建草稿对象
            draft = ContentDraft(
                draft_id=draft_id,
                content_type=content_type,
                content=content,
                metadata=metadata or {},
                status=ContentStatus.DRAFT,
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
            # 保存到文件
            drafts = self._load_data(self.drafts_file)
            draft_dict = asdict(draft)
            draft_dict['status'] = draft.status.value  # 转换枚举为字符串
            drafts[draft_id] = draft_dict
            self._save_data(self.drafts_file, drafts)
            
            logger.info(f"✅ 创建草稿成功: {draft_id}")
            return draft_id
            
        except Exception as e:
            logger.error(f"❌ 创建草稿失败: {e}")
            raise
    
    async def get_draft(self, draft_id: str) -> Optional[ContentDraft]:
        """获取草稿"""
        drafts = self._load_data(self.drafts_file)
        draft_data = drafts.get(draft_id)
        
        if draft_data:
            draft_data['status'] = ContentStatus(draft_data['status'])
            return ContentDraft(**draft_data)
        return None
    
    async def get_pending_reviews(self) -> List[ContentDraft]:
        """获取待审核的内容"""
        drafts = self._load_data(self.drafts_file)
        pending_drafts = []
        
        for draft_data in drafts.values():
            if draft_data['status'] in ['draft', 'reviewing']:
                draft_data['status'] = ContentStatus(draft_data['status'])
                pending_drafts.append(ContentDraft(**draft_data))
        
        # 按创建时间排序
        pending_drafts.sort(key=lambda x: x.created_at)
        return pending_drafts
    
    async def preview_content(self, draft_id: str) -> Dict[str, Any]:
        """预览内容"""
        draft = await self.get_draft(draft_id)
        if not draft:
            return {"error": "草稿不存在"}
        
        preview = {
            "draft_id": draft.draft_id,
            "content_type": draft.content_type,
            "content": draft.content,
            "metadata": draft.metadata,
            "status": draft.status.value,
            "created_at": draft.created_at
        }
        
        # 添加内容分析
        if isinstance(draft.content, list):
            # 线程内容
            preview["thread_length"] = len(draft.content)
            preview["total_chars"] = sum(len(tweet) for tweet in draft.content)
            preview["char_check"] = all(len(tweet) <= 280 for tweet in draft.content)
        else:
            # 单条内容
            preview["char_count"] = len(draft.content)
            preview["char_check"] = len(draft.content) <= 280
        
        return preview
    
    async def submit_for_review(self, draft_id: str) -> bool:
        """提交审核"""
        try:
            drafts = self._load_data(self.drafts_file)
            if draft_id in drafts:
                drafts[draft_id]['status'] = ContentStatus.REVIEWING.value
                self._save_data(self.drafts_file, drafts)
                logger.info(f"✅ 草稿提交审核: {draft_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 提交审核失败: {e}")
            return False
    
    async def review_content(self, draft_id: str, decision: ReviewDecision, 
                            notes: str = "", modifications: Optional[Dict[str, Any]] = None) -> str:
        """审核内容"""
        try:
            # 生成审核ID
            review_id = f"review_{draft_id}_{datetime.now().strftime('%H%M%S')}"
            
            # 创建审核记录
            review = ReviewSession(
                review_id=review_id,
                draft_id=draft_id,
                reviewer_notes=notes,
                decision=decision,
                reviewed_at=datetime.now(timezone.utc).isoformat(),
                modifications=modifications
            )
            
            # 保存审核记录
            reviews = self._load_data(self.reviews_file)
            review_dict = asdict(review)
            review_dict['decision'] = review.decision.value  # 转换枚举为字符串
            reviews[review_id] = review_dict
            self._save_data(self.reviews_file, reviews)
            
            # 更新草稿状态
            drafts = self._load_data(self.drafts_file)
            if draft_id in drafts:
                drafts[draft_id]['status'] = decision.value
                self._save_data(self.drafts_file, drafts)
            
            logger.info(f"✅ 审核完成: {review_id} - {decision.value}")
            return review_id
            
        except Exception as e:
            logger.error(f"❌ 审核失败: {e}")
            raise
    
    async def approve_content(self, draft_id: str, notes: str = "") -> str:
        """批准内容"""
        return await self.review_content(draft_id, ReviewDecision.APPROVE, notes)
    
    async def reject_content(self, draft_id: str, reason: str) -> str:
        """拒绝内容"""
        return await self.review_content(draft_id, ReviewDecision.REJECT, reason)
    
    async def get_approved_content(self) -> List[ContentDraft]:
        """获取已批准的内容"""
        drafts = self._load_data(self.drafts_file)
        approved_drafts = []
        
        for draft_data in drafts.values():
            if draft_data['status'] == 'approved':
                draft_data['status'] = ContentStatus(draft_data['status'])
                approved_drafts.append(ContentDraft(**draft_data))
        
        approved_drafts.sort(key=lambda x: x.created_at)
        return approved_drafts
    
    async def schedule_content(self, draft_id: str, scheduled_time: str) -> bool:
        """安排内容发布时间"""
        try:
            drafts = self._load_data(self.drafts_file)
            if draft_id in drafts and drafts[draft_id]['status'] == 'approved':
                drafts[draft_id]['status'] = ContentStatus.SCHEDULED.value
                drafts[draft_id]['scheduled_time'] = scheduled_time
                self._save_data(self.drafts_file, drafts)
                logger.info(f"✅ 内容已安排发布: {draft_id} at {scheduled_time}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 安排发布失败: {e}")
            return False
    
    async def mark_as_published(self, draft_id: str, tweet_ids: List[str]) -> str:
        """标记为已发布"""
        try:
            publish_id = f"pub_{draft_id}_{datetime.now().strftime('%H%M%S')}"
            
            # 创建发布记录
            publication = PublishRecord(
                publish_id=publish_id,
                draft_id=draft_id,
                tweet_ids=tweet_ids,
                published_at=datetime.now(timezone.utc).isoformat()
            )
            
            # 保存发布记录
            publications = self._load_data(self.publications_file)
            publications[publish_id] = asdict(publication)
            self._save_data(self.publications_file, publications)
            
            # 更新草稿状态
            drafts = self._load_data(self.drafts_file)
            if draft_id in drafts:
                drafts[draft_id]['status'] = ContentStatus.PUBLISHED.value
                self._save_data(self.drafts_file, drafts)
            
            logger.info(f"✅ 标记为已发布: {publish_id}")
            return publish_id
            
        except Exception as e:
            logger.error(f"❌ 标记发布失败: {e}")
            raise
    
    async def get_review_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取审核历史"""
        reviews = self._load_data(self.reviews_file)
        drafts = self._load_data(self.drafts_file)
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        recent_reviews = []
        
        for review_data in reviews.values():
            review_time = datetime.fromisoformat(review_data['reviewed_at'])
            if review_time >= cutoff_time:
                # 添加草稿信息
                draft_id = review_data['draft_id']
                if draft_id in drafts:
                    review_with_draft = review_data.copy()
                    review_with_draft['draft_content_type'] = drafts[draft_id]['content_type']
                    recent_reviews.append(review_with_draft)
        
        recent_reviews.sort(key=lambda x: x['reviewed_at'], reverse=True)
        return recent_reviews
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        drafts = self._load_data(self.drafts_file)
        reviews = self._load_data(self.reviews_file)
        publications = self._load_data(self.publications_file)
        
        stats = {
            "total_drafts": len(drafts),
            "pending_reviews": len([d for d in drafts.values() if d['status'] in ['draft', 'reviewing']]),
            "approved_content": len([d for d in drafts.values() if d['status'] == 'approved']),
            "published_content": len([d for d in drafts.values() if d['status'] == 'published']),
            "total_reviews": len(reviews),
            "total_publications": len(publications)
        }
        
        # 审核通过率
        if len(reviews) > 0:
            approved_reviews = len([r for r in reviews.values() if r['decision'] == 'approved'])
            stats["approval_rate"] = round(approved_reviews / len(reviews) * 100, 1)
        else:
            stats["approval_rate"] = 0.0
            
        return stats


# CLI 交互功能
async def interactive_review_session():
    """交互式审核会话"""
    review_system = ContentReviewSystem()
    
    print("🔍 内容复查系统")
    print("=" * 50)
    
    while True:
        print("\n📋 可用操作：")
        print("1. 查看待审核内容")
        print("2. 审核特定内容")
        print("3. 查看已批准内容")
        print("4. 查看统计信息")
        print("5. 查看审核历史")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-5): ").strip()
        
        try:
            if choice == '0':
                print("👋 退出复查系统")
                break
                
            elif choice == '1':
                # 查看待审核内容
                pending = await review_system.get_pending_reviews()
                if not pending:
                    print("✅ 没有待审核内容")
                else:
                    print(f"\n📋 待审核内容 ({len(pending)}条):")
                    for i, draft in enumerate(pending, 1):
                        print(f"{i}. [{draft.content_type}] {draft.draft_id}")
                        if isinstance(draft.content, list):
                            print(f"   线程长度: {len(draft.content)}条")
                        else:
                            print(f"   内容: {draft.content[:50]}...")
                        print(f"   创建时间: {draft.created_at}")
                        print()
            
            elif choice == '2':
                # 审核内容
                draft_id = input("请输入草稿ID: ").strip()
                if not draft_id:
                    continue
                
                preview = await review_system.preview_content(draft_id)
                if "error" in preview:
                    print(f"❌ {preview['error']}")
                    continue
                
                print(f"\n📖 内容预览:")
                print(f"类型: {preview['content_type']}")
                print(f"状态: {preview['status']}")
                
                if isinstance(preview['content'], list):
                    print(f"线程内容 ({len(preview['content'])}条):")
                    for i, tweet in enumerate(preview['content'], 1):
                        print(f"  {i}. {tweet} (字数: {len(tweet)})")
                    print(f"字数检查: {'✅' if preview['char_check'] else '❌'}")
                else:
                    print(f"内容: {preview['content']}")
                    print(f"字数: {preview['char_count']} {'✅' if preview['char_check'] else '❌'}")
                
                # 询问决定
                print("\n请选择操作:")
                print("1. 批准")
                print("2. 拒绝") 
                print("3. 跳过")
                
                action = input("选择 (1-3): ").strip()
                
                if action == '1':
                    notes = input("批准备注 (可选): ").strip()
                    review_id = await review_system.approve_content(draft_id, notes)
                    print(f"✅ 内容已批准: {review_id}")
                    
                elif action == '2':
                    reason = input("拒绝原因: ").strip()
                    if reason:
                        review_id = await review_system.reject_content(draft_id, reason)
                        print(f"❌ 内容已拒绝: {review_id}")
                    else:
                        print("⚠️ 请提供拒绝原因")
            
            elif choice == '3':
                # 查看已批准内容
                approved = await review_system.get_approved_content()
                if not approved:
                    print("📝 没有已批准的内容")
                else:
                    print(f"\n✅ 已批准内容 ({len(approved)}条):")
                    for draft in approved:
                        print(f"- [{draft.content_type}] {draft.draft_id}")
                        print(f"  创建时间: {draft.created_at}")
            
            elif choice == '4':
                # 统计信息
                stats = await review_system.get_stats()
                print(f"\n📊 统计信息:")
                print(f"总草稿数: {stats['total_drafts']}")
                print(f"待审核: {stats['pending_reviews']}")
                print(f"已批准: {stats['approved_content']}")
                print(f"已发布: {stats['published_content']}")
                print(f"审核通过率: {stats['approval_rate']}%")
            
            elif choice == '5':
                # 审核历史
                history = await review_system.get_review_history()
                if not history:
                    print("📚 没有审核历史")
                else:
                    print(f"\n📚 最近审核历史 ({len(history)}条):")
                    for review in history[:10]:  # 显示最近10条
                        decision_emoji = "✅" if review['decision'] == 'approved' else "❌"
                        print(f"{decision_emoji} [{review['draft_content_type']}] {review['draft_id']}")
                        print(f"   决定: {review['decision']}")
                        print(f"   时间: {review['reviewed_at']}")
                        if review['reviewer_notes']:
                            print(f"   备注: {review['reviewer_notes']}")
                        print()
            
            else:
                print("❌ 无效选择")
                
        except Exception as e:
            print(f"❌ 操作出错: {e}")


if __name__ == "__main__":
    # 运行交互式审核会话
    asyncio.run(interactive_review_session())
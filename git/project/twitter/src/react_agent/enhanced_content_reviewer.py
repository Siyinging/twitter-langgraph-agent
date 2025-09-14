#!/usr/bin/env python3
"""增强内容复查系统

在原有复查系统基础上增加：
- 图片内容审核
- 实时性验证 
- 内容质量评估
- 事实核查功能
- 紧急发布流程
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import base64

from src.react_agent.content_reviewer import ContentReviewSystem, ContentDraft, ContentStatus, ReviewDecision
from src.react_agent.real_time_news import RealTimeNewsCollector

logger = logging.getLogger(__name__)


class UrgencyLevel(Enum):
    """紧急程度"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    URGENT = "urgent"


class ContentQuality(Enum):
    """内容质量等级"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


@dataclass 
class ImageContent:
    """图片内容"""
    image_path: str
    image_type: str  # chart, photo, infographic, screenshot
    description: str
    alt_text: str
    file_size: int
    dimensions: Tuple[int, int]
    created_at: str


@dataclass
class QualityAssessment:
    """质量评估"""
    overall_score: float  # 0-1
    timeliness_score: float  # 0-1  
    accuracy_score: float  # 0-1
    engagement_score: float  # 0-1
    readability_score: float  # 0-1
    issues: List[str]
    recommendations: List[str]


@dataclass
class EnhancedContentDraft:
    """增强内容草稿"""
    draft_id: str
    content_type: str
    content: Union[str, List[str]]
    images: List[ImageContent]  # 新增图片内容
    metadata: Dict[str, Any]
    status: ContentStatus
    urgency: UrgencyLevel  # 新增紧急程度
    quality_assessment: Optional[QualityAssessment]  # 新增质量评估
    news_sources: List[str]  # 新增新闻来源
    created_at: str
    expires_at: Optional[str]  # 新增过期时间
    scheduled_time: Optional[str] = None


class EnhancedContentReviewSystem(ContentReviewSystem):
    """增强内容复查系统"""
    
    def __init__(self, data_dir: str = "data/review"):
        super().__init__(data_dir)
        
        # 新增文件
        self.quality_reports_file = self.data_dir / "quality_reports.json"
        self.image_cache_file = self.data_dir / "image_cache.json"
        self.fact_check_file = self.data_dir / "fact_checks.json"
        
        # 初始化新文件
        self._init_enhanced_storage()
        
        # 新闻收集器
        self.news_collector = RealTimeNewsCollector()
        
        # 质量评估权重
        self.quality_weights = {
            "timeliness": 0.3,  # 时效性
            "accuracy": 0.25,   # 准确性
            "engagement": 0.25, # 吸引力
            "readability": 0.2  # 可读性
        }
        
        # 紧急关键词
        self.urgent_keywords = [
            "breaking", "urgent", "alert", "emergency", "just in",
            "突发", "紧急", "警报", "最新消息", "刚刚"
        ]
        
        # 质量检查规则
        self.quality_rules = {
            "min_length": 10,
            "max_length": 280,
            "banned_words": ["spam", "scam", "fake", "垃圾", "欺诈"],
            "required_hashtags": ["#科技", "#AI", "#创新", "#中医科技"],
            "max_hashtags": 5
        }
    
    def _init_enhanced_storage(self):
        """初始化增强存储文件"""
        for file_path in [self.quality_reports_file, self.image_cache_file, self.fact_check_file]:
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def create_enhanced_draft(self, content_type: str, content: Union[str, List[str]],
                                  images: Optional[List[str]] = None,
                                  urgency: UrgencyLevel = UrgencyLevel.MEDIUM,
                                  expires_hours: int = 24,
                                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建增强草稿"""
        try:
            # 生成草稿ID
            draft_id = f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 处理图片内容
            image_contents = []
            if images:
                for img_path in images:
                    img_content = await self._process_image(img_path)
                    if img_content:
                        image_contents.append(img_content)
            
            # 质量评估
            quality_assessment = await self._assess_content_quality(content, image_contents)
            
            # 获取新闻来源
            news_sources = await self._extract_news_sources(content)
            
            # 设置过期时间
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=expires_hours)).isoformat()
            
            # 创建增强草稿
            draft = EnhancedContentDraft(
                draft_id=draft_id,
                content_type=content_type,
                content=content,
                images=image_contents,
                metadata=metadata or {},
                status=ContentStatus.DRAFT,
                urgency=urgency,
                quality_assessment=quality_assessment,
                news_sources=news_sources,
                created_at=datetime.now(timezone.utc).isoformat(),
                expires_at=expires_at
            )
            
            # 保存到文件
            await self._save_enhanced_draft(draft)
            
            logger.info(f"✅ 创建增强草稿成功: {draft_id} (质量分数: {quality_assessment.overall_score:.2f})")
            return draft_id
            
        except Exception as e:
            logger.error(f"❌ 创建增强草稿失败: {e}")
            raise
    
    async def _process_image(self, image_path: str) -> Optional[ImageContent]:
        """处理图片内容"""
        try:
            img_path = Path(image_path)
            if not img_path.exists():
                logger.warning(f"图片文件不存在: {image_path}")
                return None
            
            # 获取文件信息
            file_size = img_path.stat().st_size
            
            # 简单的图片类型判断
            image_type = "unknown"
            if "chart" in img_path.name.lower():
                image_type = "chart"
            elif "photo" in img_path.name.lower():
                image_type = "photo"
            elif "infographic" in img_path.name.lower():
                image_type = "infographic"
            
            # 生成描述和alt文本
            description = f"图片: {img_path.name}"
            alt_text = await self._generate_alt_text(img_path.name, image_type)
            
            return ImageContent(
                image_path=str(img_path),
                image_type=image_type,
                description=description,
                alt_text=alt_text,
                file_size=file_size,
                dimensions=(0, 0),  # 简化处理，实际应用中可以获取真实尺寸
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ 处理图片失败: {e}")
            return None
    
    async def _generate_alt_text(self, filename: str, image_type: str) -> str:
        """生成图片alt文本"""
        alt_templates = {
            "chart": f"数据图表: {filename}",
            "photo": f"照片: {filename}",
            "infographic": f"信息图: {filename}",
            "unknown": f"图片: {filename}"
        }
        
        return alt_templates.get(image_type, f"图片: {filename}")
    
    async def _assess_content_quality(self, content: Union[str, List[str]], 
                                     images: List[ImageContent]) -> QualityAssessment:
        """评估内容质量"""
        try:
            # 合并文本内容
            text_content = ""
            if isinstance(content, list):
                text_content = " ".join(content)
            else:
                text_content = content
            
            # 时效性评分
            timeliness_score = await self._assess_timeliness(text_content)
            
            # 准确性评分
            accuracy_score = await self._assess_accuracy(text_content)
            
            # 吸引力评分
            engagement_score = await self._assess_engagement(text_content, images)
            
            # 可读性评分
            readability_score = await self._assess_readability(text_content)
            
            # 计算总分
            overall_score = (
                timeliness_score * self.quality_weights["timeliness"] +
                accuracy_score * self.quality_weights["accuracy"] +
                engagement_score * self.quality_weights["engagement"] +
                readability_score * self.quality_weights["readability"]
            )
            
            # 发现问题
            issues = await self._identify_issues(text_content, images)
            
            # 生成建议
            recommendations = await self._generate_recommendations(text_content, images, overall_score)
            
            return QualityAssessment(
                overall_score=overall_score,
                timeliness_score=timeliness_score,
                accuracy_score=accuracy_score,
                engagement_score=engagement_score,
                readability_score=readability_score,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ 质量评估失败: {e}")
            # 返回默认评估
            return QualityAssessment(
                overall_score=0.5,
                timeliness_score=0.5,
                accuracy_score=0.5,
                engagement_score=0.5,
                readability_score=0.5,
                issues=["评估失败"],
                recommendations=["请手动检查内容质量"]
            )
    
    async def _assess_timeliness(self, text: str) -> float:
        """评估时效性"""
        score = 0.5  # 基础分数
        
        # 检查时间相关词汇
        time_indicators = [
            "今日", "today", "latest", "new", "breaking", "just", "现在", "刚刚", "最新"
        ]
        
        for indicator in time_indicators:
            if indicator.lower() in text.lower():
                score += 0.1
        
        # 检查日期信息
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date in text:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _assess_accuracy(self, text: str) -> float:
        """评估准确性（简化实现）"""
        score = 0.7  # 基础分数，假设大多数内容是准确的
        
        # 检查是否包含可疑内容
        suspicious_words = ["据说", "可能", "也许", "reportedly", "allegedly", "rumors"]
        
        for word in suspicious_words:
            if word.lower() in text.lower():
                score -= 0.1
        
        # 检查是否有具体数据
        if re.search(r'\d+%', text) or re.search(r'\d+\s*(万|亿|million|billion)', text):
            score += 0.1
        
        return max(score, 0.0)
    
    async def _assess_engagement(self, text: str, images: List[ImageContent]) -> float:
        """评估吸引力"""
        score = 0.5
        
        # 表情符号增加吸引力
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
        score += min(emoji_count * 0.05, 0.3)
        
        # 话题标签
        hashtag_count = len(re.findall(r'#\w+', text))
        if 1 <= hashtag_count <= 3:
            score += 0.2
        elif hashtag_count > 3:
            score -= 0.1  # 太多标签降低质量
        
        # 图片内容
        if images:
            score += min(len(images) * 0.15, 0.3)
        
        # 长度适中
        text_len = len(text)
        if 100 <= text_len <= 250:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _assess_readability(self, text: str) -> float:
        """评估可读性"""
        score = 0.7
        
        # 检查句子长度
        sentences = re.split(r'[。！？.!?]', text)
        avg_sentence_length = sum(len(s) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        
        if avg_sentence_length <= 30:
            score += 0.1
        elif avg_sentence_length > 60:
            score -= 0.2
        
        # 检查段落结构
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.1
        
        # 检查标点符号使用
        if text.count('，') + text.count(',') >= 2:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _identify_issues(self, text: str, images: List[ImageContent]) -> List[str]:
        """识别内容问题"""
        issues = []
        
        # 长度检查
        if len(text) < self.quality_rules["min_length"]:
            issues.append(f"内容过短 (少于{self.quality_rules['min_length']}字符)")
        
        if len(text) > self.quality_rules["max_length"]:
            issues.append(f"内容过长 (超过{self.quality_rules['max_length']}字符)")
        
        # 禁用词检查
        for banned_word in self.quality_rules["banned_words"]:
            if banned_word.lower() in text.lower():
                issues.append(f"包含禁用词: {banned_word}")
        
        # 话题标签检查
        hashtag_count = len(re.findall(r'#\w+', text))
        if hashtag_count > self.quality_rules["max_hashtags"]:
            issues.append(f"话题标签过多 ({hashtag_count}个，建议不超过{self.quality_rules['max_hashtags']}个)")
        
        # 图片检查
        for image in images:
            if image.file_size > 5 * 1024 * 1024:  # 5MB
                issues.append(f"图片文件过大: {image.image_path} ({image.file_size / 1024 / 1024:.1f}MB)")
        
        return issues
    
    async def _generate_recommendations(self, text: str, images: List[ImageContent], 
                                       overall_score: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if overall_score < 0.6:
            recommendations.append("内容质量偏低，建议重新编写或大幅修改")
        
        # 表情符号建议
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
        if emoji_count < 2:
            recommendations.append("建议适当添加表情符号增加吸引力")
        
        # 话题标签建议
        hashtag_count = len(re.findall(r'#\w+', text))
        if hashtag_count == 0:
            recommendations.append("建议添加相关话题标签 (#科技 #AI #创新)")
        
        # 图片建议
        if not images:
            recommendations.append("考虑添加相关图片或图表增加视觉效果")
        
        # 长度建议
        if len(text) < 50:
            recommendations.append("内容可以更详细一些")
        elif len(text) > 250:
            recommendations.append("考虑精简内容或分成多条推文")
        
        return recommendations
    
    async def _extract_news_sources(self, content: Union[str, List[str]]) -> List[str]:
        """提取新闻来源"""
        sources = []
        
        text = content if isinstance(content, str) else " ".join(content)
        
        # 简单URL提取
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            try:
                import urllib.parse
                domain = urllib.parse.urlparse(url).netloc
                sources.append(domain)
            except Exception:
                continue
        
        return sources
    
    async def _save_enhanced_draft(self, draft: EnhancedContentDraft):
        """保存增强草稿"""
        try:
            drafts = self._load_data(self.drafts_file)
            
            # 转换为可序列化格式
            draft_dict = {
                "draft_id": draft.draft_id,
                "content_type": draft.content_type,
                "content": draft.content,
                "images": [asdict(img) for img in draft.images],
                "metadata": draft.metadata,
                "status": draft.status.value,
                "urgency": draft.urgency.value,
                "quality_assessment": asdict(draft.quality_assessment) if draft.quality_assessment else None,
                "news_sources": draft.news_sources,
                "created_at": draft.created_at,
                "expires_at": draft.expires_at,
                "scheduled_time": draft.scheduled_time
            }
            
            drafts[draft.draft_id] = draft_dict
            self._save_data(self.drafts_file, drafts)
            
        except Exception as e:
            logger.error(f"❌ 保存增强草稿失败: {e}")
            raise
    
    async def get_enhanced_draft(self, draft_id: str) -> Optional[EnhancedContentDraft]:
        """获取增强草稿"""
        try:
            drafts = self._load_data(self.drafts_file)
            draft_data = drafts.get(draft_id)
            
            if not draft_data:
                return None
            
            # 重构图片对象
            images = []
            for img_data in draft_data.get("images", []):
                images.append(ImageContent(**img_data))
            
            # 重构质量评估对象
            quality_assessment = None
            if draft_data.get("quality_assessment"):
                quality_assessment = QualityAssessment(**draft_data["quality_assessment"])
            
            # 构造增强草稿对象
            return EnhancedContentDraft(
                draft_id=draft_data["draft_id"],
                content_type=draft_data["content_type"],
                content=draft_data["content"],
                images=images,
                metadata=draft_data["metadata"],
                status=ContentStatus(draft_data["status"]),
                urgency=UrgencyLevel(draft_data.get("urgency", "medium")),
                quality_assessment=quality_assessment,
                news_sources=draft_data.get("news_sources", []),
                created_at=draft_data["created_at"],
                expires_at=draft_data.get("expires_at"),
                scheduled_time=draft_data.get("scheduled_time")
            )
            
        except Exception as e:
            logger.error(f"❌ 获取增强草稿失败: {e}")
            return None
    
    async def get_urgent_drafts(self) -> List[EnhancedContentDraft]:
        """获取紧急草稿"""
        drafts = self._load_data(self.drafts_file)
        urgent_drafts = []
        
        for draft_data in drafts.values():
            if (draft_data.get("urgency") in ["high", "urgent"] and 
                draft_data.get("status") in ["draft", "reviewing"]):
                
                draft = await self.get_enhanced_draft(draft_data["draft_id"])
                if draft:
                    urgent_drafts.append(draft)
        
        # 按紧急程度和创建时间排序
        urgent_drafts.sort(key=lambda x: (x.urgency.value, x.created_at), reverse=True)
        return urgent_drafts
    
    async def check_expired_drafts(self) -> List[str]:
        """检查过期草稿"""
        expired_ids = []
        drafts = self._load_data(self.drafts_file)
        current_time = datetime.now(timezone.utc)
        
        for draft_id, draft_data in drafts.items():
            expires_at = draft_data.get("expires_at")
            if expires_at:
                try:
                    expire_time = datetime.fromisoformat(expires_at)
                    if current_time > expire_time:
                        expired_ids.append(draft_id)
                except ValueError:
                    continue
        
        return expired_ids
    
    async def enhanced_preview_content(self, draft_id: str) -> Dict[str, Any]:
        """增强内容预览"""
        draft = await self.get_enhanced_draft(draft_id)
        if not draft:
            return {"error": "草稿不存在"}
        
        preview = {
            "draft_id": draft.draft_id,
            "content_type": draft.content_type,
            "content": draft.content,
            "urgency": draft.urgency.value,
            "status": draft.status.value,
            "created_at": draft.created_at,
            "expires_at": draft.expires_at,
            "images": [
                {
                    "path": img.image_path,
                    "type": img.image_type,
                    "description": img.description,
                    "size_mb": round(img.file_size / 1024 / 1024, 2)
                }
                for img in draft.images
            ],
            "news_sources": draft.news_sources
        }
        
        # 添加质量评估信息
        if draft.quality_assessment:
            qa = draft.quality_assessment
            preview["quality"] = {
                "overall_score": round(qa.overall_score, 2),
                "timeliness": round(qa.timeliness_score, 2),
                "accuracy": round(qa.accuracy_score, 2),
                "engagement": round(qa.engagement_score, 2),
                "readability": round(qa.readability_score, 2),
                "issues": qa.issues,
                "recommendations": qa.recommendations
            }
        
        # 添加内容分析
        if isinstance(draft.content, list):
            preview["thread_length"] = len(draft.content)
            preview["total_chars"] = sum(len(tweet) for tweet in draft.content)
            preview["char_check"] = all(len(tweet) <= 280 for tweet in draft.content)
        else:
            preview["char_count"] = len(draft.content)
            preview["char_check"] = len(draft.content) <= 280
        
        return preview


# 工厂函数
def create_enhanced_reviewer() -> EnhancedContentReviewSystem:
    """创建增强复查系统实例"""
    return EnhancedContentReviewSystem()


if __name__ == "__main__":
    # 测试增强复查系统
    async def test_enhanced_reviewer():
        reviewer = EnhancedContentReviewSystem()
        
        print("=== 测试增强内容复查系统 ===")
        
        # 测试内容
        test_content = "🔥 重大科技突破！OpenAI发布最新AI模型，性能提升300%！这将彻底改变人工智能领域的发展轨迹。#AI #科技突破 #人工智能"
        
        # 创建草稿
        draft_id = await reviewer.create_enhanced_draft(
            content_type="breaking_news",
            content=test_content,
            urgency=UrgencyLevel.HIGH,
            expires_hours=6
        )
        
        print(f"创建草稿: {draft_id}")
        
        # 预览内容
        preview = await reviewer.enhanced_preview_content(draft_id)
        print(f"质量分数: {preview.get('quality', {}).get('overall_score', '未评估')}")
        print(f"问题: {preview.get('quality', {}).get('issues', [])}")
        print(f"建议: {preview.get('quality', {}).get('recommendations', [])}")
    
    asyncio.run(test_enhanced_reviewer())
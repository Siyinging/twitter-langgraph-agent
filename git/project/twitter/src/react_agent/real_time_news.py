#!/usr/bin/env python3
"""实时新闻集成系统

提供多源实时新闻获取和智能筛选功能：
- 科技新闻实时监控
- 中医健康新闻追踪
- AI/ML领域热点发现
- 新闻质量评估和筛选
- 时效性验证
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
from dataclasses import dataclass, asdict

from langchain_tavily import TavilySearch
from react_agent.tools import search

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    url: str
    content: str
    source: str
    published_time: datetime
    category: str  # tech, medical, ai, tcm
    quality_score: float
    trending_score: float
    keywords: List[str]
    summary: str


@dataclass
class TrendingTopic:
    """热点话题"""
    topic: str
    category: str
    mentions: int
    sentiment: str  # positive, neutral, negative
    first_seen: datetime
    last_updated: datetime
    related_news: List[str]  # news URLs
    

class RealTimeNewsCollector:
    """实时新闻收集器"""
    
    def __init__(self):
        self.data_dir = Path("data/news")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 新闻缓存文件
        self.news_cache = self.data_dir / "news_cache.json"
        self.trends_cache = self.data_dir / "trends_cache.json"
        
        # 搜索关键词配置
        self.search_keywords = {
            "tech": [
                "artificial intelligence breakthrough 2025",
                "AI technology innovation today",
                "machine learning research latest",
                "tech startup funding news",
                "quantum computing progress",
                "blockchain technology development",
                "robotics advancement 2025",
                "cybersecurity news today"
            ],
            "medical": [
                "medical AI breakthrough",
                "digital health innovation",
                "telemedicine technology",
                "precision medicine AI",
                "healthcare automation",
                "medical imaging AI",
                "drug discovery AI",
                "biotech innovation 2025"
            ],
            "tcm": [
                "traditional chinese medicine AI",
                "TCM digital transformation",
                "中医 人工智能 technology",
                "traditional medicine technology",
                "herbal medicine AI research",
                "acupuncture digital innovation",
                "TCM modernization news"
            ]
        }
        
        # 质量评估权重
        self.quality_weights = {
            "source_authority": 0.3,
            "content_length": 0.2,
            "keyword_relevance": 0.3,
            "recency": 0.2
        }
        
        # 可信新闻源
        self.trusted_sources = [
            "reuters.com", "bloomberg.com", "techcrunch.com", 
            "nature.com", "science.org", "nejm.org", "mit.edu",
            "stanford.edu", "openai.com", "anthropic.com",
            "google.com", "microsoft.com", "nvidia.com"
        ]
    
    async def collect_latest_news(self, hours_back: int = 24, 
                                 max_results_per_category: int = 10) -> Dict[str, List[NewsItem]]:
        """收集最新新闻"""
        logger.info(f"🔍 开始收集最近{hours_back}小时的新闻...")
        
        all_news = {}
        
        for category, keywords in self.search_keywords.items():
            logger.info(f"📰 收集{category}类别新闻...")
            category_news = []
            
            for keyword in keywords[:3]:  # 限制查询数量避免API限制
                try:
                    # 使用时间限制的搜索
                    time_filter = f"after:{(datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%d')}"
                    search_query = f"{keyword} {time_filter}"
                    
                    # 执行搜索
                    results = await self._search_news(search_query, max_results=5)
                    
                    for result in results:
                        news_item = await self._process_news_result(result, category)
                        if news_item and news_item.quality_score > 0.6:
                            category_news.append(news_item)
                    
                    # 避免API限制
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"搜索关键词'{keyword}'失败: {e}")
                    continue
            
            # 按质量分数排序并限制数量
            category_news.sort(key=lambda x: x.quality_score, reverse=True)
            all_news[category] = category_news[:max_results_per_category]
            
            logger.info(f"✅ {category}类别收集到{len(all_news[category])}条新闻")
        
        # 缓存结果
        await self._cache_news(all_news)
        
        logger.info(f"🎉 新闻收集完成，共收集{sum(len(news) for news in all_news.values())}条")
        return all_news
    
    async def _search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """执行新闻搜索"""
        try:
            # 尝试使用Tavily搜索
            search_tool = TavilySearch(max_results=max_results)
            results = await search_tool.ainvoke(query)
            
            if isinstance(results, list):
                return results
            elif isinstance(results, dict) and 'results' in results:
                return results['results']
            else:
                return []
                
        except Exception as e:
            logger.warning(f"Tavily搜索失败，尝试备用方法: {e}")
            
            # 备用：使用现有的search工具
            try:
                result = await search(query)
                if isinstance(result, dict) and 'results' in result:
                    return result['results'][:max_results]
                return []
            except Exception as e2:
                logger.error(f"备用搜索也失败: {e2}")
                return []
    
    async def _process_news_result(self, result: Dict, category: str) -> Optional[NewsItem]:
        """处理单条新闻结果"""
        try:
            title = result.get('title', '')
            url = result.get('url', '')
            content = result.get('content', '') or result.get('snippet', '')
            
            if not title or not url:
                return None
            
            # 提取发布时间
            published_time = self._extract_publish_time(result)
            
            # 提取来源
            source = self._extract_source(url)
            
            # 质量评估
            quality_score = await self._assess_quality(title, content, source, published_time)
            
            # 趋势分数评估
            trending_score = await self._assess_trending(title, content)
            
            # 提取关键词
            keywords = self._extract_keywords(title + " " + content)
            
            # 生成摘要
            summary = await self._generate_summary(title, content)
            
            return NewsItem(
                title=title,
                url=url,
                content=content[:1000],  # 限制内容长度
                source=source,
                published_time=published_time,
                category=category,
                quality_score=quality_score,
                trending_score=trending_score,
                keywords=keywords,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"处理新闻结果失败: {e}")
            return None
    
    def _extract_publish_time(self, result: Dict) -> datetime:
        """提取发布时间"""
        # 尝试从结果中提取时间
        time_str = result.get('published_date') or result.get('date') or result.get('timestamp')
        
        if time_str:
            try:
                # 尝试多种时间格式解析
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(time_str, fmt).replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
            except Exception:
                pass
        
        # 默认使用当前时间
        return datetime.now(timezone.utc)
    
    def _extract_source(self, url: str) -> str:
        """提取新闻源"""
        try:
            import urllib.parse
            domain = urllib.parse.urlparse(url).netloc
            return domain.replace('www.', '')
        except Exception:
            return "unknown"
    
    async def _assess_quality(self, title: str, content: str, 
                             source: str, published_time: datetime) -> float:
        """评估新闻质量"""
        score = 0.0
        
        # 来源权威性
        if any(trusted in source for trusted in self.trusted_sources):
            score += self.quality_weights["source_authority"]
        
        # 内容长度（合理范围内越长越好）
        content_len = len(content)
        if 200 <= content_len <= 2000:
            score += self.quality_weights["content_length"] * min(content_len / 1000, 1.0)
        
        # 关键词相关性
        tech_keywords = ['AI', 'artificial intelligence', 'machine learning', 'technology', 
                        'innovation', 'breakthrough', 'research', '人工智能', '科技', '创新']
        keyword_count = sum(1 for kw in tech_keywords if kw.lower() in (title + content).lower())
        if keyword_count > 0:
            score += self.quality_weights["keyword_relevance"] * min(keyword_count / 3, 1.0)
        
        # 时效性（24小时内发布的新闻得分更高）
        time_diff = (datetime.now(timezone.utc) - published_time).total_seconds()
        if time_diff < 24 * 3600:  # 24小时内
            score += self.quality_weights["recency"]
        elif time_diff < 72 * 3600:  # 72小时内
            score += self.quality_weights["recency"] * 0.5
        
        return min(score, 1.0)
    
    async def _assess_trending(self, title: str, content: str) -> float:
        """评估趋势热度"""
        trending_indicators = [
            'breaking', 'latest', 'just announced', 'new study', 'breakthrough',
            'first time', 'record', 'milestone', '突破', '最新', '首次', '创纪录'
        ]
        
        text = (title + " " + content).lower()
        trend_score = sum(0.2 for indicator in trending_indicators if indicator in text)
        
        return min(trend_score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        keywords = []
        
        # 技术相关词汇
        tech_terms = ['AI', 'artificial intelligence', 'machine learning', 'blockchain', 
                     'quantum', 'robotics', 'automation', '人工智能', '区块链', '机器学习']
        
        for term in tech_terms:
            if term.lower() in text.lower():
                keywords.append(term)
        
        return keywords[:10]  # 限制关键词数量
    
    async def _generate_summary(self, title: str, content: str) -> str:
        """生成新闻摘要"""
        # 简单的摘要生成：取标题 + 内容前150字符
        summary = title
        if content:
            content_clean = re.sub(r'\s+', ' ', content.strip())
            if len(content_clean) > 150:
                summary += f" - {content_clean[:150]}..."
            else:
                summary += f" - {content_clean}"
        
        return summary
    
    async def _cache_news(self, news_data: Dict[str, List[NewsItem]]):
        """缓存新闻数据"""
        try:
            # 转换为可序列化的格式
            cache_data = {}
            for category, news_list in news_data.items():
                cache_data[category] = []
                for news in news_list:
                    news_dict = asdict(news)
                    news_dict['published_time'] = news.published_time.isoformat()
                    cache_data[category].append(news_dict)
            
            # 添加时间戳
            cache_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            with open(self.news_cache, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            logger.info("✅ 新闻缓存已更新")
            
        except Exception as e:
            logger.error(f"❌ 缓存新闻失败: {e}")
    
    async def get_cached_news(self, max_age_hours: int = 2) -> Optional[Dict[str, List[NewsItem]]]:
        """获取缓存的新闻"""
        try:
            if not self.news_cache.exists():
                return None
            
            with open(self.news_cache, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存时效性
            last_updated = datetime.fromisoformat(cache_data.get('last_updated', ''))
            if (datetime.now(timezone.utc) - last_updated).total_seconds() > max_age_hours * 3600:
                logger.info("📰 缓存已过期，需要重新获取新闻")
                return None
            
            # 重构NewsItem对象
            news_data = {}
            for category, news_list in cache_data.items():
                if category == 'last_updated':
                    continue
                    
                news_data[category] = []
                for news_dict in news_list:
                    news_dict['published_time'] = datetime.fromisoformat(news_dict['published_time'])
                    news_data[category].append(NewsItem(**news_dict))
            
            logger.info(f"✅ 使用缓存新闻，共{sum(len(news) for news in news_data.values())}条")
            return news_data
            
        except Exception as e:
            logger.error(f"❌ 读取缓存新闻失败: {e}")
            return None
    
    async def get_trending_topics(self, news_data: Dict[str, List[NewsItem]]) -> List[TrendingTopic]:
        """分析热点话题"""
        topics = {}
        
        for category, news_list in news_data.items():
            for news in news_list:
                for keyword in news.keywords:
                    if keyword not in topics:
                        topics[keyword] = {
                            'mentions': 0,
                            'category': category,
                            'first_seen': news.published_time,
                            'last_updated': news.published_time,
                            'related_news': []
                        }
                    
                    topics[keyword]['mentions'] += 1
                    topics[keyword]['related_news'].append(news.url)
                    
                    if news.published_time > topics[keyword]['last_updated']:
                        topics[keyword]['last_updated'] = news.published_time
        
        # 转换为TrendingTopic对象
        trending_topics = []
        for topic, data in topics.items():
            if data['mentions'] >= 2:  # 至少被提及2次才算热点
                trending_topics.append(TrendingTopic(
                    topic=topic,
                    category=data['category'],
                    mentions=data['mentions'],
                    sentiment='positive',  # 简化处理
                    first_seen=data['first_seen'],
                    last_updated=data['last_updated'],
                    related_news=data['related_news'][:5]  # 限制相关新闻数量
                ))
        
        # 按提及次数排序
        trending_topics.sort(key=lambda x: x.mentions, reverse=True)
        
        return trending_topics[:20]  # 返回前20个热点
    
    async def generate_timely_content(self, news_data: Dict[str, List[NewsItem]], 
                                     content_type: str = "headlines") -> str:
        """基于实时新闻生成及时内容"""
        if not news_data:
            logger.warning("没有新闻数据，使用备用内容")
            return await self._get_fallback_content(content_type)
        
        try:
            # 选择最高质量的新闻
            all_news = []
            for news_list in news_data.values():
                all_news.extend(news_list)
            
            all_news.sort(key=lambda x: x.quality_score + x.trending_score, reverse=True)
            
            if not all_news:
                return await self._get_fallback_content(content_type)
            
            top_news = all_news[0]
            
            if content_type == "headlines":
                return await self._generate_headlines_from_news(top_news, all_news[:3])
            elif content_type == "thread":
                return await self._generate_thread_from_news(top_news, all_news[:5])
            elif content_type == "tcm_focus":
                tcm_news = [n for n in all_news if n.category == "tcm"]
                return await self._generate_tcm_content_from_news(tcm_news[:3])
            else:
                return await self._generate_general_content_from_news(top_news)
                
        except Exception as e:
            logger.error(f"❌ 生成及时内容失败: {e}")
            return await self._get_fallback_content(content_type)
    
    async def _generate_headlines_from_news(self, top_news: NewsItem, 
                                           recent_news: List[NewsItem]) -> str:
        """从新闻生成头条"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 更个人化的开头
        personal_intros = [
            f"🤔 {date}早上翻科技新闻，看到几个有意思的进展：",
            f"📱 今天{date}的科技圈很热闹，分享几个值得关注的：",
            f"☕ 一边喝咖啡一边看{date}的科技动态，几个点很有意思：",
            f"🧠 {date}科技前沿观察，这些发展让我眼前一亮：",
            f"💭 整理了今天{date}看到的几个科技亮点："
        ]
        
        import random
        headline = random.choice(personal_intros) + "\n\n"
        
        # 更有深度的点评
        title_lower = top_news.title.lower()
        if 'ai' in title_lower or 'artificial intelligence' in title_lower:
            commentary = "这个AI突破很有意思，可能会改变我们对人工智能的认知。"
        elif 'medical' in title_lower or 'health' in title_lower:
            commentary = "医疗技术的进步总是让人振奋，科技真的在改善人类生活。"
        elif 'quantum' in title_lower:
            commentary = "量子技术虽然复杂，但应用前景让人期待。"
        elif 'brain' in title_lower or 'neural' in title_lower:
            commentary = "脑科学和神经技术的突破总是特别吸引人。"
        else:
            commentary = "科技发展的速度真的让人惊叹。"
        
        headline += f"🔬 {top_news.title[:100]}\n{commentary}\n\n"
        
        # 如果有更多新闻，添加简短提及
        if len(recent_news) > 1:
            headline += f"另外还关注到{recent_news[1].title[:80]}，值得深入了解。\n\n"
        
        # 更自然的结尾
        endings = [
            "科技改变世界的脚步从未停歇 🚀",
            "每天都有新的突破，未来可期 ✨", 
            "技术进步让生活更美好 🌟",
            "持续关注这些前沿动态 📡"
        ]
        
        headline += random.choice(endings) + " #科技观察 #创新思考 #AI"
        
        return headline[:280]
    
    async def _generate_thread_from_news(self, top_news: NewsItem, 
                                        recent_news: List[NewsItem]) -> List[str]:
        """从新闻生成线程"""
        thread = []
        
        # 第一条：主要新闻
        thread.append(f"🔥 重大科技突破！{top_news.title}\n\n{top_news.summary[:200]}")
        
        # 第二条：分析
        thread.append(f"🧠 深度解读：{top_news.title}背后的技术创新意味着什么？这可能会改变整个行业的发展方向。")
        
        # 第三条：相关新闻
        if len(recent_news) > 1:
            thread.append(f"📊 相关动态：{recent_news[1].title}。科技领域的创新正在加速推进。")
        
        # 第四条：展望
        thread.append(f"🚀 未来展望：这类技术突破将如何影响我们的日常生活？让我们拭目以待！ #科技创新 #未来趋势")
        
        return thread
    
    async def _generate_tcm_content_from_news(self, tcm_news: List[NewsItem]) -> str:
        """从中医新闻生成专题内容"""
        if not tcm_news:
            return "🏥 中医科技专题\n\n💡 传统中医与现代科技的结合正在创造医疗健康的新可能，敬请期待最新突破！"
        
        news = tcm_news[0]
        content = f"🏥 中医科技实时动态\n\n"
        content += f"📰 最新报道：{news.title}\n\n"
        content += f"🔬 {news.summary[:150]}\n\n"
        content += f"✨ 传统智慧与现代科技的完美结合！ #中医科技 #实时新闻"
        
        return content[:280]
    
    async def _generate_general_content_from_news(self, news: NewsItem) -> str:
        """生成通用新闻内容"""
        content = f"📢 科技前沿速递\n\n"
        content += f"🎯 {news.title}\n\n"
        content += f"💡 {news.summary[:200]}\n\n"
        content += f"🔗 来源：{news.source}\n"
        content += f"#科技新闻 #实时资讯"
        
        return content[:280]
    
    async def _get_fallback_content(self, content_type: str) -> str:
        """获取备用内容"""
        fallbacks = {
            "headlines": f"📰 今日科技头条 {datetime.now().strftime('%Y-%m-%d')}\n\n🤖 AI技术持续突破创新\n💡 科技发展推动社会进步\n🚀 未来已来，精彩继续！ #科技头条 #创新",
            "thread": ["🌟 科技创新永不停歇", "💡 每一天都有新的突破", "🚀 让我们一起见证科技改变世界", "🔮 未来充满无限可能！ #科技创新"],
            "tcm_focus": "🏥 中医科技专题\n\n💡 传统中医智慧与现代科技融合，正在开创健康管理的新篇章。\n\n🌿 古老智慧，现代科技，美好未来！ #中医科技"
        }
        
        return fallbacks.get(content_type, "📢 敬请期待最新科技资讯...")


# 工厂函数
def create_news_collector() -> RealTimeNewsCollector:
    """创建新闻收集器实例"""
    return RealTimeNewsCollector()


if __name__ == "__main__":
    # 测试新闻收集器
    async def test_news_collector():
        collector = RealTimeNewsCollector()
        
        print("=== 测试实时新闻收集 ===")
        news_data = await collector.collect_latest_news(hours_back=24, max_results_per_category=3)
        
        for category, news_list in news_data.items():
            print(f"\n📰 {category.upper()}类别 ({len(news_list)}条):")
            for i, news in enumerate(news_list, 1):
                print(f"  {i}. {news.title[:80]}...")
                print(f"     质量分数: {news.quality_score:.2f}, 热度: {news.trending_score:.2f}")
                print(f"     来源: {news.source}, 时间: {news.published_time.strftime('%H:%M')}")
        
        print("\n=== 测试热点话题分析 ===")
        trending = await collector.get_trending_topics(news_data)
        for topic in trending[:10]:
            print(f"🔥 {topic.topic}: {topic.mentions}次提及 ({topic.category})")
        
        print("\n=== 测试内容生成 ===")
        headlines = await collector.generate_timely_content(news_data, "headlines")
        print("头条内容:")
        print(headlines)
    
    asyncio.run(test_news_collector())
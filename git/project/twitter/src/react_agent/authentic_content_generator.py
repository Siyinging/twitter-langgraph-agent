#!/usr/bin/env python3
"""真实化内容生成器 - 像真人博主一样自然表达

特点：
- 去除假大空的官话套话
- 真实的个人经历和感受
- 日常化的表达方式
- 有槽点、有情感、有观点
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from react_agent.real_time_news import RealTimeNewsCollector, NewsItem

logger = logging.getLogger(__name__)


class AuthenticContentGenerator:
    """真实化内容生成器 - 模仿真人博主的表达方式"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 实时新闻收集器
        self.news_collector = RealTimeNewsCollector()
        
        # AI工具推荐生成器
        from react_agent.ai_tools_content_generator import AIToolsContentGenerator
        self.ai_tools_generator = AIToolsContentGenerator()
        
        # 真实的个人化开场白 - 去掉假大空
        self.real_openings = [
            "刚刚看到个新闻，有点意思",
            "这个技术我关注了挺久的",
            "说实话这个消息挺让人意外的",
            "今天遇到个有趣的事情",
            "最近在折腾这个东西，有些心得",
            "这个新闻让我想起之前的经历",
            "朋友发给我个链接，看了挺有感触",
            "刚在群里讨论这个话题",
            "这个趋势我之前就猜到了",
            "终于等到这个技术突破了"
        ]
        
        # 真实的连接词 - 避免"让我们"这种假话
        self.real_transitions = [
            "具体来说就是",
            "简单讲就是", 
            "我的理解是",
            "关键在于",
            "问题是",
            "有意思的是",
            "最重要的是",
            "我觉得",
            "个人认为",
            "说白了就是"
        ]
        
        # 真实的结尾 - 去掉口号式的话
        self.real_endings = [
            "值得关注一下",
            "看看后续发展",
            "继续观望",
            "拖个字静观其变",
            "有新消息再说",
            "挺期待后续的",
            "应该还会有惊喜",
            "这才刚开始",
            "慢慢来吧"
        ]
        
        # 真实的技术观点 - 基于实际体验
        self.real_tech_opinions = {
            "ai": [
                "AI现在确实好用多了，不像以前那么智障",
                "ChatGPT用久了发现还是有不少局限性",
                "大模型虽然厉害，但耗电是真的夸张",
                "AI写代码还行，但别太依赖",
                "这种AI功能实用性还挺高的",
                "说实话比我预期的好用",
                "AI替代人工这事儿还早着呢"
            ],
            "medical": [
                "医疗AI这块儿确实需要更谨慎",
                "这种技术如果能普及就太好了",
                "看病难的问题可能真能缓解一些",
                "医生朋友说这个确实有用",
                "远程医疗这两年进步挺大",
                "医疗设备智能化确实是趋势",
                "希望成本能降下来"
            ],
            "tcm": [
                "中医结合科技这个方向我很看好",
                "传统医学数字化确实有前景",
                "我家老人就一直说中医好",
                "中药现代化这条路没错",
                "AI学中医诊断挺有意思的",
                "这比那些伪科学靠谱多了",
                "中医标准化确实需要技术手段"
            ],
            "general": [
                "科技发展确实挺快的",
                "这个方向感觉有搞头",
                "技术进步带来的变化还是很明显",
                "创新这事儿急不得",
                "市场反应还得看实际效果",
                "用户体验最重要",
                "成本问题始终是关键"
            ]
        }
        
        # 真实的吐槽和感受
        self.real_complaints = [
            "不过价格还是有点贵",
            "希望别又是PPT产品",
            "看起来挺好，就是不知道啥时候能用上",
            "又是一个概念炒作？",
            "技术是好技术，就看落地怎么样",
            "希望这次不要跳票",
            "感觉有点过度宣传了",
            "还得观望一下市场反应",
            "理想很丰满，现实很骨感",
            "先看看大公司怎么玩"
        ]
        
        # 个人经历模板
        self.personal_experiences = [
            "之前用过类似的产品",
            "我司正好在研究这个方向",
            "朋友圈已经有人在讨论了",
            "上次展会见过演示",
            "同事就在做这块儿",
            "之前写过相关的文章",
            "群里有人在内测",
            "刚好前段时间了解过",
            "这个我试用过早期版本"
        ]
    
    async def generate_authentic_headlines(self) -> str:
        """生成真实化的科技头条"""
        try:
            logger.info("🔍 生成真实化科技头条...")
            
            # 获取新闻
            news_data = await self._get_latest_news()
            
            if news_data and len(news_data) > 0:
                # 选择一条新闻
                all_news = []
                for news_list in news_data.values():
                    all_news.extend(news_list)
                
                if all_news:
                    all_news.sort(key=lambda x: x.quality_score + x.trending_score, reverse=True)
                    top_news = all_news[0]
                    content = await self._create_authentic_news_content(top_news)
                else:
                    content = self._create_authentic_fallback_content()
            else:
                content = self._create_authentic_fallback_content()
            
            logger.info("✅ 真实化头条生成完成")
            return content
            
        except Exception as e:
            logger.error(f"❌ 真实化头条生成失败: {e}")
            return self._create_authentic_fallback_content()
    
    async def _get_latest_news(self) -> Optional[Dict[str, List[NewsItem]]]:
        """获取最新新闻"""
        try:
            # 优先使用缓存
            news_data = await self.news_collector.get_cached_news(max_age_hours=4)
            if not news_data:
                news_data = await self.news_collector.collect_latest_news(hours_back=24, max_results_per_category=3)
            return news_data
        except Exception as e:
            logger.warning(f"获取新闻失败: {e}")
            return None
    
    async def _create_authentic_news_content(self, news: NewsItem) -> str:
        """基于真实新闻创建自然内容"""
        # 1. 真实的开场
        opening = random.choice(self.real_openings)
        
        # 2. 简化的新闻描述
        news_title = news.title
        if len(news_title) > 50:
            news_title = news_title[:47] + "..."
        
        # 3. 个人观点
        category = self._classify_news(news.title)
        opinion = random.choice(self.real_tech_opinions.get(category, self.real_tech_opinions["general"]))
        
        # 4. 可能的吐槽或感受
        has_complaint = random.random() < 0.3  # 30%概率有吐槽
        complaint = ""
        if has_complaint:
            complaint = f"\n\n{random.choice(self.real_complaints)}"
        
        # 5. 自然结尾
        ending = random.choice(self.real_endings)
        
        # 组装内容
        content = f"{opening}：\n\n{news_title}\n\n{opinion}。{complaint}\n\n{ending} 🤔"
        
        # 长度控制
        return self._ensure_length(content)
    
    def _classify_news(self, title: str) -> str:
        """分类新闻"""
        title_lower = title.lower()
        if 'ai' in title_lower or 'artificial intelligence' in title_lower:
            return "ai"
        elif 'medical' in title_lower or 'health' in title_lower:
            return "medical"
        elif '中医' in title or 'tcm' in title_lower:
            return "tcm"
        else:
            return "general"
    
    def _create_authentic_fallback_content(self) -> str:
        """真实化的备用内容"""
        # 选择一个真实的技术话题
        tech_topics = [
            {"topic": "AI写代码", "experience": "最近试了下Cursor，确实比之前的AI代码助手好用不少", "opinion": "虽然还是会犯一些低级错误，但效率提升明显"},
            {"topic": "智能手机", "experience": "朋友新买了台折叠屏，我上手体验了下", "opinion": "屏幕确实大了，但重量和厚度还是问题"},
            {"topic": "电动汽车", "experience": "这周末试驾了一台新能源车", "opinion": "加速确实爽，就是充电还不够方便"},
            {"topic": "VR设备", "experience": "同事买了个VR头显，我体验了半小时", "opinion": "沉浸感不错，但戴久了有点头晕"},
            {"topic": "AI医疗", "experience": "看了个AI诊断的新闻", "opinion": "技术进步是好事，但还是希望有人工医生把关"},
            {"topic": "量子计算", "experience": "刚看到量子计算的新突破", "opinion": "听起来很厉害，但离实用还很远"}
        ]
        
        topic_info = random.choice(tech_topics)
        opening = random.choice(self.real_openings)
        transition = random.choice(self.real_transitions)
        ending = random.choice(self.real_endings)
        
        content = f"{opening}，{topic_info['experience']}。\n\n{transition}{topic_info['opinion']}。\n\n{ending} 💭"
        
        return self._ensure_length(content)
    
    async def generate_authentic_tcm_content(self) -> str:
        """生成真实化的中医科技内容"""
        try:
            logger.info("🏥 生成真实化中医科技内容...")
            
            # 真实的中医科技话题
            tcm_topics = [
                {
                    "situation": "朋友圈看到中医AI诊断的新闻",
                    "content": "用摄像头看舌苔就能判断身体状况，准确率居然能到90%多",
                    "opinion": "这个挺有意思的，比那些看手相算命的靠谱多了",
                    "ending": "如果能普及的话，看中医可能真的会方便很多"
                },
                {
                    "situation": "刚看到智能脉诊仪的报道",
                    "content": "把脉这种主观的诊断方式居然能用传感器数字化",
                    "opinion": "中医现代化确实需要这种技术手段",
                    "ending": "希望能让更多年轻医生学会传统技艺"
                },
                {
                    "situation": "同事在研究中药成分分析AI",
                    "content": "用机器学习分析几千年的中药配方，找出最佳搭配",
                    "opinion": "古人的经验结合现代科技，这个思路没毛病",
                    "ending": "说不定能发现一些新的治疗方法"
                }
            ]
            
            topic = random.choice(tcm_topics)
            
            content = f"{topic['situation']}：\n\n{topic['content']}。{topic['opinion']}。\n\n{topic['ending']} 🌿"
            
            logger.info("✅ 真实化中医科技内容生成完成")
            return self._ensure_length(content)
            
        except Exception as e:
            logger.error(f"❌ 真实化中医科技内容生成失败: {e}")
            return self._create_tcm_fallback()
    
    def _create_tcm_fallback(self) -> str:
        """中医科技备用内容"""
        fallbacks = [
            "今天了解了下中医AI诊断，觉得这个方向挺有前景的。\n\n传统医学结合现代技术，既保留了中医的精华，又提高了准确性。\n\n期待能真正普及到基层医疗 🏥",
            "朋友圈有人在讨论智能脉诊设备。\n\n说实话，如果真能把老中医的经验数字化，那对中医传承意义重大。\n\n就怕又是个概念炒作 🤔"
        ]
        return random.choice(fallbacks)
    
    async def generate_authentic_ai_thread(self) -> List[str]:
        """生成真实化的AI话题线程"""
        try:
            logger.info("🤖 生成真实化AI线程...")
            
            # 真实的AI话题讨论
            ai_topics = [
                {
                    "trigger": "刚试了新版ChatGPT，有些感受想分享",
                    "points": [
                        "代码质量确实比之前好了，但还是需要人工review",
                        "多语言处理能力提升明显，中英混合也能理解",
                        "创意写作方面挺不错，但缺少个人特色",
                        "总的来说日常工作效率提升了不少"
                    ],
                    "conclusion": "AI工具确实在进步，但替代人类还早着呢"
                },
                {
                    "trigger": "看了AI绘画的最新进展，说几个观察",
                    "points": [
                        "画质确实越来越逼真了，细节处理很到位",
                        "但创意和情感表达还是差点意思",
                        "对设计师来说是个好工具，但不会完全替代",
                        "版权问题现在还比较混乱"
                    ],
                    "conclusion": "技术进步很快，但人的创造力还是无法替代的"
                }
            ]
            
            topic = random.choice(ai_topics)
            
            thread = [topic["trigger"]]
            
            for i, point in enumerate(topic["points"], 2):
                thread.append(f"{i}/ {point}")
            
            thread.append(f"{len(topic['points'])+2}/ {topic['conclusion']} 💭")
            
            logger.info("✅ 真实化AI线程生成完成")
            return thread
            
        except Exception as e:
            logger.error(f"❌ 真实化AI线程生成失败: {e}")
            return self._create_ai_thread_fallback()
    
    def _create_ai_thread_fallback(self) -> List[str]:
        """AI线程备用内容"""
        return [
            "最近在用各种AI工具，有些心得",
            "2/ AI确实能提高效率，但别过度依赖",
            "3/ 创意性工作还是需要人的参与",
            "4/ 学会和AI协作才是关键 🤝"
        ]
    
    def _ensure_length(self, content: str) -> str:
        """确保内容长度合适"""
        max_length = 200  # 保守限制
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        return content
    
    async def generate_ai_tools_content(self) -> str:
        """生成AI工具推荐内容"""
        try:
            logger.info("🔧 生成AI工具推荐内容...")
            
            # 随机选择内容类型
            content_types = ["recommendation", "comparison", "overview", "tips"]
            content_type = random.choice(content_types)
            
            if content_type == "recommendation":
                content = self.ai_tools_generator.generate_tool_recommendation()
            elif content_type == "comparison":
                content = self.ai_tools_generator.generate_tools_comparison()
            elif content_type == "overview":
                content = self.ai_tools_generator.generate_category_overview()
            else:  # tips
                content = self.ai_tools_generator.generate_usage_tip()
            
            logger.info("✅ AI工具推荐内容生成完成")
            return content
            
        except Exception as e:
            logger.error(f"❌ AI工具内容生成失败: {e}")
            return self._get_fallback_ai_tools_content()
    
    def _get_fallback_ai_tools_content(self) -> str:
        """备用AI工具内容"""
        fallbacks = [
            "最近试了几个免费AI工具，ChatGPT免费版日常够用，Notion AI整理笔记很方便。\n\n关键是找到适合自己工作流的，不用追最新的 🔧 #AI工具",
            "推荐个实用组合：ChatGPT写文案 + Canva做设计 + 剪映加字幕。\n\n都有免费版本，小团队够用了。工具不在多，在于用得熟 💡 #效率工具",
            "用AI工具一年多的感受：别指望一个工具解决所有问题。\n\n多备几个选择，关键时候有备案。免费版本通常就够用 🎯 #AI心得"
        ]
        
        return random.choice(fallbacks)


# 工厂函数
def create_authentic_generator() -> AuthenticContentGenerator:
    """创建真实化内容生成器"""
    return AuthenticContentGenerator()


if __name__ == "__main__":
    # 测试真实化生成器
    async def test_authentic_generator():
        generator = AuthenticContentGenerator()
        
        print("=== 测试真实化科技头条 ===")
        for i in range(3):
            headlines = await generator.generate_authentic_headlines()
            print(f"测试 {i+1}: 长度={len(headlines)}")
            print(headlines)
            print("-" * 50)
        
        print("\n=== 测试真实化中医科技内容 ===")
        for i in range(3):
            tcm_content = await generator.generate_authentic_tcm_content()
            print(f"测试 {i+1}: 长度={len(tcm_content)}")
            print(tcm_content)
            print("-" * 50)
        
        print("\n=== 测试真实化AI线程 ===")
        ai_thread = await generator.generate_authentic_ai_thread()
        for i, tweet in enumerate(ai_thread, 1):
            print(f"{i}. {tweet} (字数: {len(tweet)})")
    
    asyncio.run(test_authentic_generator())
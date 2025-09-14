#!/usr/bin/env python3
"""增强版内容生成器 - 生成更有深度和个人化的Twitter内容

特点：
- 避免空泛内容，提供具体案例和数据
- 个人化"碎碎念"风格
- 深入分析而非表面介绍  
- 真实新闻与个人见解结合
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from react_agent.real_time_news import RealTimeNewsCollector, NewsItem
from react_agent.content_generator import TechContentGenerator

logger = logging.getLogger(__name__)


class EnhancedContentGenerator:
    """增强版内容生成器 - 生成有深度的个人化内容"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 实时新闻收集器
        self.news_collector = RealTimeNewsCollector()
        
        # 基础生成器（备用）
        self.base_generator = TechContentGenerator()
        
        # 个人化观察模板 - 避免空泛内容
        self.personal_insights = {
            "morning_thoughts": [
                "🌅 今早想到一个有趣的问题：{topic}。这背后的技术原理其实很值得深挖...",
                "☕ 一边喝咖啡一边思考{topic}，突然意识到这个技术的潜力可能远超我们想象。",
                "🤔 昨晚看了关于{topic}的论文，有几个细节让我印象深刻：",
                "🧠 最近一直在关注{topic}，发现了一个很有意思的趋势..."
            ],
            "deep_analysis": [
                "让我们具体分析一下：{analysis}",
                "从技术角度来看：{analysis}", 
                "这里有个关键点值得注意：{analysis}",
                "我觉得真正有趣的是：{analysis}"
            ],
            "personal_experience": [
                "之前接触过类似的技术，感觉{experience}",
                "这让我想起了{experience}",
                "从实际应用的角度，{experience}",
                "我之前就觉得{experience}"
            ],
            "future_implications": [
                "想象一下5年后：{implication}",
                "这可能会改变：{implication}",
                "长远来看：{implication}",
                "如果这个技术成熟了：{implication}"
            ]
        }
        
        # 具体案例库 - 避免空话
        self.concrete_examples = {
            "ai_breakthroughs": [
                {
                    "case": "GPT-4o的多模态能力",
                    "detail": "可以同时处理文本、图像、音频，这种融合让AI理解世界的方式更接近人类",
                    "impact": "意味着AI助手将更加智能和实用"
                },
                {
                    "case": "AlphaFold在蛋白质预测上的突破", 
                    "detail": "准确率达到90%以上，比传统方法快了几个数量级",
                    "impact": "这直接加速了新药研发进程"
                },
                {
                    "case": "自动驾驶L4级别的商用化",
                    "detail": "在特定区域已经可以无人监管运行",
                    "impact": "交通出行方式的根本性改变即将到来"
                }
            ],
            "medical_tech": [
                {
                    "case": "AI辅助医学影像诊断",
                    "detail": "在肺癌早期筛查中准确率达到95%，比资深放射科医生还要准确",
                    "impact": "早期发现率的提升能挽救大量生命"
                },
                {
                    "case": "远程手术机器人的应用",
                    "detail": "医生可以在千里之外精确操控手术器械，延迟低于20ms",
                    "impact": "优质医疗资源的分布不均问题有望缓解"
                },
                {
                    "case": "个性化基因治疗的商业化",
                    "detail": "针对特定基因缺陷定制治疗方案，成功率显著提高",
                    "impact": "从治病到治根，医学思维的根本转变"
                }
            ],
            "tcm_innovation": [
                {
                    "case": "AI舌诊系统的临床应用",
                    "detail": "通过高分辨率图像分析，识别舌苔变化的准确率达到92%",
                    "impact": "让年轻中医师快速掌握资深医师的诊断经验"
                },
                {
                    "case": "智能脉诊设备的标准化",
                    "detail": "将主观的脉象感知转化为客观的数字化指标",
                    "impact": "传统中医诊断走向精准化和可复制化"
                },
                {
                    "case": "中药配方的AI优化",
                    "detail": "基于大数据分析古方疗效，发现新的药物配比规律",
                    "impact": "千年经验与现代科学的完美结合"
                }
            ]
        }
        
        # 数据驱动的见解
        self.data_insights = [
            "根据最新研究数据显示",
            "统计显示这个趋势很明显",
            "从市场反应来看",
            "技术指标表明",
            "实际应用效果证明"
        ]
    
    async def generate_substantial_headlines(self) -> str:
        """生成有实质内容的每日头条"""
        try:
            logger.info("🔍 生成有深度的科技头条...")
            
            # 1. 获取实时新闻
            news_data = await self.news_collector.get_cached_news(max_age_hours=2)
            if not news_data:
                news_data = await self.news_collector.collect_latest_news(hours_back=12, max_results_per_category=3)
            
            # 2. 选择最有价值的新闻
            top_news = None
            if news_data:
                all_news = []
                for news_list in news_data.values():
                    all_news.extend(news_list)
                all_news.sort(key=lambda x: x.quality_score + x.trending_score, reverse=True)
                top_news = all_news[0] if all_news else None
            
            # 3. 生成有深度的内容
            if top_news:
                content = await self._create_substantial_content(top_news)
            else:
                content = await self._create_fallback_substantial_content()
            
            logger.info("✅ 有深度的头条生成完成")
            return content
            
        except Exception as e:
            logger.error(f"❌ 头条生成失败: {e}")
            return await self._create_fallback_substantial_content()
    
    async def _create_substantial_content(self, news: NewsItem) -> str:
        """基于真实新闻创建有实质的内容"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 1. 个人化开头
        intro_template = random.choice(self.personal_insights["morning_thoughts"])
        topic = self._extract_main_topic(news.title)
        intro = intro_template.format(topic=topic)
        
        # 2. 新闻核心内容
        news_summary = f"\n\n📰 具体来说：{news.title}\n"
        
        # 3. 深度分析
        analysis = await self._generate_deep_analysis(news)
        analysis_template = random.choice(self.personal_insights["deep_analysis"])
        deep_content = analysis_template.format(analysis=analysis)
        
        # 4. 实际意义
        implication = await self._generate_implications(news)
        
        # 5. 组装内容
        content = f"{intro}{news_summary}\n{deep_content}\n\n💡 {implication}"
        
        # 6. 个人化标签
        tags = f"\n\n持续关注技术前沿 🚀 #科技观察 #深度思考"
        
        full_content = content + tags
        
        # 确保字数合理 - 极度保守策略，考虑Twitter emoji权重
        max_length = 200  # 预留80字符给emoji等特殊字符权重
        if len(full_content) > max_length:
            # 保留核心内容，压缩分析部分
            essential = f"{intro[:80]}\n\n💡 {implication[:50]}... 🚀"
            return essential[:max_length]
        
        return full_content[:max_length]
    
    async def _generate_deep_analysis(self, news: NewsItem) -> str:
        """生成深度分析内容"""
        title_lower = news.title.lower()
        
        if 'ai' in title_lower or 'artificial intelligence' in title_lower:
            examples = self.concrete_examples["ai_breakthroughs"]
            relevant_case = random.choice(examples)
            return f"这让我想到{relevant_case['case']}，{relevant_case['detail']}。{relevant_case['impact']}"
        
        elif 'medical' in title_lower or 'health' in title_lower:
            examples = self.concrete_examples["medical_tech"]
            relevant_case = random.choice(examples)
            return f"类似于{relevant_case['case']}的情况，{relevant_case['detail']}。{relevant_case['impact']}"
        
        elif '中医' in news.title or 'tcm' in title_lower:
            examples = self.concrete_examples["tcm_innovation"]
            relevant_case = random.choice(examples)
            return f"就像{relevant_case['case']}一样，{relevant_case['detail']}。{relevant_case['impact']}"
        
        else:
            # 通用深度分析
            data_intro = random.choice(self.data_insights)
            return f"{data_intro}，这类技术突破通常会带来连锁反应，影响整个行业生态"
    
    async def _generate_implications(self, news: NewsItem) -> str:
        """生成实际影响分析"""
        implications = [
            f"这意味着未来3-5年内，相关应用可能会出现质的飞跃",
            f"从商业角度看，这类技术突破往往会催生新的市场机会",
            f"对普通用户来说，可能很快就能在日常生活中体验到这些创新",
            f"技术成熟度的提升将大大降低应用门槛"
        ]
        
        return random.choice(implications)
    
    def _extract_main_topic(self, title: str) -> str:
        """从标题中提取主要话题"""
        title_lower = title.lower()
        
        if 'ai' in title_lower or 'artificial intelligence' in title_lower:
            return "AI技术的最新发展"
        elif 'quantum' in title_lower:
            return "量子计算的突破"
        elif 'medical' in title_lower or 'health' in title_lower:
            return "医疗科技的创新"
        elif 'robot' in title_lower:
            return "机器人技术的进步"
        elif 'blockchain' in title_lower:
            return "区块链应用的拓展"
        else:
            return "科技前沿的新动向"
    
    async def _create_fallback_substantial_content(self) -> str:
        """备用有实质内容的头条"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 选择一个具体案例
        category = random.choice(["ai_breakthroughs", "medical_tech", "tcm_innovation"])
        case = random.choice(self.concrete_examples[category])
        
        personal_thoughts = [
            f"🤔 {date}想聊聊{case['case'][:20]}这个突破\n\n💡 {case['detail'][:80]}\n\n{case['impact'][:60]}。技术发展超预期！\n\n🚀 #科技观察",
            
            f"☕ 今早{date}关注到{case['case'][:20]}的进展\n\n🔬 {case['detail'][:80]}\n\n{case['impact'][:60]}。对未来充满期待！\n\n⚡ #技术洞察",
            
            f"🧠 {date}思考：{case['case'][:20]}很重要\n\n📊 {case['detail'][:80]}\n\n{case['impact'][:60]}。推动行业发展！\n\n🌟 #前沿观察"
        ]
        
        content = random.choice(personal_thoughts)
        
        # 确保长度限制 - 极度保守策略
        max_length = 200
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return content
    
    async def generate_substantial_tcm_content(self) -> str:
        """生成有实质内容的中医科技专题"""
        try:
            logger.info("🏥 生成有深度的中医科技内容...")
            
            # 选择一个具体的中医科技案例
            case = random.choice(self.concrete_examples["tcm_innovation"])
            
            # 个人化的中医科技观察
            templates = [
                f"🏥 中医科技深度观察\n\n最近关注到{case['case']}的应用，很有启发。\n\n🔬 技术突破：{case['detail']}\n\n💡 {case['impact']}。传统医学与现代科技的结合，正在创造前所未有的可能性。\n\n这才是真正的传统与现代融合 ⚖️ #中医科技 #传统创新",
                
                f"🌿 今日中医科技思考\n\n深入了解了{case['case']}，发现了一些有趣的细节：\n\n📊 {case['detail']}\n\n我觉得{case['impact']}。这种融合不是简单的技术叠加，而是智慧的传承与创新。\n\n古老智慧的现代表达 🚀 #智慧传承 #科技中医",
                
                f"💡 中医科技新视角\n\n{case['case']}这个案例让我重新思考传统与现代的关系。\n\n🎯 核心价值：{case['detail']}\n\n{case['impact']}。真正的创新是让传统智慧发挥更大的价值。\n\n技术为传统赋能 ✨ #中医现代化 #技术融合"
            ]
            
            content = random.choice(templates)
            
            # 确保字数限制 - 极度保守策略
            max_length = 200
            if len(content) > max_length:
                content = content[:max_length-3] + "..."
                
            logger.info("✅ 中医科技有深度内容生成完成")
            return content
            
        except Exception as e:
            logger.error(f"❌ 中医科技内容生成失败: {e}")
            return self._get_fallback_tcm_substantial_content()
    
    def _get_fallback_tcm_substantial_content(self) -> str:
        """备用中医科技有实质内容"""
        case = random.choice(self.concrete_examples["tcm_innovation"])
        
        return f"🏥 中医科技观察\n\n今天想分享{case['case']}这个创新：\n\n{case['detail']}\n\n{case['impact']}。这就是我说的真正的传统与现代结合！\n\n#中医科技 #传统创新"
    
    async def generate_substantial_ai_thread(self) -> List[str]:
        """生成有实质内容的AI线程"""
        try:
            logger.info("🤖 生成有深度的AI线程...")
            
            # 选择具体的AI案例
            case = random.choice(self.concrete_examples["ai_breakthroughs"])
            
            thread = [
                # 第一条：引入话题
                f"🧠 想深度聊聊{case['case']}这个突破。很多人可能还没意识到它的重要性。",
                
                # 第二条：技术细节
                f"🔬 技术层面：{case['detail']}\n\n这不是简单的性能提升，而是能力的质的飞跃。",
                
                # 第三条：实际影响
                f"💡 实际意义：{case['impact']}\n\n我们正在见证AI从'工具'向'伙伴'的转变。",
                
                # 第四条：未来展望
                f"🚀 展望未来：这类突破会形成连锁反应，推动整个AI生态的进化。\n\n每个技术突破都在为下一个更大的突破铺路 ⚡",
                
                # 第五条：个人思考
                f"🤔 个人观察：AI发展的速度确实超出预期，但真正的价值还是在于解决实际问题。\n\n#AI观察 #技术思考 #创新洞察"
            ]
            
            logger.info("✅ AI线程生成完成")
            return thread
            
        except Exception as e:
            logger.error(f"❌ AI线程生成失败: {e}")
            return await self._get_fallback_ai_thread()
    
    async def _get_fallback_ai_thread(self) -> List[str]:
        """备用AI线程"""
        case = random.choice(self.concrete_examples["ai_breakthroughs"])
        
        return [
            f"🤖 今天聊聊{case['case']}这个AI突破",
            f"📊 具体表现：{case['detail']}",
            f"💡 重要意义：{case['impact']}",
            f"🔮 这种技术进步让我们看到AI的更多可能性",
            f"🚀 持续关注AI技术的发展趋势！ #AI #技术观察 #创新"
        ]


# 工厂函数
def create_enhanced_generator() -> EnhancedContentGenerator:
    """创建增强版内容生成器"""
    return EnhancedContentGenerator()


if __name__ == "__main__":
    # 测试增强版生成器
    async def test_enhanced_generator():
        generator = EnhancedContentGenerator()
        
        print("=== 测试有深度的科技头条 ===")
        headlines = await generator.generate_substantial_headlines()
        print(headlines)
        print(f"字数: {len(headlines)}\n")
        
        print("=== 测试有深度的中医科技内容 ===")
        tcm_content = await generator.generate_substantial_tcm_content()
        print(tcm_content)
        print(f"字数: {len(tcm_content)}\n")
        
        print("=== 测试有深度的AI线程 ===")
        ai_thread = await generator.generate_substantial_ai_thread()
        for i, tweet in enumerate(ai_thread, 1):
            print(f"{i}. {tweet} (字数: {len(tweet)})")
        print()
    
    asyncio.run(test_enhanced_generator())
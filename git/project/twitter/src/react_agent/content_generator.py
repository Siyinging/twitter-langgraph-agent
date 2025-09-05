#!/usr/bin/env python3
"""智能内容生成器 - 为每日Twitter发布生成各类科技内容

包含：
- 今日科技头条生成
- 可持续AI线程内容生成
- 优质转发内容发现
- 本周趋势回顾生成
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from langchain_tavily import TavilySearch
from react_agent.tools import _get_all_mcp_tools, search

logger = logging.getLogger(__name__)


class TechContentGenerator:
    """科技内容生成器"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 可持续AI话题库
        self.sustainable_ai_topics = [
            {
                "theme": "绿色计算",
                "content": [
                    "🌱 可持续AI发展已成为科技界的重要议题。随着AI模型越来越庞大，其能耗问题也日益凸显。",
                    "💡 传统大型模型训练消耗巨大电力，相当于数百个家庭一年的用电量。我们需要更高效的算法。",
                    "🔧 新兴的神经网络剪枝、知识蒸馏技术正在帮助减少模型参数，在保持性能的同时大幅降低能耗。",
                    "📊 研究显示，优化后的AI模型能效可提升70%，而准确率仅下降2%。这是值得的权衡。",
                    "🚀 未来AI发展方向：更聪明而非更大。让我们共同推动绿色AI技术，为地球贡献一份力量！ #可持续AI #绿色计算"
                ]
            },
            {
                "theme": "边缘AI",
                "content": [
                    "🌱 边缘AI正在重新定义可持续计算。将智能推向设备端，减少云端依赖，是绿色AI的关键方向。",
                    "💡 在手机、IoT设备上运行AI模型，可以减少数据传输，降低延迟，同时大幅节省云计算资源。",
                    "🔧 新的量化技术和专用芯片让复杂AI模型能在功耗仅几瓦的设备上高效运行。",
                    "📊 预计到2026年，70%的AI推理将在边缘设备完成，云端能耗将减少40%。",
                    "🚀 分布式智能时代来临！每个设备都是一个小型AI引擎，共同构建更可持续的智能生态。 #边缘AI #物联网"
                ]
            },
            {
                "theme": "AI伦理",
                "content": [
                    "🌱 可持续AI不仅关乎环境，更关乎负责任的技术发展。我们需要平衡创新与责任。",
                    "💡 AI偏见、隐私保护、算法透明度等问题，都是可持续发展必须考虑的维度。",
                    "🔧 联邦学习、差分隐私等技术让AI训练更注重隐私保护，实现'可持续的数据使用'。",
                    "📊 负责任AI开发框架正在成为行业标准，70%的科技公司已建立AI伦理委员会。",
                    "🚀 技术向善，让AI服务全人类。可持续AI的最终目标是创造一个更公平、更美好的智能世界。 #AI伦理 #技术向善"
                ]
            }
        ]
        
        # 中医科技融合主题库
        self.tcm_tech_topics = [
            {
                "theme": "智慧中医",
                "content": [
                    "🏥 智慧中医时代来临！AI正在重新定义传统中医诊疗模式，让千年医学焕发新活力。",
                    "💡 AI辅助中医诊断系统能够分析舌象、脉象数据，准确率达90%以上，为传统诊断提供科学支撑。",
                    "🔬 大数据挖掘古方宝库，从《本草纲目》到现代临床，AI帮助发现新的药物组合和治疗方案。",
                    "📊 智能舌诊、脉诊设备将经验传承数字化，让年轻中医师快速掌握诊断精髓。",
                    "🚀 传统智慧遇见现代科技，中医药走向精准化、个性化的新时代！ #智慧中医 #AI诊断 #传统与现代"
                ]
            },
            {
                "theme": "数字化传承", 
                "content": [
                    "📚 数字化传承让千年中医智慧永续流传。古籍数字化、知识图谱构建，传统医学插上科技翅膀。",
                    "🧠 AI深度学习中医思维模式，从海量医案中提取诊疗规律，让机器理解'辨证论治'的精髓。",
                    "🌐 全球中医知识共享平台建立，让世界各地的中医师都能获得最前沿的诊疗经验。",
                    "⚡ 区块链技术保护传统方剂知识产权，确保珍贵医学遗产得到合理保护和传承。",
                    "🔮 数字孪生技术还原古代名医诊疗过程，为后学者提供沉浸式学习体验。 #数字传承 #中医教育 #文化科技"
                ]
            },
            {
                "theme": "精准中医",
                "content": [
                    "🧬 精准中医新时代：基因组学指导个性化用药，让'因人制宜'更加科学精准。",
                    "📱 个性化体质分析APP结合现代检测技术，准确判断九种体质类型，指导日常养生。",
                    "⚖️ 量化中医辨证论治，将'望闻问切'转化为可测量的生理指标，提升诊断客观性。",
                    "🎯 精准针灸穴位定位系统，结合3D成像和AI算法，确保每一针都精准到位。",
                    "🔄 中西医结合诊疗模式，现代医学检测 + 中医整体调理 = 最佳治疗效果。 #精准中医 #个性化医疗 #科技养生"
                ]
            },
            {
                "theme": "创新融合",
                "content": [
                    "🌿 创新融合开启中医药新篇章。现代提取工艺让中药有效成分更纯净、更标准化。",
                    "📡 远程中医诊疗平台突破地域限制，名老中医的诊疗经验惠及更多患者。",
                    "🏭 智能制药系统实现中药生产全程质量控制，确保每一味中药都达到最高标准。",
                    "🤖 中医康复机器人结合传统按摩手法和现代康复理念，提供24小时个性化理疗服务。",
                    "💫 传统与现代的完美融合，让中医药在新时代焕发无限生机与活力！ #创新中医 #智能制药 #未来医疗"
                ]
            }
        ]
    
    async def generate_tcm_tech_headlines(self) -> str:
        """生成中医科技融合头条"""
        try:
            logger.info("🏥 开始生成中医科技头条...")
            
            # 1. 生成中医科技头条（暂时跳过搜索以避免上下文问题）
            # TODO: 修复搜索上下文问题后恢复
            web_results = None  # 暂时使用fallback内容
            
            # 2. 生成融合头条
            current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            headlines = self._format_tcm_tech_headlines(web_results, current_time)
            
            logger.info("✅ 中医科技头条生成完成")
            return headlines
            
        except Exception as e:
            logger.error(f"❌ 中医科技头条生成失败: {e}")
            return self._get_fallback_tcm_headlines()
    
    def _format_tcm_tech_headlines(self, web_data: Any, date: str) -> str:
        """格式化中医科技头条"""
        templates = [
            f"🏥 今日中医科技头条 {date}\n\n💡 AI助力中医诊断技术新突破\n🌿 传统医学与现代科技深度融合\n🚀 数字化中医为健康赋能！ #中医科技 #智慧医疗 #传统创新",
            f"📱 今日中医科技头条 {date}\n\n🧠 人工智能学习中医古典理论\n⚖️ 精准医疗让中医更科学化\n🌟 千年智慧遇见现代技术！ #数字中医 #AI医疗 #科技传承",
            f"🔬 今日中医科技头条 {date}\n\n📊 大数据挖掘中医药宝库\n🎯 个性化中医诊疗成为现实\n💫 传统与现代完美结合！ #中医大数据 #个性化医疗 #创新医学"
        ]
        
        import random
        return random.choice(templates)
    
    def _get_fallback_tcm_headlines(self) -> str:
        """备用中医科技头条"""
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"🏥 今日中医科技头条 {date}\n\n💡 智慧中医助力精准诊疗\n🌿 传统医学科技化发展持续推进\n🚀 中医药现代化进程加速！ #中医科技 #智慧医疗 #数字健康"
    
    async def generate_wisdom_ai_thread(self) -> List[str]:
        """生成AI+传统智慧线程（轮换可持续AI和中医科技）"""
        try:
            import random
            
            # 50%概率选择传统可持续AI，50%选择中医科技
            if random.random() < 0.5:
                logger.info("🤖 生成可持续AI线程")
                return await self.generate_sustainable_ai_thread()
            else:
                logger.info("🏥 生成中医科技智慧线程")
                selected_topic = random.choice(self.tcm_tech_topics)
                logger.info(f"✅ 选择中医科技主题: {selected_topic['theme']}")
                return selected_topic['content']
                
        except Exception as e:
            logger.error(f"❌ 智慧线程生成失败: {e}")
            # 降级到可持续AI内容
            return await self.generate_sustainable_ai_thread()
    
    async def generate_daily_tcm_tech_content(self) -> str:
        """生成每日中医科技专题内容"""
        try:
            logger.info("🏥 开始生成每日中医科技专题内容...")
            
            # 选择一个中医科技主题的第一条内容作为专题
            import random
            selected_topic = random.choice(self.tcm_tech_topics)
            theme = selected_topic['theme']
            
            # 创建专题内容
            templates = [
                f"🏥 每日中医科技专题\n\n主题：{theme}\n\n{selected_topic['content'][0]}\n\n传统智慧与现代科技的完美结合，正在开创医疗健康的新纪元！",
                f"💡 中医科技新视角\n\n聚焦：{theme}\n\n{selected_topic['content'][1]}\n\n让我们一起见证千年医学在数字时代的华丽转身！",
                f"🌿 传统与创新融合\n\n今日话题：{theme}\n\n{selected_topic['content'][2]}\n\n科技为传统医学插上翅膀，未来健康触手可及！"
            ]
            
            content = random.choice(templates)
            
            # 确保字数限制
            if len(content) > 280:
                content = content[:277] + "..."
                
            logger.info(f"✅ 中医科技专题内容生成完成：{theme}")
            return content
            
        except Exception as e:
            logger.error(f"❌ 中医科技专题生成失败: {e}")
            return self._get_fallback_tcm_daily_content()
    
    def _get_fallback_tcm_daily_content(self) -> str:
        """备用中医科技专题内容"""
        fallback_contents = [
            "🏥 每日中医科技专题\n\n💡 AI技术正在革命性地改变传统中医诊疗模式，让古老的医学智慧焕发新的生机。\n\n🚀 传统与现代的碰撞，正在创造医疗健康的无限可能！ #中医科技 #AI医疗",
            "🌿 中医科技新视角\n\n📱 数字化技术让中医诊断更加精准，个性化治疗成为现实。\n\n⚡ 千年智慧遇见现代科技，健康管理进入全新时代！ #数字中医 #精准医疗",
            "💫 传统智慧新篇章\n\n🔬 现代科技验证古老方剂，中西医结合开创医疗新模式。\n\n🎯 让科技为传统医学赋能，共同守护人类健康！ #中西结合 #创新医疗"
        ]
        
        import random
        return random.choice(fallback_contents)

    async def generate_daily_headlines(self) -> str:
        """生成今日科技头条"""
        try:
            logger.info("🔍 开始生成今日科技头条...")
            
            # 1. 获取最新科技新闻（暂时跳过搜索）
            # TODO: 修复搜索上下文问题后恢复  
            web_results = None  # 暂时使用fallback内容
            
            # 2. 获取Twitter趋势
            twitter_trends = ""
            try:
                tools = await _get_all_mcp_tools()
                if "get_trends" in tools:
                    trends_result = await tools["get_trends"].ainvoke({"woeid": 1})
                    twitter_trends = str(trends_result)[:300]
            except Exception as e:
                logger.warning(f"获取Twitter趋势失败: {e}")
            
            # 3. 生成头条内容
            current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            headlines = self._format_tech_headlines(web_results, twitter_trends, current_time)
            
            logger.info("✅ 今日科技头条生成完成")
            return headlines
            
        except Exception as e:
            logger.error(f"❌ 头条生成失败: {e}")
            return self._get_fallback_headlines()
    
    def _format_tech_headlines(self, web_data: Any, twitter_data: str, date: str) -> str:
        """格式化科技头条内容"""
        # 分析网络搜索结果
        key_topics = []
        if isinstance(web_data, dict) and 'results' in web_data:
            for result in web_data['results'][:3]:
                if isinstance(result, dict):
                    title = result.get('title', '')
                    if any(keyword in title.lower() for keyword in ['ai', 'tech', '人工智能', '科技', 'innovation']):
                        key_topics.append(title[:50])
        
        # 生成头条
        if key_topics:
            main_topic = key_topics[0]
            headlines = f"📰 今日科技头条 {date}\n\n🔥 {main_topic}\n"
            if len(key_topics) > 1:
                headlines += f"💡 {key_topics[1]}\n"
            headlines += f"\n科技创新永不停歇，让我们一起关注最新发展！ #科技头条 #AI #创新"
        else:
            headlines = self._get_fallback_headlines()
        
        # 确保字数限制
        if len(headlines) > 280:
            headlines = headlines[:277] + "..."
        
        return headlines
    
    def _get_fallback_headlines(self) -> str:
        """备用头条内容"""
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        fallback_headlines = [
            f"📰 今日科技头条 {date}\n\n🤖 AI技术持续突破，大模型效率不断提升\n💡 量子计算研究取得新进展\n🚀 科技创新推动社会进步，未来值得期待！ #科技头条 #AI #创新",
            f"📰 今日科技头条 {date}\n\n🔋 绿色科技成为发展新趋势\n🌐 边缘计算与云计算深度融合\n⚡ 技术变革正在改变我们的生活方式！ #科技头条 #绿色科技 #未来",
            f"📰 今日科技头条 {date}\n\n🧠 神经网络架构持续创新\n🔐 网络安全技术日益重要\n🌟 科技让世界变得更加智能和安全！ #科技头条 #神经网络 #网络安全"
        ]
        
        import random
        return random.choice(fallback_headlines)
    
    async def generate_sustainable_ai_thread(self) -> List[str]:
        """生成可持续AI线程内容"""
        try:
            logger.info("🌱 开始生成可持续AI线程...")
            
            # 随机选择一个主题
            import random
            selected_topic = random.choice(self.sustainable_ai_topics)
            
            logger.info(f"✅ 选择主题: {selected_topic['theme']}")
            return selected_topic['content']
            
        except Exception as e:
            logger.error(f"❌ 可持续AI线程生成失败: {e}")
            return self._get_fallback_ai_thread()
    
    def _get_fallback_ai_thread(self) -> List[str]:
        """备用AI线程内容"""
        return [
            "🌱 可持续AI发展是当今科技界的重要课题。在追求AI性能的同时，我们也要关注其环境影响。",
            "💡 大型AI模型的训练和部署消耗大量能源。研究表明，一个大型语言模型的训练相当于几十万公里的汽车行驶。",
            "🔧 解决方案正在涌现：模型压缩、高效算法、绿色数据中心等技术正在让AI变得更加环保。",
            "📊 目标很明确：在2030年前将AI计算的碳足迹减少50%，同时保持甚至提升AI的能力。",
            "🚀 让我们共同推动可持续AI的发展，为地球和未来负责！每个人都可以为绿色AI贡献力量。 #可持续AI #绿色计算 #环保科技"
        ]
    
    async def find_retweet_target(self) -> Optional[Dict[str, str]]:
        """找到值得转发的优质内容"""
        try:
            logger.info("🔍 搜索优质科技内容用于转发...")
            
            # 搜索高质量科技推文
            tools = await _get_all_mcp_tools()
            if "advanced_search_twitter" not in tools:
                logger.warning("Twitter搜索工具不可用")
                return None
            
            # 搜索查询组合
            search_queries = [
                "from:OpenAI OR from:AnthropicAI OR from:DeepMind recent breakthroughs",
                "artificial intelligence research breakthrough min_faves:100",
                "sustainable AI green computing innovation",
                "quantum computing progress latest",
                "#MachineLearning #AI paper findings"
            ]
            
            import random
            query = random.choice(search_queries)
            
            search_result = await tools["advanced_search_twitter"].ainvoke({"llm_text": query})
            
            # 解析搜索结果
            if isinstance(search_result, dict) and search_result.get('success'):
                tweets = search_result.get('data', {}).get('tweets', [])
                if tweets and len(tweets) > 0:
                    # 选择第一条推文
                    target_tweet = tweets[0]
                    tweet_id = target_tweet.get('id')
                    tweet_text = target_tweet.get('text', '')
                    author = target_tweet.get('author', {}).get('username', 'unknown')
                    
                    if tweet_id and len(tweet_text) > 50:  # 确保内容有足够价值
                        return {
                            "tweet_id": tweet_id,
                            "original_text": tweet_text[:100] + "..." if len(tweet_text) > 100 else tweet_text,
                            "author": author,
                            "comment": self._generate_retweet_comment(tweet_text)
                        }
            
            logger.warning("未找到合适的转发目标")
            return None
            
        except Exception as e:
            logger.error(f"❌ 搜索转发目标失败: {e}")
            return None
    
    def _generate_retweet_comment(self, original_text: str) -> str:
        """为转发生成评论"""
        comments = [
            "💡 这个观点很有启发性！AI技术的发展确实需要我们从多个角度思考。",
            "🎯 说得很好！技术创新与负责任发展并不矛盾，关键在于找到平衡点。", 
            "🔬 非常有价值的分享！这类研究成果对整个行业都有重要意义。",
            "⚡ 赞同这个看法！前沿技术的发展总是充满挑战和机遇。",
            "🌟 精彩的见解！科技进步的每一步都值得我们深入思考和讨论。"
        ]
        
        import random
        return random.choice(comments)
    
    async def generate_weekly_recap(self) -> str:
        """生成本周科技趋势回顾"""
        try:
            logger.info("📊 开始生成本周科技趋势回顾...")
            
            # 获取本周的科技新闻（暂时跳过搜索）
            # TODO: 修复搜索上下文问题后恢复
            web_results = None  # 暂时使用fallback内容
            
            current_date = datetime.now(timezone.utc)
            week_start = current_date - timedelta(days=7)
            
            recap_content = self._format_weekly_recap(web_results, week_start.strftime("%m-%d"), current_date.strftime("%m-%d"))
            
            logger.info("✅ 本周回顾生成完成")
            return recap_content
            
        except Exception as e:
            logger.error(f"❌ 本周回顾生成失败: {e}")
            return self._get_fallback_weekly_recap()
    
    def _format_weekly_recap(self, web_data: Any, start_date: str, end_date: str) -> str:
        """格式化本周回顾内容"""
        # 分析本周关键事件
        key_events = []
        if isinstance(web_data, dict) and 'results' in web_data:
            for result in web_data['results'][:3]:
                if isinstance(result, dict):
                    title = result.get('title', '')
                    if any(keyword in title.lower() for keyword in ['ai', 'tech', 'breakthrough', 'innovation']):
                        key_events.append(title[:60])
        
        recap = f"📊 本周科技趋势回顾 ({start_date} - {end_date})\n\n"
        
        if key_events:
            for i, event in enumerate(key_events, 1):
                recap += f"{i}️⃣ {event}\n"
        else:
            recap += "🤖 AI技术持续进步\n💡 创新应用不断涌现\n🌐 科技生态日益完善\n"
        
        recap += f"\n科技发展永不止步，让我们期待下周更多精彩！ #本周回顾 #科技趋势 #创新"
        
        # 确保字数限制
        if len(recap) > 280:
            recap = recap[:277] + "..."
        
        return recap
    
    def _get_fallback_weekly_recap(self) -> str:
        """备用本周回顾内容"""
        current_date = datetime.now(timezone.utc)
        week_start = current_date - timedelta(days=7)
        
        return f"""📊 本周科技趋势回顾 ({week_start.strftime("%m-%d")} - {current_date.strftime("%m-%d")})

1️⃣ AI大模型性能持续优化
2️⃣ 绿色计算理念深入人心  
3️⃣ 边缘AI应用场景扩展
4️⃣ 开源技术生态繁荣

科技创新的脚步从未停歇，让我们一起迎接更加智能的未来！ #本周回顾 #科技趋势 #AI发展"""


if __name__ == "__main__":
    # 测试内容生成器
    async def test_generator():
        generator = TechContentGenerator()
        
        print("=== 测试今日科技头条 ===")
        headlines = await generator.generate_daily_headlines()
        print(headlines)
        print(f"字数: {len(headlines)}\n")
        
        print("=== 测试可持续AI线程 ===")
        ai_thread = await generator.generate_sustainable_ai_thread()
        for i, tweet in enumerate(ai_thread, 1):
            print(f"{i}. {tweet} (字数: {len(tweet)})")
        print()
        
        print("=== 测试转发目标搜索 ===")
        retweet_target = await generator.find_retweet_target()
        if retweet_target:
            print(f"目标推文: {retweet_target['original_text']}")
            print(f"评论: {retweet_target['comment']}")
        else:
            print("未找到转发目标")
        print()
        
        print("=== 测试本周回顾 ===")
        weekly_recap = await generator.generate_weekly_recap()
        print(weekly_recap)
        print(f"字数: {len(weekly_recap)}")
    
    asyncio.run(test_generator())
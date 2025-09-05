#!/usr/bin/env python3
"""手动Twitter调度器 - 不依赖复杂的Graph调用

这个简化版本直接调用工具函数，避免Graph配置问题
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any
from pathlib import Path
import sys

from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# 现在导入自定义模块
from react_agent.tools import (
    _get_all_mcp_tools, 
    advanced_search_twitter,
    get_trends,
    post_tweet
)
from react_agent.daily_publisher import DailyTechPublisher
from langchain_tavily import TavilySearch
from react_agent.data_collector import TechDataCollector
from react_agent.tech_visualizer import TechVisualizer
from react_agent.enhanced_visualizer import EnhancedVisualizer
from react_agent.image_generator import ImageGenerator


class ManualTwitterScheduler:
    """手动Twitter调度器 - 直接调用工具"""
    
    def __init__(self, interval_hours: int = 3):
        self.interval_hours = interval_hours
        self.scheduler = AsyncIOScheduler()
        
        # 初始化数据收集器和可视化器
        self.data_collector = TechDataCollector()
        self.visualizer = TechVisualizer()
        self.enhanced_visualizer = EnhancedVisualizer()
        self.image_generator = ImageGenerator()
        
        # 初始化每日发布器
        self.daily_publisher = DailyTechPublisher()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def search_web(self, query: str) -> str:
        """使用Tavily搜索网络"""
        try:
            tavily = TavilySearch(max_results=5)
            results = await tavily.ainvoke({"query": query})
            
            # 提取有用信息
            content = []
            for result in results.get('results', [])[:3]:  # 取前3个结果
                if isinstance(result, dict):
                    title = result.get('title', '')
                    snippet = result.get('content', result.get('snippet', ''))
                    if title and snippet:
                        content.append(f"• {title}: {snippet[:100]}...")
            
            return "\n".join(content) if content else str(results)[:500]
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            return f"Search error: {str(e)}"
    
    async def execute_trend_analysis_task(self):
        """执行趋势分析任务"""
        try:
            self.logger.info("🚀 开始执行趋势分析任务")
            
            # 1. 搜索AI和科技趋势
            web_results = await self.search_web("AI technology trends 2024 latest news")
            
            # 2. 尝试获取Twitter趋势（如果MCP可用）
            twitter_trends = ""
            try:
                tools = await _get_all_mcp_tools()
                if "get_trends" in tools:
                    trends_result = await tools["get_trends"].ainvoke({"woeid": 1})
                    twitter_trends = f"Twitter trends: {str(trends_result)[:200]}..."
                else:
                    twitter_trends = "Twitter MCP unavailable"
            except Exception as e:
                twitter_trends = f"Twitter trends error: {str(e)}"
                self.logger.warning(f"Twitter trends failed: {e}")
            
            # 3. 生成基于趋势的推文内容
            current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            
            tweet_content = self.generate_tweet_from_trends(web_results, twitter_trends, current_time)
            
            # 4. 尝试发布推文（如果MCP可用）
            try:
                tools = await _get_all_mcp_tools()
                if "post_tweet" in tools:
                    post_result = await tools["post_tweet"].ainvoke({
                        "text": tweet_content,
                        "user_id": "e634c89a-a63a-40fe-af3b-b9d96de0b97a",
                        "media_inputs": []
                    })
                    self.logger.info(f"✅ 推文发布成功: {post_result}")
                else:
                    self.logger.info(f"📝 推文内容 (MCP不可用): {tweet_content}")
            except Exception as e:
                self.logger.error(f"推文发布失败: {e}")
                self.logger.info(f"📝 推文内容: {tweet_content}")
            
            self.logger.info("✅ 趋势分析任务完成")
            
        except Exception as e:
            self.logger.error(f"❌ 趋势分析任务失败: {str(e)}")
    
    def generate_tweet_from_trends(self, web_trends: str, twitter_trends: str, timestamp: str) -> str:
        """基于趋势生成推文内容"""
        # 简单的推文生成逻辑
        templates = [
            "🤖 AI正在快速发展！根据最新趋势分析，技术创新持续加速。值得关注的发展方向包括机器学习、自动化和智能系统。 #{timestamp} #AI #Tech",
            "📊 科技趋势观察：人工智能技术正在重塑各行各业。从数据分析到内容创作，AI的应用场景越来越广泛。 #{timestamp} #TechTrends #Innovation", 
            "⚡ 最新科技动态：AI技术发展迅猛，为各行业带来新机遇。持续关注技术变革，拥抱数字化未来！ #{timestamp} #ArtificialIntelligence #Future",
            "🚀 技术前沿观察：人工智能、机器学习、数据科学等领域持续创新。科技改变生活，创新驱动未来！ #{timestamp} #TechNews #AI"
        ]
        
        # 选择一个模板并填充时间戳
        import random
        template = random.choice(templates)
        tweet = template.replace("#{timestamp}", timestamp.split()[0])  # 只用日期部分
        
        # 确保推文长度不超过280字符
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        return tweet
    
    async def execute_engagement_check_task(self):
        """执行互动检查任务"""
        try:
            self.logger.info("🚀 开始执行互动检查任务")
            
            # 尝试检查互动（如果MCP可用）
            try:
                tools = await _get_all_mcp_tools()
                if "advanced_search_twitter" in tools:
                    # 搜索自己的最近推文
                    search_result = await tools["advanced_search_twitter"].ainvoke({
                        "llm_text": "from:myaccount recent interactions"
                    })
                    self.logger.info(f"📊 互动检查结果: {str(search_result)[:200]}...")
                else:
                    self.logger.info("📊 Twitter搜索MCP不可用，跳过互动检查")
            except Exception as e:
                self.logger.warning(f"互动检查失败: {e}")
            
            self.logger.info("✅ 互动检查任务完成")
            
        except Exception as e:
            self.logger.error(f"❌ 互动检查任务失败: {str(e)}")
    
    async def execute_image_tweet_task(self):
        """执行图片推文任务"""
        try:
            self.logger.info("📸 开始执行图片推文任务")
            
            # 1. 收集最新数据
            self.logger.info("📊 收集科技数据...")
            trends_data = await self.data_collector.collect_web_trends()
            
            # 2. 生成Twitter优化的图片
            self.logger.info("🎨 生成Twitter图片...")
            image_results = await self.enhanced_visualizer.batch_generate_twitter_images(trends_data)
            
            if image_results:
                self.logger.info(f"✅ 成功生成 {len(image_results)} 张图片")
                
                # 3. 随机选择一张图片发布
                import random
                selected_image, tweet_text = random.choice(image_results)
                
                self.logger.info(f"📱 准备发布图片推文: {Path(selected_image).name}")
                
                # 4. 尝试发布带图片的推文
                try:
                    tools = await _get_all_mcp_tools()
                    if "post_tweet" in tools:
                        # 读取图片文件
                        import base64
                        with open(selected_image, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        
                        # 发布带图片的推文
                        post_result = await tools["post_tweet"].ainvoke({
                            "text": tweet_text,
                            "user_id": "e634c89a-a63a-40fe-af3b-b9d96de0b97a",
                            "media_inputs": [{"data": img_data, "media_type": "image/png"}]
                        })
                        self.logger.info(f"📱 图片推文发布成功: {post_result}")
                    else:
                        self.logger.info(f"📝 图片推文内容 (MCP不可用):")
                        self.logger.info(f"   📷 图片: {selected_image}")
                        self.logger.info(f"   📝 文本: {tweet_text}")
                        
                except Exception as e:
                    self.logger.error(f"图片推文发布失败: {e}")
                    self.logger.info(f"📝 图片推文内容:")
                    self.logger.info(f"   📷 图片: {selected_image}")
                    self.logger.info(f"   📝 文本: {tweet_text}")
                
                # 5. 记录生成的图片信息
                for image_path, text in image_results:
                    image_info = self.image_generator.get_image_info(image_path)
                    self.logger.info(f"📊 图片信息: {image_info}")
                    
            else:
                self.logger.warning("⚠️ 未能生成任何图片")
            
            self.logger.info("✅ 图片推文任务完成")
            
        except Exception as e:
            self.logger.error(f"❌ 图片推文任务失败: {str(e)}")
    
    async def execute_data_visualization_task(self):
        """执行数据可视化任务"""
        try:
            self.logger.info("🎨 开始执行数据可视化任务")
            
            # 1. 收集最新的科技数据
            self.logger.info("📊 收集科技趋势数据...")
            trends_data = await self.data_collector.collect_web_trends()
            
            # 2. 生成关键词指标
            self.logger.info("🔍 分析关键词指标...")
            metrics_data = await self.data_collector.collect_keyword_metrics()
            
            # 3. 生成可视化图表
            self.logger.info("🎨 生成可视化图表...")
            chart_files = await self.visualizer.generate_all_charts(trends_data)
            
            if chart_files:
                self.logger.info(f"✅ 成功生成 {len(chart_files)} 个图表:")
                for i, chart_file in enumerate(chart_files, 1):
                    filename = Path(chart_file).name
                    self.logger.info(f"  {i}. {filename}")
                
                # 4. 生成关于图表的推文内容
                tweet_content = self.generate_chart_tweet(trends_data, len(chart_files))
                
                # 5. 尝试发布包含图表信息的推文
                try:
                    tools = await _get_all_mcp_tools()
                    if "post_tweet" in tools:
                        post_result = await tools["post_tweet"].ainvoke({
                            "text": tweet_content,
                            "user_id": "e634c89a-a63a-40fe-af3b-b9d96de0b97a",
                            "media_inputs": []
                        })
                        self.logger.info(f"📱 图表分析推文发布成功: {post_result}")
                    else:
                        self.logger.info(f"📝 图表分析推文内容 (MCP不可用): {tweet_content}")
                except Exception as e:
                    self.logger.error(f"推文发布失败: {e}")
                    self.logger.info(f"📝 图表分析推文内容: {tweet_content}")
            else:
                self.logger.warning("⚠️ 未能生成任何图表")
            
            self.logger.info("✅ 数据可视化任务完成")
            
        except Exception as e:
            self.logger.error(f"❌ 数据可视化任务失败: {str(e)}")
    
    def generate_chart_tweet(self, data: Dict[str, Any], chart_count: int) -> str:
        """生成关于图表分析的推文内容"""
        keywords_data = data.get("keywords_count", {})
        top_keyword = max(keywords_data, key=keywords_data.get) if keywords_data else "AI"
        
        templates = [
            f"📊 刚刚完成科技数据分析，生成了{chart_count}个可视化图表！当前最热话题：{top_keyword}。数据显示AI技术持续升温，值得关注！#DataVisualization #TechTrends #科技分析",
            f"🎯 最新科技趋势图表新鲜出炉！通过数据分析发现，{top_keyword}领域热度居高不下。科技发展日新月异，让我们用数据看未来！#TechAnalytics #DataScience #AI趋势",
            f"📈 用数据说话！今日科技热点分析完成，生成{chart_count}个专业图表。{top_keyword}话题讨论度最高，科技创新步伐加快！#DataDriven #Technology #Innovation",
            f"🔥 科技数据实时监控更新！当前{top_keyword}相关话题最活跃，通过可视化分析看到了有趣的趋势。技术改变世界！#RealTimeData #TechMonitoring #Future"
        ]
        
        import random
        template = random.choice(templates)
        
        # 确保推文长度不超过280字符
        if len(template) > 280:
            template = template[:277] + "..."
        
        return template
    
    def add_scheduled_jobs(self):
        """添加定时任务"""
        # === 每日科技内容发布任务（新增） ===
        
        # 06:30 - 创建内容草稿供审核
        self.scheduler.add_job(
            self.daily_publisher.create_content_drafts_for_review,
            trigger=CronTrigger(hour=6, minute=30),
            id="create_drafts_job",
            name="创建每日内容草稿",
            replace_existing=True,
            max_instances=1
        )
        
        # 07:45 - 发布已审核通过的内容（替代原有定时发布）
        self.scheduler.add_job(
            self.daily_publisher.publish_approved_content,
            trigger=CronTrigger(hour=7, minute=45),
            id="publish_approved_job",
            name="发布已审核内容",
            replace_existing=True,
            max_instances=1
        )
        
        # 08:00 - 今日科技头条（融合中医科技）
        self.scheduler.add_job(
            self.daily_publisher.publish_morning_headlines,
            trigger=CronTrigger(hour=8, minute=0),
            id="daily_headlines_job",
            name="今日科技头条发布（含中医科技）",
            replace_existing=True,
            max_instances=1
        )
        
        # 12:00 - AI+传统智慧线程
        self.scheduler.add_job(
            self.daily_publisher.publish_ai_thread,
            trigger=CronTrigger(hour=12, minute=0),
            id="ai_wisdom_thread_job",
            name="AI+传统智慧线程发布",
            replace_existing=True,
            max_instances=1
        )
        
        # 14:00 - 中医科技专题
        self.scheduler.add_job(
            self.daily_publisher.publish_tcm_tech_focus,
            trigger=CronTrigger(hour=14, minute=0),
            id="tcm_tech_focus_job",
            name="中医科技专题发布",
            replace_existing=True,
            max_instances=1
        )
        
        # 16:00 - 精选转发
        self.scheduler.add_job(
            self.daily_publisher.publish_curated_retweet,
            trigger=CronTrigger(hour=16, minute=0),
            id="curated_retweet_job",
            name="精选转发发布",
            replace_existing=True,
            max_instances=1
        )
        
        # 20:00 - 本周回顾（仅周日）
        self.scheduler.add_job(
            self.daily_publisher.publish_weekly_recap,
            trigger=CronTrigger(hour=20, minute=0, day_of_week=6),  # 周日
            id="weekly_recap_job",
            name="本周科技趋势回顾",
            replace_existing=True,
            max_instances=1
        )
        
        # === 原有的分析任务（保留但降低频率） ===
        
        # 趋势分析任务 - 每6小时（降低频率）
        self.scheduler.add_job(
            self.execute_trend_analysis_task,
            trigger=IntervalTrigger(hours=6),
            id="trend_analysis_job",
            name="深度趋势分析",
            replace_existing=True,
            max_instances=1
        )
        
        # 互动检查任务 - 每8小时
        self.scheduler.add_job(
            self.execute_engagement_check_task,
            trigger=IntervalTrigger(hours=8),
            id="engagement_check_job", 
            name="互动监控与回应",
            replace_existing=True,
            max_instances=1
        )
        
        # 数据可视化任务 - 每12小时
        self.scheduler.add_job(
            self.execute_data_visualization_task,
            trigger=IntervalTrigger(hours=12),
            id="data_visualization_job",
            name="科技数据可视化分析",
            replace_existing=True,
            max_instances=1
        )
        
        # 图片推文任务 - 每6小时
        self.scheduler.add_job(
            self.execute_image_tweet_task,
            trigger=IntervalTrigger(hours=6),
            id="image_tweet_job",
            name="图片推文自动发布",
            replace_existing=True,
            max_instances=1
        )
    
    async def start(self):
        """启动调度器"""
        try:
            self.logger.info("🔧 正在启动Manual Twitter调度器...")
            
            self.add_scheduled_jobs()
            self.scheduler.start()
            
            self.logger.info(f"✅ 调度器已启动，执行间隔: {self.interval_hours}小时")
            
            # 列出任务
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "未知"
                self.logger.info(f"  📋 {job.name} (下次执行: {next_run})")
            
        except Exception as e:
            self.logger.error(f"❌ 调度器启动失败: {str(e)}")
            raise
    
    async def stop(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown(wait=False)
            self.logger.info("🛑 调度器已停止")
        except Exception as e:
            self.logger.error(f"❌ 调度器停止失败: {str(e)}")


async def main():
    """主函数"""
    load_dotenv()
    
    # 检查环境变量
    required_vars = ["ANTHROPIC_API_KEY", "TAVILY_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return
    
    # 创建调度器
    scheduler = ManualTwitterScheduler(interval_hours=1)  # 测试时1小时
    
    try:
        # 先执行一次测试
        print("🧪 执行单次测试...")
        await scheduler.execute_trend_analysis_task()
        
        # 启动调度器
        await scheduler.start()
        
        # 运行调度器
        print("🔄 调度器正在运行... 按 Ctrl+C 停止")
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 收到停止信号...")
        
    except Exception as e:
        print(f"❌ 程序出错: {str(e)}")
    finally:
        await scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())
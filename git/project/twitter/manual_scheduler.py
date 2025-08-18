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
from langchain_tavily import TavilySearch


class ManualTwitterScheduler:
    """手动Twitter调度器 - 直接调用工具"""
    
    def __init__(self, interval_hours: int = 3):
        self.interval_hours = interval_hours
        self.scheduler = AsyncIOScheduler()
        
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
    
    def add_scheduled_jobs(self):
        """添加定时任务"""
        # 趋势分析任务 - 每3小时
        self.scheduler.add_job(
            self.execute_trend_analysis_task,
            trigger=IntervalTrigger(hours=self.interval_hours),
            id="trend_analysis_job",
            name="趋势分析与内容创作",
            replace_existing=True,
            max_instances=1
        )
        
        # 互动检查任务 - 每6小时
        self.scheduler.add_job(
            self.execute_engagement_check_task,
            trigger=IntervalTrigger(hours=self.interval_hours * 2),
            id="engagement_check_job", 
            name="互动监控与回应",
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
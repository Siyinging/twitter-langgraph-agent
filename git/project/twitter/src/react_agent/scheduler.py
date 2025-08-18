"""Twitter Agent Scheduler - 定时执行Twitter运营任务

这个模块实现了基于APScheduler的定时任务调度系统，能够：
- 定期自动获取热门趋势
- 基于趋势生成创意内容并发推
- 监控和分析推文互动
- 可配置执行频率和任务类型
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from langchain_core.messages import HumanMessage
from react_agent.context import Context
from react_agent.graph import graph
from react_agent.state import InputState


class TwitterAgentScheduler:
    """Twitter Agent定时调度器"""
    
    def __init__(self, context: Context, interval_hours: int = 3):
        """初始化调度器
        
        Args:
            context: Agent运行上下文
            interval_hours: 执行间隔小时数，默认3小时
        """
        self.context = context
        self.interval_hours = interval_hours
        self.scheduler = AsyncIOScheduler()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_scheduled_input_state(self, task_type: str = "trend_analysis") -> InputState:
        """创建固定的InputState用于定时任务
        
        Args:
            task_type: 任务类型 ("trend_analysis", "content_creation", "engagement_check")
        """
        task_prompts = {
            "trend_analysis": (
                "📈 定时任务：趋势分析与内容创作\n\n"
                "请帮我：\n"
                "1. 获取当前全球热门趋势\n"
                "2. 分析AI、科技、编程相关的话题\n"
                "3. 基于热门趋势创作一条有趣且有价值的推文\n"
                "4. 发布这条推文\n\n"
                "注意：推文应该有创意、有价值，能够引起互动。"
            ),
            "content_creation": (
                "✨ 定时任务：智能内容创作\n\n"
                "请帮我：\n"
                "1. 搜索最近AI领域的热门讨论\n"
                "2. 找出有趣的技术观点或新闻\n"
                "3. 写一条原创推文分享你的见解\n"
                "4. 发布推文\n\n"
                "推文风格：专业但不失趣味，能够启发思考。"
            ),
            "engagement_check": (
                "💬 定时任务：互动监控与回应\n\n"
                "请帮我：\n"
                "1. 检查我最近发布推文的回复和引用\n"
                "2. 分析互动情况和用户反馈\n"
                "3. 对有价值的互动进行回应或点赞\n"
                "4. 总结互动数据和用户反馈\n\n"
                "重点关注有建设性的讨论和反馈。"
            )
        }
        
        prompt = task_prompts.get(task_type, task_prompts["trend_analysis"])
        
        return InputState(
            messages=[
                HumanMessage(
                    content=prompt,
                    additional_kwargs={
                        "task_type": task_type,
                        "scheduled_time": datetime.now(timezone.utc).isoformat(),
                        "auto_task": True
                    }
                )
            ]
        )
    
    async def execute_scheduled_task(self, task_type: str = "trend_analysis"):
        """执行定时任务"""
        try:
            self.logger.info(f"🚀 开始执行定时任务: {task_type}")
            
            # 为每个任务创建新的context以确保线程安全
            from dotenv import load_dotenv
            load_dotenv()
            
            context = Context()
            self.logger.info(f"🔧 创建新Context: model={context.model}")
            
            # 创建输入状态
            input_state = self.create_scheduled_input_state(task_type)
            
            # 调用graph执行任务
            result = await graph.ainvoke(
                input_state,
                config={"recursion_limit": 25}
            )
            
            # 记录执行结果
            if result and result.get("messages"):
                last_message = result["messages"][-1]
                self.logger.info(f"✅ 任务完成: {task_type}")
                self.logger.info(f"最终响应: {last_message.content[:100]}...")
            else:
                self.logger.warning(f"⚠️ 任务执行但无响应: {task_type}")
                
        except Exception as e:
            self.logger.error(f"❌ 定时任务执行失败 ({task_type}): {str(e)}")
    
    def add_scheduled_jobs(self):
        """添加定时任务到调度器"""
        # 趋势分析与内容创作 - 每3小时一次
        self.scheduler.add_job(
            self.execute_scheduled_task,
            trigger=IntervalTrigger(hours=self.interval_hours),
            args=["trend_analysis"],
            id="trend_analysis_job",
            name="趋势分析与内容创作",
            replace_existing=True,
            max_instances=1  # 防止任务重叠
        )
        
        # 互动检查 - 每6小时一次
        self.scheduler.add_job(
            self.execute_scheduled_task,
            trigger=IntervalTrigger(hours=self.interval_hours * 2),
            args=["engagement_check"],
            id="engagement_check_job",
            name="互动监控与回应",
            replace_existing=True,
            max_instances=1
        )
        
        # 内容创作 - 每8小时一次
        self.scheduler.add_job(
            self.execute_scheduled_task,
            trigger=IntervalTrigger(hours=self.interval_hours * 2 + 2),
            args=["content_creation"],
            id="content_creation_job",
            name="智能内容创作",
            replace_existing=True,
            max_instances=1
        )
    
    async def start(self):
        """启动调度器"""
        try:
            self.logger.info("🔧 正在启动Twitter Agent调度器...")
            
            # 添加定时任务
            self.add_scheduled_jobs()
            
            # 启动调度器
            self.scheduler.start()
            
            self.logger.info(f"✅ 调度器已启动，执行间隔: {self.interval_hours}小时")
            self.logger.info("📋 已添加的定时任务:")
            
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "未知"
                self.logger.info(f"  - {job.name} (下次执行: {next_run})")
            
            # 可选：立即执行一次测试
            # await self.execute_scheduled_task("trend_analysis")
            
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
    
    def list_jobs(self):
        """列出所有定时任务"""
        jobs = self.scheduler.get_jobs()
        if not jobs:
            print("📋 暂无定时任务")
            return
            
        for job in jobs:
            next_run = "调度器未启动"
            if hasattr(job, 'next_run_time') and job.next_run_time:
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"📋 任务: {job.name}")
            print(f"   ID: {job.id}")
            print(f"   下次执行: {next_run}")
            print(f"   执行间隔: {job.trigger}")
            print()


async def run_scheduler(interval_hours: int = 3, run_forever: bool = True):
    """运行Twitter Agent调度器的便捷函数
    
    Args:
        interval_hours: 执行间隔小时数
        run_forever: 是否持续运行
    """
    # 创建context
    context = Context()
    
    # 创建调度器
    scheduler = TwitterAgentScheduler(context, interval_hours)
    
    try:
        # 启动调度器
        await scheduler.start()
        
        if run_forever:
            # 持续运行
            print("🔄 调度器正在运行中... 按 Ctrl+C 停止")
            try:
                while True:
                    await asyncio.sleep(60)  # 每分钟检查一次
            except KeyboardInterrupt:
                print("\n👋 收到停止信号...")
        
        return scheduler
        
    except Exception as e:
        print(f"❌ 调度器运行出错: {str(e)}")
        raise
    finally:
        await scheduler.stop()


if __name__ == "__main__":
    # 直接运行调度器
    asyncio.run(run_scheduler(interval_hours=1))  # 测试时使用1小时间隔
"""调度器配置管理

这个模块管理Twitter Agent调度器的配置参数，包括：
- 执行间隔设置
- 任务类型配置
- 日志级别控制
- 运行时参数
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SchedulerConfig:
    """调度器配置类"""
    
    # 基础执行间隔（小时）
    base_interval_hours: int = 3
    
    # 各类任务的执行频率（相对于基础间隔的倍数）
    task_intervals: Dict[str, int] = field(default_factory=lambda: {
        "trend_analysis": 1,      # 每3小时 = 3 * 1 
        "engagement_check": 2,    # 每6小时 = 3 * 2
        "content_creation": 3,    # 每9小时 = 3 * 3
    })
    
    # 任务配置
    max_instances_per_job: int = 1  # 防止任务重叠
    recursion_limit: int = 25       # 单次任务最大递归次数
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Twitter相关配置
    tweet_max_length: int = 280
    hashtags_per_tweet: int = 3
    
    # 任务执行策略
    enabled_tasks: List[str] = field(default_factory=lambda: [
        "trend_analysis", 
        "engagement_check", 
        "content_creation"
    ])
    
    # 安全设置
    max_tweets_per_hour: int = 5       # 每小时最大推文数
    min_interval_minutes: int = 30      # 推文间最小间隔（分钟）
    
    # 错误处理
    max_retries: int = 3               # 任务失败最大重试次数
    retry_delay_minutes: int = 10       # 重试间隔（分钟）
    
    @classmethod
    def from_env(cls) -> "SchedulerConfig":
        """从环境变量创建配置"""
        config = cls()
        
        # 从环境变量读取配置
        if interval := os.getenv("SCHEDULER_INTERVAL_HOURS"):
            config.base_interval_hours = int(interval)
        
        if log_level := os.getenv("SCHEDULER_LOG_LEVEL"):
            config.log_level = log_level.upper()
        
        if max_tweets := os.getenv("SCHEDULER_MAX_TWEETS_PER_HOUR"):
            config.max_tweets_per_hour = int(max_tweets)
        
        if enabled_tasks := os.getenv("SCHEDULER_ENABLED_TASKS"):
            config.enabled_tasks = [task.strip() for task in enabled_tasks.split(",")]
        
        return config
    
    def get_task_interval_hours(self, task_type: str) -> int:
        """获取特定任务的执行间隔（小时）"""
        multiplier = self.task_intervals.get(task_type, 1)
        return self.base_interval_hours * multiplier
    
    def is_task_enabled(self, task_type: str) -> bool:
        """检查任务是否启用"""
        return task_type in self.enabled_tasks


# 默认配置实例
DEFAULT_CONFIG = SchedulerConfig()

# 预定义的配置模板
DEVELOPMENT_CONFIG = SchedulerConfig(
    base_interval_hours=1,  # 开发时更频繁执行
    max_tweets_per_hour=10,
    log_level="DEBUG"
)

PRODUCTION_CONFIG = SchedulerConfig(
    base_interval_hours=6,  # 生产环境较低频率
    max_tweets_per_hour=3,
    log_level="INFO"
)

TESTING_CONFIG = SchedulerConfig(
    base_interval_hours=1,
    max_tweets_per_hour=1,
    max_retries=1,
    enabled_tasks=["trend_analysis"]  # 仅启用一个任务用于测试
)


def get_config(config_name: Optional[str] = None) -> SchedulerConfig:
    """获取配置实例
    
    Args:
        config_name: 配置名称 ("development", "production", "testing") 或 None
    
    Returns:
        SchedulerConfig: 配置实例
    """
    if config_name == "development":
        return DEVELOPMENT_CONFIG
    elif config_name == "production":
        return PRODUCTION_CONFIG
    elif config_name == "testing":
        return TESTING_CONFIG
    else:
        # 默认从环境变量读取
        return SchedulerConfig.from_env()
#!/usr/bin/env python3
"""智能自动发布系统 - 定时发布 + 智能内容监控

功能：
- 按时间表自动发布真实化内容
- 监控热点新闻并智能发布
- 内容去重和质量控制
- 发布频率智能调整
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

# 设置项目路径
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/intelligent_publisher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class IntelligentAutoPublisher:
    """智能自动发布器"""
    
    def __init__(self):
        self.is_running = False
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        
        # 内容去重记录
        self.published_content_hashes = set()
        self.load_published_hashes()
        
        # 发布时间表
        self.schedule = {
            8: {"type": "headlines", "name": "🌅 今日科技头条"},
            14: {"type": "tcm", "name": "🏥 中医科技专题"}
        }
        
        # 智能发布配置
        self.smart_publish_config = {
            "min_interval_minutes": 120,  # 最小发布间隔2小时
            "max_daily_posts": 6,         # 每日最多6条
            "news_freshness_hours": 4,    # 新闻新鲜度4小时
            "quality_threshold": 0.7      # 质量阈值
        }
        
        # 今日发布记录
        self.today_posts = 0
        self.last_smart_publish = None
    
    def load_published_hashes(self):
        """加载已发布内容的哈希"""
        try:
            hash_file = Path("data/published_hashes.json")
            if hash_file.exists():
                with open(hash_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.published_content_hashes = set(data.get('hashes', []))
                logger.info(f"📝 加载了{len(self.published_content_hashes)}个已发布内容哈希")
        except Exception as e:
            logger.warning(f"加载哈希文件失败: {e}")
    
    def save_published_hashes(self):
        """保存已发布内容的哈希"""
        try:
            hash_file = Path("data/published_hashes.json")
            data = {
                "hashes": list(self.published_content_hashes),
                "updated": datetime.now(timezone.utc).isoformat()
            }
            with open(hash_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存哈希文件失败: {e}")
    
    def get_content_hash(self, content: str) -> str:
        """计算内容哈希用于去重"""
        # 去除时间戳和emoji，只保留核心内容
        core_content = content.replace(' ', '').replace('\n', '')
        # 去除emoji
        import re
        core_content = re.sub(r'[^\w\u4e00-\u9fff]', '', core_content)
        return hashlib.md5(core_content.encode('utf-8')).hexdigest()[:12]
    
    def is_duplicate_content(self, content: str) -> bool:
        """检查是否重复内容"""
        content_hash = self.get_content_hash(content)
        return content_hash in self.published_content_hashes
    
    def mark_as_published(self, content: str):
        """标记内容已发布"""
        content_hash = self.get_content_hash(content)
        self.published_content_hashes.add(content_hash)
        self.save_published_hashes()
    
    async def scheduled_publish(self, hour: int, config: Dict[str, Any]) -> bool:
        """执行定时发布"""
        try:
            from react_agent.direct_publisher import direct_post_tweet, direct_post_with_media
            from react_agent.authentic_content_generator import AuthenticContentGenerator
            from react_agent.smart_media_manager import check_and_generate_image
            
            logger.info(f"⏰ 执行定时发布: {config['name']}")
            
            generator = AuthenticContentGenerator()
            
            # 生成内容
            if config['type'] == 'headlines':
                content = await generator.generate_authentic_headlines()
            elif config['type'] == 'tcm':
                content = await generator.generate_authentic_tcm_content()
            else:
                content = await generator.generate_authentic_headlines()
            
            # 检查重复
            if self.is_duplicate_content(content):
                logger.warning("⚠️ 内容重复，重新生成...")
                # 再试一次
                if config['type'] == 'headlines':
                    content = await generator.generate_authentic_headlines()
                elif config['type'] == 'tcm':
                    content = await generator.generate_authentic_tcm_content()
            
            logger.info(f"📝 生成内容: {content[:50]}...")
            
            # 检查配图
            image_path = await check_and_generate_image(content, config['type'])
            
            # 发布
            if image_path:
                logger.info(f"📸 配图: {image_path}")
                result = await direct_post_with_media(content, [image_path])
            else:
                result = await direct_post_tweet(content)
            
            if result and result.get('success'):
                tweet_id = result.get('tweet_id') or result.get('data', {}).get('tweet_id')
                logger.info(f"✅ 定时发布成功: {tweet_id}")
                self.mark_as_published(content)
                self.today_posts += 1
                return True
            else:
                error = result.get('error') if result else '发布失败'
                logger.error(f"❌ 定时发布失败: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 定时发布异常: {e}")
            return False
    
    async def check_smart_publish_opportunity(self) -> bool:
        """检查是否有智能发布机会"""
        try:
            # 检查发布频率限制
            if self.today_posts >= self.smart_publish_config['max_daily_posts']:
                return False
            
            # 检查时间间隔
            now = datetime.now(timezone.utc)
            if self.last_smart_publish:
                time_diff = (now - self.last_smart_publish).total_seconds() / 60
                if time_diff < self.smart_publish_config['min_interval_minutes']:
                    return False
            
            # 检查是否有新鲜的热点新闻
            from react_agent.real_time_news import RealTimeNewsCollector
            
            collector = RealTimeNewsCollector()
            news_data = await collector.get_cached_news(max_age_hours=1)
            
            if not news_data:
                # 尝试获取新新闻
                logger.info("🔍 搜索新的热点内容...")
                news_data = await collector.collect_latest_news(hours_back=2, max_results_per_category=2)
            
            if news_data:
                # 检查是否有高质量新闻
                all_news = []
                for news_list in news_data.values():
                    all_news.extend(news_list)
                
                high_quality_news = [n for n in all_news if n.quality_score + n.trending_score > self.smart_publish_config['quality_threshold']]
                
                if high_quality_news:
                    logger.info(f"🔥 发现{len(high_quality_news)}条高质量热点新闻")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"智能发布检查失败: {e}")
            return False
    
    async def smart_publish(self) -> bool:
        """智能发布热点内容"""
        try:
            from react_agent.direct_publisher import direct_post_tweet, direct_post_with_media
            from react_agent.authentic_content_generator import AuthenticContentGenerator
            from react_agent.smart_media_manager import check_and_generate_image
            
            logger.info("🧠 执行智能发布...")
            
            generator = AuthenticContentGenerator()
            
            # 生成基于热点的内容
            content = await generator.generate_authentic_headlines()
            
            # 检查重复
            if self.is_duplicate_content(content):
                logger.info("内容重复，跳过此次智能发布")
                return False
            
            logger.info(f"💡 智能发布内容: {content[:50]}...")
            
            # 检查配图
            image_path = await check_and_generate_image(content, "smart_publish")
            
            # 发布
            if image_path:
                result = await direct_post_with_media(content, [image_path])
            else:
                result = await direct_post_tweet(content)
            
            if result and result.get('success'):
                tweet_id = result.get('tweet_id') or result.get('data', {}).get('tweet_id')
                logger.info(f"✅ 智能发布成功: {tweet_id}")
                self.mark_as_published(content)
                self.today_posts += 1
                self.last_smart_publish = datetime.now(timezone.utc)
                return True
            else:
                error = result.get('error') if result else '发布失败'
                logger.error(f"❌ 智能发布失败: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 智能发布异常: {e}")
            return False
    
    async def reset_daily_counters(self):
        """重置每日计数器"""
        self.today_posts = 0
        self.last_smart_publish = None
        logger.info("🔄 重置每日发布计数器")
    
    async def run(self):
        """运行智能发布系统"""
        logger.info("🚀 启动智能自动发布系统...")
        logger.info("📋 系统配置:")
        logger.info(f"  • 定时发布: {len(self.schedule)}个时间点")
        logger.info(f"  • 智能发布: 最小间隔{self.smart_publish_config['min_interval_minutes']}分钟")
        logger.info(f"  • 每日限制: 最多{self.smart_publish_config['max_daily_posts']}条")
        
        self.is_running = True
        last_hour = None
        last_daily_reset = datetime.now(timezone.utc).date()
        
        try:
            while self.is_running:
                current_time = datetime.now(timezone.utc)
                current_hour = current_time.hour
                current_date = current_time.date()
                
                # 每日重置
                if current_date != last_daily_reset:
                    await self.reset_daily_counters()
                    last_daily_reset = current_date
                
                # 定时发布检查
                if current_hour != last_hour and current_hour in self.schedule:
                    config = self.schedule[current_hour]
                    await self.scheduled_publish(current_hour, config)
                    last_hour = current_hour
                
                # 智能发布检查（每30分钟）
                if current_time.minute % 30 == 0:
                    if await self.check_smart_publish_opportunity():
                        await self.smart_publish()
                
                # 每分钟检查一次
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("🛑 用户停止系统")
            self.is_running = False
        except Exception as e:
            logger.error(f"❌ 系统运行异常: {e}")

def main():
    """主函数"""
    publisher = IntelligentAutoPublisher()
    
    print("🤖 Twitter智能自动发布系统")
    print("=" * 50)
    print("📅 定时发布时间表 (UTC时间):")
    print("  • 08:00 - 🌅 真实化科技头条")
    print("  • 14:00 - 🏥 真实化中医科技专题")
    print()
    print("🧠 智能发布特点:")
    print("  • 🔥 自动监控热点新闻")
    print("  • ⚡ 智能发布时机选择")
    print("  • 🔄 内容去重防重复")
    print("  • 📊 每日发布量控制")
    print()
    print("📝 按 Ctrl+C 停止系统")
    print("=" * 50)
    
    try:
        asyncio.run(publisher.run())
    except KeyboardInterrupt:
        print("\n👋 用户主动停止系统")
    except Exception as e:
        print(f"❌ 系统异常: {e}")

if __name__ == "__main__":
    main()
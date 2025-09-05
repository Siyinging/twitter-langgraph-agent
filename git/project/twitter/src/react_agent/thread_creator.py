#!/usr/bin/env python3
"""Twitter线程创建器 - 用于创建连续的Twitter线程

支持：
- 基本线程创建（发推 -> 回复 -> 回复...）
- 可持续AI专题线程
- 自定义内容线程
- 线程完整性验证
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from react_agent.tools import post_tweet, reply_tweet
from react_agent.content_generator import TechContentGenerator

logger = logging.getLogger(__name__)


@dataclass
class ThreadResult:
    """线程创建结果"""
    success: bool
    tweet_ids: List[str]
    thread_url: Optional[str]
    error_message: Optional[str] = None
    
    def __str__(self):
        if self.success:
            return f"线程创建成功: {len(self.tweet_ids)}条推文, URL: {self.thread_url}"
        else:
            return f"线程创建失败: {self.error_message}"


class TwitterThreadCreator:
    """Twitter线程创建器"""
    
    def __init__(self):
        self.content_generator = TechContentGenerator()
        
    async def create_thread(self, thread_content: List[str], delay_seconds: int = 2) -> ThreadResult:
        """创建Twitter线程
        
        Args:
            thread_content: 线程内容列表，每个元素是一条推文
            delay_seconds: 推文间延迟时间，避免API限制
            
        Returns:
            ThreadResult: 创建结果，包含推文ID和状态信息
        """
        if not thread_content or len(thread_content) == 0:
            return ThreadResult(
                success=False,
                tweet_ids=[],
                thread_url=None,
                error_message="线程内容不能为空"
            )
        
        try:
            logger.info(f"🧵 开始创建线程，共{len(thread_content)}条推文")
            tweet_ids = []
            
            # 1. 发布第一条推文
            first_tweet = thread_content[0]
            if len(first_tweet) > 280:
                first_tweet = first_tweet[:277] + "..."
                
            logger.info(f"📝 发布第一条推文: {first_tweet[:50]}...")
            first_result = await post_tweet(first_tweet)
            
            if not first_result or not first_result.get('success'):
                error_msg = first_result.get('message', '第一条推文发布失败') if first_result else '第一条推文发布失败'
                return ThreadResult(
                    success=False,
                    tweet_ids=[],
                    thread_url=None,
                    error_message=error_msg
                )
            
            first_tweet_id = first_result['data']['id']
            tweet_ids.append(first_tweet_id)
            logger.info(f"✅ 第一条推文发布成功: {first_tweet_id}")
            
            # 2. 依次回复创建线程
            last_tweet_id = first_tweet_id
            
            for i, content in enumerate(thread_content[1:], 2):
                if delay_seconds > 0:
                    await asyncio.sleep(delay_seconds)
                
                # 确保推文长度符合限制
                if len(content) > 280:
                    content = content[:277] + "..."
                
                logger.info(f"📝 发布第{i}条推文: {content[:50]}...")
                
                reply_result = await reply_tweet(last_tweet_id, content)
                
                if not reply_result or not reply_result.get('success'):
                    logger.warning(f"⚠️ 第{i}条推文发布失败，线程可能不完整")
                    error_msg = reply_result.get('message', f'第{i}条推文发布失败') if reply_result else f'第{i}条推文发布失败'
                    break
                
                reply_tweet_id = reply_result['data']['id']
                tweet_ids.append(reply_tweet_id)
                last_tweet_id = reply_tweet_id
                logger.info(f"✅ 第{i}条推文发布成功: {reply_tweet_id}")
            
            # 3. 生成线程URL
            thread_url = f"https://twitter.com/user/status/{first_tweet_id}"
            
            logger.info(f"🎉 线程创建完成: {len(tweet_ids)}/{len(thread_content)}条推文成功")
            
            return ThreadResult(
                success=len(tweet_ids) > 0,
                tweet_ids=tweet_ids,
                thread_url=thread_url,
                error_message=None if len(tweet_ids) == len(thread_content) else f"仅发布了{len(tweet_ids)}/{len(thread_content)}条推文"
            )
            
        except Exception as e:
            logger.error(f"❌ 线程创建过程中出错: {e}")
            return ThreadResult(
                success=False,
                tweet_ids=tweet_ids if 'tweet_ids' in locals() else [],
                thread_url=None,
                error_message=f"创建过程出错: {str(e)}"
            )
    
    async def create_sustainable_ai_thread(self) -> ThreadResult:
        """创建可持续AI专题线程
        
        Returns:
            ThreadResult: 线程创建结果
        """
        try:
            logger.info("🌱 开始创建可持续AI线程")
            
            # 生成可持续AI内容
            thread_content = await self.content_generator.generate_sustainable_ai_thread()
            
            if not thread_content:
                return ThreadResult(
                    success=False,
                    tweet_ids=[],
                    thread_url=None,
                    error_message="无法生成可持续AI内容"
                )
            
            # 创建线程
            result = await self.create_thread(thread_content, delay_seconds=3)
            
            if result.success:
                logger.info(f"🌱 可持续AI线程创建成功: {len(result.tweet_ids)}条推文")
            else:
                logger.error(f"🌱 可持续AI线程创建失败: {result.error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 可持续AI线程创建出错: {e}")
            return ThreadResult(
                success=False,
                tweet_ids=[],
                thread_url=None,
                error_message=f"创建出错: {str(e)}"
            )
    
    async def create_custom_thread(self, topic: str, tweet_count: int = 3) -> ThreadResult:
        """创建自定义主题线程
        
        Args:
            topic: 线程主题
            tweet_count: 推文数量
            
        Returns:
            ThreadResult: 线程创建结果
        """
        try:
            logger.info(f"🎯 开始创建自定义线程: {topic}")
            
            # 这里可以集成更复杂的内容生成逻辑
            # 暂时使用简单的模板
            thread_content = self._generate_custom_content(topic, tweet_count)
            
            result = await self.create_thread(thread_content, delay_seconds=2)
            
            if result.success:
                logger.info(f"🎯 自定义线程创建成功: {topic}")
            else:
                logger.error(f"🎯 自定义线程创建失败: {result.error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 自定义线程创建出错: {e}")
            return ThreadResult(
                success=False,
                tweet_ids=[],
                thread_url=None,
                error_message=f"创建出错: {str(e)}"
            )
    
    def _generate_custom_content(self, topic: str, count: int) -> List[str]:
        """生成自定义内容（简单实现）"""
        templates = {
            "AI发展": [
                f"🤖 {topic}正在快速演进，让我们一起探讨其发展趋势和影响。",
                f"💡 当前{topic}在技术创新方面取得了重要突破，特别是在算法优化和应用场景扩展上。",
                f"🚀 未来{topic}将会如何改变我们的生活和工作方式？这值得深入思考和讨论。"
            ],
            "科技创新": [
                f"⚡ {topic}是推动社会进步的重要力量，让我们分析其最新发展。",
                f"🔬 在{topic}领域，我们看到了许多令人兴奋的新技术和应用案例。",
                f"🌟 {topic}的未来充满可能性，它将继续塑造我们的数字化未来。"
            ]
        }
        
        # 选择合适的模板
        if "AI" in topic or "人工智能" in topic:
            base_templates = templates["AI发展"]
        else:
            base_templates = templates["科技创新"]
        
        # 生成指定数量的内容
        content = []
        for i in range(min(count, len(base_templates))):
            content.append(base_templates[i])
        
        # 如果需要更多内容，添加通用结尾
        while len(content) < count:
            content.append(f"🔮 关于{topic}，你有什么看法？欢迎在评论中分享你的想法！ #{topic.replace(' ', '')} #科技讨论")
            break  # 避免重复
        
        return content[:count]
    
    async def verify_thread_integrity(self, tweet_ids: List[str]) -> Dict[str, Any]:
        """验证线程完整性
        
        Args:
            tweet_ids: 推文ID列表
            
        Returns:
            Dict: 验证结果信息
        """
        try:
            logger.info(f"🔍 开始验证线程完整性，共{len(tweet_ids)}条推文")
            
            # 这里可以调用get_tweet_thread_context来验证线程结构
            # 暂时返回基本信息
            
            return {
                "thread_length": len(tweet_ids),
                "first_tweet_id": tweet_ids[0] if tweet_ids else None,
                "last_tweet_id": tweet_ids[-1] if tweet_ids else None,
                "is_complete": len(tweet_ids) > 0,
                "thread_url": f"https://twitter.com/user/status/{tweet_ids[0]}" if tweet_ids else None
            }
            
        except Exception as e:
            logger.error(f"❌ 验证线程完整性失败: {e}")
            return {
                "error": str(e),
                "is_complete": False
            }


if __name__ == "__main__":
    # 测试线程创建器
    async def test_thread_creator():
        creator = TwitterThreadCreator()
        
        print("=== 测试可持续AI线程创建 ===")
        
        # 模拟线程内容（避免实际发推）
        test_content = [
            "🌱 这是可持续AI线程的第一条推文，介绍环保AI的重要性。",
            "💡 第二条推文讨论AI能耗问题和解决方案。",
            "🚀 第三条推文展望绿色AI技术的未来发展。"
        ]
        
        print(f"模拟线程内容（共{len(test_content)}条）:")
        for i, content in enumerate(test_content, 1):
            print(f"{i}. {content} (字数: {len(content)})")
        
        print("\n注意: 实际运行时会调用Twitter API发布推文")
        
        # 验证内容生成
        ai_content = await creator.content_generator.generate_sustainable_ai_thread()
        print(f"\n=== 实际生成的可持续AI内容 ===")
        for i, content in enumerate(ai_content, 1):
            print(f"{i}. {content} (字数: {len(content)})")
    
    asyncio.run(test_thread_creator())
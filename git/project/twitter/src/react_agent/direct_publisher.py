#!/usr/bin/env python3
"""直接发布器 - 使用Twitter API客户端直接发布"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from react_agent.twitter_api_client import TwitterAPIClient

logger = logging.getLogger(__name__)


class DirectTwitterPublisher:
    """直接Twitter发布器 - 使用Twitter API客户端"""
    
    def __init__(self):
        self.client = TwitterAPIClient()
    
    async def post_simple_tweet(self, text: str) -> Dict[str, Any]:
        """发布简单推文"""
        try:
            result = self.client.post_tweet(text)
            
            if result and result.get('success'):
                logger.info(f"✅ 推文发布成功: {result.get('tweet_id')}")
                return result
            else:
                logger.error(f"❌ 推文发布失败: {result}")
                return {
                    "success": False,
                    "error": result.get('error') if result else '发布失败'
                }
            
        except Exception as e:
            logger.error(f"❌ 推文发布失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_tweet_with_media(self, text: str, media_paths: List[str]) -> Dict[str, Any]:
        """发布带媒体的推文"""
        try:
            result = self.client.post_tweet_with_media(text, media_paths)
            
            if result and result.get('success'):
                logger.info(f"✅ 带媒体推文发布成功: {result.get('tweet_id')}")
                return result
            else:
                logger.error(f"❌ 带媒体推文发布失败: {result}")
                return {
                    "success": False,
                    "error": result.get('error') if result else '发布失败'
                }
            
        except Exception as e:
            logger.error(f"❌ 带媒体推文发布失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> bool:
        """测试Twitter连接"""
        try:
            if self.client.is_authenticated():
                logger.info("✅ Twitter API连接正常")
                return True
            else:
                logger.error("❌ Twitter API连接失败")
                return False
            
        except Exception as e:
            logger.error(f"❌ Twitter连接测试失败: {e}")
            return False


# 全局实例
direct_publisher = DirectTwitterPublisher()


# 便利函数
async def direct_post_tweet(text: str) -> Dict[str, Any]:
    """直接发布推文的便利函数"""
    return await direct_publisher.post_simple_tweet(text)


async def direct_post_with_media(text: str, media_paths: List[str]) -> Dict[str, Any]:
    """直接发布带媒体推文的便利函数"""
    return await direct_publisher.post_tweet_with_media(text, media_paths)


if __name__ == "__main__":
    # 测试直接发布器
    async def test_direct_publisher():
        publisher = DirectTwitterPublisher()
        
        print("🔧 测试Twitter连接...")
        if await publisher.test_connection():
            print("✅ Twitter连接正常")
        else:
            print("❌ Twitter连接失败")
            return
        
        print("📝 测试简单推文发布...")
        result = await publisher.post_simple_tweet("🧪 测试直接发布器功能")
        print(f"结果: {result}")
    
    asyncio.run(test_direct_publisher())
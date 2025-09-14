#!/usr/bin/env python3
"""直接发布器 - 绕过LangChain context问题的直接MCP调用"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from react_agent.tools import _get_all_mcp_tools

logger = logging.getLogger(__name__)


class DirectTwitterPublisher:
    """直接Twitter发布器 - 避免LangChain context问题"""
    
    def __init__(self, user_id: str = "e634c89a-a63a-40fe-af3b-b9d96de0b97a"):
        self.user_id = user_id
    
    async def post_simple_tweet(self, text: str) -> Dict[str, Any]:
        """发布简单推文"""
        try:
            tools = await _get_all_mcp_tools()
            
            if "post_tweet" not in tools:
                return {
                    "success": False,
                    "error": "post_tweet工具不可用"
                }
            
            result = await tools["post_tweet"].ainvoke({
                "text": text,
                "user_id": self.user_id,
                "media_inputs": []
            })
            
            # 处理JSON字符串返回结果
            if isinstance(result, str):
                try:
                    import json
                    result = json.loads(result)
                except json.JSONDecodeError:
                    result = {"raw_response": result}
            
            logger.info(f"✅ 推文发布成功: {result}")
            
            # 提取推文ID
            tweet_id = None
            if isinstance(result, dict):
                tweet_id = result.get("tweet_id") or result.get("id")
            
            return {
                "success": True,
                "data": result,
                "tweet_id": tweet_id
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
            tools = await _get_all_mcp_tools()
            
            if "post_tweet" not in tools:
                return {
                    "success": False,
                    "error": "post_tweet工具不可用"
                }
            
            # 准备媒体数据 - 根据工具schema，应该是字符串数组
            media_inputs = []
            for media_path in media_paths:
                try:
                    # 直接使用文件路径，让MCP工具自己处理
                    media_inputs.append(media_path)
                    
                except Exception as e:
                    logger.warning(f"处理媒体文件失败 {media_path}: {e}")
                    continue
            
            result = await tools["post_tweet"].ainvoke({
                "text": text,
                "user_id": self.user_id,
                "media_inputs": media_inputs
            })
            
            # 处理JSON字符串返回结果
            if isinstance(result, str):
                try:
                    import json
                    result = json.loads(result)
                except json.JSONDecodeError:
                    result = {"raw_response": result}
            
            logger.info(f"✅ 带媒体推文发布成功: {result}")
            
            # 提取推文ID
            tweet_id = None
            if isinstance(result, dict):
                tweet_id = result.get("tweet_id") or result.get("id")
            
            return {
                "success": True,
                "data": result,
                "tweet_id": tweet_id
            }
            
        except Exception as e:
            logger.error(f"❌ 带媒体推文发布失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_thread(self, thread_content: List[str]) -> Dict[str, Any]:
        """发布推文线程"""
        try:
            tweet_ids = []
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(thread_content):
                # 发布推文
                if previous_tweet_id:
                    # 回复前一条推文
                    result = await self._reply_to_tweet(tweet_text, previous_tweet_id)
                else:
                    # 发布第一条推文
                    result = await self.post_simple_tweet(tweet_text)
                
                if result.get("success"):
                    tweet_id = result.get("tweet_id") or result.get("data", {}).get("id")
                    if tweet_id:
                        tweet_ids.append(tweet_id)
                        previous_tweet_id = tweet_id
                    else:
                        logger.warning(f"第{i+1}条推文发布成功但未获取到ID")
                else:
                    logger.error(f"第{i+1}条推文发布失败: {result.get('error')}")
                    break
                
                # 避免过快发布
                await asyncio.sleep(1)
            
            success = len(tweet_ids) == len(thread_content)
            return {
                "success": success,
                "tweet_ids": tweet_ids,
                "thread_url": f"https://twitter.com/user/status/{tweet_ids[0]}" if tweet_ids else None,
                "published_count": len(tweet_ids),
                "total_count": len(thread_content)
            }
            
        except Exception as e:
            logger.error(f"❌ 线程发布失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "tweet_ids": tweet_ids
            }
    
    async def _reply_to_tweet(self, text: str, reply_to_id: str) -> Dict[str, Any]:
        """回复推文"""
        try:
            tools = await _get_all_mcp_tools()
            
            if "reply_to_tweet" in tools:
                # 使用专门的回复工具
                result = await tools["reply_to_tweet"].ainvoke({
                    "text": text,
                    "user_id": self.user_id,
                    "reply_to_tweet_id": reply_to_id
                })
            elif "post_tweet" in tools:
                # 使用通用发布工具
                result = await tools["post_tweet"].ainvoke({
                    "text": text,
                    "user_id": self.user_id,
                    "reply_to_tweet_id": reply_to_id,
                    "media_inputs": []
                })
            else:
                return {
                    "success": False,
                    "error": "推文回复工具不可用"
                }
            
            return {
                "success": True,
                "data": result,
                "tweet_id": result.get("id") if isinstance(result, dict) else None
            }
            
        except Exception as e:
            logger.error(f"❌ 推文回复失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> bool:
        """测试Twitter连接"""
        try:
            tools = await _get_all_mcp_tools()
            available_tools = list(tools.keys())
            logger.info(f"可用的Twitter工具: {available_tools}")
            
            # 检查必要工具
            required_tools = ["post_tweet"]
            for tool in required_tools:
                if tool not in tools:
                    logger.error(f"缺少必要工具: {tool}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Twitter连接测试失败: {e}")
            return False


# 全局实例
direct_publisher = DirectTwitterPublisher()


# 便利函数
async def direct_post_tweet(text: str) -> Dict[str, Any]:
    """直接发布推文的便利函数"""
    return await direct_publisher.post_simple_tweet(text)


async def direct_post_thread(thread_content: List[str]) -> Dict[str, Any]:
    """直接发布线程的便利函数"""
    return await direct_publisher.post_thread(thread_content)


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
        result = await publisher.post_simple_tweet("🧪 测试直接发布器功能 - " + 
                                                   str(asyncio.get_event_loop().time()))
        print(f"结果: {result}")
    
    asyncio.run(test_direct_publisher())
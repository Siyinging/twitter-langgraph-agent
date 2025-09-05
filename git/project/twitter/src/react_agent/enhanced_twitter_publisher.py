#!/usr/bin/env python3
"""增强的Twitter发布器 - 支持多种发布方式"""

import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedTwitterPublisher:
    """增强的Twitter发布器，支持多种发布方式"""
    
    def __init__(self):
        """初始化发布器"""
        self.twitter_api_client = None
        self.mcp_tools = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化所有可用的Twitter客户端"""
        # 尝试初始化直接Twitter API客户端
        try:
            from .twitter_api_client import TwitterAPIClient
            self.twitter_api_client = TwitterAPIClient()
            if self.twitter_api_client.is_authenticated():
                logger.info("✅ 直接Twitter API客户端初始化成功")
            else:
                logger.warning("⚠️ 直接Twitter API客户端认证失败")
                self.twitter_api_client = None
        except Exception as e:
            logger.warning(f"⚠️ 直接Twitter API客户端初始化失败: {e}")
            self.twitter_api_client = None
        
        # 尝试初始化MCP工具
        try:
            from .tools import _get_all_mcp_tools
            import asyncio
            loop = asyncio.get_event_loop()
            self.mcp_tools = loop.run_until_complete(_get_all_mcp_tools())
            if self.mcp_tools.get("post_tweet"):
                logger.info("✅ Twitter MCP工具初始化成功")
            else:
                logger.warning("⚠️ Twitter MCP工具中没有post_tweet")
                self.mcp_tools = None
        except Exception as e:
            logger.warning(f"⚠️ Twitter MCP工具初始化失败: {e}")
            self.mcp_tools = None
    
    def get_available_methods(self) -> List[str]:
        """获取可用的发布方法"""
        methods = []
        if self.twitter_api_client:
            methods.append("direct_api")
        if self.mcp_tools:
            methods.append("mcp")
        return methods
    
    async def post_tweet_with_media(self, text: str, media_paths: List[str]) -> Dict[str, Any]:
        """发布带媒体的推文，自动选择最佳方法"""
        
        available_methods = self.get_available_methods()
        logger.info(f"📋 可用发布方法: {available_methods}")
        
        if not available_methods:
            return {
                "success": False,
                "error": "没有可用的Twitter发布方法",
                "suggestion": "请配置Twitter API凭据或检查MCP连接"
            }
        
        # 优先尝试直接API（支持媒体上传）
        if "direct_api" in available_methods and media_paths:
            logger.info("🎯 使用直接Twitter API发布带媒体推文...")
            try:
                result = self.twitter_api_client.post_tweet_with_media(text, media_paths)
                if result and result.get("success"):
                    result["method"] = "direct_api"
                    return result
                else:
                    logger.warning("⚠️ 直接API发布失败，尝试其他方法")
            except Exception as e:
                logger.error(f"❌ 直接API发布出错: {e}")
        
        # 回退到MCP（纯文本）
        if "mcp" in available_methods:
            logger.info("🔄 回退到MCP发布纯文本推文...")
            try:
                from .context import Context
                from langgraph.runtime import get_runtime
                
                runtime = get_runtime(Context)
                result = await self.mcp_tools["post_tweet"].ainvoke({
                    "text": text,
                    "user_id": runtime.context.twitter_user_id,
                    "media_inputs": []  # MCP暂不支持媒体
                })
                
                return {
                    "success": True,
                    "method": "mcp",
                    "result": result,
                    "warning": "图片未上传（MCP限制）"
                }
                
            except Exception as e:
                logger.error(f"❌ MCP发布出错: {e}")
        
        # 所有方法都失败
        return {
            "success": False,
            "error": "所有发布方法都失败",
            "methods_tried": available_methods
        }
    
    async def post_tweet(self, text: str) -> Dict[str, Any]:
        """发布纯文本推文"""
        return await self.post_tweet_with_media(text, [])
    
    def get_setup_instructions(self) -> Dict[str, str]:
        """获取设置说明"""
        instructions = {}
        
        if not self.twitter_api_client:
            instructions["direct_api"] = """
🔧 配置直接Twitter API:
1. 访问 https://developer.twitter.com/
2. 创建开发者账户和应用
3. 生成API密钥和访问令牌
4. 在.env文件中添加:
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
5. 运行: python3 test_twitter_setup.py
"""
        
        if not self.mcp_tools:
            instructions["mcp"] = """
🔧 配置Twitter MCP:
1. 确保MCP服务器运行: http://103.149.46.64:8000/protocol/mcp/
2. 检查网络连接
3. 验证用户ID配置
"""
        
        return instructions
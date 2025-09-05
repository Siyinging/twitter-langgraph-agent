#!/usr/bin/env python3
"""直接Twitter API客户端 - 支持完整的媒体上传功能"""

import os
import logging
from typing import Optional, List, Dict, Any
import tweepy
from pathlib import Path

logger = logging.getLogger(__name__)

class TwitterAPIClient:
    """直接Twitter API客户端，支持媒体上传"""
    
    def __init__(self):
        """初始化Twitter API客户端"""
        self.client = None
        self.api = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Twitter API连接"""
        try:
            # 从环境变量获取API密钥
            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            
            # 检查必需的凭据
            required_credentials = {
                "API_KEY": api_key,
                "API_SECRET": api_secret,
                "ACCESS_TOKEN": access_token,
                "ACCESS_TOKEN_SECRET": access_token_secret
            }
            
            missing_creds = [key for key, value in required_credentials.items() if not value]
            
            if missing_creds:
                logger.warning(f"⚠️ 缺少Twitter API凭据: {', '.join(missing_creds)}")
                logger.info("💡 请在.env文件中配置Twitter API凭据")
                return
            
            # 初始化Twitter API v2客户端 (用于发推文)
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # 初始化Twitter API v1.1 (用于媒体上传)
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret,
                access_token, access_token_secret
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("✅ Twitter API客户端初始化成功")
            
        except Exception as e:
            logger.error(f"❌ Twitter API客户端初始化失败: {e}")
            self.client = None
            self.api = None
    
    def is_authenticated(self) -> bool:
        """检查是否已正确认证"""
        return self.client is not None and self.api is not None
    
    def upload_media(self, media_path: str) -> Optional[str]:
        """上传媒体文件到Twitter
        
        Args:
            media_path: 媒体文件路径
            
        Returns:
            media_id字符串，失败返回None
        """
        if not self.is_authenticated():
            logger.error("❌ Twitter API未正确配置")
            return None
            
        try:
            logger.info(f"📤 开始上传媒体文件: {media_path}")
            
            # 检查文件是否存在
            media_file = Path(media_path)
            if not media_file.exists():
                logger.error(f"❌ 媒体文件不存在: {media_path}")
                return None
            
            # 检查文件大小 (Twitter限制5MB图片)
            file_size = media_file.stat().st_size
            if file_size > 5 * 1024 * 1024:  # 5MB
                logger.error(f"❌ 文件过大: {file_size / 1024 / 1024:.2f}MB，Twitter限制5MB")
                return None
            
            # 使用Twitter API v1.1上传媒体
            media = self.api.media_upload(str(media_path))
            media_id = media.media_id_string
            
            logger.info(f"✅ 媒体上传成功，media_id: {media_id}")
            return media_id
            
        except Exception as e:
            logger.error(f"❌ 媒体上传失败: {e}")
            return None
    
    def post_tweet_with_media(self, text: str, media_paths: List[str]) -> Optional[Dict[str, Any]]:
        """发布带媒体的推文
        
        Args:
            text: 推文文本
            media_paths: 媒体文件路径列表
            
        Returns:
            推文信息字典，失败返回None
        """
        if not self.is_authenticated():
            logger.error("❌ Twitter API未正确配置")
            return None
        
        try:
            media_ids = []
            
            # 上传所有媒体文件
            for media_path in media_paths:
                media_id = self.upload_media(media_path)
                if media_id:
                    media_ids.append(media_id)
                else:
                    logger.error(f"❌ 媒体上传失败，跳过: {media_path}")
            
            # 发布推文
            if media_ids:
                logger.info(f"🐦 发布带媒体的推文，media_ids: {media_ids}")
                response = self.client.create_tweet(text=text, media_ids=media_ids)
            else:
                logger.info("🐦 发布纯文本推文")
                response = self.client.create_tweet(text=text)
            
            if response.data:
                tweet_id = response.data['id']
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                
                result = {
                    "success": True,
                    "tweet_id": tweet_id,
                    "url": tweet_url,
                    "text": text,
                    "media_count": len(media_ids)
                }
                
                logger.info(f"🎉 推文发布成功: {tweet_url}")
                return result
            else:
                logger.error("❌ 推文发布失败，无响应数据")
                return None
                
        except Exception as e:
            logger.error(f"❌ 推文发布失败: {e}")
            return None
    
    def post_tweet(self, text: str) -> Optional[Dict[str, Any]]:
        """发布纯文本推文
        
        Args:
            text: 推文文本
            
        Returns:
            推文信息字典，失败返回None
        """
        return self.post_tweet_with_media(text, [])
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        if not self.is_authenticated():
            return None
            
        try:
            user = self.client.get_me()
            if user.data:
                return {
                    "id": user.data.id,
                    "username": user.data.username,
                    "name": user.data.name
                }
        except Exception as e:
            logger.error(f"❌ 获取用户信息失败: {e}")
        
        return None
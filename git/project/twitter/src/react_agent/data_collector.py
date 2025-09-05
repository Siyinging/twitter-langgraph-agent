#!/usr/bin/env python3
"""科技数据收集模块

用于收集AI技术趋势、科技新闻、市场数据等信息，为可视化图表提供数据源
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
from langchain_tavily import TavilySearch

logger = logging.getLogger(__name__)


class TechDataCollector:
    """科技数据收集器"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 数据存储文件路径
        self.trends_file = self.data_dir / "tech_trends.json"
        self.keywords_file = self.data_dir / "keywords_tracking.json"
        self.metrics_file = self.data_dir / "engagement_metrics.json"
        
        # 科技关键词配置
        self.tech_keywords = [
            "人工智能", "AI", "机器学习", "深度学习", "大语言模型", "GPT", "Claude",
            "区块链", "加密货币", "比特币", "以太坊", "Web3", "NFT",
            "云计算", "边缘计算", "5G", "6G", "物联网", "IoT",
            "量子计算", "自动驾驶", "机器人技术", "AR", "VR", "元宇宙",
            "网络安全", "数据科学", "大数据", "Python", "开源",
            "苹果", "谷歌", "微软", "特斯拉", "英伟达", "OpenAI", "Anthropic"
        ]
        
        # 搜索主题
        self.search_topics = [
            "AI technology trends 2025",
            "latest tech breakthroughs",
            "artificial intelligence news",
            "machine learning advances",
            "quantum computing progress",
            "cybersecurity developments",
            "blockchain innovation",
            "autonomous vehicles update",
            "robotics technology",
            "tech startup funding"
        ]
    
    async def collect_web_trends(self) -> Dict[str, Any]:
        """从网络收集科技趋势数据"""
        trends_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topics": {},
            "keywords_count": {},
            "sentiment_analysis": {},
            "sources": []
        }
        
        try:
            tavily = TavilySearch(max_results=10)
            
            for topic in self.search_topics[:5]:  # 限制查询数量
                try:
                    logger.info(f"正在搜索主题: {topic}")
                    results = await tavily.ainvoke({"query": topic})
                    
                    if results and isinstance(results, dict):
                        topic_data = []
                        for result in results.get('results', [])[:3]:
                            if isinstance(result, dict):
                                article_data = {
                                    "title": result.get('title', ''),
                                    "url": result.get('url', ''),
                                    "content": result.get('content', result.get('snippet', ''))[:500],
                                    "published_date": result.get('published_date', ''),
                                    "score": result.get('score', 0)
                                }
                                topic_data.append(article_data)
                                
                                # 统计关键词
                                content_text = article_data['title'] + ' ' + article_data['content']
                                for keyword in self.tech_keywords:
                                    if keyword.lower() in content_text.lower():
                                        trends_data["keywords_count"][keyword] = trends_data["keywords_count"].get(keyword, 0) + 1
                        
                        trends_data["topics"][topic] = topic_data
                        
                except Exception as e:
                    logger.error(f"搜索主题 {topic} 失败: {e}")
                    continue
                
                # 避免请求过快
                await asyncio.sleep(1)
            
            # 保存数据
            await self._save_trends_data(trends_data)
            logger.info(f"✅ 收集到 {len(trends_data['topics'])} 个主题的数据")
            
        except Exception as e:
            logger.error(f"❌ 趋势数据收集失败: {e}")
        
        return trends_data
    
    async def collect_keyword_metrics(self) -> Dict[str, Any]:
        """收集关键词热度指标"""
        metrics_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "keyword_trends": {},
            "top_keywords": [],
            "emerging_topics": [],
            "tech_categories": {
                "AI/ML": 0,
                "Blockchain": 0,
                "Cloud Computing": 0,
                "IoT": 0,
                "Cybersecurity": 0,
                "Robotics": 0,
                "Other": 0
            }
        }
        
        try:
            # 读取历史趋势数据
            if self.trends_file.exists():
                with open(self.trends_file, 'r', encoding='utf-8') as f:
                    recent_trends = json.load(f)
                
                keyword_counts = recent_trends.get("keywords_count", {})
                
                # 分析关键词趋势
                sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
                metrics_data["top_keywords"] = sorted_keywords[:15]
                
                # 分类统计
                ai_keywords = ["人工智能", "AI", "机器学习", "深度学习", "GPT", "Claude"]
                blockchain_keywords = ["区块链", "加密货币", "比特币", "以太坊", "Web3"]
                cloud_keywords = ["云计算", "边缘计算", "AWS", "Azure"]
                iot_keywords = ["物联网", "IoT", "5G", "6G"]
                security_keywords = ["网络安全", "加密", "隐私"]
                robotics_keywords = ["机器人技术", "自动驾驶", "无人机"]
                
                for keyword, count in keyword_counts.items():
                    if keyword in ai_keywords:
                        metrics_data["tech_categories"]["AI/ML"] += count
                    elif keyword in blockchain_keywords:
                        metrics_data["tech_categories"]["Blockchain"] += count
                    elif keyword in cloud_keywords:
                        metrics_data["tech_categories"]["Cloud Computing"] += count
                    elif keyword in iot_keywords:
                        metrics_data["tech_categories"]["IoT"] += count
                    elif keyword in security_keywords:
                        metrics_data["tech_categories"]["Cybersecurity"] += count
                    elif keyword in robotics_keywords:
                        metrics_data["tech_categories"]["Robotics"] += count
                    else:
                        metrics_data["tech_categories"]["Other"] += count
                
                # 检测新兴话题（新出现或快速增长的关键词）
                emerging = [kw for kw, count in sorted_keywords[:10] if count >= 3]
                metrics_data["emerging_topics"] = emerging
            
            # 保存指标数据
            await self._save_metrics_data(metrics_data)
            logger.info(f"✅ 关键词指标分析完成")
            
        except Exception as e:
            logger.error(f"❌ 关键词指标收集失败: {e}")
        
        return metrics_data
    
    async def get_historical_data(self, days: int = 7) -> pd.DataFrame:
        """获取历史数据用于趋势分析"""
        try:
            data_files = list(self.data_dir.glob("*.json"))
            historical_data = []
            
            for file_path in data_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "timestamp" in data:
                            historical_data.append({
                                "timestamp": data["timestamp"],
                                "file": file_path.stem,
                                "keywords_count": len(data.get("keywords_count", {})),
                                "topics_count": len(data.get("topics", {})),
                                "total_mentions": sum(data.get("keywords_count", {}).values())
                            })
                except Exception as e:
                    logger.warning(f"读取文件 {file_path} 失败: {e}")
            
            df = pd.DataFrame(historical_data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp').tail(days * 24)  # 按小时采样
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 获取历史数据失败: {e}")
            return pd.DataFrame()
    
    async def _save_trends_data(self, data: Dict[str, Any]):
        """保存趋势数据"""
        try:
            with open(self.trends_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存趋势数据失败: {e}")
    
    async def _save_metrics_data(self, data: Dict[str, Any]):
        """保存指标数据"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存指标数据失败: {e}")
    
    def get_sample_data(self) -> Dict[str, Any]:
        """获取示例数据（用于测试）"""
        return {
            "keywords_count": {
                "人工智能": 15,
                "机器学习": 12,
                "深度学习": 8,
                "区块链": 6,
                "云计算": 10,
                "物联网": 5,
                "量子计算": 3,
                "自动驾驶": 7,
                "网络安全": 9,
                "大数据": 11
            },
            "tech_categories": {
                "AI/ML": 35,
                "Blockchain": 6,
                "Cloud Computing": 10,
                "IoT": 5,
                "Cybersecurity": 9,
                "Robotics": 7,
                "Other": 8
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
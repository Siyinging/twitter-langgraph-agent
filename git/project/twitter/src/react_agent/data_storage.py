#!/usr/bin/env python3
"""数据存储和历史追踪模块

用于持久化保存科技数据，支持历史数据查询和趋势分析
"""

import json
import logging
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class TechDataStorage:
    """科技数据存储器"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 数据库文件
        self.db_path = self.data_dir / "tech_data.db"
        
        # 初始化数据库
        self.init_database()
    
    def init_database(self):
        """初始化SQLite数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建关键词历史表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS keyword_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        keyword TEXT NOT NULL,
                        count INTEGER NOT NULL,
                        category TEXT,
                        source TEXT DEFAULT 'web_search'
                    )
                ''')
                
                # 创建趋势数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trend_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        data_json TEXT NOT NULL,
                        total_mentions INTEGER DEFAULT 0,
                        sentiment_score REAL DEFAULT 0.0
                    )
                ''')
                
                # 创建分类统计表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS category_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        category TEXT NOT NULL,
                        count INTEGER NOT NULL,
                        percentage REAL DEFAULT 0.0
                    )
                ''')
                
                # 创建图表生成记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chart_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        chart_type TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        data_summary TEXT,
                        status TEXT DEFAULT 'created'
                    )
                ''')
                
                # 创建索引提升查询性能
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword_timestamp ON keyword_history(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword_name ON keyword_history(keyword)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_trend_timestamp ON trend_data(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_timestamp ON category_stats(timestamp)')
                
                conn.commit()
                logger.info("✅ 数据库初始化完成")
                
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
    
    def save_keyword_data(self, keywords_data: Dict[str, int], timestamp: str = None) -> bool:
        """保存关键词数据"""
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc).isoformat()
            
            # 关键词分类映射
            category_mapping = {
                "人工智能": "AI/ML", "AI": "AI/ML", "机器学习": "AI/ML", "深度学习": "AI/ML", 
                "大语言模型": "AI/ML", "GPT": "AI/ML", "Claude": "AI/ML",
                "区块链": "Blockchain", "加密货币": "Blockchain", "比特币": "Blockchain", 
                "以太坊": "Blockchain", "Web3": "Blockchain", "NFT": "Blockchain",
                "云计算": "Cloud Computing", "边缘计算": "Cloud Computing", "AWS": "Cloud Computing",
                "物联网": "IoT", "IoT": "IoT", "5G": "IoT", "6G": "IoT",
                "网络安全": "Cybersecurity", "加密": "Cybersecurity", "隐私": "Cybersecurity",
                "机器人技术": "Robotics", "自动驾驶": "Robotics", "无人机": "Robotics"
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for keyword, count in keywords_data.items():
                    category = category_mapping.get(keyword, "Other")
                    cursor.execute('''
                        INSERT INTO keyword_history (timestamp, keyword, count, category)
                        VALUES (?, ?, ?, ?)
                    ''', (timestamp, keyword, count, category))
                
                conn.commit()
                logger.info(f"✅ 保存了 {len(keywords_data)} 个关键词数据")
                return True
                
        except Exception as e:
            logger.error(f"❌ 保存关键词数据失败: {e}")
            return False
    
    def save_trend_data(self, topic: str, data: Dict[str, Any], timestamp: str = None) -> bool:
        """保存趋势数据"""
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc).isoformat()
            
            data_json = json.dumps(data, ensure_ascii=False)
            total_mentions = sum(data.get("keywords_count", {}).values())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trend_data (timestamp, topic, data_json, total_mentions)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, topic, data_json, total_mentions))
                conn.commit()
                
            logger.info(f"✅ 保存趋势数据: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存趋势数据失败: {e}")
            return False
    
    def save_category_stats(self, categories_data: Dict[str, int], timestamp: str = None) -> bool:
        """保存分类统计数据"""
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc).isoformat()
            
            total_count = sum(categories_data.values())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for category, count in categories_data.items():
                    percentage = (count / total_count * 100) if total_count > 0 else 0
                    cursor.execute('''
                        INSERT INTO category_stats (timestamp, category, count, percentage)
                        VALUES (?, ?, ?, ?)
                    ''', (timestamp, category, count, percentage))
                
                conn.commit()
                logger.info(f"✅ 保存了 {len(categories_data)} 个分类统计")
                return True
                
        except Exception as e:
            logger.error(f"❌ 保存分类统计失败: {e}")
            return False
    
    def save_chart_record(self, chart_type: str, file_path: str, data_summary: str = None, timestamp: str = None) -> bool:
        """记录图表生成信息"""
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO chart_records (timestamp, chart_type, file_path, data_summary)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, chart_type, file_path, data_summary))
                conn.commit()
                
            logger.info(f"✅ 记录图表生成: {chart_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 记录图表生成失败: {e}")
            return False
    
    def get_keyword_history(self, days: int = 7, keyword: str = None) -> pd.DataFrame:
        """获取关键词历史数据"""
        try:
            start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                if keyword:
                    query = '''
                        SELECT timestamp, keyword, count, category
                        FROM keyword_history 
                        WHERE timestamp >= ? AND keyword = ?
                        ORDER BY timestamp
                    '''
                    df = pd.read_sql_query(query, conn, params=(start_date, keyword))
                else:
                    query = '''
                        SELECT timestamp, keyword, count, category
                        FROM keyword_history 
                        WHERE timestamp >= ?
                        ORDER BY timestamp, count DESC
                    '''
                    df = pd.read_sql_query(query, conn, params=(start_date,))
                
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                return df
                
        except Exception as e:
            logger.error(f"❌ 获取关键词历史失败: {e}")
            return pd.DataFrame()
    
    def get_category_trends(self, days: int = 7) -> pd.DataFrame:
        """获取分类趋势数据"""
        try:
            start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT timestamp, category, count, percentage
                    FROM category_stats 
                    WHERE timestamp >= ?
                    ORDER BY timestamp, count DESC
                '''
                df = pd.read_sql_query(query, conn, params=(start_date,))
                
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                return df
                
        except Exception as e:
            logger.error(f"❌ 获取分类趋势失败: {e}")
            return pd.DataFrame()
    
    def get_trending_keywords(self, days: int = 1, limit: int = 10) -> List[Tuple[str, int, float]]:
        """获取热门关键词（关键词，总提及数，增长率）"""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                # 获取时间段内的关键词统计
                query = '''
                    SELECT keyword, SUM(count) as total_count, AVG(count) as avg_count
                    FROM keyword_history 
                    WHERE timestamp >= ? AND timestamp <= ?
                    GROUP BY keyword
                    ORDER BY total_count DESC
                    LIMIT ?
                '''
                cursor = conn.cursor()
                results = cursor.execute(query, (start_date.isoformat(), end_date.isoformat(), limit)).fetchall()
                
                trending = []
                for keyword, total_count, avg_count in results:
                    # 简单的增长率计算（这里可以改进为更复杂的趋势分析）
                    growth_rate = total_count / max(avg_count, 1) - 1
                    trending.append((keyword, total_count, growth_rate))
                
                return trending
                
        except Exception as e:
            logger.error(f"❌ 获取热门关键词失败: {e}")
            return []
    
    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 统计关键词数据
                cursor.execute('SELECT COUNT(*) FROM keyword_history')
                keyword_records = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT keyword) FROM keyword_history')
                unique_keywords = cursor.fetchone()[0]
                
                # 统计趋势数据
                cursor.execute('SELECT COUNT(*) FROM trend_data')
                trend_records = cursor.fetchone()[0]
                
                # 统计图表数据
                cursor.execute('SELECT COUNT(*) FROM chart_records')
                chart_records = cursor.fetchone()[0]
                
                # 获取最新数据时间
                cursor.execute('SELECT MAX(timestamp) FROM keyword_history')
                latest_data = cursor.fetchone()[0]
                
                summary = {
                    "keyword_records": keyword_records,
                    "unique_keywords": unique_keywords,
                    "trend_records": trend_records,
                    "chart_records": chart_records,
                    "latest_data_time": latest_data,
                    "database_file": str(self.db_path),
                    "data_directory": str(self.data_dir)
                }
                
                return summary
                
        except Exception as e:
            logger.error(f"❌ 获取数据摘要失败: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """清理旧数据"""
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 删除旧的关键词历史
                cursor.execute('DELETE FROM keyword_history WHERE timestamp < ?', (cutoff_date,))
                deleted_keywords = cursor.rowcount
                
                # 删除旧的趋势数据
                cursor.execute('DELETE FROM trend_data WHERE timestamp < ?', (cutoff_date,))
                deleted_trends = cursor.rowcount
                
                # 删除旧的分类统计
                cursor.execute('DELETE FROM category_stats WHERE timestamp < ?', (cutoff_date,))
                deleted_categories = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"✅ 清理完成: 删除 {deleted_keywords} 个关键词记录, {deleted_trends} 个趋势记录, {deleted_categories} 个分类记录")
                return True
                
        except Exception as e:
            logger.error(f"❌ 清理旧数据失败: {e}")
            return False
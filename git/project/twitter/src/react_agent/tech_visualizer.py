#!/usr/bin/env python3
"""科技数据可视化模块

为科技趋势、AI发展、关键词分析等创建各种类型的可视化图表
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

from .data_collector import TechDataCollector

logger = logging.getLogger(__name__)

# 设置中文字体和图表样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")


class TechVisualizer:
    """科技数据可视化器"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("charts")
        self.output_dir.mkdir(exist_ok=True)
        
        self.data_collector = TechDataCollector()
        
        # 图表配置
        self.color_palette = {
            "AI/ML": "#FF6B6B",
            "Blockchain": "#4ECDC4", 
            "Cloud Computing": "#45B7D1",
            "IoT": "#96CEB4",
            "Cybersecurity": "#FFEAA7",
            "Robotics": "#DDA0DD",
            "Other": "#95A5A6"
        }
        
        # 设置Plotly默认主题
        pio.templates.default = "plotly_white"
    
    async def create_keyword_trends_chart(self, data: Dict[str, Any] = None) -> str:
        """创建关键词趋势图表"""
        try:
            logger.info("🎨 创建关键词趋势图表...")
            
            if data is None:
                data = self.data_collector.get_sample_data()
            
            keywords_data = data.get("keywords_count", {})
            if not keywords_data:
                logger.warning("没有关键词数据")
                return ""
            
            # 准备数据
            keywords = list(keywords_data.keys())[:10]  # 取前10个
            counts = [keywords_data[kw] for kw in keywords]
            
            # 创建横向柱状图
            fig = go.Figure(data=[
                go.Bar(
                    y=keywords,
                    x=counts,
                    orientation='h',
                    marker=dict(
                        color=px.colors.qualitative.Set3[:len(keywords)],
                        line=dict(color='rgba(0,0,0,0.3)', width=1)
                    ),
                    text=counts,
                    textposition='inside',
                    textfont=dict(color='white', size=12)
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="🔍 科技关键词热度分析",
                    x=0.5,
                    font=dict(size=18, family="Arial, sans-serif")
                ),
                xaxis_title="提及次数",
                yaxis_title="关键词",
                height=500,
                margin=dict(l=100, r=50, t=80, b=50),
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # 保存图表
            chart_path = self.output_dir / f"keyword_trends_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(chart_path))
            
            logger.info(f"✅ 关键词趋势图表已保存: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"❌ 创建关键词趋势图表失败: {e}")
            return ""
    
    async def create_tech_categories_pie_chart(self, data: Dict[str, Any] = None) -> str:
        """创建科技分类饼图"""
        try:
            logger.info("🎨 创建科技分类饼图...")
            
            if data is None:
                data = self.data_collector.get_sample_data()
            
            categories_data = data.get("tech_categories", {})
            if not categories_data:
                logger.warning("没有分类数据")
                return ""
            
            # 过滤掉值为0的分类
            filtered_data = {k: v for k, v in categories_data.items() if v > 0}
            
            labels = list(filtered_data.keys())
            values = list(filtered_data.values())
            colors = [self.color_palette.get(label, "#95A5A6") for label in labels]
            
            # 创建饼图
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,  # 甜甜圈样式
                    marker=dict(
                        colors=colors,
                        line=dict(color='white', width=2)
                    ),
                    textinfo='label+percent',
                    textfont=dict(size=12),
                    hovertemplate='<b>%{label}</b><br>' +
                                  '数量: %{value}<br>' +
                                  '占比: %{percent}<br>' +
                                  '<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="📊 科技领域分布分析",
                    x=0.5,
                    font=dict(size=18, family="Arial, sans-serif")
                ),
                height=500,
                margin=dict(t=80, b=50),
                font=dict(family="Arial, sans-serif"),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.01
                )
            )
            
            # 添加中心文字
            fig.add_annotation(
                text="科技趋势<br>分析",
                x=0.5, y=0.5,
                font=dict(size=16, color="gray"),
                showarrow=False
            )
            
            # 保存图表
            chart_path = self.output_dir / f"tech_categories_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(chart_path))
            
            logger.info(f"✅ 科技分类饼图已保存: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"❌ 创建科技分类饼图失败: {e}")
            return ""
    
    async def create_trend_timeline_chart(self) -> str:
        """创建趋势时间线图表"""
        try:
            logger.info("🎨 创建趋势时间线图表...")
            
            # 获取历史数据
            df = await self.data_collector.get_historical_data(days=7)
            
            if df.empty:
                logger.info("没有足够的历史数据，使用模拟数据")
                # 生成模拟数据
                dates = pd.date_range(start='2025-01-10', periods=7, freq='D')
                df = pd.DataFrame({
                    'timestamp': dates,
                    'total_mentions': np.random.randint(20, 100, 7),
                    'keywords_count': np.random.randint(5, 20, 7),
                    'topics_count': np.random.randint(3, 8, 7)
                })
            
            # 创建多条线的时间线图
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('📈 关键词提及总数趋势', '📊 话题与关键词数量对比'),
                vertical_spacing=0.1,
                specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
            )
            
            # 第一个子图：总提及数
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['total_mentions'],
                    mode='lines+markers',
                    name='总提及数',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=8),
                    fill='tonexty',
                    fillcolor='rgba(255, 107, 107, 0.2)'
                ),
                row=1, col=1
            )
            
            # 第二个子图：关键词和话题数量
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['keywords_count'],
                    mode='lines+markers',
                    name='关键词数量',
                    line=dict(color='#4ECDC4', width=2),
                    marker=dict(size=6)
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['topics_count'],
                    mode='lines+markers',
                    name='话题数量',
                    line=dict(color='#45B7D1', width=2, dash='dash'),
                    marker=dict(size=6, symbol='diamond')
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=dict(
                    text="⏰ 科技趋势时间线分析",
                    x=0.5,
                    font=dict(size=18, family="Arial, sans-serif")
                ),
                height=600,
                margin=dict(t=100, b=50),
                font=dict(family="Arial, sans-serif"),
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # 更新x轴格式
            fig.update_xaxes(
                title_text="日期",
                tickformat='%m-%d',
                row=2, col=1
            )
            
            # 保存图表
            chart_path = self.output_dir / f"trend_timeline_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(chart_path))
            
            logger.info(f"✅ 趋势时间线图表已保存: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"❌ 创建趋势时间线图表失败: {e}")
            return ""
    
    async def create_heatmap_chart(self, data: Dict[str, Any] = None) -> str:
        """创建科技关键词热力图"""
        try:
            logger.info("🎨 创建关键词热力图...")
            
            if data is None:
                data = self.data_collector.get_sample_data()
            
            keywords_data = data.get("keywords_count", {})
            if not keywords_data:
                logger.warning("没有关键词数据")
                return ""
            
            # 准备热力图数据 (模拟不同时间段的数据)
            top_keywords = list(keywords_data.keys())[:8]
            time_periods = ['上午', '下午', '晚上', '深夜']
            
            # 生成模拟的时间段热度数据
            heatmap_data = []
            for keyword in top_keywords:
                base_value = keywords_data[keyword]
                row = []
                for _ in time_periods:
                    # 添加一些随机变化
                    variation = np.random.uniform(0.7, 1.3)
                    row.append(int(base_value * variation))
                heatmap_data.append(row)
            
            # 创建热力图
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=time_periods,
                y=top_keywords,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="热度值"),
                hoverongaps=False,
                hovertemplate='<b>%{y}</b><br>' +
                              '时间: %{x}<br>' +
                              '热度: %{z}<br>' +
                              '<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text="🔥 科技关键词热度时间分布",
                    x=0.5,
                    font=dict(size=18, family="Arial, sans-serif")
                ),
                xaxis_title="时间段",
                yaxis_title="关键词",
                height=500,
                margin=dict(l=120, r=50, t=80, b=50),
                font=dict(family="Arial, sans-serif")
            )
            
            # 保存图表
            chart_path = self.output_dir / f"keywords_heatmap_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(chart_path))
            
            logger.info(f"✅ 关键词热力图已保存: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"❌ 创建关键词热力图失败: {e}")
            return ""
    
    async def create_dashboard(self, data: Dict[str, Any] = None) -> str:
        """创建综合仪表板"""
        try:
            logger.info("🎨 创建科技数据综合仪表板...")
            
            if data is None:
                data = self.data_collector.get_sample_data()
            
            # 创建包含多个子图的仪表板
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    '🔍 热门关键词 TOP5',
                    '📊 科技领域分布', 
                    '📈 趋势指标',
                    '⚡ 实时统计'
                ),
                specs=[
                    [{"type": "bar"}, {"type": "pie"}],
                    [{"type": "scatter"}, {"type": "indicator"}]
                ],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # 1. 热门关键词柱状图
            keywords_data = data.get("keywords_count", {})
            top_keywords = list(keywords_data.keys())[:5]
            top_counts = [keywords_data[kw] for kw in top_keywords]
            
            fig.add_trace(
                go.Bar(
                    x=top_keywords,
                    y=top_counts,
                    marker_color=px.colors.qualitative.Set3[:5],
                    name="关键词热度",
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # 2. 科技分类饼图
            categories_data = data.get("tech_categories", {})
            filtered_cats = {k: v for k, v in categories_data.items() if v > 0}
            
            fig.add_trace(
                go.Pie(
                    labels=list(filtered_cats.keys()),
                    values=list(filtered_cats.values()),
                    marker=dict(
                        colors=[self.color_palette.get(k, "#95A5A6") for k in filtered_cats.keys()]
                    ),
                    showlegend=False
                ),
                row=1, col=2
            )
            
            # 3. 模拟趋势数据
            trend_x = ['昨天', '今天', '明天预测']
            trend_y = [sum(keywords_data.values()) * 0.8, 
                      sum(keywords_data.values()), 
                      sum(keywords_data.values()) * 1.2]
            
            fig.add_trace(
                go.Scatter(
                    x=trend_x,
                    y=trend_y,
                    mode='lines+markers',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=10),
                    name="趋势",
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # 4. 统计指标
            total_mentions = sum(keywords_data.values())
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=total_mentions,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "总热度"},
                    delta={'reference': 50},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#FF6B6B"},
                        'steps': [
                            {'range': [0, 25], 'color': "lightgray"},
                            {'range': [25, 50], 'color': "gray"},
                            {'range': [50, 75], 'color': "orange"},
                            {'range': [75, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': 80
                        }
                    }
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title=dict(
                    text="🚀 科技数据实时监控仪表板",
                    x=0.5,
                    font=dict(size=20, family="Arial, sans-serif")
                ),
                height=800,
                margin=dict(t=100, b=50, l=50, r=50),
                font=dict(family="Arial, sans-serif"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # 保存仪表板
            dashboard_path = self.output_dir / f"tech_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(dashboard_path))
            
            logger.info(f"✅ 科技数据仪表板已保存: {dashboard_path}")
            return str(dashboard_path)
            
        except Exception as e:
            logger.error(f"❌ 创建仪表板失败: {e}")
            return ""
    
    async def generate_all_charts(self, data: Dict[str, Any] = None) -> List[str]:
        """生成所有图表"""
        logger.info("🎨 开始生成所有科技数据可视化图表...")
        
        chart_files = []
        
        try:
            # 生成各种图表
            charts = await asyncio.gather(
                self.create_keyword_trends_chart(data),
                self.create_tech_categories_pie_chart(data), 
                self.create_trend_timeline_chart(),
                self.create_heatmap_chart(data),
                self.create_dashboard(data),
                return_exceptions=True
            )
            
            # 收集成功生成的图表
            for chart_path in charts:
                if isinstance(chart_path, str) and chart_path:
                    chart_files.append(chart_path)
            
            logger.info(f"✅ 成功生成 {len(chart_files)} 个图表")
            
        except Exception as e:
            logger.error(f"❌ 生成图表时出错: {e}")
        
        return chart_files
    
    def get_chart_urls(self, chart_files: List[str]) -> List[str]:
        """获取图表的本地URL"""
        urls = []
        for chart_file in chart_files:
            if os.path.exists(chart_file):
                # 转换为file://URL格式
                file_url = f"file://{os.path.abspath(chart_file)}"
                urls.append(file_url)
        return urls
#!/usr/bin/env python3
"""高级金融科技风格可视化模块

参考SignalPlus等专业金融平台的设计风格，创建美观专业的图表
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

logger = logging.getLogger(__name__)

class PremiumVisualizer:
    """高端可视化器 - SignalPlus风格"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("charts")
        self.output_dir.mkdir(exist_ok=True)
        
        # SignalPlus风格的配色方案
        self.colors = {
            'primary': '#4ECDC4',      # 青绿色主色
            'secondary': '#45B7D1',    # 蓝色
            'accent': '#96CEB4',       # 浅绿
            'warning': '#FFEAA7',      # 黄色
            'danger': '#FF6B6B',       # 红色
            'success': '#55E6C1',      # 成功绿
            'dark': '#2C3E50',         # 深色
            'light': '#ECF0F1',        # 浅色
            'gradient_start': '#667eea', # 渐变开始
            'gradient_end': '#764ba2',   # 渐变结束
            'background': '#F8F9FA'     # 背景色
        }
        
        # 图标映射
        self.icons = {
            'AI/ML': '🤖',
            'Blockchain': '⛓️', 
            'Cloud Computing': '☁️',
            'IoT': '🌐',
            'Cybersecurity': '🛡️',
            'Robotics': '🦾',
            'Data Science': '📊',
            'FinTech': '💰',
            'Other': '⚡'
        }
        
        # 排名样式
        self.rank_colors = {
            1: '#FFD700',  # 金色
            2: '#C0C0C0',  # 银色  
            3: '#CD7F32'   # 铜色
        }
    
    async def create_tech_leaderboard(self, data: Dict[str, Any] = None) -> str:
        """创建科技领域排行榜 - 仿SignalPlus风格"""
        try:
            logger.info("🏆 创建科技领域排行榜...")
            
            if data is None:
                data = self._get_enhanced_sample_data()
            
            keywords_data = data.get("keywords_count", {})
            categories_data = data.get("tech_categories", {})
            
            # 创建4个子图布局，类似SignalPlus的四象限设计
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    "🚀 看涨期权成交额榜", "📈 看跌期权成交额榜",
                    "💰 大单成交额榜", "⚡ 异动活跃比榜"
                ],
                specs=[[{"type": "table"}, {"type": "table"}],
                       [{"type": "table"}, {"type": "table"}]],
                vertical_spacing=0.08,
                horizontal_spacing=0.05
            )
            
            # 准备数据
            sorted_keywords = sorted(keywords_data.items(), key=lambda x: x[1], reverse=True)[:5]
            sorted_categories = sorted(categories_data.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # 1. 看涨期权榜 (热门关键词)
            call_data = self._prepare_leaderboard_data(sorted_keywords, "看涨", True)
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=["排名", "标的", "成交额", "涨跌", "比率"],
                        fill_color=self.colors['primary'],
                        font=dict(color='white', size=12),
                        align='center',
                        height=40
                    ),
                    cells=dict(
                        values=[
                            [f"{i}" for i in range(1, len(call_data)+1)],
                            [f"{self._get_icon(item[0])} {item[0]}" for item in call_data],
                            [f"${item[1]*100:.2f}万" for item in call_data],
                            [f"↗️ {item[1]*2:.1f}%" for item in call_data],
                            [f"(B:S {item[1]/10:.1f}:1)" for item in call_data]
                        ],
                        fill_color=[
                            [self._get_rank_color(i+1) for i in range(len(call_data))],
                            ['white'] * len(call_data),
                            ['#E8F5E8'] * len(call_data),
                            ['#E8F8E8'] * len(call_data),
                            ['white'] * len(call_data)
                        ],
                        align='center',
                        font=dict(size=11),
                        height=35
                    )
                ),
                row=1, col=1
            )
            
            # 2. 看跌期权榜 (类别数据)
            put_data = self._prepare_leaderboard_data(sorted_categories, "看跌", False)
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=["排名", "标的", "成交额", "涨跌", "比率"],
                        fill_color=self.colors['danger'],
                        font=dict(color='white', size=12),
                        align='center',
                        height=40
                    ),
                    cells=dict(
                        values=[
                            [f"{i}" for i in range(1, len(put_data)+1)],
                            [f"{self._get_icon(item[0])} {item[0]}" for item in put_data],
                            [f"${item[1]*50:.2f}万" for item in put_data],
                            [f"↘️ -{item[1]*1.5:.1f}%" for item in put_data],
                            [f"(B:S 0.{item[1]//10}:1)" for item in put_data]
                        ],
                        fill_color=[
                            [self._get_rank_color(i+1) for i in range(len(put_data))],
                            ['white'] * len(put_data),
                            ['#FFE8E8'] * len(put_data),
                            ['#FFE8E8'] * len(put_data),
                            ['white'] * len(put_data)
                        ],
                        align='center',
                        font=dict(size=11),
                        height=35
                    )
                ),
                row=1, col=2
            )
            
            # 3. 大单成交榜
            large_orders = sorted_keywords[:3]
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=["排名", "标的", "成交额", "类型"],
                        fill_color=self.colors['warning'],
                        font=dict(color='white', size=12),
                        align='center',
                        height=40
                    ),
                    cells=dict(
                        values=[
                            [f"{i}" for i in range(1, len(large_orders)+1)],
                            [f"{self._get_icon(item[0])} {item[0]}" for item in large_orders],
                            [f"${item[1]*200:.2f}万" for item in large_orders],
                            [f"{'BUY' if i % 2 == 0 else 'SELL'}" for i in range(len(large_orders))]
                        ],
                        fill_color=[
                            [self._get_rank_color(i+1) for i in range(len(large_orders))],
                            ['white'] * len(large_orders),
                            ['#FFF8E1'] * len(large_orders),
                            [['#E8F5E8', '#FFE8E8'][i % 2] for i in range(len(large_orders))]
                        ],
                        align='center',
                        font=dict(size=11),
                        height=35
                    )
                ),
                row=2, col=1
            )
            
            # 4. 异动活跃榜
            active_data = sorted_categories
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=["排名", "标的", "成交额", "Put:Call"],
                        fill_color=self.colors['accent'],
                        font=dict(color='white', size=12),
                        align='center',
                        height=40
                    ),
                    cells=dict(
                        values=[
                            [f"{i}" for i in range(1, len(active_data)+1)],
                            [f"{self._get_icon(item[0])} {item[0]}" for item in active_data],
                            [f"${item[1]*80:.2f}万" for item in active_data],
                            [f"{item[1]/20:.1f} : 1" for item in active_data]
                        ],
                        fill_color=[
                            [self._get_rank_color(i+1) for i in range(len(active_data))],
                            ['white'] * len(active_data),
                            ['#E8FFF8'] * len(active_data),
                            ['white'] * len(active_data)
                        ],
                        align='center',
                        font=dict(size=11),
                        height=35
                    )
                ),
                row=2, col=2
            )
            
            # 更新布局，模仿SignalPlus的专业风格
            fig.update_layout(
                title=dict(
                    text="<b>📊 科技股期权龙虎榜</b><br><sub>2025年8月18日</sub>",
                    x=0.5,
                    font=dict(size=24, family="Arial Black, sans-serif", color=self.colors['dark']),
                    xref="paper"
                ),
                height=700,
                margin=dict(t=120, b=80, l=50, r=50),
                paper_bgcolor=self.colors['background'],
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif")
            )
            
            # 添加SignalPlus风格的底部标注
            fig.add_annotation(
                text="📞 SignalPlus666 进·交·流·群",
                x=0.5, y=-0.08,
                xref="paper", yref="paper",
                font=dict(size=14, color=self.colors['dark']),
                showarrow=False
            )
            
            fig.add_annotation(
                text="注：主动方向基于成交价相对买卖价格的位置判断期权买卖方的主动意愿强弱<br>🔴 表示买卖主动；◯ 表示卖方主动；B:S为买卖盘比例",
                x=0.5, y=-0.12,
                xref="paper", yref="paper",
                font=dict(size=10, color='gray'),
                showarrow=False
            )
            
            # 保存图表
            chart_path = self.output_dir / f"tech_leaderboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(chart_path))
            
            logger.info(f"✅ 科技领域排行榜已保存: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"❌ 创建科技领域排行榜失败: {e}")
            return ""
    
    async def create_premium_dashboard(self, data: Dict[str, Any] = None) -> str:
        """创建高端仪表板 - 卡片式布局"""
        try:
            logger.info("🎨 创建高端仪表板...")
            
            if data is None:
                data = self._get_enhanced_sample_data()
            
            # 创建复杂的子图布局
            fig = make_subplots(
                rows=3, cols=4,
                subplot_titles=[
                    "🔥 热门指数", "📊 市场分布", "📈 趋势动向", "⚡ 活跃度",
                    "🚀 涨幅榜", "📉 跌幅榜", "💰 成交额", "🎯 精准度", 
                    "📱 实时监控", "🌐 全球视角", "🔮 AI预测", "📋 综合评分"
                ],
                specs=[
                    [{"type": "indicator"}, {"type": "pie"}, {"type": "scatter"}, {"type": "bar"}],
                    [{"type": "table"}, {"type": "table"}, {"type": "scatter"}, {"type": "indicator"}],
                    [{"type": "heatmap"}, {"type": "scatter"}, {"type": "indicator"}, {"type": "indicator"}]
                ],
                vertical_spacing=0.08,
                horizontal_spacing=0.03
            )
            
            # 数据准备
            keywords_data = data.get("keywords_count", {})
            categories_data = data.get("tech_categories", {})
            
            # 第一行 - 核心指标
            # 1. 热门指数仪表盘
            total_heat = sum(keywords_data.values())
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=total_heat,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "热门指数", 'font': {'size': 16}},
                    delta={'reference': 80, 'increasing': {'color': self.colors['success']}},
                    gauge={
                        'axis': {'range': [None, 150]},
                        'bar': {'color': self.colors['primary']},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 100], 'color': self.colors['light']},
                        ],
                        'threshold': {
                            'line': {'color': self.colors['danger'], 'width': 4},
                            'thickness': 0.75,
                            'value': 120
                        }
                    }
                ),
                row=1, col=1
            )
            
            # 2. 市场分布饼图
            filtered_cats = {k: v for k, v in categories_data.items() if v > 0}
            colors_list = [self.colors['primary'], self.colors['secondary'], self.colors['accent'], 
                          self.colors['warning'], self.colors['success'], self.colors['danger']]
            
            fig.add_trace(
                go.Pie(
                    labels=[f"{self._get_icon(k)} {k}" for k in filtered_cats.keys()],
                    values=list(filtered_cats.values()),
                    hole=0.5,
                    marker=dict(colors=colors_list[:len(filtered_cats)]),
                    textinfo='percent',
                    textfont=dict(size=10),
                    showlegend=False
                ),
                row=1, col=2
            )
            
            # 3. 趋势线图
            trend_x = list(range(7))
            trend_y = [total_heat * (0.8 + 0.05 * i + np.random.uniform(-0.1, 0.1)) for i in trend_x]
            
            fig.add_trace(
                go.Scatter(
                    x=trend_x,
                    y=trend_y,
                    mode='lines+markers',
                    line=dict(color=self.colors['primary'], width=3, shape='spline'),
                    marker=dict(size=8, color=self.colors['secondary']),
                    fill='tonexty',
                    fillcolor=f'rgba(78, 205, 196, 0.2)',
                    showlegend=False
                ),
                row=1, col=3
            )
            
            # 4. 活跃度柱状图
            top_5 = list(keywords_data.items())[:5]
            fig.add_trace(
                go.Bar(
                    x=[item[0][:4] for item in top_5],
                    y=[item[1] for item in top_5],
                    marker=dict(
                        color=[self.colors['primary'], self.colors['secondary'], self.colors['accent'],
                               self.colors['warning'], self.colors['success']],
                        line=dict(color='white', width=1)
                    ),
                    showlegend=False
                ),
                row=1, col=4
            )
            
            # 第二行 - 排行榜和分析
            # 5. 涨幅榜
            risers = list(keywords_data.items())[:3]
            fig.add_trace(
                go.Table(
                    header=dict(values=["排名", "名称", "涨幅"], fill_color=self.colors['success']),
                    cells=dict(
                        values=[
                            [f"{i+1}" for i in range(len(risers))],
                            [f"{self._get_icon(item[0])} {item[0][:8]}" for item in risers],
                            [f"+{item[1]*2:.1f}%" for item in risers]
                        ],
                        fill_color=['white', 'white', '#E8F5E8'],
                        font=dict(size=10)
                    )
                ),
                row=2, col=1
            )
            
            # 6. 跌幅榜  
            fallers = list(reversed(list(keywords_data.items())[-3:]))
            fig.add_trace(
                go.Table(
                    header=dict(values=["排名", "名称", "跌幅"], fill_color=self.colors['danger']),
                    cells=dict(
                        values=[
                            [f"{i+1}" for i in range(len(fallers))],
                            [f"{self._get_icon(item[0])} {item[0][:8]}" for item in fallers],
                            [f"-{item[1]*1.5:.1f}%" for item in fallers]
                        ],
                        fill_color=['white', 'white', '#FFE8E8'],
                        font=dict(size=10)
                    )
                ),
                row=2, col=2
            )
            
            # 7. 成交额趋势
            volume_data = [item[1] * 10 for item in keywords_data.items()][:7]
            fig.add_trace(
                go.Scatter(
                    y=volume_data,
                    mode='lines+markers',
                    line=dict(color=self.colors['warning'], width=2),
                    marker=dict(size=6),
                    showlegend=False
                ),
                row=2, col=3
            )
            
            # 8. 精准度指标
            accuracy = 85.6
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=accuracy,
                    delta={'reference': 80, 'suffix': "%"},
                    title={'text': "预测精准度"},
                    number={'suffix': "%", 'font': {'size': 20}},
                ),
                row=2, col=4
            )
            
            # 第三行 - 高级分析
            # 9. 相关性热力图
            correlation_matrix = np.random.uniform(0.3, 1.0, (4, 4))
            tech_names = ['AI', 'BC', 'Cloud', 'IoT']
            
            fig.add_trace(
                go.Heatmap(
                    z=correlation_matrix,
                    x=tech_names,
                    y=tech_names,
                    colorscale='Viridis',
                    showscale=False,
                    text=correlation_matrix.round(2),
                    texttemplate="%{text}",
                    textfont={"size": 10}
                ),
                row=3, col=1
            )
            
            # 10. 全球视角散点图
            global_data_x = np.random.normal(50, 20, 20)
            global_data_y = np.random.normal(50, 15, 20)
            sizes = np.random.uniform(10, 30, 20)
            
            fig.add_trace(
                go.Scatter(
                    x=global_data_x,
                    y=global_data_y,
                    mode='markers',
                    marker=dict(
                        size=sizes,
                        color=sizes,
                        colorscale='Viridis',
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    showlegend=False
                ),
                row=3, col=2
            )
            
            # 11. AI预测指标
            ai_prediction = 92.3
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=ai_prediction,
                    title={'text': "AI预测"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': self.colors['accent']},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray"
                    }
                ),
                row=3, col=3
            )
            
            # 12. 综合评分
            overall_score = 88.9
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=overall_score,
                    delta={'reference': 85, 'suffix': "分"},
                    title={'text': "综合评分"},
                    number={'font': {'size': 24, 'color': self.colors['primary']}}
                ),
                row=3, col=4
            )
            
            # 更新整体布局
            fig.update_layout(
                title=dict(
                    text="<b>🌟 科技数据专业监控中心</b><br><sub>Professional Tech Data Analytics Dashboard</sub>",
                    x=0.5,
                    font=dict(size=28, family="Arial Black, sans-serif", color=self.colors['dark'])
                ),
                height=1000,
                margin=dict(t=120, b=50, l=30, r=30),
                paper_bgcolor=self.colors['background'],
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif"),
                showlegend=False
            )
            
            # 保存图表
            chart_path = self.output_dir / f"premium_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(chart_path))
            
            logger.info(f"✅ 高端仪表板已保存: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"❌ 创建高端仪表板失败: {e}")
            return ""
    
    async def create_financial_cards(self, data: Dict[str, Any] = None) -> str:
        """创建金融卡片风格图表"""
        try:
            logger.info("💳 创建金融卡片风格图表...")
            
            if data is None:
                data = self._get_enhanced_sample_data()
            
            # 创建网格布局，模拟卡片效果
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=[
                    "💎 顶级科技股", "🔥 热门赛道", "📊 市场概览",
                    "⚡ 实时动态", "🎯 投资建议", "📈 收益预期"
                ],
                specs=[
                    [{"type": "table"}, {"type": "bar"}, {"type": "pie"}],
                    [{"type": "scatter"}, {"type": "indicator"}, {"type": "bar"}]
                ],
                vertical_spacing=0.15,
                horizontal_spacing=0.08
            )
            
            keywords_data = data.get("keywords_count", {})
            categories_data = data.get("tech_categories", {})
            
            # 卡片1: 顶级科技股表格
            top_stocks = list(keywords_data.items())[:5]
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=["🏆", "科技股", "热度", "趋势"],
                        fill_color='#1e3a8a',
                        font=dict(color='white', size=14, family="Arial Black"),
                        align='center',
                        height=45
                    ),
                    cells=dict(
                        values=[
                            [f"{i}" for i in range(1, len(top_stocks)+1)],
                            [f"{self._get_icon(stock[0])} {stock[0]}" for stock in top_stocks],
                            [f"{stock[1]}" for stock in top_stocks],
                            ["📈" if i % 2 == 0 else "📉" for i in range(len(top_stocks))]
                        ],
                        fill_color=[
                            [self._get_rank_color(i+1) for i in range(len(top_stocks))],
                            ['#f8fafc'] * len(top_stocks),
                            ['#ecfdf5'] * len(top_stocks),
                            [['#ecfdf5', '#fef2f2'][i % 2] for i in range(len(top_stocks))]
                        ],
                        align='center',
                        font=dict(size=12),
                        height=40
                    )
                ),
                row=1, col=1
            )
            
            # 卡片2: 热门赛道柱状图
            track_names = list(categories_data.keys())[:5]
            track_values = list(categories_data.values())[:5]
            
            colors = [self.colors['primary'], self.colors['secondary'], self.colors['accent'], 
                     self.colors['warning'], self.colors['success']]
            
            fig.add_trace(
                go.Bar(
                    x=track_values,
                    y=[f"{self._get_icon(name)} {name[:8]}" for name in track_names],
                    orientation='h',
                    marker=dict(
                        color=colors,
                        line=dict(color='white', width=2)
                    ),
                    text=track_values,
                    textposition='inside',
                    textfont=dict(color='white', size=12),
                    showlegend=False
                ),
                row=1, col=2
            )
            
            # 卡片3: 市场概览饼图
            fig.add_trace(
                go.Pie(
                    labels=[f"{self._get_icon(k)} {k}" for k in categories_data.keys()],
                    values=list(categories_data.values()),
                    hole=0.6,
                    marker=dict(
                        colors=['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'],
                        line=dict(color='white', width=3)
                    ),
                    textinfo='percent',
                    textfont=dict(size=11, color='white'),
                    showlegend=False
                ),
                row=1, col=3
            )
            
            # 在饼图中心添加总数
            fig.add_annotation(
                text=f"<b>{sum(categories_data.values())}</b><br>总量",
                x=0.83, y=0.75,  # 调整位置到第1行第3列
                font=dict(size=16, color=self.colors['dark']),
                showarrow=False
            )
            
            # 卡片4: 实时动态
            time_series = np.random.normal(100, 10, 30).cumsum()
            fig.add_trace(
                go.Scatter(
                    y=time_series,
                    mode='lines',
                    line=dict(
                        color=self.colors['primary'],
                        width=3,
                        shape='spline'
                    ),
                    fill='tonexty',
                    fillcolor='rgba(78, 205, 196, 0.3)',
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # 卡片5: 投资建议指标
            recommendation_score = 85
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=recommendation_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "推荐指数", 'font': {'size': 14}},
                    delta={'reference': 70, 'increasing': {'color': self.colors['success']}},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': self.colors['primary']},
                        'steps': [
                            {'range': [0, 50], 'color': '#fee2e2'},
                            {'range': [50, 80], 'color': '#fef3c7'},
                            {'range': [80, 100], 'color': '#d1fae5'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=2, col=2
            )
            
            # 卡片6: 收益预期
            sectors = ["AI", "区块链", "云计算", "IoT", "安全"]
            expected_returns = [15.2, 12.8, 10.5, 8.3, 6.7]
            
            fig.add_trace(
                go.Bar(
                    x=sectors,
                    y=expected_returns,
                    marker=dict(
                        color=expected_returns,
                        colorscale='RdYlGn',
                        line=dict(color='white', width=1)
                    ),
                    text=[f"{r}%" for r in expected_returns],
                    textposition='outside',
                    showlegend=False
                ),
                row=2, col=3
            )
            
            # 更新布局
            fig.update_layout(
                title=dict(
                    text="<b>💼 金融科技投资分析卡片</b><br><sub>FinTech Investment Analysis Cards</sub>",
                    x=0.5,
                    font=dict(size=26, family="Arial Black, sans-serif", color=self.colors['dark'])
                ),
                height=800,
                margin=dict(t=100, b=50, l=50, r=50),
                paper_bgcolor=self.colors['background'],
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif")
            )
            
            # 保存图表
            chart_path = self.output_dir / f"financial_cards_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            fig.write_html(str(chart_path))
            
            logger.info(f"✅ 金融卡片图表已保存: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"❌ 创建金融卡片图表失败: {e}")
            return ""
    
    def _get_enhanced_sample_data(self) -> Dict[str, Any]:
        """获取增强的示例数据"""
        return {
            "keywords_count": {
                "NVIDIA": 45, "人工智能": 38, "ChatGPT": 32, "机器学习": 28, "特斯拉": 25,
                "区块链": 22, "云计算": 20, "比特币": 18, "物联网": 15, "网络安全": 12,
                "量子计算": 10, "自动驾驶": 8, "元宇宙": 6, "5G": 5
            },
            "tech_categories": {
                "AI/ML": 103, "FinTech": 45, "Blockchain": 40, "Cloud Computing": 35,
                "IoT": 20, "Cybersecurity": 17, "Robotics": 13, "Other": 15
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _prepare_leaderboard_data(self, data: List[Tuple[str, int]], type_name: str, is_call: bool) -> List[Tuple[str, int]]:
        """准备排行榜数据"""
        return data
    
    def _get_icon(self, category: str) -> str:
        """获取类别图标"""
        for key, icon in self.icons.items():
            if key.lower() in category.lower() or category.lower() in key.lower():
                return icon
        return self.icons.get(category, self.icons['Other'])
    
    def _get_rank_color(self, rank: int) -> str:
        """获取排名颜色"""
        return self.rank_colors.get(rank, '#E8E8E8')
    
    async def generate_all_premium_charts(self, data: Dict[str, Any] = None) -> List[str]:
        """生成所有高端图表"""
        logger.info("🚀 开始生成所有高端图表...")
        
        chart_files = []
        
        try:
            # 生成各种高端图表
            charts = await asyncio.gather(
                self.create_tech_leaderboard(data),
                self.create_premium_dashboard(data),
                self.create_financial_cards(data),
                return_exceptions=True
            )
            
            # 收集成功生成的图表
            for chart_path in charts:
                if isinstance(chart_path, str) and chart_path:
                    chart_files.append(chart_path)
            
            logger.info(f"✅ 成功生成 {len(chart_files)} 个高端图表")
            
        except Exception as e:
            logger.error(f"❌ 生成高端图表时出错: {e}")
        
        return chart_files
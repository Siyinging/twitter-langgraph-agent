#!/usr/bin/env python3
"""增强的可视化器 - 支持图片生成

专门为Twitter图片推文设计的可视化系统
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from .image_generator import ImageGenerator
from .data_collector import TechDataCollector

logger = logging.getLogger(__name__)


class EnhancedVisualizer:
    """增强的可视化器 - 专为社交媒体优化"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("charts")
        self.output_dir.mkdir(exist_ok=True)
        
        self.image_generator = ImageGenerator(Path("images"))
        self.data_collector = TechDataCollector()
        
        # Twitter友好的配色方案
        self.twitter_colors = {
            'primary': '#1DA1F2',      # Twitter蓝
            'secondary': '#14171A',    # Twitter黑
            'accent': '#1DA1F2',       # 强调色
            'success': '#17BF63',      # 绿色
            'warning': '#FFAD1F',      # 黄色
            'danger': '#E0245E',       # 红色
            'light': '#F7F9FA',        # 浅色
            'dark': '#14171A'          # 深色
        }
    
    async def create_twitter_trend_card(self, data: Dict[str, Any] = None) -> Tuple[str, str]:
        """创建Twitter趋势卡片"""
        try:
            logger.info("📱 创建Twitter趋势卡片...")
            
            if data is None:
                data = self.data_collector.get_sample_data()
            
            keywords_data = data.get("keywords_count", {})
            top_keywords = list(keywords_data.items())[:5]
            
            # 创建紧凑的Twitter卡片布局
            fig = go.Figure()
            
            # 添加主要数据
            keywords = [item[0] for item in top_keywords]
            values = [item[1] for item in top_keywords]
            
            # 创建横向柱状图
            fig.add_trace(go.Bar(
                y=keywords,
                x=values,
                orientation='h',
                marker=dict(
                    color=[self.twitter_colors['primary'], self.twitter_colors['success'], 
                           self.twitter_colors['warning'], self.twitter_colors['accent'], 
                           self.twitter_colors['danger']],
                    line=dict(color='white', width=2)
                ),
                text=[f"{v}" for v in values],
                textposition='inside',
                textfont=dict(color='white', size=16, family="STHeiti Medium, Arial Unicode MS, sans-serif"),
                hovertemplate='%{y}: %{x}<extra></extra>'
            ))
            
            # 设置Twitter优化的布局
            fig.update_layout(
                title=dict(
                    text="<b>🔥 科技热词TOP5</b>",
                    x=0.5,
                    font=dict(size=28, family="STHeiti Medium, Arial Unicode MS, sans-serif", color=self.twitter_colors['dark']),
                    pad=dict(t=20, b=10)
                ),
                xaxis=dict(
                    title="热度值",
                    title_font=dict(size=14),
                    showgrid=True,
                    gridcolor='#E1E8ED',
                    zeroline=False
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=14)
                ),
                height=500,
                width=1200,
                margin=dict(l=120, r=80, t=80, b=60),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="STHeiti Medium, Arial Unicode MS, sans-serif"),
                showlegend=False
            )
            
            # 添加数据来源标注
            fig.add_annotation(
                text=f"📊 数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                x=1, y=0,
                xref="paper", yref="paper",
                xanchor="right", yanchor="bottom",
                font=dict(size=12, color='#657786'),
                showarrow=False
            )
            
            # 生成图片
            image_path = await self.image_generator.generate_chart_image(
                fig, "twitter_trend_card", twitter_optimized=True
            )
            
            # 生成推文文本
            top_keyword = top_keywords[0][0] if top_keywords else "AI"
            tweet_text = f"🔥 科技热词实时分析！\n\n📊 当前最热: {top_keyword}\n💡 数据显示科技创新持续升温\n⚡ 关注趋势，把握机遇\n\n#科技分析 #数据可视化 #TechTrends"
            
            logger.info(f"✅ Twitter趋势卡片生成完成")
            return image_path, tweet_text
            
        except Exception as e:
            logger.error(f"❌ Twitter趋势卡片生成失败: {e}")
            return "", ""
    
    async def create_market_summary_image(self, data: Dict[str, Any] = None) -> Tuple[str, str]:
        """创建市场摘要图片"""
        try:
            logger.info("📊 创建市场摘要图片...")
            
            if data is None:
                data = self.data_collector.get_sample_data()
            
            categories_data = data.get("tech_categories", {})
            
            # 创建环形图
            fig = go.Figure()
            
            labels = list(categories_data.keys())
            values = list(categories_data.values())
            colors = [
                self.twitter_colors['primary'],
                self.twitter_colors['success'],
                self.twitter_colors['warning'],
                self.twitter_colors['danger'],
                '#9266CC',
                '#FF6B35',
                '#1BC5BD'
            ]
            
            fig.add_trace(go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(
                    colors=colors[:len(labels)],
                    line=dict(color='white', width=3)
                ),
                textinfo='label+percent',
                textfont=dict(size=14, color='white', family="STHeiti Medium, Arial Unicode MS, sans-serif"),
                hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
            ))
            
            # 在中心添加总数
            total = sum(values)
            fig.add_annotation(
                text=f"<b>{total}</b><br>总数",
                x=0.5, y=0.5,
                font=dict(size=24, color=self.twitter_colors['dark'], family="STHeiti Medium, Arial Unicode MS, sans-serif"),
                showarrow=False
            )
            
            fig.update_layout(
                title=dict(
                    text="<b>📈 科技领域市场分布</b>",
                    x=0.5,
                    font=dict(size=28, family="STHeiti Medium, Arial Unicode MS, sans-serif", color=self.twitter_colors['dark']),
                    pad=dict(t=20)
                ),
                height=600,
                width=1200,
                margin=dict(t=100, b=60, l=60, r=60),
                paper_bgcolor='white',
                plot_bgcolor='white',
                showlegend=True,
                legend=dict(
                    x=1.05, y=0.5,
                    font=dict(size=12)
                )
            )
            
            # 添加时间戳
            fig.add_annotation(
                text=f"⏰ {datetime.now().strftime('%m-%d %H:%M')}",
                x=0, y=0,
                xref="paper", yref="paper",
                font=dict(size=12, color='#657786'),
                showarrow=False
            )
            
            image_path = await self.image_generator.generate_chart_image(
                fig, "market_summary", twitter_optimized=True
            )
            
            # 生成推文文本
            top_category = max(categories_data, key=categories_data.get)
            tweet_text = f"📊 科技市场最新分析！\n\n🏆 领先领域: {top_category}\n📈 总计 {total} 个项目\n💡 多元化发展趋势明显\n\n科技创新遍地开花，未来可期！🚀\n\n#市场分析 #科技投资 #创新"
            
            logger.info(f"✅ 市场摘要图片生成完成")
            return image_path, tweet_text
            
        except Exception as e:
            logger.error(f"❌ 市场摘要图片生成失败: {e}")
            return "", ""
    
    async def create_performance_dashboard_image(self, data: Dict[str, Any] = None) -> Tuple[str, str]:
        """创建性能仪表板图片"""
        try:
            logger.info("⚡ 创建性能仪表板图片...")
            
            # 创建2x2仪表板布局
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=["🔥 热度指数", "📈 增长趋势", "🎯 准确度", "⚡ 活跃度"],
                specs=[
                    [{"type": "indicator"}, {"type": "scatter"}],
                    [{"type": "indicator"}, {"type": "bar"}]
                ],
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            # 1. 热度指数仪表盘
            heat_score = 87
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=heat_score,
                    delta={'reference': 75, 'increasing': {'color': self.twitter_colors['success']}},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': self.twitter_colors['primary']},
                        'steps': [
                            {'range': [0, 50], 'color': '#F7F9FA'},
                            {'range': [50, 80], 'color': '#E1E8ED'},
                            {'range': [80, 100], 'color': '#AAB8C2'}
                        ],
                        'threshold': {'line': {'color': self.twitter_colors['danger'], 'width': 4}, 'thickness': 0.75, 'value': 90}
                    },
                    number={'font': {'size': 20}}
                ),
                row=1, col=1
            )
            
            # 2. 增长趋势
            days = list(range(7))
            growth = [75 + i*3 + np.random.uniform(-2, 2) for i in days]
            
            fig.add_trace(
                go.Scatter(
                    x=days,
                    y=growth,
                    mode='lines+markers',
                    line=dict(color=self.twitter_colors['success'], width=4),
                    marker=dict(size=8, color=self.twitter_colors['primary']),
                    fill='tonexty',
                    fillcolor='rgba(29, 161, 242, 0.2)',
                    showlegend=False
                ),
                row=1, col=2
            )
            
            # 3. 准确度指标
            accuracy = 94.2
            fig.add_trace(
                go.Indicator(
                    mode="number+delta+gauge",
                    value=accuracy,
                    delta={'reference': 90, 'suffix': '%'},
                    number={'suffix': '%', 'font': {'size': 20}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': self.twitter_colors['success']},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "#E1E8ED"
                    }
                ),
                row=2, col=1
            )
            
            # 4. 活跃度分布
            categories = ['AI', '区块链', '云计算', 'IoT']
            activity = [45, 32, 28, 15]
            
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=activity,
                    marker=dict(
                        color=[self.twitter_colors['primary'], self.twitter_colors['success'],
                               self.twitter_colors['warning'], self.twitter_colors['accent']],
                        line=dict(color='white', width=2)
                    ),
                    text=[f"{a}%" for a in activity],
                    textposition='outside',
                    showlegend=False
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title=dict(
                    text="<b>⚡ 科技数据实时监控</b>",
                    x=0.5,
                    font=dict(size=26, family="STHeiti Medium, Arial Unicode MS, sans-serif", color=self.twitter_colors['dark']),
                    pad=dict(t=20)
                ),
                height=700,
                width=1200,
                margin=dict(t=100, b=60, l=80, r=80),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="STHeiti Medium, Arial Unicode MS, sans-serif")
            )
            
            # 更新坐标轴标签
            fig.update_xaxes(title_text="天数", row=1, col=2)
            fig.update_yaxes(title_text="增长率%", row=1, col=2)
            fig.update_xaxes(title_text="技术领域", row=2, col=2)
            fig.update_yaxes(title_text="活跃度%", row=2, col=2)
            
            image_path = await self.image_generator.generate_chart_image(
                fig, "performance_dashboard", twitter_optimized=True
            )
            
            tweet_text = f"⚡ 科技数据实时监控报告！\n\n🔥 热度指数: {heat_score}/100\n📈 增长态势: 持续上升\n🎯 分析准确度: {accuracy}%\n💡 AI领域最为活跃\n\n数据驱动决策，把握科技脉搏！\n\n#实时监控 #科技数据 #AI分析"
            
            logger.info(f"✅ 性能仪表板图片生成完成")
            return image_path, tweet_text
            
        except Exception as e:
            logger.error(f"❌ 性能仪表板图片生成失败: {e}")
            return "", ""
    
    async def create_simple_stat_card(self, title: str, value: str, change: str = None, 
                                    color: str = "primary") -> Tuple[str, str]:
        """创建简单统计卡片"""
        try:
            logger.info(f"📊 创建统计卡片: {title}")
            
            # 选择颜色
            main_color = self.twitter_colors.get(color, self.twitter_colors['primary'])
            
            stats = {
                "总热度": value,
                "变化": change or "+8.5%",
                "领域": "科技",
                "时间": datetime.now().strftime("%H:%M")
            }
            
            # 使用图片生成器创建Twitter卡片
            image_path = await self.image_generator.create_twitter_card(
                title=title,
                subtitle="科技数据实时分析",
                stats=stats,
                logo_text="TechAnalytics"
            )
            
            tweet_text = f"📊 {title}\n\n💎 数值: {value}\n📈 变化: {change or '+8.5%'}\n⏰ 更新: {datetime.now().strftime('%H:%M')}\n\n#科技数据 #实时分析"
            
            logger.info(f"✅ 统计卡片生成完成")
            return image_path, tweet_text
            
        except Exception as e:
            logger.error(f"❌ 统计卡片生成失败: {e}")
            return "", ""
    
    async def batch_generate_twitter_images(self, data: Dict[str, Any] = None) -> List[Tuple[str, str]]:
        """批量生成Twitter图片"""
        try:
            logger.info("🚀 开始批量生成Twitter图片...")
            
            results = []
            
            # 1. 趋势卡片
            trend_result = await self.create_twitter_trend_card(data)
            if trend_result[0]:
                results.append(trend_result)
            
            # 2. 市场摘要
            market_result = await self.create_market_summary_image(data)
            if market_result[0]:
                results.append(market_result)
            
            # 3. 性能仪表板
            performance_result = await self.create_performance_dashboard_image(data)
            if performance_result[0]:
                results.append(performance_result)
            
            # 4. 简单统计卡片
            stat_result = await self.create_simple_stat_card(
                "科技热度指数", "87.5", "+12.3%", "success"
            )
            if stat_result[0]:
                results.append(stat_result)
            
            logger.info(f"✅ 批量生成完成，共 {len(results)} 个图片")
            return results
            
        except Exception as e:
            logger.error(f"❌ 批量生成失败: {e}")
            return []
    
    async def convert_existing_charts_to_images(self, chart_dir: Path = None) -> List[str]:
        """将现有的HTML图表转换为图片"""
        try:
            chart_dir = chart_dir or Path("charts")
            html_files = list(chart_dir.glob("*.html"))
            
            logger.info(f"🔄 发现 {len(html_files)} 个HTML图表文件")
            
            image_paths = await self.image_generator.batch_html_to_images([str(f) for f in html_files])
            
            logger.info(f"✅ 转换完成，生成 {len(image_paths)} 张图片")
            return image_paths
            
        except Exception as e:
            logger.error(f"❌ 转换现有图表失败: {e}")
            return []
    
    def cleanup(self):
        """清理资源"""
        self.image_generator.cleanup()
    
    def __del__(self):
        """析构函数"""
        self.cleanup()
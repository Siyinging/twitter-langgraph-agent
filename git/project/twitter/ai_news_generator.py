#!/usr/bin/env python3
"""AI头条新闻可视化生成器"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

sys.path.insert(0, str(Path(__file__).parent / "src"))

from react_agent.image_generator import ImageGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AINewsVisualizer:
    def __init__(self):
        self.image_generator = ImageGenerator()
        self.colors = {
            'primary': '#1DA1F2',
            'secondary': '#14171A', 
            'success': '#17BF63',
            'warning': '#FFAD1F',
            'danger': '#E0245E',
            'purple': '#9266CC',
            'orange': '#FF6B35',
            'teal': '#2EC4B6'
        }

    def create_ai_headlines_chart(self, headlines, tweet_text):
        """创建AI头条新闻图表"""
        try:
            logger.info("📰 创建AI头条新闻图表...")
            
            # 创建子图布局
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=['🚀 突破性进展', '🚗 自动驾驶', '🏥 医疗AI', '⚖️ AI伦理', '🎵 AI创作'],
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "scatter"}], 
                       [{"type": "scatter", "colspan": 2}, None]],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # 为每个新闻类别创建进度条样式的可视化
            categories = [
                {"name": "语言理解", "progress": 95, "color": self.colors['primary']},
                {"name": "路况识别", "progress": 88, "color": self.colors['success']},
                {"name": "诊断准确率", "progress": 85, "color": self.colors['danger']},
                {"name": "偏见消除", "progress": 78, "color": self.colors['warning']},
                {"name": "创作能力", "progress": 82, "color": self.colors['purple']}
            ]
            
            positions = [(1,1), (1,2), (2,1), (2,2), (3,1)]
            
            for i, (cat, pos) in enumerate(zip(categories, positions)):
                # 背景条
                fig.add_trace(
                    go.Scatter(
                        x=[0, 100], y=[0, 0],
                        mode='lines',
                        line=dict(color='#E1E8ED', width=20),
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=pos[0], col=pos[1]
                )
                
                # 进度条
                fig.add_trace(
                    go.Scatter(
                        x=[0, cat['progress']], y=[0, 0],
                        mode='lines+markers',
                        line=dict(color=cat['color'], width=20),
                        marker=dict(size=15, color=cat['color']),
                        showlegend=False,
                        hovertemplate=f"{cat['name']}: {cat['progress']}%<extra></extra>"
                    ),
                    row=pos[0], col=pos[1]
                )
                
                # 添加百分比标签
                fig.add_annotation(
                    x=cat['progress']/2, y=0,
                    text=f"<b>{cat['progress']}%</b>",
                    showarrow=False,
                    font=dict(size=14, color='white', family='Arial Black'),
                    row=pos[0], col=pos[1]
                )
            
            # 更新布局
            fig.update_layout(
                title=dict(
                    text="<b>📊 今日AI头条 - 技术突破指数</b>",
                    x=0.5,
                    font=dict(size=28, family="Arial Black", color=self.colors['secondary'])
                ),
                height=800,
                width=1200,
                margin=dict(l=60, r=60, t=100, b=60),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial", size=12),
                annotations=list(fig.layout.annotations) + [
                    dict(
                        text="🤖 AI技术全面开花，多领域同步突破",
                        x=0.5, y=0.02,
                        showarrow=False,
                        font=dict(size=16, color=self.colors['secondary']),
                        xref="paper", yref="paper"
                    )
                ]
            )
            
            # 更新所有子图的轴设置
            for i in range(1, 6):
                row, col = positions[i-1] if i <= 5 else (3, 1)
                fig.update_xaxes(
                    range=[0, 100], showgrid=False, showticklabels=False,
                    row=row, col=col
                )
                fig.update_yaxes(
                    range=[-0.5, 0.5], showgrid=False, showticklabels=False,
                    row=row, col=col
                )
            
            logger.info("✅ AI头条图表创建成功")
            return fig
            
        except Exception as e:
            logger.error(f"❌ AI头条图表创建失败: {e}")
            return None

    def create_simple_ai_news_card(self):
        """创建简单的AI新闻卡片"""
        try:
            logger.info("📱 创建AI新闻卡片...")
            
            # 新闻类别和热度
            categories = ['模型突破', '自动驾驶', '医疗AI', 'AI伦理', 'AI创作']
            heat_scores = [95, 88, 85, 78, 82]
            colors = [self.colors['primary'], self.colors['success'], 
                     self.colors['danger'], self.colors['warning'], self.colors['purple']]
            
            fig = go.Figure()
            
            # 创建雷达图
            fig.add_trace(go.Scatterpolar(
                r=heat_scores,
                theta=categories,
                fill='toself',
                fillcolor='rgba(29, 161, 242, 0.3)',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8, color=colors),
                name='AI热度指数'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10),
                        gridcolor='#E1E8ED'
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=12, color=self.colors['secondary'])
                    )
                ),
                title=dict(
                    text="<b>📊 今日AI头条热度雷达</b>",
                    x=0.5,
                    font=dict(size=24, family="Arial Black", color=self.colors['secondary'])
                ),
                height=600,
                width=1200,
                margin=dict(l=80, r=80, t=100, b=80),
                paper_bgcolor='white',
                showlegend=False,
                annotations=[
                    dict(
                        text="AI全面爆发 🚀",
                        x=0.5, y=0.1,
                        showarrow=False,
                        font=dict(size=16, color=self.colors['secondary']),
                        xref="paper", yref="paper"
                    )
                ]
            )
            
            logger.info("✅ AI新闻卡片创建成功")
            return fig
            
        except Exception as e:
            logger.error(f"❌ AI新闻卡片创建失败: {e}")
            return None

    async def generate_and_save_image(self):
        """生成并保存AI头条图片"""
        try:
            # 创建图表
            fig = self.create_simple_ai_news_card()
            if not fig:
                return None, None
            
            # 生成Twitter优化的图片
            image_path = await self.image_generator.create_twitter_card(
                fig, 
                "ai_headlines", 
                add_watermark=True
            )
            
            if image_path:
                logger.info(f"✅ AI头条图片生成成功: {image_path}")
                
                # 生成推文内容
                tweet_text = """📊 今日AI头条 #AI新闻 #科技前沿

1. OpenAI新模型突破语言理解瓶颈
2. 自动驾驶AI在复杂路况测试中表现优异  
3. AI辅助癌症诊断准确率提升15%
4. 伦理AI: 新框架解决偏见问题
5. AI创作音乐登上Billboard榜单

点击查看详细信息图表👇
想深入了解哪个话题？"""
                
                return image_path, tweet_text
            else:
                logger.error("❌ 图片生成失败")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ 生成AI头条图片时出错: {e}")
            return None, None

async def main():
    """主函数"""
    visualizer = AINewsVisualizer()
    image_path, tweet_text = await visualizer.generate_and_save_image()
    
    if image_path and tweet_text:
        print(f"✅ 图片已生成: {image_path}")
        print(f"📝 推文内容:\n{tweet_text}")
        return image_path, tweet_text
    else:
        print("❌ 生成失败")
        return None, None

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
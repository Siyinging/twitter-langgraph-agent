#!/usr/bin/env python3
"""简化的可视化测试脚本

独立测试可视化功能，不依赖其他模块
"""

import asyncio
import sys
from pathlib import Path
import logging
import json
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# 直接导入可视化模块避免循环依赖
sys.path.insert(0, str(Path(__file__).parent / "src"))

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def get_sample_data():
    """获取示例数据"""
    return {
        "keywords_count": {
            "人工智能": 25,
            "机器学习": 18,
            "深度学习": 12,
            "区块链": 8,
            "云计算": 15,
            "物联网": 6,
            "量子计算": 4,
            "自动驾驶": 9,
            "网络安全": 13,
            "大数据": 16,
            "Python": 11,
            "开源": 7
        },
        "tech_categories": {
            "AI/ML": 55,
            "Blockchain": 8,
            "Cloud Computing": 15,
            "IoT": 6,
            "Cybersecurity": 13,
            "Robotics": 9,
            "Other": 18
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def create_keyword_trends_chart(data, output_dir):
    """创建关键词趋势图表"""
    try:
        logger.info("🎨 生成关键词趋势图表...")
        
        keywords_data = data.get("keywords_count", {})
        keywords = list(keywords_data.keys())[:10]
        counts = [keywords_data[kw] for kw in keywords]
        
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
                textposition='inside'
            )
        ])
        
        fig.update_layout(
            title="🔍 科技关键词热度分析",
            xaxis_title="提及次数",
            yaxis_title="关键词",
            height=500,
            margin=dict(l=100, r=50, t=80, b=50)
        )
        
        chart_path = output_dir / f"keyword_trends_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(chart_path))
        logger.info(f"✅ 关键词趋势图表: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logger.error(f"❌ 创建关键词趋势图表失败: {e}")
        return ""

def create_tech_categories_pie_chart(data, output_dir):
    """创建科技分类饼图"""
    try:
        logger.info("🎨 生成科技分类饼图...")
        
        categories_data = data.get("tech_categories", {})
        filtered_data = {k: v for k, v in categories_data.items() if v > 0}
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(filtered_data.keys()),
                values=list(filtered_data.values()),
                hole=0.4,
                textinfo='label+percent'
            )
        ])
        
        fig.update_layout(
            title="📊 科技领域分布分析",
            height=500,
            showlegend=True
        )
        
        chart_path = output_dir / f"tech_categories_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(chart_path))
        logger.info(f"✅ 科技分类饼图: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logger.error(f"❌ 创建科技分类饼图失败: {e}")
        return ""

def create_dashboard(data, output_dir):
    """创建综合仪表板"""
    try:
        logger.info("🎨 生成综合仪表板...")
        
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
        
        # 1. 热门关键词
        keywords_data = data.get("keywords_count", {})
        top_keywords = list(keywords_data.keys())[:5]
        top_counts = [keywords_data[kw] for kw in top_keywords]
        
        fig.add_trace(
            go.Bar(x=top_keywords, y=top_counts, showlegend=False),
            row=1, col=1
        )
        
        # 2. 分类饼图
        categories_data = data.get("tech_categories", {})
        filtered_cats = {k: v for k, v in categories_data.items() if v > 0}
        
        fig.add_trace(
            go.Pie(labels=list(filtered_cats.keys()), values=list(filtered_cats.values()), showlegend=False),
            row=1, col=2
        )
        
        # 3. 趋势线
        trend_x = ['昨天', '今天', '明天预测']
        trend_y = [sum(keywords_data.values()) * 0.8, sum(keywords_data.values()), sum(keywords_data.values()) * 1.2]
        
        fig.add_trace(
            go.Scatter(x=trend_x, y=trend_y, mode='lines+markers', showlegend=False),
            row=2, col=1
        )
        
        # 4. 统计指标
        total_mentions = sum(keywords_data.values())
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=total_mentions,
                title={'text': "总热度"},
                gauge={'axis': {'range': [None, 200]}, 'bar': {'color': "darkblue"}}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="🚀 科技数据实时监控仪表板",
            height=800,
            margin=dict(t=100, b=50, l=50, r=50)
        )
        
        dashboard_path = output_dir / f"tech_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(dashboard_path))
        logger.info(f"✅ 综合仪表板: {dashboard_path}")
        return str(dashboard_path)
        
    except Exception as e:
        logger.error(f"❌ 创建仪表板失败: {e}")
        return ""

async def main():
    """主测试函数"""
    logger.info("🚀 开始可视化功能测试...")
    
    # 创建输出目录
    output_dir = Path("charts")
    output_dir.mkdir(exist_ok=True)
    
    # 获取测试数据
    data = get_sample_data()
    logger.info(f"📊 测试数据: {len(data['keywords_count'])} 个关键词")
    
    # 生成图表
    charts = []
    
    # 1. 关键词趋势图
    chart1 = create_keyword_trends_chart(data, output_dir)
    if chart1:
        charts.append(chart1)
    
    # 2. 分类饼图
    chart2 = create_tech_categories_pie_chart(data, output_dir)
    if chart2:
        charts.append(chart2)
    
    # 3. 综合仪表板
    chart3 = create_dashboard(data, output_dir)
    if chart3:
        charts.append(chart3)
    
    # 总结
    logger.info("="*50)
    logger.info("🎯 测试总结")
    logger.info("="*50)
    logger.info(f"✅ 成功生成 {len(charts)} 个图表:")
    
    for i, chart in enumerate(charts, 1):
        chart_path = Path(chart)
        logger.info(f"  {i}. {chart_path.name}")
        logger.info(f"     文件路径: {chart_path.absolute()}")
    
    if charts:
        logger.info("\n💡 使用说明:")
        logger.info("   - 在浏览器中打开这些 HTML 文件查看交互式图表")
        logger.info("   - 图表支持缩放、悬停显示详情等交互功能")
        logger.info(f"   - 图表目录: {output_dir.absolute()}")
        
        # 尝试打开第一个图表（仅在macOS上）
        try:
            import subprocess
            subprocess.run(["open", charts[0]], check=False)
            logger.info(f"   - 已在浏览器中打开: {Path(charts[0]).name}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
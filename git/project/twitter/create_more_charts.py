#!/usr/bin/env python3
"""创建更多高端图表样式"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime, timezone
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "src"))

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 专业配色方案
COLORS = {
    'primary': '#1a365d',
    'secondary': '#2c5aa0', 
    'accent': '#63b3ed',
    'success': '#38a169',
    'danger': '#e53e3e',
    'warning': '#d69e2e',
    'gray': '#718096',
    'light': '#f7fafc',
    'dark': '#1a202c'
}

async def create_market_heatmap(output_dir):
    """创建市场热力图"""
    try:
        logger.info("🔥 创建市场热力图...")
        
        # 创建股票热力图数据
        stocks = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NFLX',
                 'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SPOT']
        
        # 生成随机市场数据
        np.random.seed(42)
        returns = np.random.normal(0, 3, len(stocks))  # 收益率
        volumes = np.random.uniform(50, 200, len(stocks))  # 成交量
        market_caps = np.random.uniform(100, 1000, len(stocks))  # 市值
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["📈 股价涨跌热力图", "💰 成交量分布", "🏢 市值结构", "⚡ 综合表现"],
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "treemap"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12
        )
        
        # 1. 股价涨跌散点图
        colors_map = ['#ff4444' if r < -2 else '#ffaa44' if r < 0 else '#44ff44' if r < 2 else '#00aa00' for r in returns]
        
        fig.add_trace(
            go.Scatter(
                x=volumes,
                y=returns,
                mode='markers+text',
                marker=dict(
                    size=market_caps/15,
                    color=returns,
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="收益率%", x=0.45),
                    line=dict(width=2, color='white')
                ),
                text=stocks,
                textposition='middle center',
                textfont=dict(color='white', size=10),
                showlegend=False,
                hovertemplate='股票: %{text}<br>收益率: %{y:.1f}%<br>成交量: %{x:.0f}M<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. 成交量柱状图
        sorted_data = sorted(zip(stocks, volumes, returns), key=lambda x: x[1], reverse=True)
        top_stocks = [x[0] for x in sorted_data[:8]]
        top_volumes = [x[1] for x in sorted_data[:8]]
        top_returns = [x[2] for x in sorted_data[:8]]
        
        bar_colors = ['#38a169' if r > 0 else '#e53e3e' for r in top_returns]
        
        fig.add_trace(
            go.Bar(
                x=top_stocks,
                y=top_volumes,
                marker=dict(color=bar_colors, line=dict(color='white', width=1)),
                text=[f"{v:.0f}M" for v in top_volumes],
                textposition='outside',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. 市值树状图
        fig.add_trace(
            go.Treemap(
                labels=stocks[:8],
                values=market_caps[:8],
                parents=[""] * 8,
                textinfo="label+value",
                texttemplate="<b>%{label}</b><br>$%{value:.0f}B",
                marker=dict(
                    colorscale='Blues',
                    cmid=np.mean(market_caps[:8])
                ),
                showscale=False
            ),
            row=2, col=1
        )
        
        # 4. 综合表现雷达图样式的散点图
        fig.add_trace(
            go.Scatter(
                x=market_caps,
                y=returns,
                mode='markers+text',
                marker=dict(
                    size=volumes/10,
                    color=returns,
                    colorscale='Viridis',
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                text=stocks,
                textposition='top center',
                showlegend=False,
                hovertemplate='股票: %{text}<br>市值: $%{x:.0f}B<br>收益率: %{y:.1f}%<extra></extra>'
            ),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text="<b>🔥 科技股实时市场热力图</b><br><sub>Tech Stock Market Heatmap - Real-time Analysis</sub>",
                x=0.5,
                font=dict(size=24, family="Arial Black", color=COLORS['dark'])
            ),
            height=800,
            margin=dict(t=120, b=60, l=60, r=60),
            paper_bgcolor='#fafbfc',
            plot_bgcolor='white',
            font=dict(family="Arial", size=11)
        )
        
        # 更新坐标轴标签
        fig.update_xaxes(title_text="成交量 (M)", row=1, col=1)
        fig.update_yaxes(title_text="收益率 (%)", row=1, col=1)
        fig.update_xaxes(title_text="股票代码", row=1, col=2)
        fig.update_yaxes(title_text="成交量 (M)", row=1, col=2)
        fig.update_xaxes(title_text="市值 ($B)", row=2, col=2)
        fig.update_yaxes(title_text="收益率 (%)", row=2, col=2)
        
        chart_path = output_dir / f"market_heatmap_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(chart_path))
        
        logger.info(f"✅ 市场热力图: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logger.error(f"❌ 创建市场热力图失败: {e}")
        return ""

async def create_trading_dashboard(output_dir):
    """创建交易策略仪表板"""
    try:
        logger.info("📊 创建交易策略仪表板...")
        
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=["📈 策略表现", "💰 资金流向", "🎯 风险收益", "⚡ 实时信号", "📋 持仓分布", "🔮 AI预测"],
            specs=[
                [{"type": "scatter"}, {"type": "waterfall"}, {"type": "scatter"}],
                [{"type": "indicator"}, {"type": "pie"}, {"type": "bar"}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.08
        )
        
        # 1. 策略表现曲线
        days = list(range(30))
        strategy_returns = np.cumsum(np.random.normal(0.5, 2, 30))
        benchmark_returns = np.cumsum(np.random.normal(0.2, 1.5, 30))
        
        fig.add_trace(
            go.Scatter(
                x=days, y=strategy_returns,
                name='AI策略',
                line=dict(color=COLORS['primary'], width=3),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=days, y=benchmark_returns,
                name='基准',
                line=dict(color=COLORS['gray'], width=2, dash='dash')
            ),
            row=1, col=1
        )
        
        # 2. 资金流向瀑布图
        categories = ['期初资金', '股票收益', '期权收益', '交易费用', '税费', '期末资金']
        values = [100000, 15000, 8000, -2000, -1500, 0]  # 期末资金会自动计算
        
        fig.add_trace(
            go.Waterfall(
                name="资金流向",
                orientation="v",
                measure=["absolute", "relative", "relative", "relative", "relative", "total"],
                x=categories,
                textposition="outside",
                text=[f"${v:,.0f}" if v != 0 else f"${sum(values[:-1]):,.0f}" for v in values[:-1]] + [f"${sum(values[:-1]):,.0f}"],
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": COLORS['danger']}},
                increasing={"marker": {"color": COLORS['success']}},
                totals={"marker": {"color": COLORS['primary']}}
            ),
            row=1, col=2
        )
        
        # 3. 风险收益散点图
        strategies = ['保守型', '平衡型', '成长型', '激进型', 'AI量化', '价值投资']
        risk_levels = [5, 15, 25, 35, 20, 12]
        expected_returns = [8, 12, 18, 25, 22, 15]
        
        fig.add_trace(
            go.Scatter(
                x=risk_levels,
                y=expected_returns,
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=['#38a169', '#4299e1', '#ed8936', '#e53e3e', '#805ad5', '#38b2ac'],
                    line=dict(width=2, color='white')
                ),
                text=strategies,
                textposition='top center',
                showlegend=False,
                hovertemplate='策略: %{text}<br>风险: %{x}%<br>预期收益: %{y}%<extra></extra>'
            ),
            row=1, col=3
        )
        
        # 4. 实时交易信号
        signal_strength = 85
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=signal_strength,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "买入信号强度"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': COLORS['success'] if signal_strength > 70 else COLORS['warning'] if signal_strength > 40 else COLORS['danger']},
                    'steps': [
                        {'range': [0, 30], 'color': '#ffebee'},
                        {'range': [30, 70], 'color': '#fff3e0'},
                        {'range': [70, 100], 'color': '#e8f5e8'}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
                }
            ),
            row=2, col=1
        )
        
        # 5. 持仓分布
        positions = ['科技股', '金融股', '消费股', '医疗股', '现金']
        position_values = [40, 25, 20, 10, 5]
        
        fig.add_trace(
            go.Pie(
                labels=positions,
                values=position_values,
                hole=0.4,
                marker=dict(
                    colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent',
                showlegend=False
            ),
            row=2, col=2
        )
        
        # 6. AI预测准确率
        models = ['LSTM', 'Random Forest', 'XGBoost', 'Transformer', 'CNN']
        accuracy = [78, 82, 85, 88, 75]
        
        fig.add_trace(
            go.Bar(
                x=models,
                y=accuracy,
                marker=dict(
                    color=accuracy,
                    colorscale='Viridis',
                    line=dict(color='white', width=1)
                ),
                text=[f"{a}%" for a in accuracy],
                textposition='outside',
                showlegend=False
            ),
            row=2, col=3
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text="<b>🚀 AI量化交易策略仪表板</b><br><sub>AI Quantitative Trading Strategy Dashboard</sub>",
                x=0.5,
                font=dict(size=26, family="Arial Black", color=COLORS['dark'])
            ),
            height=800,
            margin=dict(t=120, b=60, l=60, r=60),
            paper_bgcolor='#f8fafc',
            plot_bgcolor='white',
            font=dict(family="Arial", size=11),
            showlegend=False
        )
        
        # 添加坐标轴标签
        fig.update_xaxes(title_text="时间 (天)", row=1, col=1)
        fig.update_yaxes(title_text="累计收益率 (%)", row=1, col=1)
        fig.update_xaxes(title_text="风险水平 (%)", row=1, col=3)
        fig.update_yaxes(title_text="预期收益 (%)", row=1, col=3)
        fig.update_xaxes(title_text="AI模型", row=2, col=3)
        fig.update_yaxes(title_text="准确率 (%)", row=2, col=3)
        
        chart_path = output_dir / f"trading_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(chart_path))
        
        logger.info(f"✅ 交易策略仪表板: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logger.error(f"❌ 创建交易策略仪表板失败: {e}")
        return ""

async def create_executive_summary(output_dir):
    """创建高管摘要报告"""
    try:
        logger.info("👔 创建高管摘要报告...")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["📊 业务概览", "💰 财务表现", "🎯 战略指标", "📈 增长趋势"],
            specs=[
                [{"type": "table"}, {"type": "indicator"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.15
        )
        
        # 1. 业务概览表格
        business_metrics = [
            {"指标": "📈 总收入", "数值": "$2.1B", "变化": "+15.2%", "状态": "🟢"},
            {"指标": "💰 净利润", "数值": "$420M", "变化": "+22.1%", "状态": "🟢"},
            {"指标": "👥 活跃用户", "数值": "125M", "变化": "+8.5%", "状态": "🟢"},
            {"指标": "🌐 市场份额", "数值": "23.5%", "变化": "+2.1%", "状态": "🟢"},
            {"指标": "⚡ 运营效率", "数值": "94.2%", "变化": "+3.8%", "状态": "🟢"},
            {"指标": "🎯 客户满意度", "数值": "4.8/5", "变化": "+0.2", "状态": "🟢"}
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["关键指标", "当前数值", "同比变化", "状态"],
                    fill_color=COLORS['primary'],
                    font=dict(color='white', size=14, family="Arial Black"),
                    align='center',
                    height=50
                ),
                cells=dict(
                    values=[
                        [item["指标"] for item in business_metrics],
                        [item["数值"] for item in business_metrics],
                        [item["变化"] for item in business_metrics],
                        [item["状态"] for item in business_metrics]
                    ],
                    fill_color=[
                        ['white'] * len(business_metrics),
                        ['#f0f8ff'] * len(business_metrics),
                        ['#e8f5e8'] * len(business_metrics),
                        ['white'] * len(business_metrics)
                    ],
                    align='center',
                    font=dict(size=12),
                    height=45
                )
            ),
            row=1, col=1
        )
        
        # 2. 综合健康度指标
        health_score = 92.5
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=health_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "<b>企业综合健康度</b>", 'font': {'size': 16}},
                delta={'reference': 85, 'increasing': {'color': COLORS['success']}},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': COLORS['primary']},
                    'steps': [
                        {'range': [0, 60], 'color': '#ffebee'},
                        {'range': [60, 80], 'color': '#fff3e0'},
                        {'range': [80, 90], 'color': '#e8f5e8'},
                        {'range': [90, 100], 'color': '#e3f2fd'}
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                },
                number={'font': {'size': 24}}
            ),
            row=1, col=2
        )
        
        # 3. 战略重点评分
        strategic_areas = ['市场扩展', '产品创新', '运营效率', '人才发展', '技术投入']
        scores = [88, 92, 85, 79, 95]
        colors = [COLORS['success'] if s >= 85 else COLORS['warning'] if s >= 70 else COLORS['danger'] for s in scores]
        
        fig.add_trace(
            go.Bar(
                x=strategic_areas,
                y=scores,
                marker=dict(color=colors, line=dict(color='white', width=2)),
                text=[f"{s}分" for s in scores],
                textposition='outside',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # 4. 增长趋势预测
        quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025']
        actual = [1.8, 1.9, 2.0, 2.1, None, None]
        forecast = [None, None, None, 2.1, 2.3, 2.5]
        
        # 实际数据
        fig.add_trace(
            go.Scatter(
                x=quarters[:4],
                y=actual[:4],
                mode='lines+markers',
                name='实际收入',
                line=dict(color=COLORS['primary'], width=4),
                marker=dict(size=10)
            ),
            row=2, col=2
        )
        
        # 预测数据
        fig.add_trace(
            go.Scatter(
                x=quarters[3:],
                y=[actual[3]] + forecast[4:],
                mode='lines+markers',
                name='预测收入',
                line=dict(color=COLORS['accent'], width=4, dash='dash'),
                marker=dict(size=10, symbol='diamond')
            ),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text="<b>📋 Executive Summary Report</b><br><sub>高管战略决策摘要 - 2025年度</sub>",
                x=0.5,
                font=dict(size=28, family="Arial Black", color=COLORS['dark'])
            ),
            height=800,
            margin=dict(t=120, b=80, l=80, r=80),
            paper_bgcolor='#f8fafc',
            plot_bgcolor='white',
            font=dict(family="Arial", size=12),
            showlegend=True,
            legend=dict(x=0.7, y=0.2)
        )
        
        # 更新坐标轴
        fig.update_xaxes(title_text="战略重点", row=2, col=1)
        fig.update_yaxes(title_text="评分", row=2, col=1)
        fig.update_xaxes(title_text="时间", row=2, col=2)
        fig.update_yaxes(title_text="收入 ($B)", row=2, col=2)
        
        # 添加关键注释
        fig.add_annotation(
            text="💡 关键洞察：技术投入领域表现卓越，建议继续加大投资",
            x=0.5, y=-0.08,
            xref="paper", yref="paper",
            font=dict(size=12, color=COLORS['primary']),
            showarrow=False,
            bgcolor="rgba(26, 54, 93, 0.1)",
            bordercolor=COLORS['primary'],
            borderwidth=1,
            borderpad=10
        )
        
        chart_path = output_dir / f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(chart_path))
        
        logger.info(f"✅ 高管摘要报告: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logger.error(f"❌ 创建高管摘要报告失败: {e}")
        return ""

async def main():
    """主函数"""
    logger.info("🚀 开始创建更多高端图表...")
    
    output_dir = Path("charts")
    output_dir.mkdir(exist_ok=True)
    
    charts = []
    
    # 创建各种高端图表
    logger.info("\n" + "="*50)
    logger.info("1. 市场热力图")
    logger.info("="*50)
    chart1 = await create_market_heatmap(output_dir)
    if chart1:
        charts.append(chart1)
    
    logger.info("\n" + "="*50)
    logger.info("2. 交易策略仪表板")
    logger.info("="*50)
    chart2 = await create_trading_dashboard(output_dir)
    if chart2:
        charts.append(chart2)
    
    logger.info("\n" + "="*50)
    logger.info("3. 高管摘要报告")
    logger.info("="*50)
    chart3 = await create_executive_summary(output_dir)
    if chart3:
        charts.append(chart3)
    
    # 总结
    logger.info("\n" + "="*60)
    logger.info("🎯 高端图表创建完成")
    logger.info("="*60)
    logger.info(f"✅ 总共生成 {len(charts)} 个专业级图表:")
    
    for i, chart in enumerate(charts, 1):
        chart_path = Path(chart)
        logger.info(f"  {i}. {chart_path.name}")
        logger.info(f"     📍 {chart_path.absolute()}")
    
    if charts:
        logger.info("\n💎 图表特色:")
        logger.info("   🔥 市场热力图 - 实时股价、成交量、市值分析")
        logger.info("   🚀 交易仪表板 - AI策略、风险收益、资金流向")
        logger.info("   👔 高管报告 - 业务指标、战略评分、增长预测")
        logger.info("   🎨 专业配色 - SignalPlus级别视觉设计")
        logger.info("   📱 响应式布局 - 支持多设备展示")
        
        # 打开第一个图表
        try:
            import subprocess
            subprocess.run(["open", charts[0]], check=False)
            logger.info(f"\n🌟 已打开图表: {Path(charts[0]).name}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
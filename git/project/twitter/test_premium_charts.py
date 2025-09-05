#!/usr/bin/env python3
"""高端图表测试脚本

测试SignalPlus风格的专业金融图表功能
"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime, timezone
import numpy as np

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 导入可视化模块
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SignalPlus风格配色
COLORS = {
    'primary': '#1a365d',      # 深蓝主色
    'secondary': '#2c5aa0',    # 蓝色
    'accent': '#63b3ed',       # 亮蓝
    'success': '#38a169',      # 绿色
    'danger': '#e53e3e',       # 红色
    'warning': '#d69e2e',      # 黄色
    'gray': '#718096',         # 灰色
    'light': '#f7fafc',        # 浅色
    'dark': '#1a202c'          # 深色
}

def get_financial_sample_data():
    """获取金融样本数据"""
    return {
        "call_options": [
            {"symbol": "NVDA", "volume": 144000000, "change": 6990.33, "ratio": "6.1:1", "change_pct": 78.65},
            {"symbol": "RDDT", "volume": 79886700, "change": 66549.20, "ratio": "15.5:1", "change_pct": 86.76},
            {"symbol": "MSTR", "volume": 49104900, "change": -166.53, "ratio": "0.7:1", "change_pct": 70.54}
        ],
        "put_options": [
            {"symbol": "ADBE", "volume": 47761000, "change": 0, "ratio": "∞", "change_pct": 99.46},
            {"symbol": "NVDA", "volume": 39148600, "change": 1974.60, "ratio": "3.3:1", "change_pct": 21.35},
            {"symbol": "TSLA", "volume": 29998300, "change": -495.59, "ratio": "0.4:1", "change_pct": 37.94}
        ],
        "large_orders": [
            {"symbol": "NVDA", "volume": 73515000, "type": "BUY", "expiry": "25年08月130 Call"},
            {"symbol": "RDDT", "volume": 70000000, "type": "BUY", "expiry": "27年01月270 Call"},
            {"symbol": "AMD", "volume": 40327000, "type": "SELL", "expiry": "25年08月120 Call"}
        ],
        "active_ratios": [
            {"symbol": "TMO", "volume": 26798500, "put_call_ratio": "1:∞"},
            {"symbol": "CHTR", "volume": 26027700, "put_call_ratio": "∞:1", "change": 360.86},
            {"symbol": "NLOP", "volume": 17340000, "put_call_ratio": "∞:1"}
        ]
    }

async def create_professional_leaderboard(output_dir):
    """创建专业排行榜 - 完全仿照SignalPlus"""
    try:
        logger.info("🏆 创建专业金融排行榜...")
        
        data = get_financial_sample_data()
        
        # 创建4个表格的子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                "🚀 看涨期权成交额榜", "📈 看跌期权成交额榜",
                "💰 大单成交额榜", "⚡ 异动活跃比榜"
            ],
            specs=[[{"type": "table"}, {"type": "table"}],
                   [{"type": "table"}, {"type": "table"}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )
        
        # 1. 看涨期权成交额榜
        call_data = data["call_options"]
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["", "标的", "成交额", "涨跌", "比率"],
                    fill_color=COLORS['success'],
                    font=dict(color='white', size=13, family="Arial Black"),
                    align='center',
                    height=45
                ),
                cells=dict(
                    values=[
                        ["1", "2", "3"],
                        [f"📈 {item['symbol']}" for item in call_data],
                        [f"${item['volume']/10000:.0f}万" for item in call_data],
                        [f"↗️ ${item['change']:.2f}万 (B:S {item['ratio']})" if item['change'] > 0 
                         else f"↘️ ${abs(item['change']):.2f}万 (B:S {item['ratio']})" for item in call_data],
                        [f"Call占比 {item['change_pct']:.2f}%" for item in call_data]
                    ],
                    fill_color=[
                        ['#FFD700', '#C0C0C0', '#CD7F32'],  # 金银铜
                        ['white'] * 3,
                        ['#e6f7ff'] * 3,
                        [['#f6ffed', '#fff2e8'][i % 2] for i in range(3)],
                        ['white'] * 3
                    ],
                    align=['center', 'left', 'center', 'left', 'center'],
                    font=dict(size=11),
                    height=40
                )
            ),
            row=1, col=1
        )
        
        # 2. 看跌期权成交额榜
        put_data = data["put_options"]
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["", "标的", "成交额", "涨跌", "比率"],
                    fill_color=COLORS['danger'],
                    font=dict(color='white', size=13, family="Arial Black"),
                    align='center',
                    height=45
                ),
                cells=dict(
                    values=[
                        ["1", "2", "3"],
                        [f"📉 {item['symbol']}" for item in put_data],
                        [f"${item['volume']/10000:.0f}万" for item in put_data],
                        [f"↗️ ${item['change']:.2f}万 (B:S {item['ratio']})" if item['change'] > 0 
                         else f"— (B:S {item['ratio']})" if item['change'] == 0
                         else f"↘️ ${abs(item['change']):.2f}万 (B:S {item['ratio']})" for item in put_data],
                        [f"Put占比 {item['change_pct']:.2f}%" for item in put_data]
                    ],
                    fill_color=[
                        ['#FFD700', '#C0C0C0', '#CD7F32'],
                        ['white'] * 3,
                        ['#fff2f0'] * 3,
                        [['#fff2f0', '#fff7e6'][i % 2] for i in range(3)],
                        ['white'] * 3
                    ],
                    align=['center', 'left', 'center', 'left', 'center'],
                    font=dict(size=11),
                    height=40
                )
            ),
            row=1, col=2
        )
        
        # 3. 大单成交额榜
        large_data = data["large_orders"]
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["", "标的", "成交额", "类型"],
                    fill_color=COLORS['warning'],
                    font=dict(color='white', size=13, family="Arial Black"),
                    align='center',
                    height=45
                ),
                cells=dict(
                    values=[
                        ["1", "2", "3"],
                        [f"💰 {item['symbol']}" for item in large_data],
                        [f"${item['volume']/10000:.0f}万" for item in large_data],
                        [f"🟢 {item['type']}" if item['type'] == 'BUY' else f"🔴 {item['type']}" for item in large_data]
                    ],
                    fill_color=[
                        ['#FFD700', '#C0C0C0', '#CD7F32'],
                        ['white'] * 3,
                        ['#fffbe6'] * 3,
                        [['#f6ffed', '#fff2f0'][0 if item['type'] == 'BUY' else 1] for item in large_data]
                    ],
                    align=['center', 'left', 'center', 'center'],
                    font=dict(size=11),
                    height=40
                )
            ),
            row=2, col=1
        )
        
        # 4. 异动活跃比榜
        active_data = data["active_ratios"]
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["", "标的", "成交额", "Put:Call"],
                    fill_color=COLORS['primary'],
                    font=dict(color='white', size=13, family="Arial Black"),
                    align='center',
                    height=45
                ),
                cells=dict(
                    values=[
                        ["1", "2", "3"],
                        [f"⚡ {item['symbol']}" for item in active_data],
                        [f"${item['volume']/10000:.0f}万" for item in active_data],
                        [item['put_call_ratio'] for item in active_data]
                    ],
                    fill_color=[
                        ['#FFD700', '#C0C0C0', '#CD7F32'],
                        ['white'] * 3,
                        ['#f0f8ff'] * 3,
                        ['white'] * 3
                    ],
                    align=['center', 'left', 'center', 'center'],
                    font=dict(size=11),
                    height=40
                )
            ),
            row=2, col=2
        )
        
        # 设置专业的整体布局
        fig.update_layout(
            title=dict(
                text="<b>🏛️ 美股期权龙虎榜</b><br><sub style='color:#666;'>2025年8月18日</sub>",
                x=0.5,
                font=dict(size=28, family="Arial Black, sans-serif", color=COLORS['dark']),
                xref="paper"
            ),
            height=750,
            margin=dict(t=120, b=100, l=40, r=40),
            paper_bgcolor='#fafbfc',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=11)
        )
        
        # 添加专业底部注释
        fig.add_annotation(
            text="<b>📞 SignalPlus666 进·交·流·群</b>",
            x=0.5, y=-0.08,
            xref="paper", yref="paper",
            font=dict(size=16, color=COLORS['primary'], family="Arial Black"),
            showarrow=False,
            bgcolor="rgba(26, 54, 93, 0.1)",
            bordercolor=COLORS['primary'],
            borderwidth=2,
            borderpad=10
        )
        
        fig.add_annotation(
            text="注：主动方向基于成交价相对买卖价格的位置判断期权买卖方的主动意愿强弱<br>" +
                 "🔴 表示买卖主动；⭕ 表示卖方主动；B:S为买卖盘比例",
            x=0.5, y=-0.13,
            xref="paper", yref="paper",
            font=dict(size=10, color='#666', family="Arial"),
            showarrow=False
        )
        
        # 保存图表
        chart_path = output_dir / f"professional_leaderboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(chart_path))
        
        logger.info(f"✅ 专业排行榜: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logger.error(f"❌ 创建专业排行榜失败: {e}")
        return ""

async def create_executive_dashboard(output_dir):
    """创建高管级别仪表板"""
    try:
        logger.info("👔 创建高管级别仪表板...")
        
        # 创建复杂的企业级仪表板布局
        fig = make_subplots(
            rows=3, cols=4,
            subplot_titles=[
                "📊 市场总览", "📈 业绩指标", "🎯 关键KPI", "⚠️风险监控",
                "🏆 Top表现", "📉 需关注", "💰 收益分析", "🔍 细分市场",
                "🌐 全球视野", "🚀 增长预测", "📱 实时监控", "📋 综合评估"
            ],
            specs=[
                [{"type": "pie"}, {"type": "indicator"}, {"type": "bar"}, {"type": "indicator"}],
                [{"type": "table"}, {"type": "table"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "scattergeo"}, {"type": "scatter"}, {"type": "indicator"}, {"type": "table"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.05
        )
        
        # 第一行 - 高级概览
        # 1. 市场总览饼图
        market_data = {"AI技术": 35, "金融科技": 25, "云服务": 20, "区块链": 12, "其他": 8}
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        fig.add_trace(
            go.Pie(
                labels=[f"{k}" for k in market_data.keys()],
                values=list(market_data.values()),
                hole=0.5,
                marker=dict(colors=colors, line=dict(color='white', width=3)),
                textinfo='label+percent',
                textfont=dict(size=10, color='white'),
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_annotation(
            text=f"<b>100B</b><br>总市值",
            x=0.125, y=0.85,
            font=dict(size=14, color=COLORS['dark']),
            showarrow=False
        )
        
        # 2. 业绩指标
        performance = 127.5
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=performance,
                title={'text': "业绩指数", 'font': {'size': 14}},
                delta={'reference': 100, 'increasing': {'color': COLORS['success']}},
                gauge={
                    'axis': {'range': [None, 200]},
                    'bar': {'color': COLORS['primary']},
                    'steps': [
                        {'range': [0, 50], 'color': '#ffebee'},
                        {'range': [50, 100], 'color': '#fff3e0'},
                        {'range': [100, 150], 'color': '#e8f5e8'},
                        {'range': [150, 200], 'color': '#e3f2fd'}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 180}
                }
            ),
            row=1, col=2
        )
        
        # 3. 关键KPI
        kpis = ["营收增长", "用户增长", "市场份额", "利润率", "创新指数"]
        kpi_values = [85, 92, 78, 88, 95]
        kpi_colors = [COLORS['success'] if v >= 85 else COLORS['warning'] if v >= 70 else COLORS['danger'] for v in kpi_values]
        
        fig.add_trace(
            go.Bar(
                x=kpi_values,
                y=kpis,
                orientation='h',
                marker=dict(color=kpi_colors, line=dict(color='white', width=1)),
                text=[f"{v}%" for v in kpi_values],
                textposition='inside',
                showlegend=False
            ),
            row=1, col=3
        )
        
        # 4. 风险监控
        risk_level = 23
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=risk_level,
                title={'text': "风险指数", 'font': {'size': 14}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': COLORS['danger'] if risk_level > 70 else COLORS['warning'] if risk_level > 40 else COLORS['success']},
                    'steps': [
                        {'range': [0, 30], 'color': '#e8f5e8'},
                        {'range': [30, 70], 'color': '#fff3e0'},
                        {'range': [70, 100], 'color': '#ffebee'}
                    ]
                }
            ),
            row=1, col=4
        )
        
        # 第二行 - 详细分析
        # 5. Top表现表格
        top_performers = [
            {"name": "AI芯片", "growth": "+45.2%", "revenue": "$2.1B"},
            {"name": "云计算", "growth": "+32.1%", "revenue": "$1.8B"},
            {"name": "自动驾驶", "growth": "+28.9%", "revenue": "$1.2B"}
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=["🏆", "业务", "增长", "收入"], fill_color=COLORS['success']),
                cells=dict(
                    values=[
                        ["1", "2", "3"],
                        [item["name"] for item in top_performers],
                        [item["growth"] for item in top_performers],
                        [item["revenue"] for item in top_performers]
                    ],
                    fill_color=['#FFD700', 'white', '#e8f5e8', '#e3f2fd'],
                    font=dict(size=10)
                )
            ),
            row=2, col=1
        )
        
        # 6. 需关注表格
        concerns = [
            {"name": "传统硬件", "decline": "-12.3%", "action": "转型"},
            {"name": "旧平台", "decline": "-8.7%", "action": "升级"},
            {"name": "过时服务", "decline": "-15.1%", "action": "淘汰"}
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=["⚠️", "业务", "下降", "行动"], fill_color=COLORS['warning']),
                cells=dict(
                    values=[
                        ["1", "2", "3"],
                        [item["name"] for item in concerns],
                        [item["decline"] for item in concerns],
                        [item["action"] for item in concerns]
                    ],
                    fill_color=['#FFA500', 'white', '#fff2e8', '#fff8e1'],
                    font=dict(size=10)
                )
            ),
            row=2, col=2
        )
        
        # 7. 收益分析时间序列
        months = ['Q1', 'Q2', 'Q3', 'Q4', 'Q1+1']
        revenue = [85, 92, 98, 105, 112]
        profit = [25, 28, 32, 35, 38]
        
        fig.add_trace(
            go.Scatter(x=months, y=revenue, name='Revenue', line=dict(color=COLORS['primary'], width=3)),
            row=2, col=3
        )
        fig.add_trace(
            go.Scatter(x=months, y=profit, name='Profit', line=dict(color=COLORS['success'], width=3)),
            row=2, col=3
        )
        
        # 8. 细分市场
        segments = ["企业级", "消费级", "政府", "教育", "医疗"]
        segment_values = [45, 30, 12, 8, 5]
        
        fig.add_trace(
            go.Bar(
                x=segments,
                y=segment_values,
                marker=dict(color=COLORS['accent'], line=dict(color='white', width=1)),
                text=[f"{v}%" for v in segment_values],
                textposition='outside',
                showlegend=False
            ),
            row=2, col=4
        )
        
        # 第三行 - 战略视角
        # 9. 全球分布（简化的地理图）
        countries = ['US', 'CN', 'EU', 'JP', 'Others']
        global_revenue = [40, 25, 20, 10, 5]
        
        fig.add_trace(
            go.Bar(
                x=countries,
                y=global_revenue,
                marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']),
                showlegend=False
            ),
            row=3, col=1
        )
        
        # 10. 增长预测
        forecast_x = list(range(12))
        actual = [100 + i*5 + np.random.normal(0, 2) for i in range(6)]
        predicted = [actual[-1] + (i-5)*7 + np.random.normal(0, 3) for i in range(6, 12)]
        
        fig.add_trace(
            go.Scatter(x=forecast_x[:6], y=actual, name='历史', line=dict(color=COLORS['primary'], width=3)),
            row=3, col=2
        )
        fig.add_trace(
            go.Scatter(x=forecast_x[5:], y=predicted, name='预测', line=dict(color=COLORS['accent'], width=3, dash='dash')),
            row=3, col=2
        )
        
        # 11. 实时监控指标
        realtime_score = 94.2
        fig.add_trace(
            go.Indicator(
                mode="number+delta+gauge",
                value=realtime_score,
                title={'text': "综合健康度"},
                delta={'reference': 90},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': COLORS['success']}}
            ),
            row=3, col=3
        )
        
        # 12. 综合评估表
        assessment = [
            {"metric": "战略执行", "score": "A+", "trend": "↗️"},
            {"metric": "财务健康", "score": "A", "trend": "↗️"},
            {"metric": "市场地位", "score": "A+", "trend": "→"},
            {"metric": "创新能力", "score": "A+", "trend": "↗️"}
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=["指标", "评级", "趋势"], fill_color=COLORS['dark'], font=dict(color='white')),
                cells=dict(
                    values=[
                        [item["metric"] for item in assessment],
                        [item["score"] for item in assessment],
                        [item["trend"] for item in assessment]
                    ],
                    fill_color=['white', '#e8f5e8', 'white'],
                    font=dict(size=10)
                )
            ),
            row=3, col=4
        )
        
        # 更新整体布局
        fig.update_layout(
            title=dict(
                text="<b>📊 Executive Dashboard</b><br><sub>高管战略决策仪表板</sub>",
                x=0.5,
                font=dict(size=30, family="Arial Black, sans-serif", color=COLORS['dark'])
            ),
            height=1200,
            margin=dict(t=120, b=50, l=40, r=40),
            paper_bgcolor='#f8fafc',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif"),
            showlegend=False
        )
        
        # 保存图表
        chart_path = output_dir / f"executive_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        fig.write_html(str(chart_path))
        
        logger.info(f"✅ 高管仪表板: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logger.error(f"❌ 创建高管仪表板失败: {e}")
        return ""

async def main():
    """主测试函数"""
    logger.info("🚀 开始高端图表测试...")
    
    # 创建输出目录
    output_dir = Path("charts")
    output_dir.mkdir(exist_ok=True)
    
    charts = []
    
    # 1. 专业排行榜
    logger.info("\n" + "="*50)
    logger.info("创建专业金融排行榜")
    logger.info("="*50)
    chart1 = await create_professional_leaderboard(output_dir)
    if chart1:
        charts.append(chart1)
    
    # 2. 高管仪表板
    logger.info("\n" + "="*50)
    logger.info("创建高管级别仪表板")
    logger.info("="*50)
    chart2 = await create_executive_dashboard(output_dir)
    if chart2:
        charts.append(chart2)
    
    # 总结
    logger.info("\n" + "="*50)
    logger.info("🎯 高端图表测试总结")
    logger.info("="*50)
    logger.info(f"✅ 成功生成 {len(charts)} 个高端图表:")
    
    for i, chart in enumerate(charts, 1):
        chart_path = Path(chart)
        logger.info(f"  {i}. {chart_path.name}")
        logger.info(f"     📁 {chart_path.absolute()}")
    
    if charts:
        logger.info("\n💡 图表特点:")
        logger.info("   📊 专业金融风格设计")
        logger.info("   🏆 排行榜样式表格")
        logger.info("   💼 高管级别仪表板")
        logger.info("   🎨 SignalPlus配色方案")
        logger.info("   📱 响应式布局设计")
        logger.info("\n🌐 使用方法:")
        logger.info("   - 在浏览器中打开HTML文件")
        logger.info("   - 支持缩放、悬停等交互")
        logger.info("   - 适合展示和汇报使用")
        
        # 自动打开第一个图表
        try:
            import subprocess
            subprocess.run(["open", charts[0]], check=False)
            logger.info(f"\n🚀 已在浏览器中打开: {Path(charts[0]).name}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
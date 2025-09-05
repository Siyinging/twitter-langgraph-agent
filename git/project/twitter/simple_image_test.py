#!/usr/bin/env python3
"""简化版图片生成测试 - 修复API兼容性"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "src"))

import plotly.graph_objects as go
import plotly.io as pio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Twitter友好配色
TWITTER_COLORS = {
    'primary': '#1DA1F2',
    'secondary': '#14171A', 
    'success': '#17BF63',
    'warning': '#FFAD1F',
    'danger': '#E0245E'
}

def create_simple_chart():
    """创建简单的Twitter友好图表"""
    try:
        logger.info("🎨 创建简单图表...")
        
        # 示例数据
        keywords = ['AI', '区块链', '云计算', '物联网', '5G']
        values = [45, 32, 28, 15, 12]
        
        # 创建柱状图
        fig = go.Figure(data=go.Bar(
            x=keywords,
            y=values,
            marker=dict(
                color=[TWITTER_COLORS['primary'], TWITTER_COLORS['success'], 
                       TWITTER_COLORS['warning'], TWITTER_COLORS['danger'], '#9266CC'],
                line=dict(color='white', width=2)
            ),
            text=values,
            textposition='outside'
        ))
        
        # 设置布局 - 使用新的API格式
        fig.update_layout(
            title=dict(
                text="<b>🔥 科技热词排行榜</b>",
                x=0.5,
                font=dict(size=24, family="Arial Black", color=TWITTER_COLORS['secondary'])
            ),
            xaxis=dict(
                title="技术领域",
                title_font=dict(size=14),  # 新API格式
                showgrid=True,
                gridcolor='#E1E8ED'
            ),
            yaxis=dict(
                title="热度值",
                title_font=dict(size=14),  # 新API格式
                showgrid=True,
                gridcolor='#E1E8ED'
            ),
            height=500,
            width=1200,
            margin=dict(l=80, r=80, t=80, b=80),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial", size=12)
        )
        
        logger.info("✅ 图表创建成功")
        return fig
        
    except Exception as e:
        logger.error(f"❌ 图表创建失败: {e}")
        return None

def test_kaleido_export():
    """测试Kaleido图片导出"""
    try:
        logger.info("📸 测试Kaleido图片导出...")
        
        fig = create_simple_chart()
        if not fig:
            return False
        
        # 创建输出目录
        output_dir = Path("images")
        output_dir.mkdir(exist_ok=True)
        
        # 导出PNG图片
        image_path = output_dir / f"simple_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # 使用Kaleido导出
        img_bytes = fig.to_image(
            format="png",
            width=1200,
            height=675,  # Twitter推荐16:9比例
            scale=2,
            engine="kaleido"
        )
        
        with open(image_path, 'wb') as f:
            f.write(img_bytes)
        
        # 检查文件
        if image_path.exists():
            file_size = image_path.stat().st_size // 1024
            logger.info(f"✅ 图片导出成功: {image_path.name} ({file_size}KB)")
            return str(image_path)
        else:
            logger.error("❌ 图片文件未生成")
            return False
            
    except Exception as e:
        logger.error(f"❌ Kaleido导出失败: {e}")
        return False

def test_html_export():
    """测试HTML导出"""
    try:
        logger.info("🌐 测试HTML导出...")
        
        fig = create_simple_chart()
        if not fig:
            return False
        
        # 创建输出目录
        output_dir = Path("charts")
        output_dir.mkdir(exist_ok=True)
        
        # 导出HTML
        html_path = output_dir / f"simple_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(str(html_path))
        
        if html_path.exists():
            file_size = html_path.stat().st_size // 1024
            logger.info(f"✅ HTML导出成功: {html_path.name} ({file_size}KB)")
            return str(html_path)
        else:
            logger.error("❌ HTML文件未生成")
            return False
            
    except Exception as e:
        logger.error(f"❌ HTML导出失败: {e}")
        return False

def create_twitter_card_simple():
    """创建简单的Twitter卡片风格图表"""
    try:
        logger.info("📱 创建Twitter卡片风格图表...")
        
        # 创建环形图
        categories = ['AI/ML', 'Blockchain', 'Cloud', 'IoT', 'Other']
        values = [40, 25, 20, 10, 5]
        colors = ['#1DA1F2', '#17BF63', '#FFAD1F', '#E0245E', '#9266CC']
        
        fig = go.Figure(data=go.Pie(
            labels=categories,
            values=values,
            hole=0.5,
            marker=dict(colors=colors, line=dict(color='white', width=3)),
            textinfo='label+percent',
            textfont=dict(size=14, color='white')
        ))
        
        # 添加中心文字
        fig.add_annotation(
            text="<b>100</b><br>总项目",
            x=0.5, y=0.5,
            font=dict(size=18, color=TWITTER_COLORS['secondary']),
            showarrow=False
        )
        
        fig.update_layout(
            title=dict(
                text="<b>📊 科技领域分布</b>",
                x=0.5,
                font=dict(size=22, family="Arial Black", color=TWITTER_COLORS['secondary'])
            ),
            height=600,
            width=1200,
            margin=dict(t=80, b=60, l=60, r=60),
            paper_bgcolor='white',
            showlegend=True,
            legend=dict(x=1, y=0.5, font=dict(size=12))
        )
        
        # 导出图片
        output_dir = Path("images")
        output_dir.mkdir(exist_ok=True)
        image_path = output_dir / f"twitter_card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        img_bytes = fig.to_image(
            format="png",
            width=1200,
            height=675,
            scale=2,
            engine="kaleido"
        )
        
        with open(image_path, 'wb') as f:
            f.write(img_bytes)
        
        if image_path.exists():
            file_size = image_path.stat().st_size // 1024
            logger.info(f"✅ Twitter卡片生成成功: {image_path.name} ({file_size}KB)")
            
            # 生成推文文本
            tweet_text = f"📊 科技领域实时分析！\n\n🏆 AI/ML领域占比最高: {values[0]}%\n📈 多元化发展趋势明显\n💡 总计 {sum(values)} 个项目正在追踪\n\n科技创新百花齐放！🚀\n\n#科技分析 #数据可视化 #AI"
            
            logger.info(f"📝 推文内容: {tweet_text}")
            return str(image_path), tweet_text
        else:
            logger.error("❌ Twitter卡片生成失败")
            return "", ""
            
    except Exception as e:
        logger.error(f"❌ Twitter卡片创建失败: {e}")
        return "", ""

def main():
    """主测试函数"""
    logger.info("🚀 开始简化版图片生成测试...")
    
    results = []
    
    # 1. 测试基本图表创建
    logger.info("\n" + "="*50)
    logger.info("测试1: 基本图表创建")
    logger.info("="*50)
    fig = create_simple_chart()
    results.append(("基本图表创建", fig is not None))
    
    # 2. 测试Kaleido导出
    logger.info("\n" + "="*50) 
    logger.info("测试2: Kaleido图片导出")
    logger.info("="*50)
    kaleido_result = test_kaleido_export()
    results.append(("Kaleido导出", kaleido_result != False))
    
    # 3. 测试HTML导出
    logger.info("\n" + "="*50)
    logger.info("测试3: HTML导出")
    logger.info("="*50)
    html_result = test_html_export()
    results.append(("HTML导出", html_result != False))
    
    # 4. 测试Twitter卡片
    logger.info("\n" + "="*50)
    logger.info("测试4: Twitter卡片风格")
    logger.info("="*50)
    card_image, card_tweet = create_twitter_card_simple()
    results.append(("Twitter卡片", card_image != ""))
    
    # 总结
    logger.info("\n" + "="*60)
    logger.info("🎯 测试结果总结")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {test_name:<20} : {status}")
    
    logger.info(f"\n📊 测试统计: {passed}/{len(results)} 项通过")
    
    if passed == len(results):
        logger.info("🎉 所有测试通过！图片生成系统可用")
    else:
        logger.warning(f"⚠️ {len(results) - passed} 项测试失败")
    
    # 显示生成的文件
    for dir_name in ["images", "charts"]:
        dir_path = Path(dir_name)
        if dir_path.exists():
            files = list(dir_path.glob("*"))
            if files:
                logger.info(f"\n📁 {dir_name} 目录文件:")
                for file_path in files[-3:]:  # 显示最新3个文件
                    if file_path.is_file():
                        size = file_path.stat().st_size // 1024
                        logger.info(f"   📄 {file_path.name} ({size}KB)")

if __name__ == "__main__":
    main()
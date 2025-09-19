#!/usr/bin/env python3
"""字体诊断脚本 - 检测中文显示问题"""

import sys
from pathlib import Path
import logging
import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.graph_objects as go
import plotly.io as pio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_system_fonts():
    """测试系统字体"""
    logger.info("🔍 检查系统字体...")
    
    # 查找中文相关字体
    all_fonts = fm.findSystemFonts()
    chinese_fonts = []
    
    chinese_keywords = ['SimHei', 'Arial Unicode', 'PingFang', 'Hiragino', 'STHeiti', 'Microsoft YaHei']
    
    for font_path in all_fonts:
        font_name = os.path.basename(font_path)
        for keyword in chinese_keywords:
            if keyword.lower() in font_name.lower():
                chinese_fonts.append(font_path)
                break
    
    logger.info(f"找到 {len(chinese_fonts)} 个中文相关字体:")
    for font in chinese_fonts[:10]:  # 只显示前10个
        logger.info(f"  📁 {font}")
    
    return chinese_fonts

def test_pil_fonts():
    """测试PIL字体加载"""
    logger.info("🖼️ 测试PIL字体加载...")
    
    # 测试常见的macOS中文字体路径
    font_paths = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc", 
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc"
    ]
    
    working_fonts = []
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 24)
                logger.info(f"✅ PIL成功加载: {os.path.basename(font_path)}")
                working_fonts.append(font_path)
            else:
                logger.info(f"❌ 字体文件不存在: {font_path}")
        except Exception as e:
            logger.info(f"❌ PIL加载失败 {os.path.basename(font_path)}: {e}")
    
    return working_fonts

def test_chinese_text_rendering():
    """测试中文文本渲染"""
    logger.info("🎨 测试中文文本渲染...")
    
    test_text = "中文测试 AI人工智能 📊数据分析"
    
    # 1. 测试PIL渲染
    try:
        # 创建测试图像
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # 尝试不同的字体
        font_paths = [
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc"
        ]
        
        success = False
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 24)
                    draw.text((10, 10), test_text, font=font, fill='black')
                    
                    # 保存测试图片
                    test_img_path = Path("images") / "chinese_text_test.png"
                    test_img_path.parent.mkdir(exist_ok=True)
                    img.save(test_img_path)
                    
                    logger.info(f"✅ PIL中文渲染成功: {test_img_path}")
                    logger.info(f"   使用字体: {os.path.basename(font_path)}")
                    success = True
                    break
            except Exception as e:
                continue
        
        if not success:
            # 使用默认字体
            font = ImageFont.load_default()
            draw.text((10, 10), test_text, font=font, fill='black')
            test_img_path = Path("images") / "chinese_text_test_default.png"
            test_img_path.parent.mkdir(exist_ok=True)
            img.save(test_img_path)
            logger.warning(f"⚠️ 使用默认字体渲染: {test_img_path}")
            
    except Exception as e:
        logger.error(f"❌ PIL中文渲染失败: {e}")

def test_matplotlib_chinese():
    """测试matplotlib中文显示"""
    logger.info("📊 测试matplotlib中文显示...")
    
    try:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans GB', 'Arial Unicode MS', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建测试图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['人工智能', '区块链', '云计算', '物联网', '大数据']
        values = [25, 18, 15, 10, 8]
        
        bars = ax.bar(categories, values)
        ax.set_title('科技领域热度分析', fontsize=16, fontweight='bold')
        ax.set_ylabel('热度值', fontsize=12)
        ax.set_xlabel('技术领域', fontsize=12)
        
        # 旋转x轴标签以避免重叠
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表
        test_chart_path = Path("images") / "matplotlib_chinese_test.png"
        test_chart_path.parent.mkdir(exist_ok=True)
        plt.savefig(test_chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ matplotlib中文渲染成功: {test_chart_path}")
        
    except Exception as e:
        logger.error(f"❌ matplotlib中文渲染失败: {e}")

def test_plotly_chinese():
    """测试Plotly中文显示"""
    logger.info("📈 测试Plotly中文显示...")
    
    try:
        # 创建测试数据
        categories = ['人工智能', '区块链', '云计算', '物联网', '大数据']
        values = [25, 18, 15, 10, 8]
        
        # 创建柱状图
        fig = go.Figure(data=go.Bar(
            x=categories,
            y=values,
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ))
        
        fig.update_layout(
            title=dict(
                text="科技领域热度分析",
                font=dict(size=18, family="Arial, sans-serif")
            ),
            xaxis=dict(
                title="技术领域",
                title_font=dict(size=14)
            ),
            yaxis=dict(
                title="热度值", 
                title_font=dict(size=14)
            ),
            font=dict(family="Arial, sans-serif"),
            height=500,
            width=800
        )
        
        # 保存HTML
        html_path = Path("charts") / "plotly_chinese_test.html"
        html_path.parent.mkdir(exist_ok=True)
        fig.write_html(str(html_path))
        logger.info(f"✅ Plotly HTML生成成功: {html_path}")
        
        # 尝试导出PNG (需要kaleido)
        try:
            img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
            png_path = Path("images") / "plotly_chinese_test.png"
            png_path.parent.mkdir(exist_ok=True)
            
            with open(png_path, 'wb') as f:
                f.write(img_bytes)
            logger.info(f"✅ Plotly PNG导出成功: {png_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Plotly PNG导出失败: {e}")
            
    except Exception as e:
        logger.error(f"❌ Plotly中文测试失败: {e}")

def analyze_font_issues():
    """分析字体问题"""
    logger.info("🔍 分析字体问题...")
    
    issues = []
    
    # 检查matplotlib配置
    current_fonts = plt.rcParams['font.sans-serif']
    if 'SimHei' not in current_fonts and 'Hiragino Sans GB' not in current_fonts:
        issues.append("matplotlib未配置中文字体")
    
    # 检查PIL字体路径
    common_chinese_fonts = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc"
    ]
    
    available_fonts = [f for f in common_chinese_fonts if os.path.exists(f)]
    if not available_fonts:
        issues.append("PIL无法找到中文字体文件")
    
    # 检查依赖
    try:
        import kaleido
        logger.info("✅ kaleido可用于Plotly图片导出")
    except ImportError:
        issues.append("缺少kaleido依赖，无法导出Plotly图片")
    
    return issues

def recommend_solutions(issues):
    """推荐解决方案"""
    logger.info("💡 推荐解决方案:")
    
    solutions = {
        "matplotlib未配置中文字体": [
            "在代码中添加: plt.rcParams['font.sans-serif'] = ['Hiragino Sans GB', 'Arial Unicode MS']",
            "或使用: matplotlib.font_manager.fontManager.addfont('/path/to/chinese/font.ttf')"
        ],
        "PIL无法找到中文字体文件": [
            "检查macOS系统字体路径: /System/Library/Fonts/",
            "使用fontforge或其他工具验证字体文件完整性",
            "考虑下载并安装中文字体包"
        ],
        "缺少kaleido依赖，无法导出Plotly图片": [
            "安装kaleido: pip install kaleido",
            "或使用selenium作为备用导出方案"
        ]
    }
    
    for issue in issues:
        if issue in solutions:
            logger.info(f"\n🔧 问题: {issue}")
            for i, solution in enumerate(solutions[issue], 1):
                logger.info(f"   {i}. {solution}")

def main():
    """主诊断函数"""
    logger.info("🚀 开始字体诊断...")
    logger.info("="*60)
    
    # 创建输出目录
    Path("images").mkdir(exist_ok=True)
    Path("charts").mkdir(exist_ok=True)
    
    # 执行各项测试
    system_fonts = test_system_fonts()
    logger.info("-" * 40)
    
    working_fonts = test_pil_fonts() 
    logger.info("-" * 40)
    
    test_chinese_text_rendering()
    logger.info("-" * 40)
    
    test_matplotlib_chinese()
    logger.info("-" * 40)
    
    test_plotly_chinese()
    logger.info("-" * 40)
    
    # 分析问题
    issues = analyze_font_issues()
    
    logger.info("="*60)
    logger.info("🎯 诊断总结")
    logger.info("="*60)
    
    logger.info(f"系统中文字体数量: {len(system_fonts)}")
    logger.info(f"PIL可用字体数量: {len(working_fonts)}")
    logger.info(f"发现问题数量: {len(issues)}")
    
    if issues:
        logger.info("\n❌ 发现的问题:")
        for i, issue in enumerate(issues, 1):
            logger.info(f"  {i}. {issue}")
        
        recommend_solutions(issues)
    else:
        logger.info("✅ 未发现明显的字体问题")
    
    # 显示生成的测试文件
    test_files = []
    for directory in [Path("images"), Path("charts")]:
        if directory.exists():
            test_files.extend(directory.glob("*chinese_test*"))
    
    if test_files:
        logger.info(f"\n📁 生成的测试文件:")
        for file_path in test_files:
            logger.info(f"  📄 {file_path}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""可视化功能测试脚本

测试科技数据收集和图表生成功能
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from react_agent.data_collector import TechDataCollector
from react_agent.tech_visualizer import TechVisualizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_data_collection():
    """测试数据收集功能"""
    logger.info("🧪 测试数据收集功能...")
    
    try:
        collector = TechDataCollector()
        
        # 测试网络趋势收集（使用示例数据避免API调用）
        logger.info("📊 使用示例数据测试...")
        sample_data = collector.get_sample_data()
        logger.info(f"✅ 示例数据: {sample_data}")
        
        # 如果有API密钥，可以测试实际数据收集
        # trends_data = await collector.collect_web_trends()
        # metrics_data = await collector.collect_keyword_metrics()
        
        return sample_data
        
    except Exception as e:
        logger.error(f"❌ 数据收集测试失败: {e}")
        return None


async def test_visualization():
    """测试可视化功能"""
    logger.info("🎨 测试可视化功能...")
    
    try:
        visualizer = TechVisualizer()
        
        # 获取测试数据
        collector = TechDataCollector()
        test_data = collector.get_sample_data()
        
        logger.info("📊 生成测试图表...")
        
        # 逐个测试图表生成
        charts = []
        
        # 1. 关键词趋势图
        logger.info("  🔍 生成关键词趋势图...")
        chart1 = await visualizer.create_keyword_trends_chart(test_data)
        if chart1:
            charts.append(chart1)
            logger.info(f"    ✅ 关键词趋势图: {Path(chart1).name}")
        
        # 2. 科技分类饼图
        logger.info("  📊 生成科技分类饼图...")
        chart2 = await visualizer.create_tech_categories_pie_chart(test_data)
        if chart2:
            charts.append(chart2)
            logger.info(f"    ✅ 科技分类饼图: {Path(chart2).name}")
        
        # 3. 趋势时间线图
        logger.info("  📈 生成趋势时间线图...")
        chart3 = await visualizer.create_trend_timeline_chart()
        if chart3:
            charts.append(chart3)
            logger.info(f"    ✅ 趋势时间线图: {Path(chart3).name}")
        
        # 4. 关键词热力图
        logger.info("  🔥 生成关键词热力图...")
        chart4 = await visualizer.create_heatmap_chart(test_data)
        if chart4:
            charts.append(chart4)
            logger.info(f"    ✅ 关键词热力图: {Path(chart4).name}")
        
        # 5. 综合仪表板
        logger.info("  🚀 生成综合仪表板...")
        chart5 = await visualizer.create_dashboard(test_data)
        if chart5:
            charts.append(chart5)
            logger.info(f"    ✅ 综合仪表板: {Path(chart5).name}")
        
        logger.info(f"✅ 成功生成 {len(charts)} 个图表:")
        for i, chart in enumerate(charts, 1):
            chart_path = Path(chart)
            logger.info(f"  {i}. {chart_path.name}")
            logger.info(f"     路径: {chart_path.absolute()}")
        
        return charts
        
    except Exception as e:
        logger.error(f"❌ 可视化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []


async def test_full_integration():
    """测试完整集成功能"""
    logger.info("🔄 测试完整集成功能...")
    
    try:
        # 初始化组件
        collector = TechDataCollector()
        visualizer = TechVisualizer()
        
        # 1. 数据收集
        logger.info("1️⃣ 数据收集阶段...")
        data = collector.get_sample_data()
        logger.info(f"   📊 收集到关键词: {len(data.get('keywords_count', {}))}")
        logger.info(f"   📈 科技分类数量: {len(data.get('tech_categories', {}))}")
        
        # 2. 生成所有图表
        logger.info("2️⃣ 图表生成阶段...")
        charts = await visualizer.generate_all_charts(data)
        
        if charts:
            logger.info(f"   ✅ 成功生成 {len(charts)} 个图表")
            
            # 3. 获取图表URL
            urls = visualizer.get_chart_urls(charts)
            logger.info(f"   🔗 生成 {len(urls)} 个图表URL")
            
            for i, url in enumerate(urls, 1):
                logger.info(f"      {i}. {url}")
        else:
            logger.warning("   ⚠️ 未能生成任何图表")
        
        logger.info("✅ 完整集成测试完成")
        return charts
        
    except Exception as e:
        logger.error(f"❌ 完整集成测试失败: {e}")
        return []


async def main():
    """主测试函数"""
    logger.info("🚀 开始可视化功能测试...")
    
    # 加载环境变量
    load_dotenv()
    
    try:
        # 1. 测试数据收集
        logger.info("\n" + "="*50)
        logger.info("第一阶段：数据收集测试")
        logger.info("="*50)
        data = await test_data_collection()
        
        # 2. 测试可视化
        logger.info("\n" + "="*50)
        logger.info("第二阶段：可视化测试")  
        logger.info("="*50)
        charts = await test_visualization()
        
        # 3. 测试完整集成
        logger.info("\n" + "="*50)
        logger.info("第三阶段：完整集成测试")
        logger.info("="*50)
        integration_charts = await test_full_integration()
        
        # 总结
        logger.info("\n" + "="*50)
        logger.info("测试总结")
        logger.info("="*50)
        logger.info(f"✅ 数据收集: {'成功' if data else '失败'}")
        logger.info(f"✅ 可视化生成: 成功生成 {len(charts)} 个图表")
        logger.info(f"✅ 完整集成: 成功生成 {len(integration_charts)} 个图表")
        
        if charts or integration_charts:
            logger.info("\n📂 图表文件位置:")
            charts_dir = Path("charts")
            if charts_dir.exists():
                for chart_file in charts_dir.glob("*.html"):
                    logger.info(f"   📊 {chart_file.name}")
                logger.info(f"\n💡 可以在浏览器中打开这些文件查看图表")
                logger.info(f"   图表目录: {charts_dir.absolute()}")
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
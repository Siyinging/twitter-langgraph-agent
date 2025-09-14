#!/usr/bin/env python3
"""测试实时新闻集成和发布系统"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.react_agent.real_time_news import RealTimeNewsCollector
from src.react_agent.content_generator import TechContentGenerator
from src.react_agent.enhanced_content_reviewer import EnhancedContentReviewSystem

async def test_real_time_integration():
    """测试实时新闻集成"""
    print("🧪 开始测试实时新闻集成系统...")
    
    # 1. 测试新闻收集器
    print("\n=== 1. 测试新闻收集器 ===")
    news_collector = RealTimeNewsCollector()
    
    try:
        # 获取缓存新闻或收集新闻
        news_data = await news_collector.get_cached_news(max_age_hours=4)
        if not news_data:
            print("📡 缓存过期，收集最新新闻...")
            news_data = await news_collector.collect_latest_news(hours_back=12, max_results_per_category=3)
        else:
            print("✅ 使用缓存新闻数据")
        
        # 显示收集结果
        for category, news_list in news_data.items():
            print(f"📰 {category}: {len(news_list)}条新闻")
            for news in news_list[:2]:
                print(f"  • {news.title[:60]}... (质量: {news.quality_score:.2f})")
    
    except Exception as e:
        print(f"❌ 新闻收集失败: {e}")
        return
    
    # 2. 测试内容生成器
    print("\n=== 2. 测试内容生成器 ===")
    generator = TechContentGenerator()
    
    try:
        # 测试头条生成
        print("📰 生成今日头条...")
        headlines = await generator.generate_daily_headlines()
        print("头条内容:")
        print(headlines)
        print(f"字数: {len(headlines)}")
        
        # 测试线程生成
        print("\n📝 生成智慧线程...")
        thread = await generator.generate_wisdom_ai_thread()
        print(f"线程长度: {len(thread)}条")
        for i, tweet in enumerate(thread[:3], 1):
            print(f"  {i}. {tweet[:80]}...")
        
        # 测试中医科技内容
        print("\n🏥 生成中医科技专题...")
        tcm_content = await generator.generate_daily_tcm_tech_content()
        print("中医科技内容:")
        print(tcm_content)
        print(f"字数: {len(tcm_content)}")
    
    except Exception as e:
        print(f"❌ 内容生成失败: {e}")
        return
    
    # 3. 测试增强复查系统
    print("\n=== 3. 测试增强复查系统 ===")
    reviewer = EnhancedContentReviewSystem()
    
    try:
        # 创建测试草稿
        test_content = "🔥 AI技术重大突破！最新研究显示人工智能在医疗诊断领域取得显著进展，准确率提升至95%以上。这项创新将revolutionize传统医疗模式。#AI #医疗科技 #创新突破"
        
        print("📝 创建增强草稿...")
        from src.react_agent.enhanced_content_reviewer import UrgencyLevel
        
        draft_id = await reviewer.create_enhanced_draft(
            content_type="breaking_news",
            content=test_content,
            urgency=UrgencyLevel.HIGH,
            expires_hours=24
        )
        
        print(f"✅ 草稿创建成功: {draft_id}")
        
        # 预览内容质量评估
        preview = await reviewer.enhanced_preview_content(draft_id)
        print("\n质量评估结果:")
        quality = preview.get('quality', {})
        print(f"  总分: {quality.get('overall_score', 0):.2f}")
        print(f"  时效性: {quality.get('timeliness', 0):.2f}")
        print(f"  准确性: {quality.get('accuracy', 0):.2f}")
        print(f"  吸引力: {quality.get('engagement', 0):.2f}")
        print(f"  可读性: {quality.get('readability', 0):.2f}")
        
        if quality.get('issues'):
            print(f"  问题: {quality.get('issues')}")
        if quality.get('recommendations'):
            print(f"  建议: {quality.get('recommendations')}")
    
    except Exception as e:
        print(f"❌ 复查系统测试失败: {e}")
        return
    
    print("\n🎉 实时新闻集成系统测试完成!")
    print("✅ 系统各组件运行正常，实效性内容生成和审核功能已就绪")

if __name__ == "__main__":
    asyncio.run(test_real_time_integration())
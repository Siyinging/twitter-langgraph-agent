#!/usr/bin/env python3
"""发布AI头条推文"""

import sys
import asyncio
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from react_agent.enhanced_visualizer import EnhancedVisualizer
from react_agent.twitter_publisher import TwitterPublisher

async def publish_ai_headlines():
    """发布AI头条推文"""
    try:
        print("🚀 开始生成AI头条图表和推文...")
        
        # 初始化组件
        visualizer = EnhancedVisualizer()
        publisher = TwitterPublisher()
        
        # 生成AI趋势图表
        print("📊 生成AI技术趋势图表...")
        image_path, generated_tweet = await visualizer.create_twitter_trend_card(
            title="今日AI头条热度指数",
            data={
                "模型突破": 95,
                "自动驾驶": 88, 
                "医疗AI": 85,
                "AI伦理": 78,
                "AI创作": 82
            },
            chart_type="radar"
        )
        
        if not image_path:
            print("❌ 图表生成失败")
            return False
            
        print(f"✅ 图表生成成功: {image_path}")
        
        # 用户指定的推文内容
        tweet_content = """📊 今日AI头条 #AI新闻 #科技前沿

1. OpenAI新模型突破语言理解瓶颈
2. 自动驾驶AI在复杂路况测试中表现优异
3. AI辅助癌症诊断准确率提升15%
4. 伦理AI: 新框架解决偏见问题
5. AI创作音乐登上Billboard榜单

点击查看详细信息图表👇
想深入了解哪个话题？"""
        
        # 发布推文
        print("🐦 发布推文到Twitter...")
        success = await publisher.post_tweet_with_media(tweet_content, image_path)
        
        if success:
            print("🎉 AI头条推文发布成功！")
            print(f"📝 推文内容:\n{tweet_content}")
            print(f"🖼️ 配图: {image_path}")
            return True
        else:
            print("❌ 推文发布失败")
            return False
            
    except Exception as e:
        print(f"❌ 发布AI头条时出错: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(publish_ai_headlines())
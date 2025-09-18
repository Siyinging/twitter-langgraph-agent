#!/usr/bin/env python3
"""智能媒体管理器 - 检测内容是否需要配图并自动生成"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
import os

from react_agent.image_generator import ImageGenerator
from react_agent.enhanced_visualizer import EnhancedVisualizer
from react_agent.tech_visualizer import TechVisualizer

logger = logging.getLogger(__name__)


class SmartMediaManager:
    """智能媒体管理器"""
    
    def __init__(self):
        self.image_generator = ImageGenerator()
        self.enhanced_visualizer = EnhancedVisualizer()
        self.tech_visualizer = TechVisualizer()
        
        # 创建媒体缓存目录
        self.media_cache_dir = Path("data/media_cache")
        self.media_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 需要配图的关键词
        self.image_required_patterns = [
            # 直接提及图片/图表
            r'图表|图片|截图|示意图|流程图|架构图|对比图',
            r'chart|graph|diagram|image|screenshot|visualization',
            r'可视化|数据图|统计图|趋势图',
            
            # 技术概念需要可视化
            r'架构|framework|系统设计|流程|算法',
            r'AI模型|神经网络|deep learning|machine learning',
            r'数据分析|performance|benchmark|对比',
            
            # 中医科技相关
            r'中医|TCM|穴位|脉诊|舌诊|方剂',
            r'传统医学|草药|针灸'
        ]
        
        # 图片生成提示模板
        self.image_prompts = {
            'tech_analysis': "Technology analysis chart showing {topic} with modern clean design",
            'ai_concept': "AI and machine learning concept illustration for {topic}",
            'tcm_tech': "Traditional Chinese Medicine meets modern technology illustration for {topic}",
            'data_viz': "Data visualization and analytics dashboard for {topic}",
            'system_arch': "System architecture diagram for {topic}",
            'comparison': "Comparison chart or infographic for {topic}"
        }
    
    def needs_image(self, content: str) -> Tuple[bool, List[str]]:
        """检测内容是否需要配图"""
        matches = []
        content_lower = content.lower()
        
        for pattern in self.image_required_patterns:
            found = re.findall(pattern, content_lower, re.IGNORECASE)
            if found:
                matches.extend(found)
        
        needs_img = len(matches) > 0
        
        if needs_img:
            logger.info(f"🎨 内容需要配图，匹配到关键词: {matches}")
        
        return needs_img, matches
    
    async def generate_image_for_content(self, content: str, content_type: str = "general") -> Optional[str]:
        """为内容生成合适的图片"""
        try:
            needs_img, keywords = self.needs_image(content)
            
            if not needs_img:
                logger.info("📝 内容无需配图")
                return None
            
            logger.info(f"🎨 开始为内容生成图片，关键词: {keywords}")
            
            # 根据内容类型和关键词选择生成策略
            image_path = await self._generate_contextual_image(content, keywords, content_type)
            
            if image_path:
                logger.info(f"✅ 图片生成成功: {image_path}")
                return image_path
            else:
                logger.warning("⚠️ 图片生成失败，尝试备用方案")
                return await self._generate_fallback_image(content_type)
                
        except Exception as e:
            logger.error(f"❌ 图片生成过程出错: {e}")
            return await self._generate_fallback_image(content_type)
    
    async def _generate_contextual_image(self, content: str, keywords: List[str], content_type: str) -> Optional[str]:
        """根据内容上下文生成图片"""
        try:
            # 分析内容主题
            theme = self._analyze_content_theme(content, keywords)
            
            # 生成缓存键
            cache_key = hashlib.md5(f"{content}_{theme}_{content_type}".encode()).hexdigest()[:12]
            cache_path = self.media_cache_dir / f"{cache_key}_{theme}.png"
            
            # 检查缓存
            if cache_path.exists():
                logger.info(f"📂 使用缓存图片: {cache_path}")
                return str(cache_path)
            
            # 生成提示词
            prompt = self._create_image_prompt(content, theme, keywords)
            
            # 尝试不同的生成策略
            strategies = [
                self._try_enhanced_visualizer,
                self._try_tech_visualizer,
                self._try_simple_chart
            ]
            
            for strategy in strategies:
                try:
                    image_path = await strategy(prompt, theme, cache_key)
                    if image_path:
                        return image_path
                except Exception as e:
                    logger.warning(f"生成策略失败: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 上下文图片生成失败: {e}")
            return None
    
    def _analyze_content_theme(self, content: str, keywords: List[str]) -> str:
        """分析内容主题"""
        content_lower = content.lower()
        
        # 主题优先级判断
        if any(word in content_lower for word in ['中医', 'tcm', '传统医学', '针灸', '脉诊']):
            return 'tcm_tech'
        elif any(word in content_lower for word in ['ai', 'artificial intelligence', '神经网络', 'machine learning']):
            return 'ai_concept'
        elif any(word in content_lower for word in ['数据', 'data', '分析', 'analytics', '统计']):
            return 'data_viz'
        elif any(word in content_lower for word in ['架构', 'architecture', '系统', 'system']):
            return 'system_arch'
        elif any(word in content_lower for word in ['对比', 'comparison', 'vs', '比较']):
            return 'comparison'
        else:
            return 'tech_analysis'
    
    def _create_image_prompt(self, content: str, theme: str, keywords: List[str]) -> str:
        """创建图片生成提示"""
        # 提取内容中的关键概念
        key_concept = self._extract_key_concept(content)
        
        base_prompt = self.image_prompts.get(theme, self.image_prompts['tech_analysis'])
        prompt = base_prompt.format(topic=key_concept)
        
        # 添加风格指导
        style_suffix = " in modern minimalist style, professional, clean, high-tech aesthetic"
        
        return prompt + style_suffix
    
    def _extract_key_concept(self, content: str) -> str:
        """从内容中提取关键概念"""
        # 简单的关键概念提取
        concepts = []
        
        # 技术词汇
        tech_words = ['AI', '人工智能', '机器学习', '深度学习', '量子计算', '区块链', 
                     '神经网络', '算法', '大数据', '云计算', '边缘计算']
        
        for word in tech_words:
            if word in content:
                concepts.append(word)
        
        # 中医相关
        tcm_words = ['中医', '传统医学', '针灸', '脉诊', '舌诊', '中药']
        for word in tcm_words:
            if word in content:
                concepts.append(word)
        
        if concepts:
            return concepts[0]
        else:
            return "technology innovation"
    
    async def _try_enhanced_visualizer(self, prompt: str, theme: str, cache_key: str) -> Optional[str]:
        """尝试使用增强可视化器"""
        try:
            logger.info("🎨 尝试使用增强可视化器生成图片")
            
            # 构造伪数据用于可视化
            mock_data = self._create_mock_data_for_theme(theme)
            
            # 生成图片
            results = await self.enhanced_visualizer.batch_generate_twitter_images(mock_data)
            
            if results:
                source_path, _ = results[0]  # 取第一个结果
                
                # 复制到缓存
                cache_path = self.media_cache_dir / f"{cache_key}_{theme}.png"
                import shutil
                shutil.copy2(source_path, cache_path)
                
                return str(cache_path)
                
        except Exception as e:
            logger.warning(f"增强可视化器策略失败: {e}")
            
        return None
    
    async def _try_tech_visualizer(self, prompt: str, theme: str, cache_key: str) -> Optional[str]:
        """尝试使用技术可视化器"""
        try:
            logger.info("📊 尝试使用技术可视化器生成图表")
            
            mock_data = self._create_mock_data_for_theme(theme)
            chart_files = await self.tech_visualizer.generate_all_charts(mock_data)
            
            if chart_files:
                # 选择最合适的图表
                source_path = chart_files[0]
                
                # 复制到缓存
                cache_path = self.media_cache_dir / f"{cache_key}_{theme}.png"
                import shutil
                shutil.copy2(source_path, cache_path)
                
                return str(cache_path)
                
        except Exception as e:
            logger.warning(f"技术可视化器策略失败: {e}")
            
        return None
    
    async def _try_simple_chart(self, prompt: str, theme: str, cache_key: str) -> Optional[str]:
        """尝试生成简单图表"""
        try:
            logger.info("📈 尝试生成简单图表")
            
            # 创建简单的概念图表
            cache_path = self.media_cache_dir / f"{cache_key}_{theme}.png"
            
            # 使用matplotlib创建简单图表
            await self._create_simple_concept_chart(theme, cache_path)
            
            if cache_path.exists():
                return str(cache_path)
                
        except Exception as e:
            logger.warning(f"简单图表策略失败: {e}")
            
        return None
    
    async def _create_simple_concept_chart(self, theme: str, output_path: Path):
        """创建简单的概念图表"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            import numpy as np
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['STHeiti Medium', 'STHeiti Light', 'Songti TC', 'Arial Unicode MS', 'DejaVu Sans', 'Helvetica']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # 根据主题创建不同的图表
            if theme == 'ai_concept':
                # AI概念图
                ax.text(5, 5, '🤖 AI Technology', fontsize=24, ha='center', fontweight='bold')
                ax.text(5, 4, 'Innovation & Progress', fontsize=16, ha='center', alpha=0.8)
                
                # 添加进度条
                progress_bar = patches.Rectangle((2, 2.5), 6, 0.5, 
                                               linewidth=2, edgecolor='blue', facecolor='lightblue')
                ax.add_patch(progress_bar)
                ax.text(5, 2.1, 'Development Progress', fontsize=12, ha='center')
                
            elif theme == 'tcm_tech':
                # 中医科技概念图
                ax.text(5, 5, '🏥 TCM + Technology', fontsize=22, ha='center', fontweight='bold')
                ax.text(5, 4, '传统智慧与现代科技融合', fontsize=14, ha='center', alpha=0.8)
                
                # 添加连接线
                ax.plot([2, 8], [3, 3], 'g-', linewidth=3, alpha=0.7)
                ax.text(1.5, 3.2, '传统医学', fontsize=12, ha='center', 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
                ax.text(8.5, 3.2, '现代科技', fontsize=12, ha='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
                
            else:
                # 通用科技图表
                ax.text(5, 5, '💡 Tech Innovation', fontsize=22, ha='center', fontweight='bold')
                ax.text(5, 4, 'Future Technology Trends', fontsize=14, ha='center', alpha=0.8)
                
                # 添加趋势线
                x = np.linspace(1, 9, 20)
                y = 2 + 0.5 * np.sin(x) + 0.1 * x
                ax.plot(x, y, 'b-', linewidth=3, alpha=0.7)
                ax.fill_between(x, 2, y, alpha=0.3, color='lightblue')
                ax.text(5, 1.5, 'Growth Trajectory', fontsize=12, ha='center')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"✅ 简单概念图表已生成: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ 简单图表生成失败: {e}")
            raise
    
    def _create_mock_data_for_theme(self, theme: str) -> Dict[str, Any]:
        """为主题创建模拟数据"""
        base_data = {
            "keywords_count": {"AI": 45, "Technology": 38, "Innovation": 32},
            "sentiment_data": {"positive": 0.65, "neutral": 0.25, "negative": 0.10},
            "tech_categories": {"AI": 30, "IoT": 25, "Blockchain": 20, "Cloud": 25}
        }
        
        if theme == 'tcm_tech':
            base_data["keywords_count"] = {"中医": 40, "AI": 35, "健康": 30}
            base_data["tech_categories"] = {"中医AI": 35, "数字化": 25, "远程诊疗": 20, "智能诊断": 20}
        elif theme == 'ai_concept':
            base_data["keywords_count"] = {"Machine Learning": 50, "Deep Learning": 40, "Neural Networks": 35}
        
        return base_data
    
    async def _generate_fallback_image(self, content_type: str) -> Optional[str]:
        """生成备用图片"""
        try:
            logger.info("🔄 生成备用图片")
            
            fallback_path = self.media_cache_dir / f"fallback_{content_type}.png"
            
            # 如果备用图片已存在，直接返回
            if fallback_path.exists():
                return str(fallback_path)
            
            # 生成简单的备用图片
            await self._create_simple_concept_chart("tech_analysis", fallback_path)
            
            if fallback_path.exists():
                return str(fallback_path)
                
        except Exception as e:
            logger.error(f"❌ 备用图片生成失败: {e}")
        
        return None


# 全局实例
smart_media_manager = SmartMediaManager()


# 便利函数
async def check_and_generate_image(content: str, content_type: str = "general") -> Optional[str]:
    """检查内容并生成图片的便利函数"""
    return await smart_media_manager.generate_image_for_content(content, content_type)


if __name__ == "__main__":
    # 测试智能媒体管理器
    async def test_smart_media():
        manager = SmartMediaManager()
        
        test_contents = [
            "🔬 今天看到一个很有意思的AI架构图，显示了神经网络的层次结构",
            "分析了最新的数据图表，发现中医诊断准确率提升明显",
            "这是一个普通的科技新闻，没有涉及任何图片内容",
            "📊 通过可视化分析，我们可以看到量子计算的发展趋势"
        ]
        
        for i, content in enumerate(test_contents, 1):
            print(f"\n=== 测试内容 {i} ===")
            print(f"内容: {content}")
            
            needs_img, keywords = manager.needs_image(content)
            print(f"需要配图: {needs_img}")
            if needs_img:
                print(f"关键词: {keywords}")
                
                image_path = await manager.generate_image_for_content(content, f"test_{i}")
                if image_path:
                    print(f"✅ 生成图片: {image_path}")
                else:
                    print("❌ 图片生成失败")
            else:
                print("📝 无需配图")
    
    asyncio.run(test_smart_media())
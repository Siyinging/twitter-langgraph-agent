#!/usr/bin/env python3
"""图片生成模块

将可视化图表转换为图片格式，支持PNG、JPG等格式
用于Twitter等社交媒体平台的图片推文发布
"""

import asyncio
import logging
import os
import time
import base64
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import tempfile
import shutil

import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImageGenerator:
    """图片生成器 - 将图表转换为社交媒体友好的图片"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("images")
        self.output_dir.mkdir(exist_ok=True)
        
        # 图片配置
        self.image_config = {
            'width': 1200,
            'height': 800,
            'scale': 2,  # 高清图片
            'format': 'png'
        }
        
        # Twitter优化配置
        self.twitter_config = {
            'width': 1200,
            'height': 675,  # 16:9 比例，Twitter推荐
            'scale': 2,
            'format': 'png'
        }
        
        # 配置Plotly图像引擎
        try:
            import kaleido
            pio.kaleido.scope.default_width = self.image_config['width']
            pio.kaleido.scope.default_height = self.image_config['height']
            pio.kaleido.scope.default_scale = self.image_config['scale']
            self.kaleido_available = True
            logger.info("✅ Kaleido图像引擎可用")
        except ImportError:
            self.kaleido_available = False
            logger.warning("⚠️ Kaleido不可用，将使用Selenium备用方案")
        
        self.selenium_driver = None
    
    async def setup_selenium(self):
        """设置Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            logger.error("❌ Selenium不可用")
            return False
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={self.image_config["width"]},{self.image_config["height"]}')
            
            # 自动管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.selenium_driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("✅ Selenium WebDriver已配置")
            return True
            
        except Exception as e:
            logger.error(f"❌ Selenium配置失败: {e}")
            return False
    
    async def plotly_to_image(self, fig: go.Figure, filename: str, twitter_optimized: bool = True) -> Optional[str]:
        """将Plotly图表转换为图片"""
        try:
            config = self.twitter_config if twitter_optimized else self.image_config
            
            if self.kaleido_available:
                return await self._plotly_to_image_kaleido(fig, filename, config)
            elif SELENIUM_AVAILABLE:
                return await self._plotly_to_image_selenium(fig, filename, config)
            else:
                logger.error("❌ 没有可用的图片生成引擎")
                return None
                
        except Exception as e:
            logger.error(f"❌ 图表转图片失败: {e}")
            return None
    
    async def _plotly_to_image_kaleido(self, fig: go.Figure, filename: str, config: Dict[str, Any]) -> Optional[str]:
        """使用Kaleido将Plotly图表转换为图片"""
        try:
            image_path = self.output_dir / f"{filename}.{config['format']}"
            
            # 使用Kaleido生成图片
            img_bytes = fig.to_image(
                format=config['format'],
                width=config['width'],
                height=config['height'],
                scale=config['scale'],
                engine='kaleido'
            )
            
            with open(image_path, 'wb') as f:
                f.write(img_bytes)
            
            logger.info(f"✅ Kaleido图片生成: {image_path}")
            return str(image_path)
            
        except Exception as e:
            logger.error(f"❌ Kaleido图片生成失败: {e}")
            return None
    
    async def _plotly_to_image_selenium(self, fig: go.Figure, filename: str, config: Dict[str, Any]) -> Optional[str]:
        """使用Selenium将HTML转换为图片"""
        try:
            if not self.selenium_driver:
                await self.setup_selenium()
            
            if not self.selenium_driver:
                return None
            
            # 生成临时HTML文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                html_content = fig.to_html(
                    include_plotlyjs='cdn',
                    div_id='chart',
                    config={'displayModeBar': False}
                )
                f.write(html_content)
                temp_html = f.name
            
            # 使用Selenium截图
            self.selenium_driver.get(f'file://{temp_html}')
            time.sleep(2)  # 等待图表渲染
            
            image_path = self.output_dir / f"{filename}.{config['format']}"
            self.selenium_driver.save_screenshot(str(image_path))
            
            # 清理临时文件
            os.unlink(temp_html)
            
            logger.info(f"✅ Selenium图片生成: {image_path}")
            return str(image_path)
            
        except Exception as e:
            logger.error(f"❌ Selenium图片生成失败: {e}")
            return None
    
    async def html_to_image(self, html_file: str, output_filename: str = None) -> Optional[str]:
        """将HTML文件转换为图片"""
        try:
            html_path = Path(html_file)
            if not html_path.exists():
                logger.error(f"❌ HTML文件不存在: {html_file}")
                return None
            
            if output_filename is None:
                output_filename = html_path.stem
            
            if not self.selenium_driver:
                selenium_ok = await self.setup_selenium()
                if not selenium_ok:
                    return None
            
            # 加载HTML文件
            self.selenium_driver.get(f'file://{html_path.absolute()}')
            time.sleep(3)  # 等待页面完全渲染
            
            # 截图
            image_path = self.output_dir / f"{output_filename}.png"
            self.selenium_driver.save_screenshot(str(image_path))
            
            logger.info(f"✅ HTML转图片: {image_path}")
            return str(image_path)
            
        except Exception as e:
            logger.error(f"❌ HTML转图片失败: {e}")
            return None
    
    async def create_twitter_card(self, title: str, subtitle: str = None, stats: Dict[str, str] = None,
                                logo_text: str = "TechAnalytics") -> str:
        """创建Twitter卡片样式的图片"""
        try:
            # 创建画布
            width, height = 1200, 675
            img = Image.new('RGB', (width, height), color='#1a365d')
            draw = ImageDraw.Draw(img)
            
            try:
                # 尝试使用系统字体
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 48)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 24)
                stats_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 20)
                logo_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 28)
            except:
                # 备用默认字体
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                stats_font = ImageFont.load_default()
                logo_font = ImageFont.load_default()
            
            # 绘制背景渐变（简化版）
            for i in range(height):
                alpha = i / height
                color = (
                    int(26 + (63 - 26) * alpha),    # R
                    int(54 + (179 - 54) * alpha),   # G  
                    int(93 + (237 - 93) * alpha)    # B
                )
                draw.rectangle([0, i, width, i+1], fill=color)
            
            # 绘制标题
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_w = title_bbox[2] - title_bbox[0]
            draw.text(((width - title_w) // 2, 150), title, font=title_font, fill='white')
            
            # 绘制副标题
            if subtitle:
                subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
                draw.text(((width - subtitle_w) // 2, 220), subtitle, font=subtitle_font, fill='#e2e8f0')
            
            # 绘制统计数据
            if stats:
                y_start = 320
                x_positions = [200, 400, 600, 800, 1000]
                for i, (key, value) in enumerate(stats.items()):
                    if i >= len(x_positions):
                        break
                    
                    x = x_positions[i]
                    # 数值
                    value_bbox = draw.textbbox((0, 0), str(value), font=stats_font)
                    value_w = value_bbox[2] - value_bbox[0]
                    draw.text((x - value_w // 2, y_start), str(value), font=stats_font, fill='#4ade80')
                    
                    # 标签
                    key_bbox = draw.textbbox((0, 0), key, font=stats_font)
                    key_w = key_bbox[2] - key_bbox[0]
                    draw.text((x - key_w // 2, y_start + 30), key, font=stats_font, fill='#cbd5e1')
            
            # 绘制品牌标识
            draw.text((50, height - 80), logo_text, font=logo_font, fill='#94a3b8')
            
            # 绘制时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            draw.text((width - 200, height - 50), timestamp, font=stats_font, fill='#64748b')
            
            # 保存图片
            image_path = self.output_dir / f"twitter_card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(image_path, 'PNG')
            
            logger.info(f"✅ Twitter卡片生成: {image_path}")
            return str(image_path)
            
        except Exception as e:
            logger.error(f"❌ Twitter卡片生成失败: {e}")
            return ""
    
    async def add_watermark(self, image_path: str, watermark_text: str = "TechAnalytics") -> str:
        """为图片添加水印"""
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # 设置水印属性
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 24)
            except:
                font = ImageFont.load_default()
            
            # 计算水印位置（右下角）
            watermark_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            watermark_w = watermark_bbox[2] - watermark_bbox[0]
            watermark_h = watermark_bbox[3] - watermark_bbox[1]
            
            x = img.width - watermark_w - 20
            y = img.height - watermark_h - 20
            
            # 添加半透明背景
            overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([x-10, y-5, x+watermark_w+10, y+watermark_h+5], 
                                 fill=(0, 0, 0, 128))
            
            # 合并水印背景
            img = img.convert('RGBA')
            img = Image.alpha_composite(img, overlay)
            
            # 添加水印文字
            draw = ImageDraw.Draw(img)
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 255))
            
            # 保存带水印的图片
            watermarked_path = image_path.replace('.png', '_watermarked.png')
            img.convert('RGB').save(watermarked_path, 'PNG')
            
            logger.info(f"✅ 水印添加完成: {watermarked_path}")
            return watermarked_path
            
        except Exception as e:
            logger.error(f"❌ 添加水印失败: {e}")
            return image_path  # 返回原图片
    
    async def optimize_for_twitter(self, image_path: str) -> str:
        """优化图片用于Twitter发布"""
        try:
            img = Image.open(image_path)
            
            # Twitter推荐尺寸: 1200x675 (16:9)
            target_width, target_height = 1200, 675
            
            # 计算缩放比例
            width_ratio = target_width / img.width
            height_ratio = target_height / img.height
            scale_ratio = min(width_ratio, height_ratio)
            
            # 缩放图片
            new_width = int(img.width * scale_ratio)
            new_height = int(img.height * scale_ratio)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 创建目标画布并居中放置图片
            canvas = Image.new('RGB', (target_width, target_height), color='white')
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
            canvas.paste(img_resized, (paste_x, paste_y))
            
            # 压缩并保存
            optimized_path = image_path.replace('.png', '_twitter.jpg')
            canvas.save(optimized_path, 'JPEG', quality=85, optimize=True)
            
            logger.info(f"✅ Twitter优化完成: {optimized_path}")
            return optimized_path
            
        except Exception as e:
            logger.error(f"❌ Twitter优化失败: {e}")
            return image_path
    
    async def generate_chart_image(self, fig: go.Figure, title: str, twitter_optimized: bool = True) -> Optional[str]:
        """生成图表图片的完整流程"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"chart_{title}_{timestamp}"
            
            # 1. 生成基础图片
            image_path = await self.plotly_to_image(fig, filename, twitter_optimized)
            if not image_path:
                return None
            
            # 2. 添加水印
            watermarked_path = await self.add_watermark(image_path, "科技数据分析 TechAnalytics")
            
            # 3. 如果需要Twitter优化
            if twitter_optimized:
                final_path = await self.optimize_for_twitter(watermarked_path)
            else:
                final_path = watermarked_path
            
            logger.info(f"✅ 图表图片生成完成: {final_path}")
            return final_path
            
        except Exception as e:
            logger.error(f"❌ 图表图片生成失败: {e}")
            return None
    
    def cleanup(self):
        """清理资源"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
                logger.info("✅ Selenium WebDriver已清理")
            except Exception as e:
                logger.error(f"❌ Selenium清理失败: {e}")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()
    
    async def batch_html_to_images(self, html_files: List[str]) -> List[str]:
        """批量将HTML文件转换为图片"""
        image_paths = []
        
        for html_file in html_files:
            try:
                image_path = await self.html_to_image(html_file)
                if image_path:
                    # 优化为Twitter格式
                    twitter_path = await self.optimize_for_twitter(image_path)
                    image_paths.append(twitter_path)
            except Exception as e:
                logger.error(f"❌ 批量转换失败 {html_file}: {e}")
        
        logger.info(f"✅ 批量转换完成，生成 {len(image_paths)} 张图片")
        return image_paths
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """获取图片信息"""
        try:
            img = Image.open(image_path)
            return {
                'path': image_path,
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_kb': os.path.getsize(image_path) // 1024
            }
        except Exception as e:
            logger.error(f"❌ 获取图片信息失败: {e}")
            return {'path': image_path, 'error': str(e)}
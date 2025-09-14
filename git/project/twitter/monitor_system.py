#!/usr/bin/env python3
"""系统监控脚本 - 监控发布状态和系统健康"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime, timezone
import time

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def check_system_status():
    """检查系统状态"""
    print("🔍 Twitter智能发布系统状态检查")
    print("=" * 50)
    
    # 检查日志文件
    log_file = Path("logs/intelligent_publisher.log")
    if log_file.exists():
        print("✅ 系统日志文件存在")
        # 读取最后几行日志
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                print("📝 最新日志:")
                for line in lines[-3:]:
                    print(f"   {line.strip()}")
    else:
        print("⚠️ 系统日志文件不存在")
    
    # 检查发布记录
    hash_file = Path("data/published_hashes.json")
    if hash_file.exists():
        try:
            with open(hash_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                hashes = data.get('hashes', [])
                updated = data.get('updated', 'unknown')
                print(f"✅ 已发布内容: {len(hashes)}条")
                print(f"📅 最后更新: {updated}")
        except Exception as e:
            print(f"❌ 读取发布记录失败: {e}")
    else:
        print("⚠️ 发布记录文件不存在")
    
    # 检查内容生成
    print("\n🧪 测试内容生成...")
    try:
        import asyncio
        from react_agent.authentic_content_generator import AuthenticContentGenerator
        
        async def test_content():
            generator = AuthenticContentGenerator()
            content = await generator.generate_authentic_headlines()
            return content
        
        content = asyncio.run(test_content())
        print(f"✅ 内容生成正常: {content[:50]}...")
    except Exception as e:
        print(f"❌ 内容生成失败: {e}")
    
    print("\n" + "=" * 50)

def show_next_publish_times():
    """显示下次发布时间"""
    now = datetime.now(timezone.utc)
    
    # 计算下次08:00 UTC发布时间
    next_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if now.hour >= 8:
        next_8am = next_8am.replace(day=next_8am.day + 1)
    
    # 计算下次14:00 UTC发布时间  
    next_2pm = now.replace(hour=14, minute=0, second=0, microsecond=0)
    if now.hour >= 14:
        next_2pm = next_2pm.replace(day=next_2pm.day + 1)
    
    print("⏰ 下次发布时间:")
    print(f"   🌅 科技头条: {next_8am.strftime('%Y-%m-%d %H:%M UTC')} (约{int((next_8am - now).total_seconds() / 3600)}小时后)")
    print(f"   🏥 中医科技: {next_2pm.strftime('%Y-%m-%d %H:%M UTC')} (约{int((next_2pm - now).total_seconds() / 3600)}小时后)")

def main():
    """主函数"""
    while True:
        try:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"🕐 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            check_system_status()
            show_next_publish_times()
            
            print("\n💡 提示:")
            print("   • 系统正在后台自动运行")
            print("   • 按 Ctrl+C 退出监控")
            print("   • 5秒后自动刷新...")
            
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 退出监控")
            break
        except Exception as e:
            print(f"❌ 监控异常: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
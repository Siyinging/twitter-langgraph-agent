#!/usr/bin/env python3
"""系统状态检查工具

无需微信通知，直接查看系统运行状态
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


def check_process_status():
    """检查进程状态"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        publisher_running = 'start_daily_publisher.py' in result.stdout
        monitor_running = 'monitoring_system.py' in result.stdout
        
        print("🔍 进程状态:")
        print(f"  发布系统: {'✅ 运行中' if publisher_running else '❌ 未运行'}")
        print(f"  监控系统: {'✅ 运行中' if monitor_running else '❌ 未运行'}")
        
        return publisher_running, monitor_running
    except Exception as e:
        print(f"❌ 检查进程失败: {e}")
        return False, False


def check_log_status():
    """检查日志状态"""
    log_file = Path("logs/publisher.log")
    
    if not log_file.exists():
        print("📋 日志状态: ❌ 日志文件不存在")
        return
    
    # 检查最近的日志
    file_stat = log_file.stat()
    last_modified = file_stat.st_mtime
    time_diff = time.time() - last_modified
    
    print("📋 日志状态:")
    print(f"  最后更新: {datetime.fromtimestamp(last_modified).strftime('%H:%M:%S')}")
    print(f"  距今: {int(time_diff/60)}分钟前")
    
    # 检查最近的日志内容
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-10:]  # 最近10行
            
        error_count = sum(1 for line in lines if '❌' in line or 'ERROR' in line)
        success_count = sum(1 for line in lines if '✅' in line)
        
        print(f"  最近状态: {success_count}个成功, {error_count}个错误")
        
        # 显示最近的重要日志
        print("\n📄 最近日志:")
        for line in lines[-3:]:
            if '✅' in line or '❌' in line or 'INFO' in line:
                print(f"  {line.strip()}")
                
    except Exception as e:
        print(f"  读取日志失败: {e}")


def check_scheduler_status():
    """检查调度器状态"""
    status_file = Path("logs/system_status.json")
    
    if status_file.exists():
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            print("⏰ 调度状态:")
            print(f"  系统健康: {status.get('overall_status', '未知')}")
            print(f"  进程运行: {'✅' if status.get('process_running') else '❌'}")
            print(f"  日志更新: {'✅' if status.get('log_recent') else '❌'}")
            print(f"  错误数量: {len(status.get('errors_found', []))}")
            
            if status.get('last_publish'):
                print(f"  最后发布: {status['last_publish']}")
                
        except Exception as e:
            print(f"⏰ 调度状态: ❌ 读取失败 ({e})")
    else:
        print("⏰ 调度状态: ⚠️ 状态文件不存在")


def show_next_schedule():
    """显示下一个发布时间"""
    now = datetime.now()
    schedule = [
        (6, 30, "创建内容草稿"),
        (7, 45, "发布已审核内容"), 
        (8, 0, "今日科技头条"),
        (12, 0, "AI+传统智慧线程"),
        (14, 0, "中医科技专题"),
        (16, 0, "精选转发内容"),
        (20, 0, "本周趋势回顾")
    ]
    
    print("\n📅 今日发布计划:")
    for hour, minute, task in schedule:
        time_str = f"{hour:02d}:{minute:02d}"
        if now.hour < hour or (now.hour == hour and now.minute < minute):
            status = "⏳ 待执行"
        else:
            status = "✅ 已执行"
        print(f"  {time_str} - {task} {status}")


def main():
    """主函数"""
    print("🔍 Twitter发布系统状态检查")
    print("=" * 50)
    
    # 检查进程
    publisher_running, monitor_running = check_process_status()
    print()
    
    # 检查日志
    check_log_status()
    print()
    
    # 检查调度器
    check_scheduler_status()
    
    # 显示发布计划
    show_next_schedule()
    
    print("\n" + "=" * 50)
    if publisher_running:
        print("🎉 系统运行正常！内容将按时间表自动发布")
    else:
        print("⚠️ 发布系统未运行，请检查并重启")
    
    print("\n💡 提示:")
    print("  • 运行此脚本随时查看系统状态")
    print("  • 查看日志: tail -f logs/publisher.log") 
    print("  • 查看监控: tail -f logs/monitor.log")


if __name__ == "__main__":
    main()
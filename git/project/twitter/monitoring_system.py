#!/usr/bin/env python3
"""系统监控和微信通知模块

监控Twitter发布系统运行状态，出现问题时发送微信通知
"""

import asyncio
import logging
import os
import time
import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WeChatNotifier:
    """微信通知器"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        # 企业微信机器人webhook（需要你提供）
        self.webhook_url = webhook_url or os.getenv("WECHAT_WEBHOOK_URL")
        
    async def send_notification(self, title: str, message: str, level: str = "warning"):
        """发送微信通知"""
        if not self.webhook_url:
            logger.warning("微信webhook未配置，无法发送通知")
            return False
            
        try:
            # 企业微信机器人消息格式
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"## {title}\n\n{message}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            
            response = requests.post(self.webhook_url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ 微信通知发送成功: {title}")
                return True
            else:
                logger.error(f"❌ 微信通知发送失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 发送微信通知出错: {e}")
            return False


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.notifier = WeChatNotifier()
        self.log_file = Path("logs/publisher.log")
        self.status_file = Path("logs/system_status.json")
        self.last_check_time = time.time()
        self.error_count = 0
        self.last_successful_publish = None
        
    async def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "process_running": False,
            "log_recent": False,
            "errors_found": [],
            "last_publish": None,
            "overall_status": "unknown"
        }
        
        try:
            # 1. 检查进程是否运行
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'start_daily_publisher.py' in result.stdout:
                health_status["process_running"] = True
                
            # 2. 检查日志文件
            if self.log_file.exists():
                # 检查最近的日志时间
                import stat
                file_stat = self.log_file.stat()
                last_modified = file_stat.st_mtime
                if time.time() - last_modified < 3600:  # 1小时内有日志
                    health_status["log_recent"] = True
                    
                # 检查错误
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    recent_lines = f.readlines()[-100:]  # 最近100行
                    for line in recent_lines:
                        if 'ERROR' in line or '❌' in line:
                            health_status["errors_found"].append(line.strip())
                            
                # 查找最后一次成功发布
                for line in reversed(recent_lines):
                    if '✅' in line and ('发布成功' in line or 'published' in line):
                        health_status["last_publish"] = line.strip()
                        break
            
            # 3. 综合判断状态
            if health_status["process_running"] and health_status["log_recent"] and len(health_status["errors_found"]) == 0:
                health_status["overall_status"] = "healthy"
            elif health_status["process_running"] and len(health_status["errors_found"]) < 5:
                health_status["overall_status"] = "warning"  
            else:
                health_status["overall_status"] = "critical"
                
        except Exception as e:
            health_status["errors_found"].append(f"监控系统错误: {str(e)}")
            health_status["overall_status"] = "critical"
            
        return health_status
    
    async def handle_issues(self, health_status: Dict[str, Any]):
        """处理发现的问题"""
        status = health_status["overall_status"]
        
        if status == "critical":
            await self.notifier.send_notification(
                "🚨 Twitter发布系统严重故障",
                f"系统状态: {status}\n"
                f"进程运行: {'✅' if health_status['process_running'] else '❌'}\n"
                f"日志更新: {'✅' if health_status['log_recent'] else '❌'}\n"
                f"错误数量: {len(health_status['errors_found'])}\n"
                f"需要立即检查和修复！",
                "critical"
            )
            
        elif status == "warning" and len(health_status["errors_found"]) > 0:
            await self.notifier.send_notification(
                "⚠️ Twitter发布系统警告",
                f"发现了一些错误，但系统仍在运行:\n" +
                "\n".join(health_status["errors_found"][-3:]) +  # 最近3个错误
                f"\n\n请关注系统状态",
                "warning"
            )
    
    async def send_daily_report(self):
        """发送每日状态报告"""
        health_status = await self.check_system_health()
        
        # 读取发布统计
        today = datetime.now().strftime("%Y-%m-%d")
        publish_log = Path(f"logs/daily_publisher/publish_log_{today}.json")
        
        stats = {"successful": 0, "failed": 0, "total": 0}
        if publish_log.exists():
            try:
                with open(publish_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    stats["total"] = len(logs)
                    stats["successful"] = len([l for l in logs if l.get("success")])
                    stats["failed"] = stats["total"] - stats["successful"]
            except:
                pass
        
        await self.notifier.send_notification(
            f"📊 Twitter发布系统日报 {today}",
            f"系统状态: {'✅ 正常' if health_status['overall_status'] == 'healthy' else '⚠️ 异常'}\n"
            f"今日发布: {stats['successful']}/{stats['total']} 成功\n"
            f"系统运行: {'✅' if health_status['process_running'] else '❌'}\n"
            f"最后发布: {health_status['last_publish'] or '暂无'}\n"
            f"\n明天继续自动发布科技与中医融合内容！",
            "info"
        )
    
    async def monitor_loop(self):
        """监控循环"""
        logger.info("🔍 启动系统监控...")
        
        while True:
            try:
                # 检查系统健康状态
                health_status = await self.check_system_health()
                
                # 保存状态
                with open(self.status_file, 'w', encoding='utf-8') as f:
                    json.dump(health_status, f, ensure_ascii=False, indent=2)
                
                # 处理问题
                if health_status["overall_status"] in ["critical", "warning"]:
                    await self.handle_issues(health_status)
                
                # 每天20:30发送日报
                now = datetime.now()
                if now.hour == 20 and now.minute == 30:
                    await self.send_daily_report()
                
                # 30分钟检查一次
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"❌ 监控循环出错: {e}")
                await asyncio.sleep(300)  # 5分钟后重试


async def main():
    """启动监控系统"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/monitor.log'),
            logging.StreamHandler()
        ]
    )
    
    monitor = SystemMonitor()
    
    # 发送启动通知
    await monitor.notifier.send_notification(
        "🚀 Twitter发布系统监控启动",
        "系统监控已启动，将每30分钟检查一次系统健康状态\n"
        "发布时间表:\n"
        "• 06:30 - 创建内容草稿\n"
        "• 07:45 - 发布已审核内容\n"  
        "• 08:00 - 今日科技头条\n"
        "• 12:00 - AI+传统智慧线程\n"
        "• 14:00 - 中医科技专题\n"
        "• 16:00 - 精选转发\n"
        "• 20:00 - 周报(周日)\n\n"
        "有问题会及时通知您！",
        "info"
    )
    
    # 启动监控循环
    await monitor.monitor_loop()


if __name__ == "__main__":
    asyncio.run(main())
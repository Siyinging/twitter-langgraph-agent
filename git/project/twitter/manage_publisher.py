#!/usr/bin/env python3
"""Twitter自动发布系统管理工具"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.react_agent.daily_publisher import DailyTechPublisher

class PublisherManager:
    """发布系统管理器"""
    
    def __init__(self):
        self.publisher = DailyTechPublisher()
        
    async def test_single_task(self, task_name: str):
        """测试单个发布任务"""
        print(f"🧪 测试 {task_name} 任务...")
        
        task_methods = {
            "headlines": self.publisher.publish_morning_headlines,
            "thread": self.publisher.publish_ai_thread,
            "tcm": self.publisher.publish_tcm_tech_focus,
            "retweet": self.publisher.publish_curated_retweet,
            "recap": self.publisher.publish_weekly_recap,
        }
        
        if task_name not in task_methods:
            print(f"❌ 未知任务: {task_name}")
            print(f"📋 可用任务: {', '.join(task_methods.keys())}")
            return
            
        try:
            result = await task_methods[task_name]()
            
            if result.get('success'):
                print(f"✅ {task_name} 测试成功")
                if result.get('tweet_id'):
                    print(f"🆔 推文ID: {result['tweet_id']}")
                if result.get('tweet_ids'):
                    print(f"🆔 线程推文IDs: {result['tweet_ids']}")
            else:
                print(f"❌ {task_name} 测试失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ {task_name} 测试异常: {e}")
            
    async def run_all_tests(self):
        """运行所有任务测试"""
        print("🧪 运行完整发布流程测试...")
        print("=" * 50)
        
        tasks = [
            ("headlines", "今日科技头条"),
            ("thread", "AI+传统智慧线程"),  
            ("tcm", "中医科技专题"),
            ("retweet", "精选转发"),
            ("recap", "本周回顾")
        ]
        
        results = []
        
        for task_key, task_name in tasks:
            print(f"\n🔄 测试 {task_name}...")
            
            try:
                if task_key == "headlines":
                    result = await self.publisher.publish_morning_headlines()
                elif task_key == "thread":
                    result = await self.publisher.publish_ai_thread()
                elif task_key == "tcm":
                    result = await self.publisher.publish_tcm_tech_focus()
                elif task_key == "retweet":
                    result = await self.publisher.publish_curated_retweet()
                elif task_key == "recap":
                    result = await self.publisher.publish_weekly_recap()
                    
                results.append((task_name, result.get('success', False), result.get('error')))
                
                if result.get('success'):
                    print(f"  ✅ {task_name} 成功")
                else:
                    print(f"  ❌ {task_name} 失败: {result.get('error')}")
                    
                # 任务间隔
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"  ❌ {task_name} 异常: {e}")
                results.append((task_name, False, str(e)))
                
        # 输出测试摘要
        print("\n" + "=" * 50)
        print("📊 测试结果摘要:")
        
        successful = [r for r in results if r[1]]
        failed = [r for r in results if not r[1]]
        
        print(f"✅ 成功: {len(successful)} 个任务")
        print(f"❌ 失败: {len(failed)} 个任务")
        
        if failed:
            print("\n❌ 失败任务详情:")
            for name, _, error in failed:
                print(f"  • {name}: {error}")
                
    async def check_status(self):
        """检查发布状态"""
        print("📊 检查今日发布状态...")
        
        try:
            status = await self.publisher.get_publish_status()
            
            if status.get('status') == 'no_logs':
                print("📝 今日暂无发布记录")
            else:
                print(f"📈 今日已执行 {status.get('total_tasks', 0)} 个任务")
                print(f"✅ 成功任务: {status.get('successful_tasks', 0)} 个")
                
                # 显示任务详情
                for task in status.get('tasks', [])[-5:]:  # 只显示最近5个
                    status_icon = "✅" if task.get('success') else "❌"
                    task_name = task.get('task', '未知')
                    time_str = task.get('time', '').split('T')[1][:5] if task.get('time') else '未知'
                    print(f"  {status_icon} {time_str} - {task_name}")
                    
        except Exception as e:
            print(f"❌ 状态检查失败: {e}")
            
    async def generate_test_content(self):
        """生成测试内容（不发布）"""
        print("📝 生成测试内容...")
        
        try:
            # 测试头条生成
            headlines = await self.publisher.content_generator.generate_daily_headlines()
            print(f"\n🌅 今日科技头条:")
            print(f"   {headlines}")
            print(f"   字数: {len(headlines)}")
            
            # 测试AI线程生成
            ai_thread = await self.publisher.content_generator.generate_wisdom_ai_thread()
            print(f"\n🧠 AI+传统智慧线程:")
            for i, content in enumerate(ai_thread, 1):
                print(f"   {i}. {content[:60]}... (字数: {len(content)})")
                
            # 测试中医科技专题
            tcm_content = await self.publisher.content_generator.generate_daily_tcm_tech_content()
            print(f"\n🏥 中医科技专题:")
            print(f"   {tcm_content}")
            print(f"   字数: {len(tcm_content)}")
            
            print("\n✅ 内容生成测试完成")
            
        except Exception as e:
            print(f"❌ 内容生成测试失败: {e}")

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🔧 Twitter自动发布系统管理工具")
        print("\n📋 使用方法:")
        print("  python manage_publisher.py <命令>")
        print("\n🛠️ 可用命令:")
        print("  test <task>     - 测试单个任务 (headlines/thread/tcm/retweet/recap)")
        print("  test-all        - 测试所有发布任务")
        print("  status          - 检查今日发布状态")
        print("  content         - 生成测试内容(不发布)")
        print("\n💡 示例:")
        print("  python manage_publisher.py test headlines")
        print("  python manage_publisher.py test-all")
        print("  python manage_publisher.py status")
        return
        
    command = sys.argv[1]
    manager = PublisherManager()
    
    if command == "test" and len(sys.argv) > 2:
        task = sys.argv[2]
        await manager.test_single_task(task)
        
    elif command == "test-all":
        await manager.run_all_tests()
        
    elif command == "status":
        await manager.check_status()
        
    elif command == "content":
        await manager.generate_test_content()
        
    else:
        print(f"❌ 未知命令: {command}")
        print("💡 运行 'python manage_publisher.py' 查看帮助")

if __name__ == "__main__":
    asyncio.run(main())
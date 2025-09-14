#!/usr/bin/env python3
"""每日科技内容发布器 - 整合所有每日发布功能

发布时间表:
08:00 - 今日科技头条 (Tech Headlines + TCM Tech)
12:00 - AI+传统智慧线程 (AI/TCM Wisdom Thread)  
14:00 - 中医科技专题 (Daily TCM Tech Focus)
16:00 - 模拟转发内容 (Curated Retweet)
20:00 - 本周趋势回顾 (Weekly Recap, 仅周日)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

from react_agent.content_generator import TechContentGenerator
from react_agent.thread_creator import TwitterThreadCreator, ThreadResult
from react_agent.content_reviewer import ContentReviewSystem
from react_agent.tools import post_tweet, quote_tweet
from react_agent.direct_publisher import direct_post_tweet, direct_post_thread, direct_post_with_media
from react_agent.smart_media_manager import check_and_generate_image

logger = logging.getLogger(__name__)


class DailyTechPublisher:
    """每日科技内容发布器"""
    
    def __init__(self, use_review_system: bool = True):
        self.content_generator = TechContentGenerator()
        self.thread_creator = TwitterThreadCreator()
        self.review_system = ContentReviewSystem() if use_review_system else None
        
        # 创建日志目录
        self.log_dir = Path("logs/daily_publisher")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    async def publish_approved_content(self) -> Dict[str, Any]:
        """发布已审核通过的内容"""
        if not self.review_system:
            return {"error": "复查系统未启用"}
        
        try:
            logger.info("📋 开始发布已审核通过的内容")
            approved_content = await self.review_system.get_approved_content()
            
            if not approved_content:
                logger.info("✅ 没有待发布的已审核内容")
                return {"message": "没有待发布的内容", "published": 0}
            
            published_count = 0
            results = []
            
            for draft in approved_content:
                try:
                    if isinstance(draft.content, list):
                        # 发布线程
                        thread_result = await direct_post_thread(draft.content)
                        if thread_result.get("success"):
                            tweet_ids = thread_result.get("tweet_ids", [])
                            await self.review_system.mark_as_published(draft.draft_id, tweet_ids)
                            published_count += 1
                            results.append({
                                "draft_id": draft.draft_id,
                                "type": "thread",
                                "tweet_ids": tweet_ids,
                                "success": True
                            })
                            logger.info(f"✅ 线程发布成功: {draft.draft_id}")
                    else:
                        # 发布单条推文
                        result = await direct_post_tweet(draft.content)
                        if result and result.get('success'):
                            tweet_id = result.get('tweet_id') or (result.get('data', {}).get('tweet_id') if isinstance(result.get('data'), dict) else None)
                            await self.review_system.mark_as_published(draft.draft_id, [tweet_id])
                            published_count += 1
                            results.append({
                                "draft_id": draft.draft_id,
                                "type": "single",
                                "tweet_ids": [tweet_id],
                                "success": True
                            })
                            logger.info(f"✅ 推文发布成功: {draft.draft_id}")
                        else:
                            results.append({
                                "draft_id": draft.draft_id,
                                "success": False,
                                "error": result.get('message', '发布失败') if result else '发布失败'
                            })
                            logger.error(f"❌ 推文发布失败: {draft.draft_id}")
                            
                except Exception as e:
                    results.append({
                        "draft_id": draft.draft_id,
                        "success": False,
                        "error": str(e)
                    })
                    logger.error(f"❌ 发布出错 {draft.draft_id}: {e}")
            
            return {
                "message": f"发布完成，成功 {published_count}/{len(approved_content)} 条",
                "published": published_count,
                "total": len(approved_content),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ 发布已审核内容出错: {e}")
            return {"error": str(e)}
    
    async def create_content_drafts_for_review(self) -> Dict[str, Any]:
        """创建内容草稿供审核（每日06:30执行）"""
        if not self.review_system:
            return {"error": "复查系统未启用"}
            
        try:
            logger.info("📝 开始创建每日内容草稿")
            created_drafts = []
            
            # 创建各类内容草稿
            draft_tasks = [
                ("headlines", self.content_generator.generate_daily_headlines),
                ("tcm_headlines", self.content_generator.generate_tcm_tech_headlines), 
                ("ai_thread", self.content_generator.generate_wisdom_ai_thread),
                ("tcm_focus", self.content_generator.generate_daily_tcm_tech_content),
            ]
            
            # 周日添加周报
            current_time = datetime.now(timezone.utc)
            if current_time.weekday() == 6:  # Sunday
                draft_tasks.append(("weekly_recap", self.content_generator.generate_weekly_recap))
            
            for content_type, generator_func in draft_tasks:
                try:
                    content = await generator_func()
                    metadata = {
                        "generated_at": current_time.isoformat(),
                        "content_type": content_type
                    }
                    
                    draft_id = await self.review_system.create_draft(content_type, content, metadata)
                    created_drafts.append({
                        "draft_id": draft_id,
                        "content_type": content_type,
                        "success": True
                    })
                    logger.info(f"✅ 创建草稿: {draft_id}")
                    
                except Exception as e:
                    created_drafts.append({
                        "content_type": content_type,
                        "success": False,
                        "error": str(e)
                    })
                    logger.error(f"❌ 创建草稿失败 {content_type}: {e}")
            
            return {
                "message": f"草稿创建完成: {len([d for d in created_drafts if d['success']])}/{len(created_drafts)}",
                "drafts": created_drafts
            }
            
        except Exception as e:
            logger.error(f"❌ 创建内容草稿出错: {e}")
            return {"error": str(e)}
        
    async def publish_morning_headlines(self) -> Dict[str, Any]:
        """08:00 发布今日科技头条（融合中医科技）"""
        try:
            logger.info("📰 开始发布今日科技头条")
            current_time = datetime.now(timezone.utc)
            
            # 50%概率发布传统科技头条，50%发布中医科技头条
            import random
            if random.random() < 0.5:
                logger.info("🔬 生成传统科技头条")
                headlines = await self.content_generator.generate_daily_headlines()
            else:
                logger.info("🏥 生成中医科技头条")
                headlines = await self.content_generator.generate_tcm_tech_headlines()
            
            # 检查是否需要配图
            image_path = await check_and_generate_image(headlines, "morning_headlines")
            
            # 发布推文（使用直接发布器避免context问题）
            if image_path:
                logger.info(f"📸 为头条配图: {image_path}")
                result = await direct_post_with_media(headlines, [image_path])
            else:
                result = await direct_post_tweet(headlines)
            
            publish_result = {
                "task": "morning_headlines",
                "time": current_time.isoformat(),
                "success": False,
                "content": headlines,
                "tweet_id": None,
                "error": None
            }
            
            if result and result.get('success'):
                tweet_id = result.get('tweet_id') or (result.get('data', {}).get('tweet_id') if isinstance(result.get('data'), dict) else None)
                publish_result.update({
                    "success": True,
                    "tweet_id": tweet_id,
                })
                logger.info(f"✅ 今日科技头条发布成功: {tweet_id}")
            else:
                error_msg = result.get('error', '发布失败') if result else '发布失败'
                publish_result["error"] = error_msg
                logger.error(f"❌ 今日科技头条发布失败: {error_msg}")
            
            # 记录发布日志
            await self._log_publish_result(publish_result)
            return publish_result
            
        except Exception as e:
            logger.error(f"❌ 发布今日科技头条出错: {e}")
            return {
                "task": "morning_headlines",
                "time": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def publish_ai_thread(self) -> Dict[str, Any]:
        """12:00 发布AI+传统智慧线程"""
        try:
            logger.info("🧠 开始发布AI+传统智慧线程")
            current_time = datetime.now(timezone.utc)
            
            # 生成智慧线程内容（轮换AI和中医科技）
            thread_content = await self.content_generator.generate_wisdom_ai_thread()
            
            # 创建线程（使用直接发布器）
            thread_result = await direct_post_thread(thread_content)
            
            publish_result = {
                "task": "ai_thread",
                "time": current_time.isoformat(),
                "success": thread_result.get("success", False),
                "tweet_ids": thread_result.get("tweet_ids", []),
                "thread_url": thread_result.get("thread_url"),
                "error": thread_result.get("error")
            }
            
            if thread_result.get("success"):
                tweet_count = len(thread_result.get("tweet_ids", []))
                logger.info(f"✅ 可持续AI线程发布成功: {tweet_count}条推文")
            else:
                error = thread_result.get("error", "未知错误")
                logger.error(f"❌ 可持续AI线程发布失败: {error}")
            
            # 记录发布日志
            await self._log_publish_result(publish_result)
            return publish_result
            
        except Exception as e:
            logger.error(f"❌ 发布可持续AI线程出错: {e}")
            return {
                "task": "ai_thread",
                "time": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def publish_tcm_tech_focus(self) -> Dict[str, Any]:
        """14:00 发布中医科技专题"""
        try:
            logger.info("🏥 开始发布中医科技专题")
            current_time = datetime.now(timezone.utc)
            
            # 生成中医科技专题内容
            tcm_content = await self.content_generator.generate_daily_tcm_tech_content()
            
            # 检查是否需要配图
            image_path = await check_and_generate_image(tcm_content, "tcm_tech_focus")
            
            # 发布推文
            if image_path:
                logger.info(f"📸 为中医科技专题配图: {image_path}")
                result = await direct_post_with_media(tcm_content, [image_path])
            else:
                result = await direct_post_tweet(tcm_content)
            
            publish_result = {
                "task": "tcm_tech_focus",
                "time": current_time.isoformat(),
                "success": False,
                "content": tcm_content,
                "tweet_id": None,
                "error": None
            }
            
            if result and result.get('success'):
                tweet_id = result.get('data', {}).get('id')
                publish_result.update({
                    "success": True,
                    "tweet_id": tweet_id,
                })
                logger.info(f"✅ 中医科技专题发布成功: {tweet_id}")
            else:
                error_msg = result.get('message', '发布失败') if result else '发布失败'
                publish_result["error"] = error_msg
                logger.error(f"❌ 中医科技专题发布失败: {error_msg}")
            
            # 记录发布日志
            await self._log_publish_result(publish_result)
            return publish_result
            
        except Exception as e:
            logger.error(f"❌ 发布中医科技专题出错: {e}")
            return {
                "task": "tcm_tech_focus",
                "time": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def publish_curated_retweet(self) -> Dict[str, Any]:
        """16:00 发布精选转发"""
        try:
            logger.info("🔄 开始发布精选转发")
            current_time = datetime.now(timezone.utc)
            
            # 寻找转发目标
            retweet_target = await self.content_generator.find_retweet_target()
            
            publish_result = {
                "task": "curated_retweet",
                "time": current_time.isoformat(),
                "success": False,
                "original_tweet_id": None,
                "quote_tweet_id": None,
                "comment": None,
                "error": None
            }
            
            if not retweet_target:
                publish_result["error"] = "未找到合适的转发目标"
                logger.warning("⚠️ 未找到合适的转发目标")
                await self._log_publish_result(publish_result)
                return publish_result
            
            # 执行引用转发
            quote_result = await quote_tweet(
                retweet_target["tweet_id"],
                retweet_target["comment"]
            )
            
            publish_result.update({
                "original_tweet_id": retweet_target["tweet_id"],
                "comment": retweet_target["comment"]
            })
            
            if quote_result and quote_result.get('success'):
                quote_tweet_id = quote_result.get('data', {}).get('id')
                publish_result.update({
                    "success": True,
                    "quote_tweet_id": quote_tweet_id
                })
                logger.info(f"✅ 精选转发发布成功: {quote_tweet_id}")
            else:
                error_msg = quote_result.get('message', '转发失败') if quote_result else '转发失败'
                publish_result["error"] = error_msg
                logger.error(f"❌ 精选转发失败: {error_msg}")
            
            # 记录发布日志
            await self._log_publish_result(publish_result)
            return publish_result
            
        except Exception as e:
            logger.error(f"❌ 发布精选转发出错: {e}")
            return {
                "task": "curated_retweet",
                "time": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def publish_weekly_recap(self) -> Dict[str, Any]:
        """20:00 发布周报（仅周日）"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # 检查是否为周日
            if current_time.weekday() != 6:  # 0=Monday, 6=Sunday
                logger.info("📊 今天不是周日，跳过周报发布")
                return {
                    "task": "weekly_recap",
                    "time": current_time.isoformat(),
                    "success": True,
                    "skipped": True,
                    "reason": "今天不是周日"
                }
            
            logger.info("📊 开始发布本周科技趋势回顾")
            
            # 生成周报内容
            recap_content = await self.content_generator.generate_weekly_recap()
            
            # 发布推文
            result = await direct_post_tweet(recap_content)
            
            publish_result = {
                "task": "weekly_recap",
                "time": current_time.isoformat(),
                "success": False,
                "content": recap_content,
                "tweet_id": None,
                "error": None
            }
            
            if result and result.get('success'):
                tweet_id = result.get('data', {}).get('id')
                publish_result.update({
                    "success": True,
                    "tweet_id": tweet_id
                })
                logger.info(f"✅ 本周回顾发布成功: {tweet_id}")
            else:
                error_msg = result.get('message', '发布失败') if result else '发布失败'
                publish_result["error"] = error_msg
                logger.error(f"❌ 本周回顾发布失败: {error_msg}")
            
            # 记录发布日志
            await self._log_publish_result(publish_result)
            return publish_result
            
        except Exception as e:
            logger.error(f"❌ 发布本周回顾出错: {e}")
            return {
                "task": "weekly_recap",
                "time": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def _log_publish_result(self, result: Dict[str, Any]):
        """记录发布结果日志"""
        try:
            current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log_file = self.log_dir / f"publish_log_{current_date}.json"
            
            import json
            
            # 读取现有日志
            existing_logs = []
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        existing_logs = json.load(f)
                except json.JSONDecodeError:
                    existing_logs = []
            
            # 添加新日志
            existing_logs.append(result)
            
            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.warning(f"⚠️ 记录发布日志失败: {e}")
    
    async def run_daily_schedule(self):
        """运行一天的完整发布计划（测试用）"""
        logger.info("🚀 开始运行每日发布计划")
        results = []
        
        # 模拟一天的发布任务
        tasks = [
            ("08:00", self.publish_morning_headlines),
            ("12:00", self.publish_ai_thread),
            ("14:00", self.publish_tcm_tech_focus),
            ("16:00", self.publish_curated_retweet),
            ("20:00", self.publish_weekly_recap)
        ]
        
        for time_str, task_func in tasks:
            logger.info(f"⏰ 执行 {time_str} 任务: {task_func.__name__}")
            result = await task_func()
            results.append(result)
            
            # 任务间隔30秒（测试时使用）
            await asyncio.sleep(30)
        
        # 输出总结
        successful_tasks = [r for r in results if r.get('success') and not r.get('skipped')]
        failed_tasks = [r for r in results if not r.get('success') and not r.get('skipped')]
        skipped_tasks = [r for r in results if r.get('skipped')]
        
        logger.info(f"📈 每日发布完成统计:")
        logger.info(f"  ✅ 成功: {len(successful_tasks)}个任务")
        logger.info(f"  ❌ 失败: {len(failed_tasks)}个任务")
        logger.info(f"  ⏭️  跳过: {len(skipped_tasks)}个任务")
        
        return {
            "total_tasks": len(results),
            "successful": len(successful_tasks),
            "failed": len(failed_tasks),
            "skipped": len(skipped_tasks),
            "results": results
        }
    
    async def get_publish_status(self, date: Optional[str] = None) -> Dict[str, Any]:
        """获取发布状态"""
        try:
            if not date:
                date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            log_file = self.log_dir / f"publish_log_{date}.json"
            
            if not log_file.exists():
                return {
                    "date": date,
                    "status": "no_logs",
                    "tasks": []
                }
            
            import json
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            return {
                "date": date,
                "status": "has_logs",
                "total_tasks": len(logs),
                "successful_tasks": len([l for l in logs if l.get('success')]),
                "tasks": logs
            }
            
        except Exception as e:
            logger.error(f"❌ 获取发布状态出错: {e}")
            return {
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试每日发布器
    async def test_daily_publisher():
        publisher = DailyTechPublisher()
        
        print("=== 每日发布器功能测试 ===\n")
        
        # 测试内容生成（不实际发布）
        print("1. 测试今日科技头条生成:")
        headlines = await publisher.content_generator.generate_daily_headlines()
        print(f"   内容: {headlines}")
        print(f"   字数: {len(headlines)}\n")
        
        print("2. 测试可持续AI线程生成:")
        ai_content = await publisher.content_generator.generate_sustainable_ai_thread()
        for i, content in enumerate(ai_content, 1):
            print(f"   {i}. {content[:60]}... (字数: {len(content)})")
        print()
        
        print("3. 测试转发目标搜索:")
        retweet_target = await publisher.content_generator.find_retweet_target()
        if retweet_target:
            print(f"   目标: {retweet_target['original_text']}")
            print(f"   评论: {retweet_target['comment']}")
        else:
            print("   未找到转发目标")
        print()
        
        print("4. 测试周报生成:")
        weekly_recap = await publisher.content_generator.generate_weekly_recap()
        print(f"   内容: {weekly_recap}")
        print(f"   字数: {len(weekly_recap)}\n")
        
        print("注意: 实际运行时会调用Twitter API发布内容")
        print("使用 python run_scheduler.py 启动定时发布")
    
    asyncio.run(test_daily_publisher())
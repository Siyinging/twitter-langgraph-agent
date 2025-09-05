# 每日科技内容发布系统

## 🎯 功能概述

这个系统每天自动发布4类科技内容到Twitter：

| 时间 | 内容类型 | 描述 |
|------|---------|------|
| 08:00 | 今日科技头条 | 汇总当天最重要的科技新闻 |
| 12:00 | 可持续AI线程 | 3-5条推文组成的原创线程，探讨绿色AI发展 |
| 16:00 | 精选转发 | 发现并转发优质科技内容，附加个人见解 |
| 20:00 | 本周趋势回顾 | 总结本周科技发展趋势（仅周日发布） |

## 🚀 快速开始

### 1. 环境配置

确保`.env`文件包含必要的API密钥：

```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
TAVILY_API_KEY=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
```

### 2. 启动系统

```bash
# 启动完整的每日发布调度器
python start_daily_publisher.py

# 或者使用原有的调度器
python manual_scheduler.py
```

### 3. 测试功能

```bash
# 运行完整测试套件
python test_daily_publisher.py

# 测试单个功能
python start_daily_publisher.py --test headlines  # 今日头条
python start_daily_publisher.py --test ai-thread  # AI线程  
python start_daily_publisher.py --test retweet    # 精选转发
python start_daily_publisher.py --test weekly     # 周报
```

## 📁 核心模块

```
src/react_agent/
├── content_generator.py     # 智能内容生成器
├── thread_creator.py        # Twitter线程创建器
├── daily_publisher.py       # 每日发布器（整合所有功能）
└── tools.py                # Twitter工具（已更新支持reply_tweet和quote_tweet）
```

## 🔧 新增功能

### Twitter线程支持
- ✅ `reply_tweet()` - 回复推文，用于创建线程
- ✅ `quote_tweet()` - 引用推文，用于转发评论

### 可持续AI内容库
系统包含3个主要可持续AI话题：
- 🌱 绿色计算 - 讨论AI能耗和节能技术
- 💡 边缘AI - 探讨分布式智能和效率优化  
- 🤖 AI伦理 - 关注负责任的AI发展

### 智能内容生成
- 📰 动态获取最新科技新闻并生成头条
- 🔍 搜索高质量推文用于转发
- 📊 自动分析本周趋势生成回顾

## 📊 调度配置

### 每日任务
- `08:00` - 今日科技头条发布
- `12:00` - 可持续AI线程发布 
- `16:00` - 精选转发发布
- `20:00` - 本周回顾发布（仅周日）

### 分析任务（降频）
- 每6小时 - 深度趋势分析
- 每8小时 - 互动监控回应
- 每12小时 - 数据可视化分析
- 每6小时 - 图片推文发布

## 📝 日志系统

发布结果会自动记录到：
```
logs/daily_publisher/publish_log_YYYY-MM-DD.json
```

查看发布状态：
```python
from react_agent.daily_publisher import DailyTechPublisher
publisher = DailyTechPublisher()
status = await publisher.get_publish_status("2025-09-02")
print(status)
```

## 🛠️ 自定义配置

### 修改发布时间
编辑`manual_scheduler.py`中的CronTrigger配置：
```python
# 改为09:00发布头条
trigger=CronTrigger(hour=9, minute=0)
```

### 添加新的AI话题
在`content_generator.py`中的`sustainable_ai_topics`列表添加新主题：
```python
{
    "theme": "量子AI融合",
    "content": [
        "🌱 量子计算与AI的结合将开启新时代...",
        "💡 量子算法可以指数级提升AI效率...", 
        # ... 更多内容
    ]
}
```

## 🔍 故障排查

### 常见问题

1. **MCP工具连接失败**
   - 检查网络连接
   - 确认MCP服务器状态
   
2. **推文发布失败**
   - 检查Twitter API限制
   - 验证用户ID配置
   
3. **内容生成错误**
   - 确认TAVILY_API_KEY配置
   - 检查网络搜索权限

### 调试命令

```bash
# 查看详细日志
tail -f logs/daily_publisher.log

# 测试MCP连接
python -c "from react_agent.tools import _get_all_mcp_tools; import asyncio; print(asyncio.run(_get_all_mcp_tools()))"

# 测试内容生成
python src/react_agent/content_generator.py
```

## 📈 系统监控

系统会自动记录：
- ✅ 成功发布的内容
- ❌ 失败的任务和错误信息
- 📊 每日发布统计
- 🔄 调度器运行状态

## 🎯 下一步优化

- [ ] 添加互动数据分析
- [ ] 支持多语言内容生成
- [ ] 集成更多数据源
- [ ] 优化内容个性化
- [ ] 添加A/B测试功能

---

📧 如有问题，请检查日志文件或运行测试脚本进行诊断。
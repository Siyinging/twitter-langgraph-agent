# Twitter智能自动发布系统

🤖 全自动智能Twitter发布系统，每天定时发布高质量科技内容，支持实时新闻获取和智能配图。

## 🎯 系统特点

- **📅 定时发布** - 每天多时段自动发布内容
- **🔄 实时内容** - 集成最新科技新闻和趋势 
- **🖼️ 智能配图** - 自动识别需要图片的内容并生成配图
- **📝 严格审核** - 多维度内容质量评估
- **💬 自然表达** - 避免模板化，内容像个人思考
- **🚀 高可靠性** - 完善的错误处理和监控

## ⏰ 发布时间表

| 时间 | 内容类型 | 描述 |
|------|----------|------|
| 08:00 UTC | 🌅 今日科技头条 | 每日最新科技动态，带智能配图 |
| 12:00 UTC | 🧠 AI+传统智慧线程 | AI与传统文化融合的深度思考 |
| 14:00 UTC | 🏥 中医科技专题 | 中医与现代科技结合的内容 |
| 16:00 UTC | 🔄 精选转发评论 | 转发优质内容并添加见解 |
| 20:00 UTC | 📊 本周趋势回顾 | 每周日发布一周科技趋势总结 |
| 每小时30分 | 📋 审核内容检查 | 发布通过人工审核的内容 |

## 🚀 快速开始

### 1. 启动系统

```bash
# 方法一: 使用便捷脚本
./run.sh start

# 方法二: 直接运行Python脚本
python3 start_auto_publisher.py
```

### 2. 测试系统

```bash
# 测试所有发布任务
./run.sh test

# 测试特定任务
./run.sh test-headlines    # 测试今日头条
./run.sh test-thread       # 测试AI线程
./run.sh test-tcm          # 测试中医科技

# 生成测试内容(不发布)
./run.sh test-content
```

### 3. 监控状态

```bash
# 查看今日发布状态
./run.sh status

# 查看系统日志
tail -f logs/auto_publisher.log
```

## 🛠️ 管理工具

### 命令行管理

```bash
# 使用管理脚本
python3 manage_publisher.py <命令>

# 可用命令:
# test <task>     - 测试单个任务
# test-all        - 测试所有任务
# status          - 检查发布状态  
# content         - 生成测试内容
```

### 便捷脚本

```bash
./run.sh <命令>

# 主要命令:
# start           - 启动系统
# test            - 完整测试
# status          - 查看状态
# test-content    - 生成内容测试
```

## 🔧 高级配置

### 安装为系统服务 (Linux/macOS)

```bash
# 安装服务
./run.sh install-service

# 控制服务
sudo systemctl start twitter-auto-publisher    # 启动
sudo systemctl stop twitter-auto-publisher     # 停止  
sudo systemctl status twitter-auto-publisher   # 状态
sudo systemctl enable twitter-auto-publisher   # 开机启动
```

### 环境变量配置

系统会自动从环境变量或`.env`文件读取配置：

```bash
# Twitter API配置
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# 搜索API配置
TAVILY_API_KEY=your_tavily_api_key
SERPAPI_API_KEY=your_serpapi_key
```

## 📊 监控与日志

### 日志文件

- `logs/auto_publisher.log` - 系统主日志
- `logs/daily_publisher/publish_log_YYYY-MM-DD.json` - 每日发布记录
- `logs/monitor.log` - 系统监控日志

### 发布记录

每个发布任务都会记录详细信息：

```json
{
  "task": "morning_headlines",
  "time": "2025-09-10T08:00:00Z",
  "success": true,
  "content": "发布的内容...",
  "tweet_id": "1234567890",
  "error": null
}
```

## 🔍 内容质量控制

### 智能审核系统

- **时效性评估** - 确保内容与最新动态相关
- **准确性检查** - 验证信息的可靠性
- **参与度评估** - 优化内容的吸引力
- **可读性分析** - 确保内容易于理解

### 配图智能化

- **自动识别** - 检测内容中提到的视觉元素
- **智能生成** - 根据内容主题生成相关图表
- **格式优化** - 自动处理图片格式和大小

## 🚨 故障排除

### 常见问题

1. **发布失败**
   ```bash
   # 检查系统状态
   ./run.sh status
   
   # 查看错误日志
   tail -f logs/auto_publisher.log
   ```

2. **API配额超限**
   - 检查Twitter API使用配额
   - 调整发布频率或内容量

3. **内容质量问题**
   - 查看内容审核日志
   - 调整质量评估参数

### 系统重启

```bash
# 停止系统 (Ctrl+C)
# 重新启动
./run.sh start
```

## 📈 性能优化

### 系统资源

- **内存使用**: 约200-400MB
- **CPU使用**: 发布时短暂升高，平时很低
- **存储需求**: 日志和缓存约100MB/月

### 优化建议

1. 定期清理旧日志文件
2. 监控API使用量
3. 优化图片生成质量和速度

## 🤝 技术支持

### 系统架构

```
Twitter自动发布系统
├── auto_publisher_scheduler.py    # 主调度器
├── start_auto_publisher.py        # 启动脚本
├── manage_publisher.py           # 管理工具
├── run.sh                        # 便捷脚本
└── src/react_agent/
    ├── daily_publisher.py        # 核心发布器
    ├── content_generator.py      # 内容生成器
    ├── direct_publisher.py       # 直接发布器
    ├── smart_media_manager.py    # 智能配图
    └── enhanced_content_reviewer.py # 内容审核
```

### 核心依赖

- `apscheduler` - 任务调度
- `asyncio` - 异步处理
- `langchain` - AI内容处理
- `plotly` - 图表生成
- `requests` - API调用

## 📞 联系方式

如果遇到问题或需要技术支持，请：

1. 检查日志文件获取错误详情
2. 运行测试命令定位问题
3. 查看系统状态确认配置

---

**🎉 享受你的智能自动发布系统！每天都有高质量的内容自动发布到Twitter。**
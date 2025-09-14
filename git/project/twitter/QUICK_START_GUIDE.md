# Twitter智能自动发布系统使用指南

🎉 **恭喜！你的Twitter智能自动发布系统已经配置完成！**

## 🚀 立即开始使用

### 方式一：一键启动 (推荐)

```bash
./start_publisher.sh
```

然后按提示选择：
- **选项1** - 智能自动发布系统 (推荐)
- **选项2** - 简单定时发布系统  
- **选项3** - 手动测试发布

### 方式二：直接启动

```bash
# 启动智能自动发布系统 (推荐)
python3 intelligent_auto_publisher.py

# 或启动简单版本
python3 ultra_simple_publisher.py
```

### 手动测试

```bash
# 发布真实化科技头条
python3 ultra_simple_publisher.py headlines

# 发布真实化中医科技专题  
python3 ultra_simple_publisher.py tcm

# 系统测试
python3 ultra_simple_publisher.py test
```

## 📅 自动发布时间表

### 🕐 定时发布
- **08:00 UTC** - 🌅 真实化科技头条 (带智能配图)
- **14:00 UTC** - 🏥 真实化中医科技专题 (带智能配图)

### 🧠 智能发布 (新功能)
- **自动监控热点新闻** - 发现重要科技新闻时自动发布
- **智能时机选择** - 避开定时发布，选择最佳发布时间
- **内容去重控制** - 自动检测避免重复内容
- **频率智能控制** - 每日最多6条，最小间隔2小时

## 📅 发布内容类型

### 🌅 今日科技头条 (08:00 UTC)
- **真实化表达**：像真人博主一样自然分享
- **个人化观点**：真实的使用感受和技术心得
- **去除假大空**：不再有官话套话，只有真实想法
- 自动配图：技术分析图表

### 🏥 中医科技专题 (14:00 UTC)  
- **日常化分享**：朋友圈、同事、个人经历的真实场景
- **客观评价**：有优点也有缺点，有期待也有担忧
- **实用价值**：关注实际应用而非概念炒作
- 自动配图：医疗科技图表

## 🎯 系统特点

- ✅ **真人化表达** - 告别AI味，像真人博主一样自然
- ✅ **个人化内容** - 有观点、有情感、有经历分享
- ✅ **实时新闻** - 获取最新科技动态并给出真实感受
- ✅ **智能配图** - 自动生成相关图表
- ✅ **去除假大空** - 不再有"让我们一起"式的空话
- ✅ **错误恢复** - 自动处理异常情况

## 🔧 系统控制

```bash
# 启动自动发布
python3 ultra_simple_publisher.py

# 测试系统
python3 ultra_simple_publisher.py test

# 手动发布头条
python3 ultra_simple_publisher.py headlines

# 手动发布中医科技
python3 ultra_simple_publisher.py tcm
```

按 `Ctrl+C` 停止系统。

## 📊 系统监控

### 查看日志
```bash
# 查看系统日志
tail -f logs/quick_auto_publisher.log

# 查看监控日志
tail -f logs/monitor.log
```

### 日志位置
- `logs/quick_auto_publisher.log` - 发布系统日志
- `logs/monitor.log` - 系统监控日志
- `data/` - 缓存数据和生成的图片

## ⚡ 快速故障排除

### 问题：发布失败
```bash
# 1. 检查网络连接
ping google.com

# 2. 重新测试系统
python3 ultra_simple_publisher.py test

# 3. 查看错误日志
tail logs/quick_auto_publisher.log
```

### 问题：缺少依赖
```bash
# 安装所有依赖
pip install plotly Pillow numpy langchain-tavily apscheduler langchain-mcp-adapters
```

### 问题：内容太长
- 系统会自动调整内容长度
- 确保推文不超过280字符

## 🎉 享受自动化发布！

你的系统现在会：

1. **每天08:00 UTC** 自动发布科技头条
2. **每天14:00 UTC** 自动发布中医科技专题  
3. **自动生成配图** 让推文更有吸引力
4. **持续监控** 确保系统稳定运行

只需要运行一次 `python3 ultra_simple_publisher.py`，然后就可以享受全自动的高质量Twitter内容发布了！

---

**🤖 你的AI助手已经为你设置好了一切。每天都有精彩的科技内容自动发布到你的Twitter！**
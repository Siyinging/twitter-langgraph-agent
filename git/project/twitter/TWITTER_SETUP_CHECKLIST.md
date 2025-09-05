# Twitter API 配置清单 ✅

## 🎯 目标
配置Twitter API凭据，实现带图片的推文发布功能

## ✅ 配置步骤

### 第1步: 访问Twitter开发者平台
- [ ] 打开浏览器访问: https://developer.twitter.com/
- [ ] 使用你的Twitter账户登录

### 第2步: 申请开发者账户（如果需要）
- [ ] 点击 "Apply for a developer account"
- [ ] 选择用途: **Hobbyist** -> **Making a bot**
- [ ] 填写申请信息:
  - 项目名称: **AI News Bot**
  - 用途描述: **自动发布AI新闻和数据可视化图表**
- [ ] 提交申请并等待审批（通常几分钟）

### 第3步: 创建应用
- [ ] 在开发者面板点击 **"Create App"** 或 **"Create Project"**
- [ ] 填写应用信息:
  - **App name**: `AI News Bot`
  - **App description**: `自动发布AI新闻推文和数据图表`

### 第4步: 配置应用权限
- [ ] 在应用设置中找到 **"App permissions"**
- [ ] 选择 **"Read and Write"** 权限
- [ ] 确保勾选 **"Upload media"** 权限

### 第5步: 生成并复制API密钥
在 **"Keys and tokens"** 标签页:

- [ ] 复制 **API Key** (Consumer Key)
- [ ] 复制 **API Key Secret** (Consumer Secret)
- [ ] 点击 **"Generate"** 生成 Access Token
- [ ] 复制 **Access Token**
- [ ] 复制 **Access Token Secret**
- [ ] 复制 **Bearer Token** (如果显示)

### 第6步: 配置.env文件
- [ ] 打开文件: `/Users/siying/git/project/twitter/.env`
- [ ] 找到以下行并替换为真实的API凭据:

```bash
# 替换这些占位符:
TWITTER_API_KEY=你的API_Key这里           # 替换为真实的API Key
TWITTER_API_SECRET=你的API_Secret这里     # 替换为真实的API Secret  
TWITTER_ACCESS_TOKEN=你的Access_Token这里 # 替换为真实的Access Token
TWITTER_ACCESS_TOKEN_SECRET=你的Access_Token_Secret这里 # 替换为真实的Access Token Secret
TWITTER_BEARER_TOKEN=你的Bearer_Token这里 # 替换为真实的Bearer Token
```

### 第7步: 测试配置
- [ ] 运行测试命令: `python3 test_twitter_setup.py`
- [ ] 确认看到 "✅ Twitter API连接成功!" 消息

### 第8步: 发布推文
- [ ] 运行发布命令: `python3 final_image_publisher.py`
- [ ] 确认推文成功发布到Twitter

## 🚨 重要提醒

- ⚠️ **API密钥是敏感信息**，不要分享给任何人
- ⚠️ **不要将.env文件提交到git**
- ⚠️ 如果密钥泄露，立即在Twitter开发者页面重新生成

## 📞 获取帮助

- **Twitter开发者文档**: https://developer.twitter.com/en/docs
- **API参考**: https://developer.twitter.com/en/docs/api-reference-index
- **问题排查**: 运行 `python3 quick_setup_guide.py`

## 🎉 配置完成后

一旦配置完成，你就可以：
- ✅ 自动发布带图片的推文
- ✅ 定时发布AI新闻头条
- ✅ 上传各种数据可视化图表
- ✅ 完全控制Twitter内容发布

---

**祝配置顺利！** 🚀
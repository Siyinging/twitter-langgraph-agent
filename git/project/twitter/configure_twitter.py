#!/usr/bin/env python3
"""Twitter API 配置助手"""

import os
from pathlib import Path

def create_env_template():
    """创建.env模板文件"""
    env_path = Path(".env")
    
    if env_path.exists():
        print(f"✅ .env文件已存在: {env_path.absolute()}")
        return str(env_path.absolute())
    
    # 创建模板内容
    template = """# Anthropic API Key (用于 LLM)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Tavily API Key (用于网页搜索)
TAVILY_API_KEY=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

# Twitter API 凭据 - 请在下面填入你的真实凭据
# 获取方式: 访问 https://developer.twitter.com/
TWITTER_API_KEY=你的API_Key这里
TWITTER_API_SECRET=你的API_Secret这里
TWITTER_ACCESS_TOKEN=你的Access_Token这里
TWITTER_ACCESS_TOKEN_SECRET=你的Access_Token_Secret这里
TWITTER_BEARER_TOKEN=你的Bearer_Token这里

# LangChain 追踪 (可选)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_key_here
LANGCHAIN_PROJECT=twitter-mcp-agent
"""
    
    # 写入文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✅ 已创建.env模板文件: {env_path.absolute()}")
    return str(env_path.absolute())

def show_detailed_steps():
    """显示详细配置步骤"""
    print("🔧 详细配置步骤:")
    print("=" * 50)
    
    print("\n📝 第1步: 访问Twitter开发者页面")
    print("   🌐 打开浏览器，访问: https://developer.twitter.com/")
    print("   👤 使用你的Twitter账户登录")
    
    print("\n📝 第2步: 创建开发者账户（如果需要）")
    print("   🎯 选择 'Apply for a developer account'")
    print("   📋 填写申请表单:")
    print("      - 选择用途: Hobbyist -> Making a bot")
    print("      - 应用名称: AI News Bot") 
    print("      - 用途描述: 自动发布AI新闻和数据可视化")
    
    print("\n📝 第3步: 创建应用")
    print("   ➕ 登录后，点击 'Create App' 或 'Create Project'")
    print("   📄 填写应用信息:")
    print("      - App name: AI News Bot")
    print("      - Description: 自动发布AI新闻推文")
    
    print("\n📝 第4步: 设置权限")
    print("   ⚙️ 在应用设置中，找到 'App permissions'")
    print("   ✅ 选择 'Read and Write' 权限")
    print("   📸 确保包含 'Upload media' 权限")
    
    print("\n📝 第5步: 生成API密钥")
    print("   🔑 在 'Keys and tokens' 标签页:")
    print("      1. 复制 'API Key' (Consumer Key)")
    print("      2. 复制 'API Key Secret' (Consumer Secret)")
    print("      3. 点击 'Generate' 生成 Access Token")
    print("      4. 复制 'Access Token'")
    print("      5. 复制 'Access Token Secret'")
    print("      6. 复制 'Bearer Token' (如果有)")

def show_env_instructions(env_path):
    """显示.env文件配置说明"""
    print(f"\n📝 第6步: 配置.env文件")
    print("=" * 50)
    print(f"   📁 文件位置: {env_path}")
    print("   ✏️ 编辑方式: 用任何文本编辑器打开")
    print("   🔄 替换步骤:")
    print("      - 将 '你的API_Key这里' 替换为实际的API Key")
    print("      - 将 '你的API_Secret这里' 替换为实际的API Secret")
    print("      - 将 '你的Access_Token这里' 替换为实际的Access Token")
    print("      - 将 '你的Access_Token_Secret这里' 替换为实际的Access Token Secret")
    print("      - 将 '你的Bearer_Token这里' 替换为实际的Bearer Token")
    
    print(f"\n💡 示例:")
    print("   TWITTER_API_KEY=ABCDEFghijklMNOPqrst12345")
    print("   TWITTER_API_SECRET=XYZabcdefghijklmnopqrstuvwxyz1234567890ABCD")
    print("   ...")

def main():
    """主函数"""
    print("🚀 Twitter API 配置助手")
    print("=" * 60)
    
    # 创建.env模板
    env_path = create_env_template()
    
    # 显示详细步骤
    show_detailed_steps()
    show_env_instructions(env_path)
    
    print("\n🎯 配置完成后的测试:")
    print("=" * 50)
    print("   1️⃣ 运行测试: python3 test_twitter_setup.py")
    print("   2️⃣ 发布推文: python3 final_image_publisher.py")
    
    print("\n⚠️ 重要提醒:")
    print("   • API密钥是敏感信息，不要分享给他人")
    print("   • 不要将.env文件提交到git仓库")
    print("   • 如果密钥泄露，请立即在Twitter开发者页面重新生成")

if __name__ == "__main__":
    main()
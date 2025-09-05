#!/usr/bin/env python3
"""一键式Twitter配置工具 - 最大程度自动化"""

import os
import time
import webbrowser
from pathlib import Path

def auto_open_and_guide():
    """自动打开页面并提供指导"""
    print("🚀 一键式Twitter API配置")
    print("=" * 50)
    
    print("🌐 正在为你自动打开Twitter开发者页面...")
    try:
        webbrowser.open("https://developer.twitter.com/")
        print("✅ 页面已打开，请按照以下步骤操作:")
    except:
        print("📋 请手动打开: https://developer.twitter.com/")
    
    print("\n🎯 详细操作步骤 (请跟着做):")
    print("-" * 40)
    
    steps = [
        "1️⃣ 登录你的Twitter账户",
        "2️⃣ 如果没有开发者账户，点击 'Apply for a developer account'",
        "   └─ 选择 'Hobbyist' -> 'Making a bot'",
        "   └─ 应用名称: AI News Bot",
        "   └─ 用途: 自动发布AI新闻和数据可视化",
        "3️⃣ 创建新应用 (Create App/Create Project)",
        "   └─ App name: AI News Bot",
        "   └─ Description: 自动发布AI新闻推文",
        "4️⃣ 设置应用权限",
        "   └─ 找到 'App permissions'",
        "   └─ 选择 'Read and Write'",
        "   └─ 确保包含 'Upload media'",
        "5️⃣ 生成API密钥 (在 Keys and tokens 标签)",
        "   └─ 复制 API Key",
        "   └─ 复制 API Key Secret", 
        "   └─ 生成并复制 Access Token",
        "   └─ 复制 Access Token Secret",
        "   └─ 复制 Bearer Token (如果有)"
    ]
    
    for step in steps:
        print(f"   {step}")
        if step.startswith(("2️⃣", "3️⃣", "4️⃣", "5️⃣")):
            input("   按 Enter 继续下一步...")
    
    return True

def guided_env_setup():
    """引导式.env文件配置"""
    print("\n🔧 现在配置.env文件:")
    print("-" * 30)
    
    env_path = Path(".env").absolute()
    print(f"📁 配置文件位置: {env_path}")
    
    print("\n📝 接下来我会帮你一个个配置API密钥:")
    print("   (直接粘贴从Twitter复制的内容即可)")
    
    # API密钥配置字典
    credentials = [
        ("TWITTER_API_KEY", "API Key (Consumer Key)", False),
        ("TWITTER_API_SECRET", "API Key Secret (Consumer Secret)", False),
        ("TWITTER_ACCESS_TOKEN", "Access Token", False),
        ("TWITTER_ACCESS_TOKEN_SECRET", "Access Token Secret", False),
        ("TWITTER_BEARER_TOKEN", "Bearer Token", True)  # 可选
    ]
    
    # 读取当前.env内容
    env_content = ""
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # 逐个配置
    for key, description, optional in credentials:
        print(f"\n🔑 {description}:")
        
        if optional:
            print("   (这个是可选的，可以留空)")
            value = input("   请粘贴或输入 (留空按Enter): ").strip()
        else:
            print("   (必需项)")
            while True:
                value = input("   请粘贴或输入: ").strip()
                if value:
                    break
                print("   ⚠️ 这是必需项，请输入值")
        
        if value:
            # 更新.env内容
            if f"{key}=" in env_content:
                # 替换现有值
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith(f"{key}="):
                        lines[i] = f"{key}={value}"
                        break
                env_content = '\n'.join(lines)
            else:
                # 添加新值
                env_content += f"\n{key}={value}"
            
            print(f"   ✅ {key} 已设置")
    
    # 保存文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n💾 配置已保存到: {env_path}")
    return True

def run_test():
    """运行配置测试"""
    print("\n🧪 测试API配置...")
    print("-" * 20)
    
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "test_twitter_setup.py"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        # 显示输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
        
        if result.returncode == 0:
            print("🎉 配置测试成功!")
            return True
        else:
            print("❌ 配置测试失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 测试超时，可能网络连接有问题")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def publish_test_tweet():
    """发布测试推文"""
    print("\n🐦 准备发布AI头条推文...")
    print("-" * 25)
    
    choice = input("是否现在发布测试推文? (y/n): ").strip().lower()
    
    if choice == 'y':
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "final_image_publisher.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("错误:", result.stderr)
            
            if result.returncode == 0:
                print("🎉 推文发布成功!")
                print("🔗 请检查你的Twitter账户确认")
                return True
            else:
                print("❌ 推文发布失败")
                return False
                
        except Exception as e:
            print(f"❌ 发布出错: {e}")
            return False
    else:
        print("⏭️ 稍后可运行: python3 final_image_publisher.py")
        return True

def main():
    """主程序 - 一键式配置流程"""
    print("🎯 Twitter图片发布 - 一键配置工具")
    print("=" * 60)
    
    try:
        # 步骤1: 打开页面并指导
        auto_open_and_guide()
        
        # 步骤2: 配置.env文件
        guided_env_setup()
        
        # 步骤3: 测试配置
        if run_test():
            # 步骤4: 发布推文
            publish_test_tweet()
            
            print("\n🎉 全部配置完成!")
            print("现在你可以随时运行以下命令发布带图片的推文:")
            print("   python3 final_image_publisher.py")
        else:
            print("\n⚠️ 配置测试失败，请检查API密钥是否正确")
            
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置过程出错: {e}")
    
    print("\n📋 如需帮助，可查看:")
    print("   - 详细指南: TWITTER_SETUP_CHECKLIST.md")
    print("   - 配置助手: python3 configure_twitter.py")

if __name__ == "__main__":
    main()
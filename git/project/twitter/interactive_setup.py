#!/usr/bin/env python3
"""交互式Twitter API配置工具"""

import os
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv, set_key

def open_twitter_developer():
    """自动打开Twitter开发者页面"""
    try:
        print("🌐 正在为你打开Twitter开发者页面...")
        webbrowser.open("https://developer.twitter.com/")
        print("✅ 页面已在浏览器中打开")
        return True
    except Exception as e:
        print(f"❌ 无法自动打开浏览器: {e}")
        print("📋 请手动访问: https://developer.twitter.com/")
        return False

def show_quick_steps():
    """显示快速操作步骤"""
    print("\n🎯 快速操作指南:")
    print("=" * 50)
    
    print("\n在打开的Twitter页面中:")
    print("1️⃣ 登录你的Twitter账户")
    print("2️⃣ 如果需要，申请开发者账户")
    print("3️⃣ 创建新应用:")
    print("   - 名称: AI News Bot")
    print("   - 用途: 发布AI新闻")
    print("4️⃣ 设置权限为 'Read and Write'")
    print("5️⃣ 生成API密钥和访问令牌")

def interactive_config():
    """交互式配置API密钥"""
    print("\n🔑 API密钥配置:")
    print("=" * 50)
    
    env_file = Path(".env")
    
    credentials = {
        "TWITTER_API_KEY": "API Key (Consumer Key)",
        "TWITTER_API_SECRET": "API Key Secret (Consumer Secret)",
        "TWITTER_ACCESS_TOKEN": "Access Token", 
        "TWITTER_ACCESS_TOKEN_SECRET": "Access Token Secret",
        "TWITTER_BEARER_TOKEN": "Bearer Token (可选)"
    }
    
    print("📝 请从Twitter开发者页面复制以下信息:")
    print("   (直接粘贴即可，程序会自动保存)")
    
    updated = False
    
    for key, description in credentials.items():
        current_value = os.getenv(key, "")
        
        if current_value and "你的" not in current_value:
            print(f"\n✅ {description}: 已配置")
            continue
            
        print(f"\n📋 {description}:")
        if "可选" in description:
            value = input("   请输入 (可留空): ").strip()
        else:
            value = input("   请输入: ").strip()
        
        if value:
            set_key(env_file, key, value)
            print(f"   ✅ {key} 已保存")
            updated = True
    
    return updated

def test_configuration():
    """测试配置"""
    print("\n🧪 测试Twitter API配置...")
    
    try:
        # 重新加载环境变量
        load_dotenv(override=True)
        
        result = subprocess.run(
            ["python3", "test_twitter_setup.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def publish_tweet():
    """发布测试推文"""
    print("\n🐦 发布AI头条推文...")
    
    try:
        result = subprocess.run(
            ["python3", "final_image_publisher.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        return False

def main():
    """主程序"""
    print("🚀 交互式Twitter API配置工具")
    print("=" * 60)
    
    # Step 1: 打开开发者页面
    print("步骤1: 打开Twitter开发者页面")
    open_twitter_developer()
    
    # Step 2: 显示操作指南
    show_quick_steps()
    
    # Step 3: 等待用户完成注册
    print("\n⏳ 请在浏览器中完成开发者账户和应用的创建...")
    input("完成后按 Enter 键继续...")
    
    # Step 4: 配置API密钥
    print("\n步骤2: 配置API密钥")
    if interactive_config():
        print("✅ API密钥配置完成")
    else:
        print("⚠️ 未更新任何配置")
    
    # Step 5: 测试配置
    print("\n步骤3: 测试配置")
    if test_configuration():
        print("🎉 配置测试成功！")
        
        # Step 6: 发布推文
        print("\n步骤4: 发布测试推文")
        choice = input("是否现在发布AI头条推文? (y/n): ").strip().lower()
        
        if choice == 'y':
            if publish_tweet():
                print("🎉 推文发布成功！")
                print("🔗 请检查你的Twitter账户确认")
            else:
                print("❌ 推文发布失败，请检查错误信息")
        else:
            print("⏭️ 可以稍后运行: python3 final_image_publisher.py")
    else:
        print("❌ 配置测试失败，请检查API密钥")
    
    print("\n" + "=" * 60)
    print("🏁 配置完成！")

if __name__ == "__main__":
    main()
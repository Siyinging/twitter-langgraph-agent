#!/usr/bin/env python3
"""Twitter API 快速配置指南"""

import os
from pathlib import Path
from dotenv import load_dotenv

def show_setup_guide():
    """显示设置向导"""
    print("🚀 Twitter API 配置向导")
    print("=" * 60)
    
    print("\n📋 步骤1: 获取Twitter API凭据")
    print("   1. 访问: https://developer.twitter.com/")
    print("   2. 创建开发者账户（如果还没有）")
    print("   3. 创建新应用")
    print("   4. 生成API密钥和访问令牌")
    
    print("\n📋 步骤2: 在.env文件中添加凭据")
    env_path = Path(".env")
    print(f"   文件位置: {env_path.absolute()}")
    
    print("\n   添加以下内容到.env文件:")
    print("   " + "-" * 50)
    print("""   # Twitter API 凭据
   TWITTER_API_KEY=你的API_Key这里
   TWITTER_API_SECRET=你的API_Secret这里
   TWITTER_ACCESS_TOKEN=你的Access_Token这里
   TWITTER_ACCESS_TOKEN_SECRET=你的Access_Token_Secret这里
   TWITTER_BEARER_TOKEN=你的Bearer_Token这里""")
    print("   " + "-" * 50)
    
    print("\n📋 步骤3: 测试配置")
    print("   运行: python3 test_twitter_setup.py")
    
    print("\n📋 步骤4: 发布推文")
    print("   运行: python3 final_image_publisher.py")

def check_current_config():
    """检查当前配置状态"""
    print("\n🔍 当前配置检查:")
    print("-" * 30)
    
    load_dotenv()
    
    credentials = {
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN")
    }
    
    configured_count = 0
    
    for key, value in credentials.items():
        if value:
            status = "✅ 已配置"
            # 显示前8个字符
            display_value = f"{value[:8]}..."
            configured_count += 1
        else:
            status = "❌ 未配置"
            display_value = "无"
        
        print(f"   {key:<30}: {status} ({display_value})")
    
    print(f"\n📊 配置进度: {configured_count}/5")
    
    if configured_count >= 4:
        print("🎉 配置基本完成！可以尝试发布推文了")
        return True
    else:
        print("⚠️ 还需要配置更多凭据")
        return False

def show_troubleshooting():
    """显示故障排除指南"""
    print("\n🛠️ 常见问题解决:")
    print("-" * 30)
    
    print("❓ 问题1: 找不到开发者页面")
    print("   💡 确保用正确的Twitter账户登录")
    print("   💡 有些地区可能需要等待审批")
    
    print("\n❓ 问题2: API调用失败")
    print("   💡 检查应用权限是否设置为 'Read and Write'")
    print("   💡 确保Access Token是最新生成的")
    
    print("\n❓ 问题3: 图片上传失败")
    print("   💡 图片大小不能超过5MB")
    print("   💡 支持的格式: JPG, PNG, GIF, WebP")
    
    print("\n❓ 问题4: .env文件不生效")
    print("   💡 确保文件名正确：.env（不是.env.txt）")
    print("   💡 重启终端或Python程序")
    
    print("\n📞 获取帮助:")
    print("   • Twitter开发者文档: https://developer.twitter.com/en/docs")
    print("   • API参考: https://developer.twitter.com/en/docs/api-reference-index")

if __name__ == "__main__":
    show_setup_guide()
    
    is_configured = check_current_config()
    
    if not is_configured:
        show_troubleshooting()
        
        print("\n" + "=" * 60)
        print("🎯 下一步:")
        print("1. 按照上述步骤配置Twitter API凭据")
        print("2. 配置完成后重新运行此脚本检查")
        print("3. 然后就可以发布带图片的推文了！")
    else:
        print("\n" + "=" * 60)
        print("🚀 配置完成！现在可以发布推文了:")
        print("   python3 final_image_publisher.py")
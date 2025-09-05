#!/usr/bin/env python3
"""测试Twitter API设置"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_twitter_credentials():
    """检查Twitter API凭据配置状态"""
    print("🔍 检查Twitter API凭据配置...")
    
    credentials = {
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN")
    }
    
    print("\n📊 凭据状态:")
    configured_count = 0
    
    for key, value in credentials.items():
        if value:
            status = "✅ 已配置"
            masked_value = f"{value[:8]}..." if len(value) > 8 else value
            configured_count += 1
        else:
            status = "❌ 未配置"
            masked_value = "无"
        
        print(f"  {key}: {status} ({masked_value})")
    
    print(f"\n📈 配置进度: {configured_count}/5")
    
    return configured_count >= 4  # 至少需要前4个凭据

def test_twitter_api_client():
    """测试Twitter API客户端"""
    try:
        print("\n🔧 测试Twitter API客户端...")
        
        # 添加项目路径
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from react_agent.twitter_api_client import TwitterAPIClient
        
        client = TwitterAPIClient()
        
        if not client.is_authenticated():
            print("❌ Twitter API客户端未正确认证")
            return False
        
        # 获取用户信息
        user_info = client.get_user_info()
        if user_info:
            print(f"✅ Twitter API连接成功!")
            print(f"👤 用户: @{user_info['username']} ({user_info['name']})")
            print(f"🆔 用户ID: {user_info['id']}")
            return True
        else:
            print("❌ 无法获取用户信息")
            return False
            
    except Exception as e:
        print(f"❌ Twitter API客户端测试失败: {e}")
        return False

def main():
    print("🚀 Twitter API 设置检查")
    print("=" * 40)
    
    # 检查凭据配置
    has_credentials = check_twitter_credentials()
    
    if not has_credentials:
        print("\n❌ Twitter API凭据未完整配置")
        print("💡 解决方案:")
        print("1. 访问 https://developer.twitter.com/ 获取API凭据")
        print("2. 在.env文件中添加以下配置:")
        print("""
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here  
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
""")
        print("3. 重新运行此测试")
        return False
    
    # 测试API连接
    api_works = test_twitter_api_client()
    
    if api_works:
        print("\n🎉 Twitter API配置完成，可以发布带图片的推文了!")
        print("💡 运行以下命令发布AI头条:")
        print("   python3 publish_ai_news_fixed.py")
        return True
    else:
        print("\n❌ Twitter API配置有问题")
        print("💡 请检查API凭据是否正确以及是否有足够权限")
        return False

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""配置Twitter API凭据"""

import os
from pathlib import Path
from dotenv import load_dotenv, set_key

def setup_twitter_api():
    """引导用户配置Twitter API凭据"""
    print("🔐 Twitter API 凭据配置向导")
    print("=" * 50)
    
    env_file = Path(".env")
    load_dotenv(env_file)
    
    print("\n📋 需要配置以下Twitter API凭据:")
    print("1. API Key (Consumer Key)")
    print("2. API Secret (Consumer Secret)")
    print("3. Access Token")
    print("4. Access Token Secret") 
    print("5. Bearer Token (可选)")
    
    print("\n💡 获取Twitter API凭据的步骤:")
    print("1. 访问 https://developer.twitter.com/")
    print("2. 创建开发者账户和应用")
    print("3. 在应用设置中生成API密钥和访问令牌")
    
    # 检查现有凭据
    existing_creds = {
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN")
    }
    
    print(f"\n📄 当前.env文件状态: {'存在' if env_file.exists() else '不存在'}")
    
    # 显示现有凭据状态
    print("\n📊 现有凭据状态:")
    for key, value in existing_creds.items():
        status = "已配置" if value else "未配置"
        masked_value = f"{value[:8]}..." if value and len(value) > 8 else "无"
        print(f"  {key}: {status} ({masked_value})")
    
    print("\n" + "=" * 50)
    choice = input("是否要配置/更新Twitter API凭据？(y/n): ").strip().lower()
    
    if choice != 'y':
        print("⏭️ 跳过Twitter API配置")
        return False
    
    # 配置凭据
    credentials = {
        "TWITTER_API_KEY": "API Key (Consumer Key)",
        "TWITTER_API_SECRET": "API Secret (Consumer Secret)", 
        "TWITTER_ACCESS_TOKEN": "Access Token",
        "TWITTER_ACCESS_TOKEN_SECRET": "Access Token Secret",
        "TWITTER_BEARER_TOKEN": "Bearer Token (可选，按回车跳过)"
    }
    
    print("\n🔑 请输入Twitter API凭据:")
    updated = False
    
    for env_key, description in credentials.items():
        current_value = existing_creds.get(env_key, "")
        
        if current_value:
            print(f"\n{description}:")
            print(f"  当前值: {current_value[:8]}...")
            new_value = input(f"  新值 (按回车保持不变): ").strip()
            if new_value:
                set_key(env_file, env_key, new_value)
                print(f"  ✅ {env_key} 已更新")
                updated = True
        else:
            new_value = input(f"\n{description}: ").strip()
            if new_value:
                set_key(env_file, env_key, new_value)
                print(f"✅ {env_key} 已设置")
                updated = True
            elif "可选" not in description:
                print(f"⚠️ {env_key} 为必需项，但未设置")
    
    if updated:
        print(f"\n🎉 Twitter API凭据已保存到 {env_file}")
        print("💡 请重启应用以使新凭据生效")
        return True
    else:
        print("\n📝 未更新任何凭据")
        return False

def test_twitter_api():
    """测试Twitter API连接"""
    print("\n🔧 测试Twitter API连接...")
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from react_agent.twitter_api_client import TwitterAPIClient
        
        client = TwitterAPIClient()
        
        if not client.is_authenticated():
            print("❌ Twitter API认证失败")
            print("💡 请检查API凭据配置")
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
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请确保安装了必要的依赖")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Twitter API 配置和测试工具")
    print("=" * 50)
    
    # 配置凭据
    if setup_twitter_api():
        print("\n" + "=" * 50)
        # 测试连接
        test_twitter_api()
    else:
        print("\n🔍 尝试使用现有凭据测试连接...")
        test_twitter_api()
    
    print("\n" + "=" * 50)
    print("🏁 配置完成")
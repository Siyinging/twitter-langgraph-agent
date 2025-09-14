#!/usr/bin/env python3
"""测试真实化内容生成器"""
import sys
import os
from pathlib import Path

# 设置路径
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import asyncio
from react_agent.authentic_content_generator import AuthenticContentGenerator

async def test_authentic_content():
    gen = AuthenticContentGenerator()
    
    print("=== 测试真实化备用内容 ===")
    for i in range(3):
        content = gen._create_authentic_fallback_content()
        print(f"测试 {i+1}: 长度={len(content)}")
        print(content)
        print("-" * 50)
    
    print("\n=== 测试中医科技内容 ===")
    for i in range(2):
        content = await gen.generate_authentic_tcm_content()
        print(f"测试 {i+1}: 长度={len(content)}")
        print(content)
        print("-" * 50)
    
    print("\n=== 测试AI线程 ===")
    ai_thread = await gen.generate_authentic_ai_thread()
    for i, tweet in enumerate(ai_thread, 1):
        print(f"{i}. {tweet} (长度: {len(tweet)})")

if __name__ == "__main__":
    asyncio.run(test_authentic_content())
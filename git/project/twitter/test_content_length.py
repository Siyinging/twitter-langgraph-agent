#!/usr/bin/env python3
"""测试内容长度"""
import sys
import os
from pathlib import Path

# 设置路径
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import asyncio
from react_agent.enhanced_content_generator import EnhancedContentGenerator

async def test_content_length():
    gen = EnhancedContentGenerator()
    
    print("=== 测试头条内容长度 ===")
    for i in range(3):
        content = await gen.generate_substantial_headlines()
        print(f"测试 {i+1}: 长度={len(content)}")
        print(f"内容: {content}")
        print("-" * 50)
    
    print("\n=== 测试中医科技内容长度 ===")
    for i in range(3):
        content = await gen.generate_substantial_tcm_content()
        print(f"测试 {i+1}: 长度={len(content)}")
        print(f"内容: {content}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_content_length())
#!/usr/bin/env python
"""
直接测试AI服务
"""

import os
import django
from dotenv import load_dotenv

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_tutor_system.settings')
django.setup()

from ai_services import ask_gemini

def test_ai_service():
    """测试AI服务"""
    print("=== 测试AI服务 ===")
    
    # 加载环境变量
    load_dotenv()
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    print(f"API Key: {'SET' if api_key else 'NOT SET'}")
    
    if not api_key or api_key == 'your_api_key_here':
        print("❌ API密钥未设置或为默认值")
        return
    
    # 测试简单的AI调用
    try:
        print("📝 测试简单问题...")
        response = ask_gemini("你好，请回答：1+1等于几？", temperature=0.3)
        print(f"✅ AI响应: {response}")
        
        print("\n📝 测试批改场景...")
        prompt = """
请作为一名专业教师，批改以下学生答案：

题目：什么是Python？
参考答案：Python是一种高级编程语言，具有简洁的语法和强大的功能。
学生答案：Python是一种编程语言，很好用。
满分：10分

请按以下格式回复：
分数：[0-10]
反馈：[具体的批改意见和建议]
"""
        
        response = ask_gemini(prompt, temperature=0.3)
        print(f"✅ 批改响应: {response}")
        
    except Exception as e:
        print(f"❌ AI服务错误: {e}")

if __name__ == "__main__":
    test_ai_service()

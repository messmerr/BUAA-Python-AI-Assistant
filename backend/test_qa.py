#!/usr/bin/env python
"""
测试智能答疑功能
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_qa_functionality():
    """测试智能答疑功能"""
    print("=== 测试智能答疑功能 ===")
    
    # 1. 学生登录
    student_login = {
        "username": "student1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=student_login)
    if response.status_code != 200:
        print("学生登录失败")
        return
    
    student_token = response.json()['data']['access_token']
    print("✅ 学生登录成功")
    
    # 2. 教师登录
    teacher_login = {
        "username": "teacher1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=teacher_login)
    if response.status_code != 200:
        print("教师登录失败")
        return
        
    teacher_token = response.json()['data']['access_token']
    print("✅ 教师登录成功")
    
    # 3. 学生提交问题
    student_headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    questions = [
        {
            "question_text": "什么是递归？请举个例子说明。",
            "subject": "计算机科学",
            "context": "我在学习算法时遇到了递归的概念，但不太理解"
        },
        {
            "question_text": "Python中的装饰器是什么？",
            "subject": "Python编程",
            "context": ""
        },
        {
            "question_text": "如何理解面向对象编程中的继承？",
            "subject": "编程基础"
        }
    ]
    
    question_ids = []
    
    for i, question_data in enumerate(questions, 1):
        print(f"\n📝 提交第{i}个问题...")
        print(f"问题：{question_data['question_text']}")
        
        response = requests.post(
            f"{BASE_URL}/qa/questions/", 
            json=question_data, 
            headers=student_headers
        )
        
        if response.status_code == 201:
            result = response.json()
            question_id = result['data']['question_id']
            ai_answer = result['data']['ai_answer']
            question_ids.append(question_id)
            
            print(f"✅ 问题提交成功")
            print(f"问题ID: {question_id}")
            print(f"AI回答: {ai_answer[:100]}...")
        else:
            print(f"❌ 问题提交失败: {response.json()}")
    
    # 4. 获取问题详情
    if question_ids:
        print(f"\n🔍 获取第一个问题的详情...")
        response = requests.get(
            f"{BASE_URL}/qa/questions/{question_ids[0]}/", 
            headers=student_headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取问题详情成功")
            print(f"问题: {result['data']['question_text']}")
            print(f"学科: {result['data']['subject']}")
            print(f"上下文: {result['data']['context']}")
            print(f"AI回答: {result['data']['answer']['ai_answer'][:100]}...")
        else:
            print(f"❌ 获取问题详情失败: {response.json()}")
    
    # 5. 学生获取自己的问答历史
    print(f"\n📋 获取学生问答历史...")
    response = requests.get(
        f"{BASE_URL}/qa/questions/list/", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        questions_list = result['data']['questions']
        pagination = result['data']['pagination']
        
        print("✅ 获取问答历史成功")
        print(f"总问题数: {pagination['total']}")
        print(f"当前页: {pagination['page']}/{pagination['total_pages']}")
        
        for i, q in enumerate(questions_list, 1):
            print(f"\n第{i}个问题:")
            print(f"  问题: {q['question_text']}")
            print(f"  学科: {q['subject']}")
            print(f"  AI回答: {q['ai_answer'][:50]}...")
            print(f"  创建时间: {q['created_at']}")
    else:
        print(f"❌ 获取问答历史失败: {response.json()}")
    
    # 6. 教师查看所有问题
    teacher_headers = {
        "Authorization": f"Bearer {teacher_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n👨‍🏫 教师查看所有问题...")
    response = requests.get(
        f"{BASE_URL}/qa/questions/list/", 
        headers=teacher_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        questions_list = result['data']['questions']
        
        print("✅ 教师获取问题列表成功")
        print(f"总问题数: {len(questions_list)}")
        
        for i, q in enumerate(questions_list, 1):
            print(f"\n第{i}个问题:")
            print(f"  问题: {q['question_text']}")
            print(f"  学科: {q['subject']}")
            print(f"  AI回答: {q['ai_answer'][:50]}...")
    else:
        print(f"❌ 教师获取问题列表失败: {response.json()}")
    
    # 7. 测试学科筛选
    print(f"\n🔍 测试学科筛选功能...")
    response = requests.get(
        f"{BASE_URL}/qa/questions/list/?subject=Python", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        questions_list = result['data']['questions']
        
        print("✅ 学科筛选成功")
        print(f"Python相关问题数: {len(questions_list)}")
        
        for q in questions_list:
            print(f"  - {q['question_text']} (学科: {q['subject']})")
    else:
        print(f"❌ 学科筛选失败: {response.json()}")
    
    print(f"\n✅ 智能答疑功能测试完成！")

if __name__ == "__main__":
    test_qa_functionality()

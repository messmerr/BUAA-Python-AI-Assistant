#!/usr/bin/env python
"""
API测试脚本 - 测试用户认证和作业管理功能
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_user_registration():
    """测试用户注册"""
    print("=== 测试用户注册 ===")
    
    # 注册教师
    teacher_data = {
        "username": "teacher1",
        "password": "testpass123",
        "email": "teacher1@test.com",
        "role": "teacher",
        "real_name": "张老师"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=teacher_data)
    print(f"教师注册: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 注册学生
    student_data = {
        "username": "student1",
        "password": "testpass123",
        "email": "student1@test.com",
        "role": "student",
        "real_name": "李同学",
        "student_id": "2021001"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=student_data)
    print(f"学生注册: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_user_login():
    """测试用户登录"""
    print("=== 测试用户登录 ===")
    
    # 教师登录
    teacher_login = {
        "username": "teacher1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=teacher_login)
    print(f"教师登录: {response.status_code}")
    teacher_tokens = response.json()
    print(f"响应: {teacher_tokens}")
    
    # 学生登录
    student_login = {
        "username": "student1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=student_login)
    print(f"学生登录: {response.status_code}")
    student_tokens = response.json()
    print(f"响应: {student_tokens}")
    print()
    
    return teacher_tokens, student_tokens

def test_create_assignment(teacher_token):
    """测试创建作业"""
    print("=== 测试创建作业 ===")
    
    headers = {
        "Authorization": f"Bearer {teacher_token}",
        "Content-Type": "application/json"
    }
    
    # 计算明天的截止时间
    deadline = (datetime.now() + timedelta(days=1)).isoformat()
    
    assignment_data = {
        "title": "Python基础测试",
        "description": "测试Python基础知识",
        "subject": "Python编程",
        "questions": [
            {
                "question_text": "什么是Python？",
                "reference_answer": "Python是一种高级编程语言，具有简洁的语法和强大的功能。",
                "score": 10
            },
            {
                "question_text": "列表和元组的区别是什么？",
                "reference_answer": "列表是可变的，元组是不可变的。列表用[]表示，元组用()表示。",
                "score": 15
            }
        ],
        "deadline": deadline,
        "total_score": 25
    }
    
    response = requests.post(f"{BASE_URL}/assignments/create/", json=assignment_data, headers=headers)
    print(f"创建作业: {response.status_code}")
    result = response.json()
    print(f"响应: {result}")
    print()
    
    if response.status_code == 201:
        return result['data']['assignment_id']
    return None

def test_get_assignments(token, role):
    """测试获取作业列表"""
    print(f"=== 测试获取作业列表 ({role}) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    response = requests.get(f"{BASE_URL}/assignments/list/", headers=headers)
    print(f"获取作业列表: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_get_assignment_detail(token, assignment_id):
    """测试获取作业详情"""
    print("=== 测试获取作业详情 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}/", headers=headers)
    print(f"获取作业详情: {response.status_code}")
    result = response.json()
    print(f"响应: {result}")
    print()
    
    return result

def test_submit_assignment(student_token, assignment_id, questions):
    """测试提交作业"""
    print("=== 测试提交作业 ===")
    
    headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    # 构建学生答案
    answers = []
    for question in questions:
        if "Python" in question['question_text']:
            answer_text = "Python是一种解释型、面向对象的编程语言。"
        else:
            answer_text = "列表可以修改，元组不能修改。"
        
        answers.append({
            "question_id": question['id'],
            "answer_text": answer_text
        })
    
    submission_data = {
        "answers": answers
    }
    
    response = requests.post(
        f"{BASE_URL}/assignments/{assignment_id}/submissions/", 
        json=submission_data, 
        headers=headers
    )
    print(f"提交作业: {response.status_code}")
    result = response.json()
    print(f"响应: {result}")
    print()
    
    if response.status_code == 201:
        return result['data']['submission_id']
    return None

def test_get_submission_result(token, assignment_id, submission_id):
    """测试获取批改结果"""
    print("=== 测试获取批改结果 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    response = requests.get(
        f"{BASE_URL}/assignments/{assignment_id}/submissions/{submission_id}/", 
        headers=headers
    )
    print(f"获取批改结果: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def main():
    """主测试函数"""
    print("开始API测试...")
    print()
    
    try:
        # 1. 测试用户注册
        test_user_registration()
        
        # 2. 测试用户登录
        teacher_tokens, student_tokens = test_user_login()
        
        if teacher_tokens.get('code') != 200 or student_tokens.get('code') != 200:
            print("登录失败，停止测试")
            return
        
        teacher_token = teacher_tokens['data']['access_token']
        student_token = student_tokens['data']['access_token']
        
        # 3. 测试创建作业
        assignment_id = test_create_assignment(teacher_token)
        
        if not assignment_id:
            print("创建作业失败，停止测试")
            return
        
        # 4. 测试获取作业列表
        test_get_assignments(teacher_token, "教师")
        test_get_assignments(student_token, "学生")
        
        # 5. 测试获取作业详情
        assignment_detail = test_get_assignment_detail(student_token, assignment_id)
        
        if assignment_detail.get('code') != 200:
            print("获取作业详情失败，停止测试")
            return
        
        questions = assignment_detail['data']['questions']
        
        # 6. 测试提交作业
        submission_id = test_submit_assignment(student_token, assignment_id, questions)
        
        if not submission_id:
            print("提交作业失败，停止测试")
            return
        
        # 7. 测试获取批改结果
        test_get_submission_result(student_token, assignment_id, submission_id)
        
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()

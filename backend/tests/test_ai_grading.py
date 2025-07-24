#!/usr/bin/env python
"""
测试AI批改功能
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_ai_grading():
    """测试AI批改功能"""
    print("=== 测试AI批改功能 ===")
    
    # 1. 登录获取token
    teacher_login = {
        "username": "teacher1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=teacher_login)
    if response.status_code != 200:
        print("教师登录失败")
        return
    
    teacher_token = response.json()['data']['access_token']
    
    student_login = {
        "username": "student1", 
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=student_login)
    if response.status_code != 200:
        print("学生登录失败")
        return
        
    student_token = response.json()['data']['access_token']
    
    # 2. 创建新的测试作业
    headers = {
        "Authorization": f"Bearer {teacher_token}",
        "Content-Type": "application/json"
    }
    
    deadline = (datetime.now() + timedelta(days=1)).isoformat()
    
    assignment_data = {
        "title": "AI批改测试作业",
        "description": "测试AI批改功能是否正常工作",
        "questions": [
            {
                "question_text": "请解释什么是机器学习？",
                "reference_answer": "机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习和改进。",
                "score": 20
            },
            {
                "question_text": "Python中列表和字典的主要区别是什么？",
                "reference_answer": "列表是有序的可变序列，使用索引访问；字典是无序的键值对集合，使用键访问。",
                "score": 15
            }
        ],
        "deadline": deadline,
        "total_score": 35
    }
    
    response = requests.post(f"{BASE_URL}/assignments/create/", json=assignment_data, headers=headers)
    if response.status_code != 201:
        print(f"创建作业失败: {response.json()}")
        return
    
    assignment_id = response.json()['data']['assignment_id']
    print(f"✅ 创建作业成功: {assignment_id}")
    
    # 3. 获取作业详情
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}/", headers={"Authorization": f"Bearer {student_token}"})
    if response.status_code != 200:
        print("获取作业详情失败")
        return
    
    questions = response.json()['data']['questions']
    print(f"✅ 获取作业详情成功，共{len(questions)}道题")
    
    # 4. 提交学生答案
    student_headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    answers = [
        {
            "question_id": questions[0]['id'],
            "answer_text": "机器学习是一种让计算机通过数据自动学习规律的技术，不需要人工编写具体的规则。它可以用来做预测、分类等任务。"
        },
        {
            "question_id": questions[1]['id'], 
            "answer_text": "列表用方括号[]，可以存储多个有序的元素，通过下标访问。字典用花括号{}，存储键值对，通过键来访问值。"
        }
    ]
    
    submission_data = {
        "answers": answers
    }
    
    print("📝 正在提交作业并进行AI批改...")
    response = requests.post(
        f"{BASE_URL}/assignments/{assignment_id}/submissions/", 
        json=submission_data, 
        headers=student_headers
    )
    
    if response.status_code != 201:
        print(f"❌ 提交作业失败: {response.json()}")
        return
    
    submission_id = response.json()['data']['submission_id']
    print(f"✅ 作业提交成功: {submission_id}")
    
    # 5. 获取批改结果
    response = requests.get(
        f"{BASE_URL}/assignments/{assignment_id}/submissions/{submission_id}/", 
        headers=student_headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取批改结果失败: {response.json()}")
        return
    
    result = response.json()['data']
    print(f"\n🎯 批改结果:")
    print(f"总分: {result['total_score']}")
    print(f"获得分数: {result['obtained_score']}")
    print(f"得分率: {result['obtained_score']/result['total_score']*100:.1f}%")
    print(f"总体反馈: {result['overall_feedback']}")
    
    print(f"\n📋 详细批改:")
    for i, answer in enumerate(result['answers'], 1):
        print(f"\n第{i}题:")
        print(f"问题: {answer['question_text']}")
        print(f"学生答案: {answer['student_answer']}")
        print(f"参考答案: {answer['reference_answer']}")
        print(f"得分: {answer['obtained_score']}/{answer['score']}")
        print(f"AI反馈: {answer['ai_feedback']}")
    
    print(f"\n✅ AI批改测试完成！")

if __name__ == "__main__":
    test_ai_grading()

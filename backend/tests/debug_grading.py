#!/usr/bin/env python
"""
调试批改功能
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

def debug_grading():
    """调试批改功能"""
    print("=== 调试批改功能 ===")
    
    # 1. 登录
    teacher_login = {
        "username": "teacher1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=teacher_login)
    teacher_token = response.json()['data']['access_token']
    
    student_login = {
        "username": "student1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=student_login)
    student_token = response.json()['data']['access_token']
    
    # 2. 创建一个简单的测试作业
    teacher_headers = {
        "Authorization": f"Bearer {teacher_token}",
        "Content-Type": "application/json"
    }
    
    assignment_data = {
        "title": "调试批改测试",
        "description": "测试AI批改功能",
        "subject": "测试科目",
        "questions": [
            {
                "question_text": "1+1等于几？",
                "reference_answer": "1+1等于2",
                "score": 10
            }
        ],
        "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
        "total_score": 10
    }
    
    print("📝 创建测试作业...")
    response = requests.post(
        f"{BASE_URL}/assignments/create/", 
        json=assignment_data, 
        headers=teacher_headers
    )
    
    if response.status_code != 201:
        print(f"❌ 作业创建失败: {response.json()}")
        return
    
    assignment_id = response.json()['data']['assignment_id']
    print(f"✅ 作业创建成功: {assignment_id}")
    
    # 3. 获取作业详情
    student_headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/assignments/{assignment_id}/", 
        headers=student_headers
    )
    
    assignment_detail = response.json()['data']
    question_id = assignment_detail['questions'][0]['id']
    
    # 4. 测试不同质量的答案
    test_answers = [
        {
            "name": "正确答案",
            "text": "1+1等于2，这是基本的数学运算。"
        },
        {
            "name": "部分正确答案", 
            "text": "1+1=2"
        },
        {
            "name": "错误答案",
            "text": "1+1等于3"
        },
        {
            "name": "无关答案",
            "text": "这是我的答案"
        }
    ]
    
    for i, test_answer in enumerate(test_answers, 1):
        print(f"\n🧪 测试第{i}个答案: {test_answer['name']}")
        print(f"答案内容: {test_answer['text']}")
        
        # 提交答案
        submission_data = {
            "answers": [{
                "question_id": question_id,
                "answer_text": test_answer['text']
            }]
        }
        
        response = requests.post(
            f"{BASE_URL}/assignments/{assignment_id}/submissions/", 
            json=submission_data, 
            headers=student_headers
        )
        
        if response.status_code == 201:
            submission_id = response.json()['data']['submission_id']
            print(f"✅ 提交成功: {submission_id}")
            
            # 获取批改结果
            response = requests.get(
                f"{BASE_URL}/assignments/{assignment_id}/submissions/{submission_id}/", 
                headers=student_headers
            )
            
            if response.status_code == 200:
                result = response.json()['data']
                answer_detail = result['answers'][0]
                
                print(f"📊 批改结果:")
                print(f"  得分: {answer_detail['obtained_score']}/{answer_detail['score']}")
                print(f"  AI反馈: {answer_detail['ai_feedback'][:100]}...")
                print(f"  总体反馈: {result['overall_feedback'][:100]}...")
            else:
                print(f"❌ 获取批改结果失败: {response.json()}")
        else:
            print(f"❌ 提交失败: {response.json()}")
        
        # 为了避免重复提交错误，我们需要用不同的学生账号或者删除之前的提交
        # 这里我们简单地跳过后续测试
        if i == 1:
            break
    
    print(f"\n✅ 调试完成！")

if __name__ == "__main__":
    debug_grading()

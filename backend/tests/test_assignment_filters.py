#!/usr/bin/env python
"""
测试作业筛选功能
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_assignment_filters():
    """测试作业筛选功能"""
    print("=== 测试作业筛选功能 ===")
    
    # 1. 登录
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
    
    # 2. 创建不同科目的作业
    teacher_headers = {
        "Authorization": f"Bearer {teacher_token}",
        "Content-Type": "application/json"
    }
    
    assignments_data = [
        {
            "title": "Python基础练习",
            "description": "Python语法和基础概念练习",
            "subject": "Python编程",
            "questions": [
                {
                    "question_text": "什么是Python中的列表推导式？",
                    "reference_answer": "列表推导式是Python中创建列表的简洁方式。",
                    "score": 10
                }
            ],
            "deadline": (datetime.now() + timedelta(days=3)).isoformat(),
            "total_score": 10
        },
        {
            "title": "数据结构作业",
            "description": "栈和队列的实现",
            "subject": "数据结构",
            "questions": [
                {
                    "question_text": "请解释栈和队列的区别",
                    "reference_answer": "栈是后进先出(LIFO)，队列是先进先出(FIFO)。",
                    "score": 15
                }
            ],
            "deadline": (datetime.now() + timedelta(days=5)).isoformat(),
            "total_score": 15
        },
        {
            "title": "算法分析",
            "description": "时间复杂度分析练习",
            "subject": "算法",
            "questions": [
                {
                    "question_text": "分析冒泡排序的时间复杂度",
                    "reference_answer": "冒泡排序的时间复杂度是O(n²)。",
                    "score": 20
                }
            ],
            "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
            "total_score": 20
        }
    ]
    
    assignment_ids = []
    
    for i, assignment_data in enumerate(assignments_data, 1):
        print(f"\n📝 创建第{i}个作业: {assignment_data['title']}")
        
        response = requests.post(
            f"{BASE_URL}/assignments/create/", 
            json=assignment_data, 
            headers=teacher_headers
        )
        
        if response.status_code == 201:
            result = response.json()
            assignment_id = result['data']['assignment_id']
            assignment_ids.append(assignment_id)
            print(f"✅ 作业创建成功: {assignment_id}")
        else:
            print(f"❌ 作业创建失败: {response.json()}")
    
    # 3. 学生完成部分作业
    student_headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    if len(assignment_ids) >= 2:
        print(f"\n📝 学生完成前两个作业...")
        
        for i in range(2):  # 完成前两个作业
            assignment_id = assignment_ids[i]
            
            # 获取作业详情
            response = requests.get(
                f"{BASE_URL}/assignments/{assignment_id}/", 
                headers=student_headers
            )
            
            if response.status_code == 200:
                assignment_detail = response.json()['data']
                questions = assignment_detail['questions']
                
                # 提交答案
                answers = [{
                    "question_id": questions[0]['id'],
                    "answer_text": "这是我的答案"
                }]
                
                submission_data = {"answers": answers}
                
                response = requests.post(
                    f"{BASE_URL}/assignments/{assignment_id}/submissions/", 
                    json=submission_data, 
                    headers=student_headers
                )
                
                if response.status_code == 201:
                    print(f"✅ 完成作业: {assignment_detail['title']}")
                else:
                    print(f"❌ 提交失败: {response.json()}")
    
    # 4. 测试各种筛选功能
    print(f"\n🔍 测试筛选功能...")
    
    # 4.1 学生查看所有作业
    print(f"\n📋 学生查看所有作业:")
    response = requests.get(
        f"{BASE_URL}/assignments/list/", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        assignments = result['data']['assignments']
        print(f"总作业数: {len(assignments)}")
        
        for assignment in assignments:
            print(f"  - {assignment['title']} ({assignment['subject']}) - 已完成: {assignment['is_completed']}")
    
    # 4.2 按科目筛选
    print(f"\n🔍 按科目筛选 (Python编程):")
    response = requests.get(
        f"{BASE_URL}/assignments/list/?subject=Python", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        assignments = result['data']['assignments']
        print(f"Python相关作业数: {len(assignments)}")
        
        for assignment in assignments:
            print(f"  - {assignment['title']} ({assignment['subject']})")
    
    # 4.3 按完成状态筛选 - 已完成
    print(f"\n✅ 筛选已完成的作业:")
    response = requests.get(
        f"{BASE_URL}/assignments/list/?completion_status=completed", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        assignments = result['data']['assignments']
        print(f"已完成作业数: {len(assignments)}")
        
        for assignment in assignments:
            print(f"  - {assignment['title']} - 得分: {assignment['obtained_score']}")
    
    # 4.4 按完成状态筛选 - 未完成
    print(f"\n⏳ 筛选未完成的作业:")
    response = requests.get(
        f"{BASE_URL}/assignments/list/?completion_status=pending", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        assignments = result['data']['assignments']
        print(f"未完成作业数: {len(assignments)}")
        
        for assignment in assignments:
            print(f"  - {assignment['title']} ({assignment['subject']})")
    
    # 4.5 组合筛选
    print(f"\n🔍 组合筛选 (数据结构 + 未完成):")
    response = requests.get(
        f"{BASE_URL}/assignments/list/?subject=数据结构&completion_status=pending", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        result = response.json()
        assignments = result['data']['assignments']
        print(f"数据结构未完成作业数: {len(assignments)}")
        
        for assignment in assignments:
            print(f"  - {assignment['title']} ({assignment['subject']})")
    
    # 5. 测试作业详情中的完成状态
    if assignment_ids:
        print(f"\n📄 测试作业详情中的完成状态:")
        assignment_id = assignment_ids[0]
        
        response = requests.get(
            f"{BASE_URL}/assignments/{assignment_id}/", 
            headers=student_headers
        )
        
        if response.status_code == 200:
            result = response.json()['data']
            print(f"作业: {result['title']}")
            print(f"科目: {result['subject']}")
            print(f"已完成: {result['is_completed']}")
            print(f"获得分数: {result['obtained_score']}")
    
    print(f"\n✅ 作业筛选功能测试完成！")

if __name__ == "__main__":
    test_assignment_filters()

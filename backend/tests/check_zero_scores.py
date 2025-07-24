#!/usr/bin/env python
"""
检查0分提交的详细信息
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def check_zero_scores():
    """检查0分提交的详细信息"""
    print("=== 检查0分提交详情 ===")
    
    # 1. 学生登录
    student_login = {
        "username": "student1",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=student_login)
    student_token = response.json()['data']['access_token']
    
    student_headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    # 2. 获取所有已完成的作业
    response = requests.get(
        f"{BASE_URL}/assignments/list/?completion_status=completed", 
        headers=student_headers
    )
    
    if response.status_code != 200:
        print("获取作业列表失败")
        return
    
    assignments = response.json()['data']['assignments']
    zero_score_assignments = [a for a in assignments if a['obtained_score'] == 0]
    
    print(f"总已完成作业数: {len(assignments)}")
    print(f"0分作业数: {len(zero_score_assignments)}")
    
    # 3. 检查前几个0分作业的详细信息
    for i, assignment in enumerate(zero_score_assignments[:3], 1):
        print(f"\n🔍 检查第{i}个0分作业:")
        print(f"作业标题: {assignment['title']}")
        print(f"科目: {assignment['subject']}")
        print(f"总分: {assignment['total_score']}")
        print(f"获得分数: {assignment['obtained_score']}")
        
        assignment_id = assignment['id']
        
        # 获取作业详情
        response = requests.get(
            f"{BASE_URL}/assignments/{assignment_id}/", 
            headers=student_headers
        )
        
        if response.status_code == 200:
            assignment_detail = response.json()['data']
            
            # 查找这个学生的提交记录
            # 我们需要通过某种方式获取submission_id
            # 由于API设计限制，我们可能需要从数据库直接查询
            print(f"作业问题数: {len(assignment_detail['questions'])}")
            
            for j, question in enumerate(assignment_detail['questions'], 1):
                print(f"  问题{j}: {question['question_text'][:50]}...")
                print(f"  参考答案: {question['reference_answer'][:50]}...")
                print(f"  分值: {question['score']}")

def check_specific_submission():
    """检查特定提交的详细批改信息"""
    print("\n=== 检查特定提交详情 ===")
    
    # 这里我们需要一个已知的submission_id
    # 从之前的测试中，我们知道有一些0分的提交
    
    # 让我们创建一个新的测试来查看批改详情
    student_login = {
        "username": "student1", 
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=student_login)
    student_token = response.json()['data']['access_token']
    
    student_headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    # 获取最近的一个作业
    response = requests.get(
        f"{BASE_URL}/assignments/list/?page_size=1", 
        headers=student_headers
    )
    
    if response.status_code == 200:
        assignments = response.json()['data']['assignments']
        if assignments and assignments[0]['is_completed']:
            assignment = assignments[0]
            assignment_id = assignment['id']
            
            print(f"检查作业: {assignment['title']}")
            print(f"获得分数: {assignment['obtained_score']}")
            
            # 由于我们无法直接获取submission_id，我们需要修改API
            # 或者从数据库直接查询
            print("需要submission_id来获取详细批改信息...")

if __name__ == "__main__":
    check_zero_scores()
    check_specific_submission()

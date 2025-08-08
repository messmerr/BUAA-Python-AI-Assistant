#!/usr/bin/env python
"""
数据填充脚本（演示用）

功能：
1) 批量创建教师与学生账号（如用户已存在则跳过）
2) 按学科创建“足量”作业（含多题目）
3) 由学生提交作业答案（混合：精准正确/部分错误/完全错误），触发后端批改

说明：
- 本脚本通过后端正式 API 调用完成（非直接写库），确保业务逻辑与批改流程生效。
- 若未配置 GOOGLE_AI_API_KEY，"精准匹配"答案会满分；非精准答案可能因无法调用大模型而得 0 分，用于制造分数差异。

使用：
1) 先启动后端：python manage.py runserver
2) 运行脚本：python backend/tests/populate_demo_data.py
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import requests


BASE_URL = "http://127.0.0.1:8000/api/v1"


def register_user(
    username: str,
    password: str,
    role: str,
    real_name: str,
    email: str = "",
    student_id: str | None = None,
) -> bool:
    """注册用户；已存在则容错返回 False，不中断流程。"""
    payload = {
        "username": username,
        "password": password,
        "email": email or f"{username}@demo.test",
        "role": role,
        "real_name": real_name,
    }
    if role == "student":
        payload["student_id"] = student_id or f"SID{random.randint(100000, 999999)}"

    resp = requests.post(f"{BASE_URL}/auth/register/", json=payload)
    if resp.status_code == 201:
        print(f"[OK] 注册成功: {username} ({role})")
        return True
    else:
        # 重复用户名或其它错误时，尝试忽略继续
        try:
            data = resp.json()
        except Exception:
            data = {"message": resp.text}
        print(f"[SKIP] 注册跳过: {username} ({role}) - {resp.status_code} - {data}")
        return False


def login(username: str, password: str) -> str:
    """登录获取 access_token。失败将抛出异常。"""
    resp = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"username": username, "password": password},
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and data.get("code") == 200:
        token = data["data"]["access_token"]
        return token
    raise RuntimeError(f"登录失败: {username} -> {data}")


def auth_headers(token: str) -> Dict[str, str]:
    """JSON 提交用头（包含 Content-Type）。"""
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def auth_only_headers(token: str) -> Dict[str, str]:
    """表单/Multipart 提交用头（不声明 Content-Type 交给 requests 自动设置）。"""
    return {"Authorization": f"Bearer {token}"}


def create_assignment(
    teacher_token: str,
    title: str,
    description: str,
    subject: str,
    questions: List[Dict],
    deadline_days: int = 7,
) -> str | None:
    """创建作业，返回 assignment_id。"""
    deadline = (datetime.now() + timedelta(days=deadline_days)).isoformat()
    total_score = sum(q.get("score", 0) for q in questions)
    payload = {
        "title": title,
        "description": description,
        "subject": subject,
        "questions": questions,
        "deadline": deadline,
        "total_score": total_score,
    }
    resp = requests.post(
        f"{BASE_URL}/assignments/create/", json=payload, headers=auth_headers(teacher_token)
    )
    try:
        data = resp.json()
    except Exception:
        data = {"message": resp.text}
    if resp.status_code == 201:
        assignment_id = data["data"]["assignment_id"]
        print(f"[OK] 创建作业: {title} ({subject}) -> {assignment_id}")
        return assignment_id
    print(f"[ERR] 创建作业失败: {title} ({subject}) -> {resp.status_code} - {data}")
    return None


def get_assignment_detail(token: str, assignment_id: str) -> Dict:
    resp = requests.get(
        f"{BASE_URL}/assignments/{assignment_id}/", headers=auth_headers(token)
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") == 200:
        return data["data"]
    raise RuntimeError(f"获取作业详情失败: {assignment_id} -> {data}")


def submit_answers(
    student_token: str,
    assignment_id: str,
    answers: List[Dict],
) -> str | None:
    # 使用 multipart/form-data 并严格匹配前端字段命名：answers[0]question_id / answers[0]answer_text
    # 这样可与后端 FormParser/MultiPartParser 的现有解析方式对齐
    files: List[Tuple[str, Tuple[None, str]]] = []
    for i, a in enumerate(answers):
        files.append((f"answers[{i}]question_id", (None, str(a["question_id"]))))
        if a.get("answer_text") is not None:
            files.append((f"answers[{i}]answer_text", (None, a["answer_text"])))
        # 若包含图片：files.append((f"answers[{i}]answer_image", ("answer.png", image_bytes, "image/png")))

    resp = requests.post(
        f"{BASE_URL}/assignments/{assignment_id}/submissions/",
        files=files,
        headers=auth_only_headers(student_token),
    )
    try:
        data = resp.json()
    except Exception:
        data = {"message": resp.text}
    if resp.status_code == 201:
        sub_id = data["data"]["submission_id"]
        print(f"[OK] 提交作业成功 -> submission_id={sub_id}")
        return sub_id
    print(f"[WARN] 提交失败 -> {resp.status_code} - {data}")
    return None


def generate_student_answers(
    questions: List[Dict],
    mode: str,
) -> List[Dict]:
    """按模式生成学生答案。

    mode:
      - exact: 全部精准正确（与参考答案完全一致）
      - mixed: 前半对，后半错
      - wrong: 全错
    """
    answers: List[Dict] = []
    n = len(questions)
    split = n // 2
    for idx, q in enumerate(questions):
        qid = q["id"]
        ref = q["reference_answer"].strip()
        if mode == "exact":
            text = ref
        elif mode == "mixed":
            text = ref if idx < split else "这个答案是随意的，与问题无关。"
        else:  # wrong
            text = "错误答案，与参考答案不一致。"
        answers.append({"question_id": qid, "answer_text": text})
    return answers


def main():
    # 1) 账号池
    teacher_specs = [
        ("teacher01", "张老师", "teacher"),
        ("teacher02", "王老师", "teacher"),
        ("teacher03", "刘老师", "teacher"),
    ]
    student_specs = [
        (f"student{str(i).zfill(2)}", f"学生{str(i).zfill(2)}") for i in range(1, 13)
    ]
    default_password = "testpass123"  # 与项目内测试一致

    print("\n=== 注册教师 ===")
    for uname, real_name, role in teacher_specs:
        register_user(uname, default_password, role, real_name)

    print("\n=== 注册学生 ===")
    for uname, real_name in student_specs:
        register_user(uname, default_password, "student", real_name, student_id=f"2025{uname[-2:]}")

    # 2) 登录，获取 token
    print("\n=== 登录获取Token ===")
    teacher_tokens: Dict[str, str] = {}
    for uname, _, _ in teacher_specs:
        teacher_tokens[uname] = login(uname, default_password)
        print(f"[OK] 教师登录: {uname}")

    student_tokens: Dict[str, str] = {}
    for uname, _ in student_specs:
        student_tokens[uname] = login(uname, default_password)
        print(f"[OK] 学生登录: {uname}")

    # 3) 学科与题库（参考答案尽量可精确匹配）
    subjects_bank: Dict[str, List[Tuple[str, List[Dict]]]] = {
        "Python编程": [
            (
                "Python基础测试",
                [
                    {
                        "question_text": "什么是Python？",
                        "reference_answer": "Python是一种高级编程语言，具有简洁的语法和强大的功能。",
                        "score": 10,
                    },
                    {
                        "question_text": "列表和元组的区别是什么？",
                        "reference_answer": "列表是可变的，元组是不可变的。列表用[]表示，元组用()表示。",
                        "score": 15,
                    },
                    {
                        "question_text": "什么是列表推导式？",
                        "reference_answer": "列表推导式是Python中创建列表的简洁方式。",
                        "score": 10,
                    },
                ],
            ),
            (
                "函数与模块",
                [
                    {
                        "question_text": "什么是可变参数*args？",
                        "reference_answer": "*args用于接收任意数量的位置参数，作为元组传入。",
                        "score": 10,
                    },
                    {
                        "question_text": "什么是关键字参数**kwargs？",
                        "reference_answer": "**kwargs用于接收任意数量的关键字参数，作为字典传入。",
                        "score": 10,
                    },
                    {
                        "question_text": "如何导入模块？",
                        "reference_answer": "使用import语句或from ... import ...语句导入模块。",
                        "score": 10,
                    },
                ],
            ),
        ],
        "数据结构": [
            (
                "线性结构基础",
                [
                    {
                        "question_text": "栈和队列的区别是什么？",
                        "reference_answer": "栈是后进先出(LIFO)，队列是先进先出(FIFO)。",
                        "score": 15,
                    },
                    {
                        "question_text": "链表和数组的主要区别？",
                        "reference_answer": "数组支持随机访问，链表插入删除更高效。",
                        "score": 10,
                    },
                ],
            ),
            (
                "树与哈希",
                [
                    {
                        "question_text": "二叉搜索树的性质？",
                        "reference_answer": "二叉搜索树中任一节点，左子树小于该节点，右子树大于该节点。",
                        "score": 10,
                    },
                    {
                        "question_text": "哈希表冲突如何解决？",
                        "reference_answer": "可采用开放定址或链地址法解决哈希冲突。",
                        "score": 10,
                    },
                ],
            ),
        ],
        "算法": [
            (
                "排序与复杂度",
                [
                    {
                        "question_text": "冒泡排序的时间复杂度？",
                        "reference_answer": "冒泡排序的时间复杂度是O(n²)。",
                        "score": 10,
                    },
                    {
                        "question_text": "快速排序的平均时间复杂度？",
                        "reference_answer": "快速排序的平均时间复杂度是O(n log n)。",
                        "score": 10,
                    },
                ],
            ),
            (
                "贪心与动态规划",
                [
                    {
                        "question_text": "动态规划的核心思想是什么？",
                        "reference_answer": "动态规划通过保存子问题结果避免重复计算，从而降低时间复杂度。",
                        "score": 15,
                    },
                    {
                        "question_text": "贪心算法的适用前提？",
                        "reference_answer": "问题需满足贪心选择性质和最优子结构。",
                        "score": 10,
                    },
                ],
            ),
        ],
        "计算机网络": [
            (
                "网络分层与协议",
                [
                    {
                        "question_text": "OSI七层模型有哪些？",
                        "reference_answer": "物理、数据链路、网络、传输、会话、表示、应用。",
                        "score": 15,
                    },
                    {
                        "question_text": "TCP与UDP的区别？",
                        "reference_answer": "TCP面向连接可靠传输，UDP无连接不保证可靠。",
                        "score": 10,
                    },
                ],
            )
        ],
        "操作系统": [
            (
                "进程与线程",
                [
                    {
                        "question_text": "进程与线程的区别？",
                        "reference_answer": "进程是资源分配基本单位，线程是CPU调度基本单位。",
                        "score": 15,
                    },
                    {
                        "question_text": "什么是上下文切换？",
                        "reference_answer": "上下文切换是保存与恢复任务执行现场的过程。",
                        "score": 10,
                    },
                ],
            )
        ],
        "数学": [
            (
                "离散数学基础",
                [
                    {
                        "question_text": "集合与子集的关系？",
                        "reference_answer": "若A是B的子集，则A中任意元素也属于B。",
                        "score": 10,
                    },
                    {
                        "question_text": "命题逻辑中的蕴含含义？",
                        "reference_answer": "p蕴含q表示若p为真则q必为真。",
                        "score": 10,
                    },
                ],
            )
        ],
    }

    # 4) 创建作业（轮流给三位教师分配）
    print("\n=== 按学科创建作业 ===")
    all_assignments: List[Tuple[str, str]] = []  # (assignment_id, subject)
    t_unames = [t[0] for t in teacher_specs]
    t_idx = 0
    for subject, packs in subjects_bank.items():
        for title, questions in packs:
            teacher_uname = t_unames[t_idx % len(t_unames)]
            t_idx += 1
            aid = create_assignment(
                teacher_tokens[teacher_uname],
                title=title,
                description=f"{subject}-{title} 的练习",
                subject=subject,
                questions=questions,
                deadline_days=random.randint(7, 14),
            )
            if aid:
                all_assignments.append((aid, subject))
            # 避免过快触发限流
            time.sleep(0.1)

    # 5) 学生提交（制造不同表现）
    print("\n=== 学生提交作业（触发批改） ===")
    modes = ["exact", "mixed", "wrong"]

    for idx, (assignment_id, _subject) in enumerate(all_assignments):
        # 获取题目详情用于提交
        # 使用第一个学生的 token 获取详情即可
        any_student = student_specs[0][0]
        detail = get_assignment_detail(student_tokens[any_student], assignment_id)
        questions = detail.get("questions", [])
        if not questions:
            print(f"[WARN] 作业无题目，跳过: {assignment_id}")
            continue

        # 选取部分学生提交，以产生“已完成/未完成”混合列表
        selected_students = random.sample(student_specs, k=random.randint(6, len(student_specs)))
        for s_idx, (s_uname, _s_realname) in enumerate(selected_students):
            mode = modes[(idx + s_idx) % len(modes)]
            ans = generate_student_answers(questions, mode=mode)
            submit_answers(student_tokens[s_uname], assignment_id, ans)
            time.sleep(0.05)

    print("\n=== 数据填充完成 ===")
    print(f"教师数量: {len(teacher_specs)}，学生数量: {len(student_specs)}，作业数量: {len(all_assignments)}")
    print("可在前端或 /api/docs/ 验证：\n- 作业列表/详情/提交列表\n- 学生成绩与总体反馈\n- 各学科覆盖情况")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL] 脚本失败: {e}")


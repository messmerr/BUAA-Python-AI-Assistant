# AI助教系统 API 规范文档

本文档与后端实际实现完全一致，覆盖账号与认证、作业管理与批改、智能答疑、学习报告、站内私信模块。

## 基础信息
- Base URL: `http://localhost:8000/api/v1`
- 认证: JWT（`Authorization: Bearer <access_token>`）
- 数据格式: JSON（部分接口支持 `multipart/form-data`）
- 字符编码: UTF-8

## 通用响应
成功
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```
错误
```json
{
  "code": 400,
  "message": "error",
  "errors": {}
}
```

---

## 1. 账号与认证（accounts）

### 1.1 注册
- URL: POST `/auth/register/`
- 说明: 注册 teacher|student。student 必填 `student_id`
- 请求体
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "role": "teacher|student",
  "real_name": "string",
  "student_id": "string"
}
```
- 响应 201
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "user_id": "uuid",
    "username": "string",
    "role": "teacher|student"
  }
}
```

### 1.2 登录
- URL: POST `/auth/login/`
- 响应 200
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "jwt",
    "refresh_token": "jwt",
    "user": {
      "id": "uuid",
      "username": "string",
      "role": "teacher|student",
      "real_name": "string"
    }
  }
}
```

### 1.3 刷新令牌
- URL: POST `/auth/refresh/`
- 请求体
```json
{
  "refresh": "jwt"
}
```
- 响应 200
```json
{
  "code": 200,
  "message": "Token刷新成功",
  "data": {
    "access_token": "jwt"
  }
}
```

### 1.4 当前用户信息
- URL: GET `/auth/profile/`
- 响应 200: 返回 `UserSerializer`

### 1.5 更新当前用户信息
- URL: PUT `/auth/profile/`
- 请求体（均可选）
```json
{
  "email": "string",
  "real_name": "string",
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```
- 密码更新需提供 `current_password`，且 `new_password` 与 `confirm_password` 一致

### 1.6 教师获取学生列表
- URL: GET `/auth/students/`
- 仅教师；返回 `[{ id, real_name, username }]`

---

## 2. 作业管理与批改（assignments）

### 2.1 教师创建作业
- URL: POST `/assignments/create/`
- 请求体（`questions` 必填）
```json
{
  "title": "string",
  "description": "string",
  "subject": "string",
  "questions": [
    {
      "question_text": "string",
      "reference_answer": "string",
      "score": 10
    }
  ],
  "deadline": "ISO-8601",
  "total_score": 100
}
```
- 响应 201
```json
{
  "code": 201,
  "message": "作业创建成功",
  "data": {
    "assignment_id": "uuid",
    "title": "string",
    "created_at": "datetime"
  }
}
```

### 2.2 作业列表
- URL: GET `/assignments/list/`
- 查询: `page`, `page_size`, `status`=`active|expired`, `subject`, `completion_status`=`completed|pending|all`
- 学生返回 `is_completed`/`obtained_score`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "assignments": [
      {
        "id": "uuid",
        "title": "string",
        "description": "string",
        "subject": "string",
        "deadline": "datetime",
        "total_score": 100,
        "submission_count": 10,
        "is_completed": true,
        "obtained_score": 95,
        "created_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 100,
      "total_pages": 10
    }
  }
}
```

### 2.3 作业详情
- URL: GET `/assignments/{assignment_id}/`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "subject": "string",
    "questions": [
      {
        "id": "uuid",
        "question_text": "string",
        "reference_answer": "string",
        "score": 10
      }
    ],
    "deadline": "datetime",
    "total_score": 100,
    "is_completed": true,
    "obtained_score": 95,
    "created_at": "datetime"
  }
}
```

### 2.4 学生提交作业
- URL: POST `/assignments/{assignment_id}/submissions/`
- 仅学生；答案项二择一：`answer_text` 或 `answer_image`
- JSON 示例
```json
{
  "answers": [
    {
      "question_id": "uuid",
      "answer_text": "string"
    }
  ]
}
```
- 表单示例：`answers[0][question_id]=...` 与 `answers[0][answer_image]=@xxx.png`
- 响应 201
```json
{
  "code": 201,
  "message": "作业提交成功",
  "data": {
    "submission_id": "uuid",
    "submitted_at": "datetime",
    "status": "graded"
  }
}
```

### 2.5 获取批改结果（按 submission_id，旧接口）
- URL: GET `/assignments/{assignment_id}/submissions/{submission_id}/`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "uuid",
    "assignment_title": "string",
    "submitted_at": "datetime",
    "graded_at": "datetime",
    "total_score": 100,
    "obtained_score": 95,
    "answers": [
      {
        "question_id": "uuid",
        "question_text": "string",
        "student_answer": "string",
        "reference_answer": "string",
        "score": 10,
        "obtained_score": 10,
        "ai_feedback": "string"
      }
    ],
    "overall_feedback": "string"
  }
}
```

### 2.6 获取批改结果（按 assignment_id）
- URL: GET `/assignments/{assignment_id}/result/`
- 学生查看自身；教师需传 `student_id`

### 2.7 提交列表
- URL: GET `/assignments/{assignment_id}/submissions/list/`
- 教师：本作业全部；学生：仅自己
- 查询: `page`, `page_size`, `student`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "submissions": [
      {
        "id": "uuid",
        "student_id": "uuid",
        "student_name": "string",
        "student_username": "string",
        "status": "graded",
        "obtained_score": 95,
        "total_score": 100,
        "submitted_at": "datetime",
        "graded_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 100,
      "total_pages": 10
    },
    "assignment_info": {
      "id": "uuid",
      "title": "string",
      "total_score": 100,
      "deadline": "datetime",
      "submission_count": 20
    }
  }
}
```

---

## 3. 智能答疑（qa）

### 3.1 学生与AI多轮对话
- URL: POST `/qa/chat/`
- 请求体
```json
{
  "session_id": "uuid(可选)",
  "message": "string",
  "subject": "string(默认通用)"
}
```
- 响应 200
```json
{
  "code": 200,
  "message": "聊天成功",
  "data": {
    "session_id": "uuid",
    "ai_response": "string",
    "created_at": "datetime"
  }
}
```

### 3.2 会话列表
- URL: GET `/qa/sessions/`
- 查询: `page`, `page_size`, `subject`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "sessions": [
      {
        "id": "uuid",
        "subject": "string",
        "created_at": "datetime",
        "updated_at": "datetime",
        "last_message": {
          "role": "user|ai",
          "content": "string",
          "created_at": "datetime"
        },
        "message_count": 10
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 50,
      "total_pages": 5
    }
  }
}
```

### 3.3 会话详情
- URL: GET `/qa/sessions/{session_id}/`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "uuid",
    "subject": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "messages": [
      {
        "id": "uuid",
        "role": "user|ai",
        "content": "string",
        "created_at": "datetime"
      }
    ]
  }
}
```

### 3.4 旧接口：提交问题
- URL: POST `/qa/questions/`
- 请求体
```json
{
  "question_text": "string",
  "subject": "string",
  "context": "string"
}
```
- 响应 201
```json
{
  "code": 201,
  "message": "问题提交成功",
  "data": {
    "question_id": "uuid",
    "ai_answer": "string",
    "created_at": "datetime"
  }
}
```

### 3.5 旧接口：问题详情/列表
- URL: GET `/qa/questions/{question_id}/`
- URL: GET `/qa/questions/list/`
- 查询: `page`, `page_size`, `subject`

---

## 4. 学习报告（reports）

### 4.1 生成学习报告（学生/教师）
- URL: POST `/reports/generate/`
- 请求体
```json
{
  "student_id": "uuid(教师必填)",
  "period": "week|month|semester|all",
  "subjects": [
    "string"
  ]
}
```
- 响应 201
```json
{
  "code": 201,
  "message": "报告生成成功",
  "data": {
    "report_id": "uuid",
    "status": "completed",
    "created_at": "datetime"
  }
}
```

### 4.2 报告列表
- URL: GET `/reports/list/`
- 学生仅看自己；教师全部
- 查询: `page`, `page_size`, `status`, `period`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "reports": [
      {
        "id": "uuid",
        "student_name": "string",
        "generated_by_name": "string",
        "period": "week|month|semester|all",
        "period_display": "string",
        "subjects": [
          "string"
        ],
        "status": "completed",
        "status_display": "string",
        "total_assignments": 0,
        "completed_assignments": 0,
        "average_score": 0.0,
        "total_questions": 0,
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 100,
      "total_pages": 10
    }
  }
}
```

### 4.3 报告详情
- URL: GET `/reports/{report_id}/`
- 响应 200（结构示例）
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "uuid",
    "student_name": "string",
    "student_id_number": "string",
    "generated_by_name": "string",
    "period": "week|month|semester|all",
    "period_display": "string",
    "subjects": [
      "string"
    ],
    "status": "completed",
    "status_display": "string",
    "total_assignments": 0,
    "completed_assignments": 0,
    "average_score": 0.0,
    "total_questions": 0,
    "report_content": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

### 4.4 教师生成班级报告
- URL: POST `/reports/class/generate/`
- 请求体
```json
{
  "period": "week|month|semester|all",
  "subjects": [
    "string"
  ]
}
```
- 响应 200
```json
{
  "code": 200,
  "message": "班级报告生成成功",
  "data": {
    "statistics": {},
    "report_content": "string",
    "generated_at": "datetime"
  }
}
```

---

## 5. 站内私信（chat）

### 5.1 可聊天用户列表
- URL: GET `/chat/users/`
- 教师获取学生，学生获取教师

### 5.2 拉取会话消息
- URL: GET `/chat/messages/{user_id}/`
- 查询: `page`, `page_size`

### 5.3 发送消息
- URL: POST `/chat/messages/`
- 请求体
```json
{
  "receiver_id": "uuid",
  "content": "string"
}
```
- 响应 201: 返回保存的消息对象

### 5.4 将与某用户消息设为已读
- URL: POST `/chat/messages/{user_id}/read/`
- 响应 200
```json
{
  "code": 200,
  "message": "已标记 X 条消息为已读"
}
```

### 5.5 未读总数
- URL: GET `/chat/unread-count/`
- 响应 200
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total_unread": 3
  }
}
```

---

## 状态码
200, 201, 400, 401, 403, 404, 500（其余视具体实现返回）

## 备注
- 学生/教师权限严格校验；教师仅可操作自己创建的作业或按接口要求查看指定学生数据
- 作业提交支持图片识别（后端自动OCR到文本再批改）
- OpenAPI 在线文档与真实接口一致，可直接试调

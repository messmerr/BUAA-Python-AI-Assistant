# AI助教系统 API 规范文档

## 概述

本文档定义了AI助教系统的RESTful API接口规范，支持前后端分离的开发模式。系统分为必做功能和选做功能两部分。

### 基础信息
- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 通用响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {},
    "timestamp": "2025-07-23T10:00:00Z"
}
```

### 错误响应格式
```json
{
    "code": 400,
    "message": "error description",
    "errors": {},
    "timestamp": "2025-07-23T10:00:00Z"
}
```

## 一、必做功能接口

### 1. 用户认证系统

#### 1.1 用户注册
- **URL**: `POST /auth/register`
- **描述**: 用户注册（教师/学生）
- **请求体**:
```json
{
    "username": "string",
    "password": "string",
    "email": "string",
    "role": "teacher|student",
    "real_name": "string",
    "student_id": "string" // 学生必填
}
```
- **响应**:
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

#### 1.2 用户登录
- **URL**: `POST /auth/login`
- **描述**: 用户登录获取JWT token
- **请求体**:
```json
{
    "username": "string",
    "password": "string"
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "access_token": "jwt_token",
        "refresh_token": "jwt_token",
        "user": {
            "id": "uuid",
            "username": "string",
            "role": "teacher|student",
            "real_name": "string"
        }
    }
}
```

#### 1.3 刷新Token
- **URL**: `POST /auth/refresh`
- **描述**: 刷新访问令牌
- **请求头**: `Authorization: Bearer <refresh_token>`
- **响应**:
```json
{
    "code": 200,
    "message": "Token刷新成功",
    "data": {
        "access_token": "new_jwt_token"
    }
}
```

#### 1.4 用户信息管理
- **URL**: `GET /auth/profile`
- **描述**: 获取当前用户信息
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": "uuid",
        "username": "string",
        "email": "string",
        "role": "teacher|student",
        "real_name": "string",
        "student_id": "string",
        "created_at": "datetime"
    }
}
```

- **URL**: `PUT /auth/profile`
- **描述**: 更新用户信息
- **请求头**: `Authorization: Bearer <access_token>`
- **请求体**:
```json
{
    "email": "string",
    "real_name": "string"
}
```

### 2. 作业批改功能

#### 2.1 作业管理（教师端）

##### 2.1.1 创建作业
- **URL**: `POST /assignments/create`
- **描述**: 教师创建作业
- **权限**: 仅教师
- **请求体**:
```json
{
    "title": "string",
    "description": "string",
    "subject": "string",  // 科目名称，如"数学"、"Python编程"等
    "questions": [
        {
            "question_text": "string",
            "reference_answer": "string",
            "score": "integer"
        }
    ],
    "deadline": "datetime",
    "total_score": "integer"
}
```
- **响应**:
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

##### 2.1.2 获取作业列表
- **URL**: `GET /assignments/list`
- **描述**: 获取作业列表
- **查询参数**:
  - `page`: 页码（默认1）
  - `page_size`: 每页数量（默认10）
  - `status`: 作业状态（active|expired|draft）
  - `subject`: 科目筛选
  - `completion_status`: 完成状态筛选 (completed|pending|all) // 仅学生可用
- **响应**:
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
                "total_score": "integer",
                "submission_count": "integer", // 教师视角：提交人数
                "is_completed": "boolean",     // 学生视角：是否已完成
                "obtained_score": "integer",   // 学生视角：获得分数(已完成时)
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

##### 2.1.3 获取作业详情
- **URL**: `GET /assignments/{assignment_id}`
- **描述**: 获取作业详细信息
- **响应**:
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
                "score": "integer"
            }
        ],
        "deadline": "datetime",
        "total_score": "integer",
        "is_completed": "boolean",     // 学生视角：是否已完成
        "obtained_score": "integer",   // 学生视角：获得分数(已完成时)
        "created_at": "datetime"
    }
}
```

#### 2.2 作业提交（学生端）

##### 2.2.1 提交作业
- **URL**: `POST /assignments/{assignment_id}/submissions`
- **描述**: 学生提交作业答案
- **权限**: 仅学生
- **请求体**:
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
- **响应**:
```json
{
    "code": 201,
    "message": "作业提交成功",
    "data": {
        "submission_id": "uuid",
        "submitted_at": "datetime",
        "status": "submitted|grading|graded"
    }
}
```

##### 2.2.2 获取作业批改结果
- **URL**: `GET /assignments/{assignment_id}/result`
- **描述**: 获取作业批改结果（学生查看自己的结果）
- **权限**: 学生查看自己的，教师查看指定学生的
- **查询参数**:
  - `student_id` (可选): 教师查看指定学生的结果
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "submission_id": "uuid",
        "assignment_title": "string",
        "submitted_at": "datetime",
        "graded_at": "datetime",
        "total_score": "integer",
        "obtained_score": "integer",
        "status": "graded",
        "answers": [
            {
                "question_id": "uuid",
                "question_text": "string",
                "student_answer": "string",
                "reference_answer": "string",
                "score": "integer",
                "obtained_score": "integer",
                "ai_feedback": "string"
            }
        ],
        "overall_feedback": "string"
    }
}
```

**错误响应**:
```json
{
    "code": 404,
    "message": "作业尚未提交或不存在"
}
```

##### 2.2.3 获取作业提交列表
- **URL**: `GET /assignments/{assignment_id}/submissions/list`
- **描述**: 获取作业提交列表（教师查看所有提交，学生查看自己的提交）
- **权限**: 教师查看所有，学生查看自己的
- **查询参数**:
  - `page` (可选): 页码，默认1
  - `page_size` (可选): 每页数量，默认10
  - `student` (可选): 学生用户名筛选（仅教师可用）
- **响应**:
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
                "status": "submitted|grading|graded",
                "obtained_score": "integer",
                "total_score": "integer",
                "submitted_at": "datetime",
                "graded_at": "datetime"
            }
        ],
        "pagination": {
            "page": "integer",
            "page_size": "integer",
            "total": "integer",
            "total_pages": "integer"
        },
        "assignment_info": {
            "id": "uuid",
            "title": "string",
            "total_score": "integer",
            "deadline": "datetime",
            "submission_count": "integer"
        }
    }
}
```

### 3. 智能答疑功能 ✅ 已升级

智能答疑模块提供AI驱动的多轮对话功能，支持会话管理和上下文记忆。

#### 3.1 发送聊天消息（新接口）
- **URL**: `POST /qa/chat/`
- **描述**: 发送聊天消息，支持多轮对话和上下文记忆
- **权限**: 仅学生
- **请求体**:
```json
{
    "session_id": "uuid", // 可选，新对话时不传
    "message": "string",
    "subject": "string" // 可选，默认为'通用'
}
```
- **响应**:
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

#### 3.2 获取会话列表（新接口）
- **URL**: `GET /qa/sessions/`
- **描述**: 获取用户的聊天会话列表
- **权限**: 学生查看自己的，教师查看所有
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `subject`: 学科筛选
- **响应**:
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

#### 3.3 获取会话详情（新接口）
- **URL**: `GET /qa/sessions/{session_id}/`
- **描述**: 获取指定会话的完整对话记录
- **权限**: 学生查看自己的，教师查看所有
- **响应**:
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

#### 3.4 提问（旧接口，保持兼容）
- **URL**: `POST /qa/questions/`
- **描述**: 学生提交问题，AI自动回答（单轮对话）
- **权限**: 仅学生
- **请求体**:
```json
{
    "question_text": "string",
    "subject": "string",
    "context": "string" // 可选，问题上下文
}
```
- **响应**:
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

#### 3.5 获取问答历史（旧接口，保持兼容）
- **URL**: `GET /qa/questions/list/`
- **描述**: 获取用户问答历史（学生查看自己的，教师查看所有）
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `subject`: 学科筛选
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "questions": [
            {
                "id": "uuid",
                "question_text": "string",
                "ai_answer": "string",
                "subject": "string",
                "created_at": "datetime"
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

#### 3.3 获取问题详情
- **URL**: `GET /qa/questions/{question_id}/`
- **描述**: 获取问题详情和AI回答
- **权限**: 登录用户
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": "uuid",
        "question_text": "string",
        "subject": "string",
        "context": "string",
        "ai_answer": "string",
        "created_at": "datetime",
        "student": {
            "id": "uuid",
            "username": "string",
            "real_name": "string"
        }
    }
}
```

### 4. 学习报告功能

学习报告模块负责根据学生的学习数据（作业、问答等）生成综合性评估报告。

#### 4.1 生成学习报告
- **URL**: `POST /reports/generate/`
- **描述**: 按需生成一份新的学生学习报告。后端将收集指定范围内的学习数据，调用AI大模型生成报告内容，并将结果持久化保存。
- **权���**: 学生（仅自己）, 教师（可为指定学生）
- **请求体**:
```json
{
    "student_id": "uuid", // 教师为学生生成报告时必填
    "period": "week|month|semester|all", // 报告统计周期, 'all'表示全部
    "subjects": ["string"] // 可选，指定报告覆盖的学科范围，为空则代表全部学科
}
```
- **响应 (201 Created)**:
```json
{
    "code": 201,
    "message": "学习报告生成成功",
    "data": {
        "id": "uuid",
        "student_id": "uuid",
        "generated_at": "datetime",
        "period": "string",
        "subjects": ["string"],
        "content": "string" 
    }
}
```

#### 4.2 获取学习报告列表
- **URL**: `GET /reports/list/`
- **描述**: 获取历史学习报告列表（不含报告正文）。
- **权限**: 学生（仅自己）, 教师（可查看学生）
- **查询参数**:
  - `student_id` (可选): 教师按学生ID筛选
  - `page` (可选): 页码
  - `page_size` (可选): 每页数量
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "reports": [
            {
                "id": "uuid",
                "student_id": "uuid",
                "student_name": "string",
                "generated_at": "datetime",
                "period": "string",
                "subjects": ["string"]
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "total": 20,
            "total_pages": 2
        }
    }
}
```

#### 4.3 获取学习报告详情
- **URL**: `GET /reports/{report_id}/`
- **描述**: 获取指定ID的学习报告的完整内容。
- **权限**: 报告所有者或教师
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": "uuid",
        "student_id": "uuid",
        "student_name": "string",
        "generated_at": "datetime",
        "period": "string",
        "subjects": ["string"],
        "content": "string" 
    }
}
```
## 二、选做功能接口

### 1. 图片作业识别功能

#### 1.1 上传图片作业
- **URL**: `POST /assignments/{assignment_id}/submissions/image`
- **描述**: 上传图片形式的作业，AI自动OCR识别并批改
- **权限**: 仅学生
- **请求体**: `multipart/form-data`
```
image: file (支持jpg, png, pdf格式)
```
- **响应**:
```json
{
    "code": 201,
    "message": "图片作业提交成功",
    "data": {
        "submission_id": "uuid",
        "image_url": "string",
        "status": "submitted|processing|graded",
        "submitted_at": "datetime"
    }
}
```

### 2. 高级答疑功能

#### 2.1 深度问答
- **URL**: `POST /qa/questions/advanced`
- **描述**: 复杂问题的深度AI分析
- **权限**: 仅学生
- **请求体**:
```json
{
    "question_text": "string",
    "context": "string", // 可选上下文
    "difficulty": "basic|intermediate|advanced"
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "深度分析完成",
    "data": {
        "question_id": "uuid",
        "ai_answer": "string",
        "explanation": "string", // 详细解释
        "examples": ["string"], // 相关例子
        "created_at": "datetime"
    }
}
```

### 3. 学习资源推荐功能

#### 3.1 获取个性化推荐
- **URL**: `GET /recommendations`
- **描述**: 根据学习报告推荐学习资料
- **权限**: 仅学生
- **查询参数**:
  - `subject`: 学科筛选
  - `difficulty`: 难度级别（easy|medium|hard）
  - `type`: 资源类型（video|article|exercise|book）
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "recommendations": [
            {
                "id": "uuid",
                "title": "string",
                "description": "string",
                "type": "video|article|exercise|book",
                "url": "string",
                "difficulty": "easy|medium|hard",
                "subject": "string",
                "rating": "float",
                "estimated_time": "integer", // 预计学习时间（分钟）
                "reason": "string" // 推荐理由
            }
        ],
        "total": "integer"
    }
}
```

#### 3.2 资源收藏
- **URL**: `POST /recommendations/{resource_id}/favorite`
- **描述**: 收藏学习资源
- **权限**: 仅学生
- **响应**:
```json
{
    "code": 200,
    "message": "收藏成功",
    "data": {
        "favorited": true,
        "favorited_at": "datetime"
    }
}
```

#### 3.3 获取收藏列表
- **URL**: `GET /recommendations/favorites`
- **描述**: 获取用户收藏的学习资源
- **权限**: 仅学生
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "favorites": [
            {
                "id": "uuid",
                "title": "string",
                "type": "video|article|exercise|book",
                "url": "string",
                "favorited_at": "datetime"
            }
        ],
        "total": "integer"
    }
}
```

### 4. 班级数据可视化分析（教师端）

#### 4.1 班级整体统计
- **URL**: `GET /analytics/class/overview`
- **描述**: 获取班级整体学习情况统计
- **权限**: 仅教师
- **查询参数**:
  - `class_id`: 班级ID（可选，默认所有班级）
  - `period`: 统计周期（week|month|semester）
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "class_info": {
            "class_id": "uuid",
            "class_name": "string",
            "student_count": "integer"
        },
        "assignment_stats": {
            "total_assignments": "integer",
            "average_completion_rate": "float",
            "average_score": "float",
            "score_distribution": {
                "excellent": "integer", // 90-100分人数
                "good": "integer",      // 80-89分人数
                "fair": "integer",      // 70-79分人数
                "poor": "integer"       // <70分人数
            }
        },
        "qa_stats": {
            "total_questions": "integer",
            "active_students": "integer",
            "common_topics": [
                {
                    "topic": "string",
                    "question_count": "integer"
                }
            ]
        },
        "period": "string",
        "generated_at": "datetime"
    }
}
```

#### 4.2 作业完成情况分析
- **URL**: `GET /analytics/assignments/{assignment_id}/stats`
- **描述**: 获取特定作业的完成情况统计
- **权限**: 仅教师
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "assignment_info": {
            "id": "uuid",
            "title": "string",
            "total_score": "integer",
            "deadline": "datetime"
        },
        "submission_stats": {
            "total_students": "integer",
            "submitted_count": "integer",
            "completion_rate": "float",
            "on_time_submissions": "integer",
            "late_submissions": "integer"
        },
        "score_analysis": {
            "average_score": "float",
            "highest_score": "integer",
            "lowest_score": "integer",
            "score_distribution": [
                {
                    "range": "90-100",
                    "count": "integer",
                    "percentage": "float"
                }
            ]
        },
        "question_analysis": [
            {
                "question_id": "uuid",
                "question_text": "string",
                "average_score": "float",
                "correct_rate": "float",
                "common_errors": ["string"]
            }
        ]
    }
}
```

#### 4.3 常见问题汇总
- **URL**: `GET /analytics/qa/common-issues`
- **描述**: 获取学生常见问题汇总
- **权限**: 仅教师
- **查询参数**:
  - `period`: 统计周期（week|month|semester）
  - `subject`: 学科筛选
  - `limit`: 返回数量限制（默认20）
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "common_issues": [
            {
                "topic": "string",
                "question_count": "integer",
                "sample_questions": ["string"],
                "suggested_solution": "string",
                "difficulty_level": "easy|medium|hard"
            }
        ],
        "period": "string",
        "total_questions": "integer",
        "generated_at": "datetime"
    }
}
```

### 5. 实时互动功能

#### 5.1 发送消息
- **URL**: `POST /chat/messages`
- **描述**: 发送实时消息
- **权限**: 教师和学生
- **请求体**:
```json
{
    "recipient_id": "uuid", // 接收者ID
    "message_text": "string",
    "message_type": "text|image|file",
    "attachment_url": "string" // 可选，附件URL
}
```
- **响应**:
```json
{
    "code": 201,
    "message": "消息发送成功",
    "data": {
        "message_id": "uuid",
        "sent_at": "datetime",
        "status": "sent|delivered|read"
    }
}
```

#### 5.2 获取聊天记录
- **URL**: `GET /chat/conversations/{user_id}`
- **描述**: 获取与特定用户的聊天记录
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `before`: 获取指定时间之前的消息
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "conversation": {
            "participant": {
                "id": "uuid",
                "name": "string",
                "role": "teacher|student"
            },
            "messages": [
                {
                    "id": "uuid",
                    "sender_id": "uuid",
                    "message_text": "string",
                    "message_type": "text|image|file",
                    "attachment_url": "string",
                    "sent_at": "datetime",
                    "read_at": "datetime"
                }
            ]
        },
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 100,
            "has_more": true
        }
    }
}
```

#### 5.3 WebSocket连接（实时通信）
- **URL**: `ws://localhost:8000/ws/chat/{user_id}/`
- **描述**: 建立WebSocket连接进行实时通信
- **认证**: 通过查询参数传递token: `?token=jwt_token`
- **消息格式**:
```json
{
    "type": "message|typing|read_receipt",
    "data": {
        "message_id": "uuid",
        "recipient_id": "uuid",
        "content": "string",
        "timestamp": "datetime"
    }
}
```

## 三、通用接口

### 1. 文件上传
- **URL**: `POST /files/upload`
- **描述**: 通用文件上传接口
- **请求体**: `multipart/form-data`
```
file: file
type: string (avatar|assignment|attachment)
```
- **响应**:
```json
{
    "code": 200,
    "message": "上传成功",
    "data": {
        "file_id": "uuid",
        "file_url": "string",
        "file_name": "string",
        "file_size": "integer",
        "file_type": "string",
        "uploaded_at": "datetime"
    }
}
```

### 2. 系统配置
- **URL**: `GET /system/config`
- **描述**: 获取系统配置信息
- **响应**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "system_name": "AI助教系统",
        "version": "1.0.0",
        "features": {
            "ocr_enabled": true,
            "ai_search_enabled": true,
            "chat_enabled": true
        },
        "limits": {
            "max_file_size": "10MB",
            "max_questions_per_day": 100,
            "max_assignments_per_course": 50
        }
    }
}
```

## 四、状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录或token无效） |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如用户名已存在） |
| 422 | 请求参数验证失败 |
| 429 | 请求频率限制 |
| 500 | 服务器内部错误 |

## 五、开发注意事项

1. **认证机制**: 除了注册和登录接口，其他接口都需要在请求头中携带JWT token
2. **权限控制**: 严格区分教师和学生权限，防止越权访问
3. **数据验证**: 所有输入数据都需要进行严格的验证和过滤
4. **错误处理**: 统一的错误响应格式，便于前端处理
5. **性能优化**: 对于数据量大的接口，实现分页和缓存机制
6. **安全考虑**:
   - 密码加密存储
   - 防止SQL注入和XSS攻击
   - 文件上传安全检查
   - API访问频率限制
7. **日志记录**: 记录关键操作日志，便于问题排查和审计
```

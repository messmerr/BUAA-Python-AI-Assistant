## AI助教系统 API 快速参考

### 基础信息
- Base URL: `http://localhost:8000/api/v1`
- 认证: `Authorization: Bearer <access_token>`（除注册/登录外均需）
- 数据格式: `application/json`（作业提交也支持 `multipart/form-data`）
- 在线文档: `http://localhost:8000/api/docs/`

### 模块与端点速览

#### 账号与认证（accounts）
- POST `/auth/register/` 用户注册（teacher|student）
- POST `/auth/login/` 登录，返回 `access_token` 与 `refresh_token`
- POST `/auth/refresh/` 刷新访问令牌（请求体需携带 `refresh`）
- GET  `/auth/profile/` 获取当前用户信息
- PUT  `/auth/profile/` 更新当前用户信息（支持修改密码：`current_password`/`new_password`/`confirm_password`）
- GET  `/auth/students/` 教师获取学生列表

#### 作业管理与批改（assignments）
- POST `/assignments/create/` 教师创建作业
- GET  `/assignments/list/` 作业列表（支持科目、状态、完成度筛选与分页）
- GET  `/assignments/{assignment_id}/` 作业详情
- POST `/assignments/{assignment_id}/submissions/` 学生提交作业（文本或图片二选一）
- GET  `/assignments/{assignment_id}/submissions/list/` 提交列表（教师全部/学生本人）
- GET  `/assignments/{assignment_id}/result/` 获取批改结果（教师需传 `student_id`）
- GET  `/assignments/{assignment_id}/submissions/{submission_id}/` 获取批改结果（旧接口，兼容）

常用查询参数：
- 列表分页: `page`, `page_size`
- 作业列表: `status`=`active|expired`, `subject`, `completion_status`=`completed|pending|all`
- 提交列表: `student`（教师按用户名模糊筛）

#### 智能答疑（qa）
- POST `/qa/chat/` 学生向AI发送聊天消息（多轮，会创建/复用 `session`）
- GET  `/qa/sessions/` 会话列表（按学科与分页筛选）
- GET  `/qa/sessions/{session_id}/` 会话详情（含消息）
- POST `/qa/questions/` 学生提交问题（旧接口，单轮）
- GET  `/qa/questions/list/` 问题列表
- GET  `/qa/questions/{question_id}/` 问题详情

#### 学习报告（reports）
- POST `/reports/generate/` 生成学习报告（学生自身/教师为指定学生）
- GET  `/reports/list/` 报告列表（学生仅自己，教师全部）
- GET  `/reports/{report_id}/` 报告详情
- POST `/reports/class/generate/` 教师生成班级报告（返回统计与AI报告文本）

#### 站内私信（chat）
- GET  `/chat/users/` 可聊天用户列表（教师⇄学生）
- GET  `/chat/messages/{user_id}/` 与指定用户的聊天记录（分页）
- POST `/chat/messages/` 发送消息（`receiver_id`, `content`）
- POST `/chat/messages/{user_id}/read/` 将与该用户的未读设为已读
- GET  `/chat/unread-count/` 当前用户未读总数

### 典型请求示例

注册
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student001",
    "password": "password123",
    "email": "student@example.com",
    "role": "student",
    "real_name": "张三",
    "student_id": "2023001"
  }'
```

登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student001",
    "password": "password123"
  }'
```

创建作业（教师）
```bash
curl -X POST http://localhost:8000/api/v1/assignments/create/ \
  -H "Authorization: Bearer <teacher_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python基础测试",
    "description": "测试Python基础",
    "subject": "Python编程",
    "questions": [
      {
        "question_text": "什么是Python？",
        "reference_answer": "示例参考答案",
        "score": 10
      }
    ],
    "deadline": "2025-12-01T23:59:59Z",
    "total_score": 10
  }'
```

提交作业（学生，文本）
```bash
curl -X POST http://localhost:8000/api/v1/assignments/<assignment_id>/submissions/ \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": "<question_uuid>",
        "answer_text": "我的答案"
      }
    ]
  }'
```

提交作业（学生，图片）
```bash
curl -X POST http://localhost:8000/api/v1/assignments/<assignment_id>/submissions/ \
  -H "Authorization: Bearer <student_token>" \
  -F "answers[0][question_id]=<question_uuid>" \
  -F "answers[0][answer_image]=@answer.png"
```

智能答疑（多轮）
```bash
curl -X POST http://localhost:8000/api/v1/qa/chat/ \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "什么是递归？",
    "subject": "计算机科学"
  }'
```

生成学习报告
```bash
curl -X POST http://localhost:8000/api/v1/reports/generate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "period": "month",
    "subjects": [
      "Python编程"
    ],
    "student_id": "<仅教师必填>"
  }'
```

发送站内私信
```bash
curl -X POST http://localhost:8000/api/v1/chat/messages/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": "<uuid>",
    "content": "你好"
  }'
```

### 响应约定与状态码
- 成功: `{ code: 200|201, message: string, data: any }`
- 失败: `{ code: 4xx|5xx, message: string, errors?: object }`
- 常见状态码: 200/201/400/401/403/404/500

# AI助教系统 API 快速参考

## 基础信息
- **Base URL**: `http://localhost:8000/api/v1`
- **认证**: `Authorization: Bearer <jwt_token>`
- **格式**: JSON
- **AI处理**: 所有批改、OCR、答疑均由大模型API处理

## 📊 实现状态总览

### 必做功能 (3/4 模块)
- ✅ **用户认证** - 5/5 接口已实现
- ✅ **作业管理** - 7/7 接口已实现
- ✅ **智能答疑** - 6/6 接口已实现（升级为多轮对话）
- ❌ **学习报告** - 0/3 接口已实现

### 选做功能 (0/6 模块)
- ❌ **图片识别** - 0/1 接口已实现
- ⚠️ **高级答疑** - 1/2 接口已实现
- ❌ **资源推荐** - 0/3 接口已实现
- ❌ **数据分析** - 0/3 接口已实现
- ❌ **实时互动** - 0/3 接口已实现
- ❌ **通用���口** - 0/2 接口已实现

**总体进度**: 19/30 接口已实现 (63%)

## 必做功能接口

### 用户认证 ✅ 已实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/auth/register/` | 用户注册 | 公开 | ✅ |
| POST | `/auth/login/` | 用户登录 | 公开 | ✅ |
| POST | `/auth/refresh/` | 刷新Token | 需要refresh_token | ✅ |
| GET | `/auth/profile/` | 获取用户信息 | 登录用户 | ✅ |
| PUT | `/auth/profile/update/` | 更新用户信息 | 登录用户 | ✅ |

### 作业管理 ✅ 已实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/assignments/create/` | 创建作业 | 教师 | ✅ |
| GET | `/assignments/list/` | 获取作业列表 | 登录用户 | ✅ |
| GET | `/assignments/{id}/` | 获取作业详情 | 登录用户 | ✅ |
| POST | `/assignments/{id}/submissions/` | 提交作业 | 学生 | ✅ |
| GET | `/assignments/{id}/submissions/list/` | 获取提交列表 | 学生/教师 | ✅ |
| GET | `/assignments/{id}/result/` | 获取批改结果 | 学生/教师 | ✅ |
| GET | `/assignments/{id}/submissions/{sub_id}/` | 获取批改结果(旧) | 学生/教师 | ✅ |

### 智能答疑 ✅ 已升级（多轮对话）
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/qa/chat/` | 发送聊天消息（新） | 学生 | ✅ |
| GET | `/qa/sessions/` | 获取会话列表（新） | 登录用户 | ✅ |
| GET | `/qa/sessions/{id}/` | 获取会话详情（新） | 登录用户 | ✅ |
| POST | `/qa/questions/` | 提交问题（兼容） | 学生 | ✅ |
| GET | `/qa/questions/list/` | 获取问题列表（兼容） | 登录用户 | ✅ |
| GET | `/qa/questions/{id}/` | 获取问题详情（兼容） | 登录用户 | ✅ |

### 学习报告 ❌ 未实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/reports/generate/` | 生成学习报告 | 学生/教师 | ❌ |
| GET | `/reports/list/` | 获取报告列表 | 学生/教师 | ❌ |
| GET | `/reports/{id}/` | 获取报告详情 | 学生/教师 | ❌ |

## 选做功能接口

### 图片识别 ❌ 未实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/assignments/{id}/submissions/image/` | 上传图片作业 | 学生 | ❌ |

### 高级答疑 ⚠️ 部分实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/qa/questions/advanced/` | 深度AI问答 | 学生 | ❌ |
| GET | `/qa/questions/list/` | 获取问答历史 | 登录用户 | ✅ |

### 资源推荐 ❌ 未实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| GET | `/recommendations/` | 获取个性化推荐 | 学生 | ❌ |
| POST | `/recommendations/{id}/favorite/` | 收藏资源 | 学生 | ❌ |
| GET | `/recommendations/favorites/` | 获取收藏列表 | 学生 | ❌ |

### 数据分析（教师端） ❌ 未实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| GET | `/analytics/class/overview/` | 班级整体统计 | 教师 | ❌ |
| GET | `/analytics/assignments/{id}/stats/` | 作业统计分析 | 教师 | ❌ |
| GET | `/analytics/qa/common-issues/` | 常见问题汇总 | 教师 | ❌ |

### 实时互动 ❌ 未实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/chat/messages/` | 发送消息 | 登录用户 | ❌ |
| GET | `/chat/conversations/{user_id}/` | 获取聊天记录 | 登录用户 | ❌ |
| WS | `/ws/chat/{user_id}/` | WebSocket连接 | 登录用户 | ❌ |

### 其他选做功能 ❌ 未实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| GET | `/reports/` | 获取历史报告 | 学生/教师 | ❌ |

### 通用接口 ❌ 未实现
| 方法 | 路径 | 描述 | 权限 | 状态 |
|------|------|------|------|------|
| POST | `/files/upload/` | 文件上传 | 登录用户 | ❌ |
| GET | `/system/config/` | 系统配置 | 公开 | ❌ |

## 常用请求示例

### 用户注册 ✅
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

### 用户登录 ✅
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student001",
    "password": "password123"
  }'
```

### 创建作业（教师）✅
```bash
curl -X POST http://localhost:8000/api/v1/assignments/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <teacher_token>" \
  -d '{
    "title": "Python基础练习",
    "description": "完成以下Python编程题目",
    "subject": "Python编程",
    "questions": [
      {
        "question_text": "编写一个函数计算斐波那契数列",
        "reference_answer": "def fibonacci(n): ...",
        "score": 20,
        "order": 1
      }
    ],
    "deadline": "2025-08-01T23:59:59Z",
    "total_score": 100
  }'
```

### 提交作业（学生）✅
```bash
curl -X POST http://localhost:8000/api/v1/assignments/{assignment_id}/submissions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <student_token>" \
  -d '{
    "answers": [
      {
        "question_id": "uuid",
        "answer_text": "def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)"
      }
    ]
  }'
```

### 智能答疑（新聊天接口）✅
```bash
# 开始新对话
curl -X POST http://localhost:8000/api/v1/qa/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <student_token>" \
  -d '{
    "message": "Python中列表和元组的区别是什么？",
    "subject": "Python编程"
  }'

# 继续对话（使用返回的session_id）
curl -X POST http://localhost:8000/api/v1/qa/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <student_token>" \
  -d '{
    "session_id": "uuid-from-previous-response",
    "message": "能给我一个具体的代码示例吗？"
  }'
```

### 获取会话列表（新接口）✅
```bash
curl -X GET "http://localhost:8000/api/v1/qa/sessions/?page=1&page_size=10&subject=Python" \
  -H "Authorization: Bearer <student_token>"
```

### 获取会话详情（新接口）✅
```bash
curl -X GET http://localhost:8000/api/v1/qa/sessions/{session_id}/ \
  -H "Authorization: Bearer <student_token>"
```

### 获取作业列表 ✅
```bash
curl -X GET "http://localhost:8000/api/v1/assignments/list/?page=1&page_size=10&subject=Python&completion_status=pending" \
  -H "Authorization: Bearer <student_token>"
```

### 获取作业详情 ✅
```bash
curl -X GET http://localhost:8000/api/v1/assignments/{assignment_id}/ \
  -H "Authorization: Bearer <token>"
```

### 获取批改结果 ✅
```bash
curl -X GET http://localhost:8000/api/v1/assignments/{assignment_id}/submissions/{submission_id}/ \
  -H "Authorization: Bearer <student_token>"
```

<!-- 以下为未实现功能的示例，暂时注释
### 深度问答 ❌
```bash
curl -X POST http://localhost:8000/api/v1/qa/questions/advanced/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <student_token>" \
  -d '{
    "question_text": "解释机器学习中的过拟合现象",
    "context": "正在学习机器学习算法",
    "difficulty": "advanced"
  }'
```

### 上传图片作业 ❌
```bash
curl -X POST http://localhost:8000/api/v1/assignments/{assignment_id}/submissions/image/ \
  -H "Authorization: Bearer <student_token>" \
  -F "image=@homework.jpg"
```

### 生成学习报告 ❌
```bash
# 教师为学生生成报告
curl -X POST http://localhost:8000/api/v1/reports/generate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <teacher_token>" \
  -d '{
    "student_id": "student-uuid",
    "period": "month",
    "subjects": ["Python编程"]
  }'

# 学生为自己生成报告
curl -X POST http://localhost:8000/api/v1/reports/generate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <student_token>" \
  -d '{
    "period": "all"
  }'
```
-->


## 响应格式示例

### 成功响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "uuid",
        "name": "example"
    },
    "timestamp": "2025-07-23T10:00:00Z"
}
```

### 错误响应
```json
{
    "code": 400,
    "message": "参数验证失败",
    "errors": {
        "username": ["用户名不能为空"],
        "email": ["邮箱格式不正确"]
    },
    "timestamp": "2025-07-23T10:00:00Z"
}
```

### 分页响应
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [...],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "total": 100,
            "total_pages": 10,
            "has_next": true,
            "has_prev": false
        }
    },
    "timestamp": "2025-07-23T10:00:00Z"
}
```

## 状态码快速参考

| 状态码 | 含义 | 常见场景 |
|--------|------|----------|
| 200 | 成功 | 正常请求 |
| 201 | 创建成功 | 注册、创建资源 |
| 400 | 请求错误 | 参数验证失败 |
| 401 | 未授权 | 未登录或token过期 |
| 403 | 权限不足 | 学生访问教师接口 |
| 404 | 资源不存在 | 访问不存在的作业 |
| 409 | 冲突 | 用户名已存在 |
| 422 | 验证失败 | 数据格式错误 |
| 429 | 频率限制 | 请求过于频繁 |
| 500 | 服务器错误 | 系统异常 |

## 开发提示

1. **认证**: 除注册/登录外，所有接口都需要JWT token
2. **权限**: 严格区分教师和学生权限
3. **分页**: 列表接口支持分页，默认每页10条
4. **文件上传**: 支持多种格式，注意大小限制
5. **实时功能**: 使用WebSocket实现实时通信
6. **错误处理**: 统一错误格式，便于前端处理
7. **安全**: 所有输入都需要验证和过滤

## 📝 开发状态说明

### ✅ 已完成的核心功能
- **用户系统**: 注册、登录、认证、权限控制
- **作业管理**: 创建、列表、详情、提交、批改
- **智能答疑**: 多轮对话、会话管理、上下文记忆、历史查询
- **AI集成**: Google Gemini API集成，支持自动批改和答疑

### 🔄 当前开发重点
- **前端界面**: Vue.js前端页面开发中
- **用户体验**: 界面优化和交互完善

### 📋 待实现功能
- **学习报告**: 数据分析和报告生成
- **图片识别**: OCR功能和图片作业处理
- **高级功能**: 资源推荐、数据可视化、实时互动

### 🚀 部署信息
- **开发环境**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/api/docs/`
- **数据库**: SQLite (开发环境)
- **AI服务**: Google Gemini API

**最后更新**: 2025-07-24

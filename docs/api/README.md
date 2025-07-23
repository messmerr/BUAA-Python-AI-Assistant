# AI助教系统 API 文档总览

## 文档结构

本目录包含了AI助教系统的完整API设计文档，为前后端协作开发提供标准规范。

### 📋 文档列表

| 文档名称 | 描述 | 用途 |
|---------|------|------|
| [api_specification.md](./api_specification.md) | 完整的API接口规范 | 详细的接口定义、请求响应格式 |
| [api_quick_reference.md](./api_quick_reference.md) | API快速参考手册 | 快速查找接口、示例代码 |
| [database_models.md](./database_models.md) | 数据库模型设计 | Django模型定义、数据库结构 |

## 🎯 项目需求概述

基于题目要求，系统需要实现以下功能：

### 必做功能 ✅
1. **用户系统**: 教师/学生注册登录、权限管理
2. **作业批改**: 作业创建、提交、自动批改、评分
3. **智能答疑**: 问题提交、NLP解析、知识库检索
4. **学习报告**: 学习数据分析、个性化报告生成

### 选做功能 🔄
1. **图片识别**: 手写作业OCR识别
2. **扩展答疑**: 网络搜索、大模型问答
3. **资源推荐**: 个性化学习资料推荐
4. **数据可视化**: 班级学习情况分析
5. **实时互动**: 师生在线交流

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django 4.x + Django REST Framework
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT Token
- **实时通信**: WebSocket (Django Channels)
- **AI处理**: 大模型API (批改、OCR、答疑统一处理)

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **UI组件**: Element Plus / Ant Design Vue

### API设计原则
- **RESTful**: 遵循REST设计规范
- **统一响应**: 标准化的响应格式
- **权限控制**: 基于角色的访问控制
- **错误处理**: 统一的错误码和消息
- **分页支持**: 大数据量接口分页处理

## 📊 数据库设计

### 核心实体关系
```
用户 (User)
├── 用户资料 (UserProfile) [1:1]
├── 作业 (Assignment) [1:N] - 教师创建
├── 作业提交 (Submission) [1:N] - 学生提交
├── 问答 (QAQuestion) [1:N] - 学生提问
├── 学习报告 (LearningReport) [1:N]
├── 聊天消息 (ChatMessage) [1:N]
└── 收藏资源 (FavoriteResource) [1:N]

作业 (Assignment)
├── 问题 (Question) [1:N]
└── 提交记录 (Submission) [1:N]

提交记录 (Submission)
├── 答案 (Answer) [1:N]
└── 图片提交 (ImageSubmission) [1:1]

问答 (QAQuestion)
└── 回答 (QAAnswer) [1:1]
```

### 关键字段设计
- **UUID主键**: 所有实体使用UUID作为主键
- **时间戳**: 创建时间、更新时间自动维护
- **软删除**: 重要数据支持软删除
- **JSON字段**: 灵活存储复杂数据结构
- **索引优化**: 查询频繁的字段添加索引

## 🔐 认证与权限

### 认证机制
- **JWT Token**: 无状态的token认证
- **双Token**: Access Token + Refresh Token
- **Token过期**: 自动刷新机制

### 权限设计
```
角色权限矩阵:
                    | 学生 | 教师 | 管理员
作业管理            |  R   | CRUD |  CRUD
作业提交            | CRUD |  R   |   R
智能答疑            | CRUD |  R   |   R
学习报告            |  R   | CRUD |  CRUD
班级分析            |  -   |  R   |   R
系统配置            |  -   |  -   |  CRUD
用户管理            |  R   |  R   |  CRUD
```

## 📡 API接口概览

### 必做功能接口 (16个)

#### 用户认证 (5个)
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新Token
- `GET /auth/profile` - 获取用户信息
- `PUT /auth/profile` - 更新用户信息

#### 作业管理 (8个)
- `POST /assignments` - 创建作业
- `GET /assignments` - 获取作业列表
- `GET /assignments/{id}` - 获取作业详情
- `PUT /assignments/{id}` - 更新作业
- `DELETE /assignments/{id}` - 删除作业
- `POST /assignments/{id}/submissions` - 提交作业
- `GET /assignments/{id}/submissions` - 获取提交列表
- `GET /assignments/{id}/submissions/{sub_id}` - 获取批改结果

#### 智能答疑 (2个)
- `POST /qa/questions` - 提交问题
- `GET /qa/questions/{id}` - 获取问题详情

#### 学习报告 (1个)
- `POST /reports/generate` - 生成学习报告

### 选做功能接口 (14个)

#### 图片识别 (1个)
- `POST /assignments/{id}/submissions/image` - 上传图片作业(AI自动OCR+批改)

#### 高级答疑 (2个)
- `POST /qa/questions/advanced` - 深度AI问答
- `GET /qa/questions` - 获取问答历史

#### 资源推荐 (3个)
- `GET /recommendations` - 获取个性化推荐
- `POST /recommendations/{id}/favorite` - 收藏资源
- `GET /recommendations/favorites` - 获取收藏列表

#### 数据分析 (3个)
- `GET /analytics/class/overview` - 班级整体统计
- `GET /analytics/assignments/{id}/stats` - 作业统计分析
- `GET /analytics/qa/common-issues` - 常见问题汇总

#### 实时互动 (3个)
- `POST /chat/messages` - 发送消息
- `GET /chat/conversations/{user_id}` - 获取聊天记录
- `WS /ws/chat/{user_id}/` - WebSocket连接

#### 报告管理 (3个)
- `GET /reports` - 获取历史报告
- `GET /reports/{id}` - 获取报告详情
- `DELETE /reports/{id}` - 删除报告

#### 通用接口 (2个)
- `POST /files/upload` - 文件上传
- `GET /system/config` - 系统配置

## 🚀 开发建议

### 开发优先级
1. **第一阶段**: 用户认证 + 基础作业管理
2. **第二阶段**: 智能答疑 + 学习报告
3. **第三阶段**: 选做功能实现
4. **第四阶段**: 性能优化 + 部署

### 协作开发
1. **前后端分离**: 基于API文档并行开发
2. **Mock数据**: 前端可使用Mock.js模拟API
3. **接口测试**: 使用Postman/Insomnia测试API
4. **文档维护**: 及时更新API变更

### 质量保证
1. **单元测试**: 覆盖核心业务逻辑
2. **集成测试**: 测试API接口功能
3. **性能测试**: 压力测试和性能优化
4. **安全测试**: 权限验证和数据安全

## 📞 技术支持

如有API设计相关问题，请参考：
1. **详细规范**: [api_specification.md](./api_specification.md)
2. **快速查询**: [api_quick_reference.md](./api_quick_reference.md)
3. **数据模型**: [database_models.md](./database_models.md)
4. **开发指南**: [../development/development_guide.md](../development/development_guide.md)

---

**最后更新**: 2025-07-23  
**版本**: v1.0.0  
**维护者**: AI助教系统开发团队

# 🚀 快速启动指南

## 📋 环境要求

- **Python**: 3.8+ (推荐 3.10+)
- **Node.js**: 16+ (推荐 18+)
- **npm**: 8+ 或 **yarn**: 1.22+

## ⚡ 快速启动（5分钟搞定）

### 1. 克隆项目
```bash
git clone <repository-url>
cd BUAA-Python-AI-Assistant
```

### 2. 后端配置

#### 2.1 创建虚拟环境
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 配置环境变量
```bash
cp .env.example .env
```

#### 2.4 数据库迁移

清空数据库（可选）
```bash
del db.sqlite3 
```

数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 2.5 创建超级用户（可选）
```bash
python manage.py createsuperuser
```

#### 2.6 启动后端服务
```bash
python manage.py runserver
```
后端将运行在: http://127.0.0.1:8000

### 3. 前端配置

#### 3.1 安装依赖
```bash
cd frontend
npm install
# 或者使用 yarn
yarn install
```

#### 3.2 启动前端服务
```bash
npm run dev
# 或者使用 yarn
yarn dev
```
前端将运行在: http://localhost:5173

## 🎯 验证安装

1. **访问前端**: http://localhost:5173
2. **注册账号**: 创建教师或学生账号
3. **测试功能**: 
   - 教师：创建作业
   - 学生：提交作业、智能答疑

## 📦 依赖说明

### 后端依赖 (requirements.txt)
- **Django 5.2.4**: Web框架
- **djangorestframework**: REST API框架
- **django-cors-headers**: 跨域支持
- **djangorestframework-simplejwt**: JWT认证
- **google-generativeai**: Google AI API
- **drf-spectacular**: API文档生成
- **python-dotenv**: 环境变量管理

### 前端依赖 (package.json)
- **Vue 3**: 前端框架
- **Vue Router**: 路由管理
- **Pinia**: 状态管理
- **Element Plus**: UI组件库
- **Axios**: HTTP客户端
- **TypeScript**: 类型支持

## 🔧 常见问题

### Q: 后端启动失败，提示找不到模块
A: 确保已激活虚拟环境并安装了所有依赖

### Q: 前端启动失败，提示端口被占用
A: 修改端口或关闭占用端口的程序
```bash
npm run dev -- --port 3000
```

### Q: AI功能不工作
A: 检查 `.env` 文件中的 `GOOGLE_AI_API_KEY` 是否正确配置

### Q: 跨域错误
A: 确保后端的 CORS 配置包含前端地址

## 📚 更多信息

- **API文档**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **管理后台**: http://127.0.0.1:8000/admin/
- **项目文档**: 查看 `docs/` 目录

## 🆘 需要帮助？

如果遇到问题，请检查：
1. Python 和 Node.js 版本是否符合要求
2. 所有依赖是否正确安装
3. 环境变量是否正确配置
4. 端口是否被占用

---

**🎉 恭喜！现在你可以开始使用 AI 智能教学辅助系统了！**

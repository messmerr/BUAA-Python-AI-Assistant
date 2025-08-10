# BUAA-Python-AI-Assistant

## 项目简介
AI 助教系统（北航 Python 课程大作业）。包含：
- 账号与认证（JWT）
- 作业管理与 AI 批改（文本/图片答案支持 OCR 再批改）
- 智能答疑（多轮会话 + 历史）
- 学习报告与班级报告（基于 AI 生成）
- 教师⇄学生站内私信聊天

后端 Django 通过 Google Generative AI（Gemini）提供批改/答疑/报告能力。

## 技术栈
- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router
- 后端：Django 5 + DRF + SimpleJWT + SQLite

## 环境要求（Windows）
- Windows 10/11（64 位）
- Python 3.10 ~ 3.12（建议 3.11）
- Node.js 18+（含 npm）

## 后端配置与启动（Django）
### 1) 克隆与进入目录
```powershell
git clone <your-repo-url>
cd BUAA-Python-AI-Assistant
```

### 2) API Key 与科学上网配置（必需）
- 在 `backend/` 目录将.env.example重命名为.env，其中已内置一个有效期至8.16的Google AI Studio API Key，如果逾期，需要自行申请 Google AI Studio API Key，并在后端配置中设置 `GOOGLE_AI_API_KEY`：
  ```ini
  # backend/.env
  GOOGLE_AI_API_KEY=你的GoogleAPIKey
  ```
- 确保后端进程能访问 Google。若使用本地代理工具（如 Clash / Surge / V2Ray 等），可能需要为当前会话设置代理环境变量:
  ```powershell
  # 仅当前 PowerShell 会话生效
  $env:HTTP_PROXY = "http://127.0.0.1:7890"
  $env:HTTPS_PROXY = "http://127.0.0.1:7890"
  ```
  也可开启代理工具的TUN模式。请确保后端运行时能够访问 `generativelanguage.googleapis.com`。

### 3) 创建虚拟环境并安装依赖
```powershell
cd backend
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

### 4) 初始化数据库并启动
```powershell
python manage.py migrate
python manage.py runserver   # http://127.0.0.1:8000
```

启动成功后：
- API Base：`http://127.0.0.1:8000/api/v1/`

可选：创建管理员账户
```powershell
python manage.py createsuperuser
```

## 前端配置与启动（Vue）
### 安装依赖并启动
```powershell
cd frontend
npm install
npm run dev   # http://localhost:5173
```

如需代理前端到本地后端，默认已允许 `http://127.0.0.1:5173` 跨域访问。

## 目录结构
```
BUAA-Python-AI-Assistant/
├─ backend/                     # Django 后端
│  ├─ ai_tutor_system/          # 项目配置
│  ├─ accounts/ assignments/ qa/ reports/ chat/  # 业务应用
│  ├─ requirements.txt          # Python 依赖
│  └─ manage.py
├─ frontend/                    # Vue 前端
│  ├─ src/                      # 源码
│  ├─ package.json
│  └─ vite.config.ts
├─ docs/                        # API 文档
   └─ api/ (api_quick_reference.md, api_specification.md)
```

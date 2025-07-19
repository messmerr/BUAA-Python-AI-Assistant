# BUAA-Python-AI-Assistant

## 项目简介
AI助教系统 - 北航Python暑期课大作业

## 技术栈
**前端**: Vue 3 + TypeScript + Vue Router + Pinia + Vite
**后端**: Django + Django REST Framework + SQLite

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm

### 配置步骤

**1. 克隆项目**
```bash
git clone <repository-url>
cd BUAA-Python-AI-Assistant
```

**2. 后端配置（当前是Django默认项目）**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver     # 启动后端 http://127.0.0.1:8000
```

**3. 前端配置（同上）**
```bash
cd frontend
npm install
npm run dev                    # 启动前端 http://localhost:5173
```

## 项目结构
```
BUAA-Python-AI-Assistant/
├── backend/                 # Django后端
│   ├── ai_tutor_system/    # 主项目配置
│   ├── requirements.txt    # Python依赖
│   └── manage.py          # Django管理脚本
├── frontend/               # Vue前端
│   ├── src/               # 源代码
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # Vite配置
└── docs/                  # 文档
```
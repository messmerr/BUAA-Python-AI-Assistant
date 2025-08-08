# 这是一个 PowerShell 脚本，用于一键更新并启动后端服务

# 打印彩色的标题，看起来更清晰
Write-Host "========================================" -ForegroundColor Green
Write-Host "🚀 开始更新并启动【后端】服务..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 1. 拉取最新的代码
Write-Host "`n[步骤 1/5] 正在从 Git 仓库拉取最新代码..." -ForegroundColor Cyan
git pull

# 2. 进入后端目录
cd backend

# 3. 激活 Python 虚拟环境
Write-Host "`n[步骤 2/5] 正在激活 Python 虚拟环境..." -ForegroundColor Cyan
.\venv\Scripts\activate

# 4. 安装/更新后端依赖
Write-Host "`n[步骤 3/5] 正在检查并更新后端依赖 (pip install)..." -ForegroundColor Cyan
pip install -r requirements.txt

# 5. 执行数据库迁移
Write-Host "`n[步骤 4/5] 正在检查并更新数据库 (migrate)..." -ForegroundColor Cyan
python manage.py migrate

# 6. 启动后端开发服务器
Write-Host "`n[步骤 5/5] 一切就绪！正在启动 Django 开发服务器..." -ForegroundColor Green
Write-Host "请保持此窗口开启。要停止服务请按 Ctrl+C。" -ForegroundColor Yellow
python manage.py runserver
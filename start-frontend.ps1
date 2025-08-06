# 这是一个 PowerShell 脚本，用于一键更新并启动前端服务

# 打印彩色的标题
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "🚀 开始更新并启动【前端】服务..." -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# 1. 进入前端目录
cd frontend

# 2. 安装/更新前端依赖
Write-Host "`n[步骤 1/2] 正在检查并更新前端依赖 (npm install)..." -ForegroundColor Cyan
npm install

# 3. 启动前端开发服务器
Write-Host "`n[步骤 2/2] 一切就绪！正在启动 Vite 开发服务器..." -ForegroundColor Magenta
Write-Host "请保持此窗口开启。要停止服务请按 Ctrl+C。" -ForegroundColor Yellow
npm run dev
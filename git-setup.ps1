# Chat Web - Git 初始化脚本
# 使用方法: 右键点击 -> 使用 PowerShell 运行

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Chat Web - Git 初始化脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
try {
    $gitVersion = git --version
    Write-Host "[1/7] Git 版本: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] Git 未安装或不在 PATH 中" -ForegroundColor Red
    Write-Host "请安装 Git: https://git-scm.com/download/win"
    Read-Host "按 Enter 键退出"
    exit 1
}
Write-Host ""

# 配置用户信息
Write-Host "[2/7] 配置 Git 用户信息..." -ForegroundColor Yellow
git config --global user.name "ChatWeb Developer"
git config --global user.email "787598909@qq.com"
Write-Host "完成" -ForegroundColor Green
Write-Host ""

# 初始化仓库
Write-Host "[3/7] 初始化 Git 仓库..." -ForegroundColor Yellow
if (Test-Path .git) {
    Write-Host "仓库已存在，跳过初始化" -ForegroundColor Green
} else {
    git init
    Write-Host "仓库初始化完成" -ForegroundColor Green
}
Write-Host ""

# 添加远程仓库
Write-Host "[4/7] 配置远程仓库..." -ForegroundColor Yellow
Write-Host "请在 GitHub 上创建新仓库，然后输入仓库地址" -ForegroundColor Cyan
Write-Host "格式: https://github.com/你的用户名/chatweb.git" -ForegroundColor Cyan
Write-Host ""
$remoteUrl = Read-Host "请输入仓库地址"

git remote remove origin 2>$null
git remote add origin $remoteUrl
Write-Host "远程仓库已配置" -ForegroundColor Green
git remote -v
Write-Host ""

# 添加文件
Write-Host "[5/7] 添加文件到暂存区..." -ForegroundColor Yellow
git add .
Write-Host "文件已添加" -ForegroundColor Green
Write-Host ""

# 提交
Write-Host "[6/7] 提交更改..." -ForegroundColor Yellow
git commit -m "Initial commit: Add chat web application with Vue 3 + TypeScript"
Write-Host "完成" -ForegroundColor Green
Write-Host ""

# 推送
Write-Host "[7/7] 推送到 GitHub..." -ForegroundColor Yellow
Write-Host "提示: 当要求输入密码时，请使用 Personal Access Token (PAT)" -ForegroundColor Cyan
Write-Host "而不是你的 GitHub 密码" -ForegroundColor Cyan
Write-Host ""

try {
    git push -u origin main
    Write-Host "推送成功!" -ForegroundColor Green
} catch {
    Write-Host "尝试使用 master 分支..." -ForegroundColor Yellow
    git branch -m master
    git push -u origin master
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Read-Host "按 Enter 键退出"

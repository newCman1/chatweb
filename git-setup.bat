@echo off
chcp 65001
cls
echo ==========================================
echo    Chat Web - Git 初始化脚本
echo ==========================================
echo.

REM 检查 Git 是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Git 未安装或不在 PATH 中
    echo 请安装 Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/7] Git 版本:
git --version
echo.

REM 配置用户信息
echo [2/7] 配置 Git 用户信息...
git config --global user.name "ChatWeb Developer"
git config --global user.email "787598909@qq.com"
echo 完成
echo.

REM 初始化仓库
echo [3/7] 初始化 Git 仓库...
if exist .git (
    echo 仓库已存在，跳过初始化
) else (
    git init
    echo 仓库初始化完成
)
echo.

REM 添加远程仓库
echo [4/7] 配置远程仓库...
echo 请在 GitHub 上创建新仓库，然后输入仓库地址
echo 格式: https://github.com/你的用户名/chatweb.git
echo.
set /p remote_url="请输入仓库地址: "

git remote remove origin 2>nul
git remote add origin %remote_url%
echo 远程仓库已配置
git remote -v
echo.

REM 添加文件
echo [5/7] 添加文件到暂存区...
git add .
echo 文件已添加
echo.

REM 提交
echo [6/7] 提交更改...
git commit -m "Initial commit: Add chat web application with Vue 3 + TypeScript"
echo 完成
echo.

REM 推送
echo [7/7] 推送到 GitHub...
echo 提示: 当要求输入密码时，请使用 Personal Access Token (PAT)
echo 而不是你的 GitHub 密码
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo 尝试使用 master 分支...
    git branch -m master
    git push -u origin master
)

echo.
echo ==========================================
echo    完成！
echo ==========================================
pause

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    武汉理工社团管理系统
echo ========================================
echo.

REM 进入脚本目录
cd /d %~dp0

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [信息] 检测到 Python 环境
python --version

REM 创建虚拟环境（如不存在）
if not exist .venv (
	echo.
	echo [设置] 首次运行，正在创建虚拟环境...
	python -m venv .venv
	if errorlevel 1 (
		echo [错误] 创建虚拟环境失败
		pause
		exit /b 1
	)
	echo [成功] 虚拟环境创建完成
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat
if errorlevel 1 (
	echo [警告] 虚拟环境激活失败，使用系统 Python
)

echo.
echo [环境] 虚拟环境已激活

REM 安装依赖
if exist requirements.txt (
	echo.
	echo [依赖] 正在检查并安装依赖包...
	pip install -r requirements.txt --quiet --disable-pip-version-check
	if errorlevel 1 (
		echo [警告] 部分依赖安装可能失败，但将尝试继续运行
	) else (
		echo [成功] 依赖包安装完成
	)
)

echo.
REM 检查管理员账号（可选）
if exist create_admin.py (
	echo.
	choice /C YN /M "[询问] 是否创建或更新管理员账号？(Y/N)"
	if errorlevel 2 (
		echo [信息] 跳过管理员账号创建。
	) else (
		set /p ADMIN_USER="[输入] 管理员用户名: "
		if "%ADMIN_USER%"=="" (
			echo [警告] 用户名为空，跳过管理员创建。
		) else (
			echo 输入密码时不会回显，请注意。
			python create_admin.py -u "%ADMIN_USER%"
		)
	)
)

echo.
echo ========================================
echo [启动] 正在启动系统...
echo ========================================
echo.
echo 请在浏览器中访问: http://127.0.0.1:5000
echo 或者访问: http://localhost:5000
echo.
echo 按 Ctrl+C 可以停止服务器
echo ========================================
echo.

python app.py

echo.
echo ========================================
echo [信息] 服务器已停止
echo ========================================
pause






Param(
	[switch]$NoInstall
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# 临时放开当前会话脚本执行限制
try {
	Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null
} catch {}

# 创建虚拟环境（如不存在）
if (-not (Test-Path ".venv")) {
	Write-Host "[setup] 创建虚拟环境 .venv" -ForegroundColor Cyan
	python -m venv .venv
}

# 激活虚拟环境
. .\.venv\Scripts\Activate.ps1
Write-Host "[env] 已激活虚拟环境" -ForegroundColor Green

# 安装依赖（可用 -NoInstall 跳过）
if (-not $NoInstall) {
	if (Test-Path "requirements.txt") {
		Write-Host "[deps] 安装依赖中..." -ForegroundColor Cyan
		pip install -r requirements.txt
	}
}

# 启动应用
Write-Host "[run] 启动 Flask 应用..." -ForegroundColor Yellow
python app.py





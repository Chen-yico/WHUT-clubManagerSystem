#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键部署脚本

功能：
1. 检查 Python 版本
2. 创建或复用虚拟环境 (.venv)
3. 安装 requirements.txt 中的依赖
4. 可选：创建/更新管理员账号
5. 启动 Flask 应用（默认）

使用示例：
    python oneclick_deploy.py --admin-user admin --admin-password 123456
    python oneclick_deploy.py --no-run
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"


class DeployError(RuntimeError):
    pass


def check_python_version() -> None:
    major, minor = sys.version_info.major, sys.version_info.minor
    if (major, minor) < (3, 8):
        raise DeployError("需要 Python 3.8 及以上版本，请升级后重试。")


def run_command(cmd: list[str], env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print(f"[执行] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=PROJECT_ROOT, env=env or os.environ.copy(), check=check)


def ensure_venv() -> Path:
    if VENV_DIR.exists():
        print("[信息] 检测到已有虚拟环境，将直接复用。")
    else:
        print("[设置] 正在创建虚拟环境 (.venv)...")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
        print("[成功] 虚拟环境创建完成。")

    if platform.system().lower().startswith("win"):
        python_path = VENV_DIR / "Scripts" / "python.exe"
    else:
        python_path = VENV_DIR / "bin" / "python"

    if not python_path.exists():
        raise DeployError("未找到虚拟环境中的 python 可执行文件，请检查虚拟环境是否创建成功。")

    return python_path


def install_dependencies(python_executable: Path) -> None:
    req_file = PROJECT_ROOT / "requirements.txt"
    if not req_file.exists():
        print("[警告] 未找到 requirements.txt，将跳过依赖安装。")
        return

    print("[依赖] 正在安装/更新依赖包...")
    run_command([str(python_executable), "-m", "pip", "install", "--upgrade", "pip"])
    try:
        run_command([str(python_executable), "-m", "pip", "install", "-r", str(req_file)])
    except subprocess.CalledProcessError as exc:
        raise DeployError(f"依赖安装失败，请检查网络或 requirements.txt：{exc}") from exc
    print("[成功] 依赖安装完成。")


def create_admin_account(python_executable: Path, username: str, password: str) -> None:
    script = PROJECT_ROOT / "create_admin.py"
    if not script.exists():
        raise DeployError("未找到 create_admin.py，无法创建管理员。")
    print(f"[管理员] 正在创建/更新管理员账号：{username}")
    run_command([str(python_executable), str(script), "-u", username, "-p", password])


def start_application(python_executable: Path) -> None:
    print("[启动] 即将启动 Flask 应用，按 Ctrl+C 可退出。")
    run_command([str(python_executable), str(PROJECT_ROOT / "app.py")], check=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="武汉理工社团管理系统一键部署脚本")
    parser.add_argument("--admin-user", help="部署时自动创建/更新的管理员用户名")
    parser.add_argument("--admin-password", help="部署时自动创建/更新的管理员密码（注意保密）")
    parser.add_argument("--no-run", action="store_true", help="仅完成部署，不自动启动服务")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        check_python_version()
        python_in_venv = ensure_venv()
        install_dependencies(python_in_venv)

        if args.admin_user and args.admin_password:
            create_admin_account(python_in_venv, args.admin_user, args.admin_password)
        elif args.admin_user or args.admin_password:
            print("[警告] 需同时提供 --admin-user 与 --admin-password，已跳过管理员创建。")

        if args.no_run:
            print("[完成] 部署流程已结束，可手动执行 start.bat 或 python app.py 启动应用。")
        else:
            start_application(python_in_venv)
    except DeployError as exc:
        print(f"[错误] {exc}")
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        print(f"[错误] 命令执行失败，退出码 {exc.returncode}")
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()


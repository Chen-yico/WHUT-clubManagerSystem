#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速创建管理员账号的脚本。
支持命令行参数输入或交互式输入用户名与密码。
"""

import argparse
import getpass
import sqlite3
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

# 为了复用应用内的数据库初始化逻辑，将项目根目录加入 sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app import init_db, DATABASE_PATH  # type: ignore
except Exception as exc:  # pragma: no cover - 脚本运行时才可能触发
    print(f"[错误] 导入 app 模块失败: {exc}")
    print("[提示] 请确认脚本与 app.py 位于同一目录，或手动调整 sys.path。")
    sys.exit(1)


def ensure_database(db_path: Path) -> None:
    """确保数据库和必要的表已经创建。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    init_db(str(db_path))


def create_admin_user(db_path: Path, username: str, password: str) -> None:
    """在指定数据库中创建管理员用户。"""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        existing = cur.execute("SELECT id, is_admin FROM users WHERE username = ?", (username,)).fetchone()
        password_hash = generate_password_hash(password)

        if existing:
            if existing["is_admin"]:
                cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, existing["id"]))
                print(f"[信息] 用户 '{username}' 已是管理员，已更新密码。")
            else:
                cur.execute("UPDATE users SET password_hash = ?, is_admin = 1 WHERE id = ?", (password_hash, existing["id"]))
                print(f"[成功] 用户 '{username}' 已升级为管理员并更新密码。")
        else:
            cur.execute(
                "INSERT INTO users(username, password_hash, is_admin) VALUES(?, ?, 1)",
                (username, password_hash),
            )
            print(f"[成功] 新建管理员用户 '{username}'。")

        conn.commit()
    finally:
        conn.close()
    print("[提示] 请使用该账号登录后台，即可进行社团审核等管理员操作。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="创建或更新管理员账号")
    parser.add_argument("-u", "--username", help="管理员用户名")
    parser.add_argument("-p", "--password", help="管理员密码（建议仅在安全环境使用）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    username = args.username or input("请输入管理员用户名: ").strip()
    while not username:
        username = input("用户名不能为空，请重新输入: ").strip()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("请输入管理员密码: ").strip()
        while not password:
            password = getpass.getpass("密码不能为空，请重新输入: ").strip()

    db_path = (BASE_DIR / DATABASE_PATH).resolve()
    ensure_database(db_path)
    create_admin_user(db_path, username, password)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[信息] 已取消操作。")


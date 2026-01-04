#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员权限设置工具
用于将指定用户设置为管理员
"""

import sqlite3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "clubmgr.db"


def set_admin(username):
    """将指定用户设置为管理员"""
    db_path = DB_PATH

    # 检查数据库文件是否存在
    if not db_path.exists():
        print(f"[错误] 数据库文件不存在: {db_path}")
        print("[提示] 请先运行系统，系统会自动创建数据库")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute("SELECT id, username, is_admin FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"[错误] 用户 '{username}' 不存在")
            print("[提示] 请先注册该账号")
            
            # 显示所有已注册用户
            cursor.execute("SELECT username FROM users")
            users = cursor.fetchall()
            if users:
                print("\n[信息] 已注册的用户：")
                for u in users:
                    print(f"  - {u[0]}")
            
            conn.close()
            return False
        
        user_id, username, is_admin = user
        
        if is_admin == 1:
            print(f"[信息] 用户 '{username}' 已经是管理员")
            conn.close()
            return True
        
        # 设置为管理员
        cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
        conn.commit()
        
        print(f"[成功] 已将用户 '{username}' 设置为管理员")
        print("[提示] 请重新登录以使权限生效")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"[错误] 数据库操作失败: {e}")
        return False
    except Exception as e:
        print(f"[错误] 发生未知错误: {e}")
        return False


def list_users():
    """列出所有用户"""
    db_path = DB_PATH

    if not db_path.exists():
        print(f"[错误] 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin FROM users ORDER BY id")
        users = cursor.fetchall()
        
        if not users:
            print("[信息] 暂无注册用户")
        else:
            print("\n" + "="*50)
            print("用户列表".center(50))
            print("="*50)
            print(f"{'ID':<8} {'用户名':<20} {'角色':<10}")
            print("-"*50)
            for user_id, username, is_admin in users:
                role = "管理员" if is_admin == 1 else "普通用户"
                print(f"{user_id:<8} {username:<20} {role:<10}")
            print("="*50)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"[错误] 数据库操作失败: {e}")


def main():
    """主函数"""
    print("="*50)
    print("武汉理工社团管理系统 - 管理员设置工具".center(50))
    print("="*50)
    print()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "list" or sys.argv[1] == "-l":
            list_users()
            return
        else:
            username = sys.argv[1]
            set_admin(username)
            return
    
    # 交互式模式
    print("请选择操作：")
    print("1. 设置管理员")
    print("2. 查看所有用户")
    print("3. 退出")
    print()
    
    choice = input("请输入选项 (1-3): ").strip()
    
    if choice == "1":
        print()
        list_users()
        print()
        username = input("请输入要设置为管理员的用户名: ").strip()
        if username:
            set_admin(username)
        else:
            print("[错误] 用户名不能为空")
    
    elif choice == "2":
        list_users()
    
    elif choice == "3":
        print("[信息] 退出程序")
    
    else:
        print("[错误] 无效的选项")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[信息] 用户中断操作")
    except Exception as e:
        print(f"\n[错误] 程序异常: {e}")
    
    # Windows 下暂停
    if sys.platform == "win32":
        print()
        input("按回车键退出...")





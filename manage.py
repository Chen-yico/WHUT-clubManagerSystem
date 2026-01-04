import sqlite3
from pathlib import Path
import click
from werkzeug.security import generate_password_hash

DB_PATH = Path("instance") / "clubmgr.db"


def ensure_db():
	DB_PATH.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(DB_PATH)
	conn.executescript(
		"""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password_hash TEXT NOT NULL,
			is_admin INTEGER NOT NULL DEFAULT 0
		);
		"""
	)
	conn.commit()
	conn.close()


@click.group()
def cli():
	"""管理工具：创建/提升管理员用户等。"""


@cli.command("promote-admin")
@click.option("--username", required=True, help="用户名")
@click.option("--password", required=False, help="如果用户不存在，将用该密码创建")
def promote_admin(username: str, password: str | None):
	"""将用户设为管理员；若不存在且给了密码则创建。"""
	ensure_db()
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	user = cur.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
	if not user:
		if not password:
			click.echo("[错误] 用户不存在，请提供 --password 以创建该用户。")
			return
		cur.execute(
			"INSERT INTO users(username, password_hash, is_admin) VALUES(?, ?, 1)",
			(username, generate_password_hash(password)),
		)
		conn.commit()
		click.echo(f"[完成] 已创建管理员用户：{username}")
		return
	cur.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
	conn.commit()
	click.echo(f"[完成] 已将用户设为管理员：{username}")


if __name__ == "__main__":
	cli()











import sqlite3
from contextlib import closing
import discord


class SQLManager(object):
    def __init__(self, db: str):
        self.dbname = db

    def create_user(self, username: str, user_id: int) -> tuple or bool:
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            sql = 'insert into users (id, name, user_id) values (?,?,?)'
            u = (self.get_last_id("users") + 1, username, user_id)
            c.execute(sql, u)
            conn.commit()
        return self.get_user(user_id)

    def get_user(self, user_id: int) -> tuple or bool:
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            sql = 'select * from users WHERE user_id = ?'
            users = list(c.execute(sql, (user_id,)))
            if not users:
                return self.create_user("{N>", user_id)
            return users[0]

    def get_all_user(self):
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            select_sql = 'select * from users'
            for row in c.execute(select_sql):
                print(row)

    def get_point(self, user_id: int) -> int:
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            sql = 'select * from point WHERE user_id = ?'
            users = list(c.execute(sql, (user_id,)))
            if not users:
                return self.create_point(user_id)
            return users[0][2]

    def create_point(self, user_id: int) -> int:
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            sql = 'insert into point (id, user_id, point) values (?,?,?)'
            u = (self.get_last_id("point"), user_id, 0)
            c.execute(sql, u)
            conn.commit()
        return self.get_point(user_id)

    def add_point(self, user_id: int, point: int) -> int:
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            sql = 'update point set point = point + ? where user_id = ?'
            u = (point, user_id)
            c.execute(sql, u)
            conn.commit()
        return self.get_point(user_id)

    def get_last_id(self, table: str) -> int:
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            select_sql = 'select * from %s'
            users = list(c.execute(select_sql % table))
            if not users:
                return -1
            return users[-1][0]

    def tables(self):
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            c.execute("select * from sqlite_master where type='table'")
            return list(c.fetchall())

    def _sql(self, sql):
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()
            print(c.execute(sql))
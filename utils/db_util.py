import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor

MY_SQL_PARAMS = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'homework',
    'charset': 'utf8',
    'cursorclass': pymysql.cursors.DictCursor
}

POOL = PooledDB(
    creator=pymysql,
    maxconnections=5,
    mincached=1,
    maxcached=5,
    blocking=True,
    setsession=[],
    ping=0,
    maxusage=None,
    **MY_SQL_PARAMS
)

class DBUtil:
    def __init__(self):
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.db.close()

    def fetch_one(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def fetch_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def update(self, sql, params=None):
        try:
            self.cursor.execute(sql, params)
            self.db.commit()
        except:
            self.db.rollback()
            raise

    def insert(self, sql, params=None):
        try:
            self.cursor.execute(sql, params)
            self.db.commit()
        except:
            self.db.rollback()
            raise

    def delete(self, sql, params=None):
        try:
            self.cursor.execute(sql, params)
            self.db.commit()
        except:
            self.db.rollback()
            raise

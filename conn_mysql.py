import pymysql
from contextlib import contextmanager

@contextmanager
def get_db_cursor():
    """上下文管理器，自动处理连接的打开和关闭"""
    conn = pymysql.connect(
        host='10.10.217.173',
        user='admin',
        password='123456',
        database='scs_cpp',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()  # 自动提交事务
    except Exception as e:
        conn.rollback()  # 发生异常时回滚
        raise e
    finally:
        cursor.close()
        conn.close()
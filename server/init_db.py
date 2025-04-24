import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.path.join("..", "database", "finance.db")

def init_db():
    """初始化数据库"""
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 读取并执行 schema.sql 文件
        with open("schema.sql", "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        
        # 提交更改
        conn.commit()
        print("数据库初始化成功!")
    except Exception as e:
        print(f"初始化数据库时发生错误: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db() 
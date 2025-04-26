import sqlite3
import os

def init_db():
    # 确保database目录存在
    os.makedirs('database', exist_ok=True)
    
    # 连接到数据库（如果不存在会自动创建）
    db_path = os.path.join('database', 'app.db')
    conn = sqlite3.connect(db_path)
    
    try:
        # 读取SQL文件
        with open(os.path.join('server', 'database', 'migrations', 'create_monitoring_tables.sql'), 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行SQL脚本
        conn.executescript(sql_script)
        
        # 提交更改
        conn.commit()
        print("数据库表创建成功！")
        
    except Exception as e:
        print(f"创建数据库表时出错: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db() 
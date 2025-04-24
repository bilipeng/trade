import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'finance.db')

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建财务交易表
cursor.execute('''
CREATE TABLE IF NOT EXISTS financial_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_event_id INTEGER NOT NULL,
    account_code TEXT NOT NULL, 
    account_name TEXT NOT NULL, 
    amount REAL NOT NULL,
    direction TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_event_id) REFERENCES business_events (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
)
''')

# 创建视图
try:
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS business_financial_records AS
    SELECT 
        ft.id,
        ft.business_event_id,
        ft.account_code,
        ft.account_name,
        ft.amount,
        ft.direction,
        ft.transaction_date,
        ft.fiscal_year,
        ft.fiscal_period,
        ft.description,
        ft.created_by,
        u.username AS created_by_name,
        be.project_name,
        be.event_type,
        ft.created_at
    FROM 
        financial_transactions ft
    JOIN 
        business_events be ON ft.business_event_id = be.id
    JOIN 
        users u ON ft.created_by = u.id
    ''')
except Exception as e:
    print(f"创建视图时出错: {str(e)}")

# 提交更改
conn.commit()
print("数据库更新完成!")

# 关闭连接
conn.close() 
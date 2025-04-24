-- 创建新的财务交易表
CREATE TABLE IF NOT EXISTS financial_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_event_id INTEGER NOT NULL,         -- 关联的业务事件ID
    account_code TEXT NOT NULL,                 -- 会计科目编码
    account_name TEXT NOT NULL,                 -- 会计科目名称
    amount REAL NOT NULL,                       -- 金额
    direction TEXT NOT NULL,                    -- 方向：收入/支出
    transaction_date TEXT NOT NULL,             -- 交易日期
    fiscal_year INTEGER NOT NULL,               -- 财年
    fiscal_period INTEGER NOT NULL,             -- 会计期间
    description TEXT,                           -- 描述
    created_by INTEGER NOT NULL,                -- 创建人ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_event_id) REFERENCES business_events (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- 修改业务事件表的状态选项
-- 注意：SQLite不支持直接修改CHECK约束，需要添加新的可能值
-- 状态：待审批/已审批/执行中/已完成/已拒绝

-- 添加新的API视图
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
    users u ON ft.created_by = u.id; 
-- 客户表
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                         -- 客户名称
    code TEXT UNIQUE,                           -- 客户编码
    contact_person TEXT,                        -- 联系人
    contact_phone TEXT,                         -- 联系电话
    contact_email TEXT,                         -- 联系邮箱
    address TEXT,                               -- 地址
    email TEXT,                                 -- 客户邮箱
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 
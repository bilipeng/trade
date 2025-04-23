-- 数据库架构文件
-- 业财融合管理系统数据库
-- 简洁版本，包含基本功能支持

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,              -- 用户名
    password TEXT NOT NULL,                     -- 密码
    role TEXT NOT NULL,                         -- 角色：管理员/财务/业务/审批
    department TEXT NOT NULL,                   -- 所属部门
    email TEXT,                                 -- 电子邮件
    phone TEXT,                                 -- 联系电话
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 部门表
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                  -- 部门名称
    code TEXT NOT NULL UNIQUE,                  -- 部门编码
    parent_id INTEGER,                          -- 上级部门ID
    manager_id INTEGER,                         -- 部门负责人ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES departments (id),
    FOREIGN KEY (manager_id) REFERENCES users (id)
);

-- 业务事件表
CREATE TABLE IF NOT EXISTS business_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,                   -- 事件类型：合同/销售/采购/报销
    project_name TEXT NOT NULL,                 -- 项目名称
    project_code TEXT,                          -- 项目编号
    customer_id INTEGER,                        -- 客户ID
    amount REAL NOT NULL,                       -- 金额
    event_date DATE NOT NULL,                   -- 事件日期
    description TEXT,                           -- 描述
    department_id INTEGER NOT NULL,             -- 所属部门
    created_by INTEGER NOT NULL,                -- 创建人
    status TEXT NOT NULL DEFAULT '待审批',      -- 状态：待审批/已审批/已拒绝/已完成
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id),
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- 客户信息表
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

-- 财务记录表
CREATE TABLE IF NOT EXISTS financial_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_event_id INTEGER NOT NULL,         -- 关联业务事件ID
    account_code TEXT NOT NULL,                 -- 会计科目编码
    account_name TEXT NOT NULL,                 -- 会计科目名称
    amount REAL NOT NULL,                       -- 金额
    direction TEXT NOT NULL CHECK (direction IN ('收入', '支出')), -- 收入/支出
    record_date DATE NOT NULL,                  -- 记账日期
    fiscal_year INTEGER NOT NULL,               -- 财年
    fiscal_period INTEGER NOT NULL,             -- 会计期间（月份）
    description TEXT,                           -- 描述
    created_by INTEGER NOT NULL,                -- 创建人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_event_id) REFERENCES business_events (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- 会计科目表
CREATE TABLE IF NOT EXISTS account_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,                  -- 科目编码
    name TEXT NOT NULL,                         -- 科目名称
    parent_code TEXT,                           -- 父级科目编码
    direction TEXT NOT NULL CHECK (direction IN ('借', '贷')), -- 余额方向
    is_active BOOLEAN DEFAULT 1,                -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_code) REFERENCES account_subjects (code)
);

-- 预算表
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,             -- 部门ID
    year INTEGER NOT NULL,                      -- 年度
    month INTEGER NOT NULL,                     -- 月份
    account_subject_id INTEGER,                 -- 科目ID
    amount REAL NOT NULL,                       -- 预算金额
    used_amount REAL NOT NULL DEFAULT 0,        -- 已用金额
    created_by INTEGER,                         -- 创建人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (account_subject_id) REFERENCES account_subjects (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- 审批流程表
CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_event_id INTEGER NOT NULL,         -- 业务事件ID
    approver_id INTEGER NOT NULL,               -- 审批人ID
    approval_level INTEGER NOT NULL DEFAULT 1,  -- 审批级别
    status TEXT NOT NULL DEFAULT '待审批',      -- 状态：待审批/已通过/已拒绝
    comment TEXT,                               -- 审批意见
    approval_date TIMESTAMP,                    -- 审批时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_event_id) REFERENCES business_events (id),
    FOREIGN KEY (approver_id) REFERENCES users (id)
);

-- 审批流程配置表
CREATE TABLE IF NOT EXISTS approval_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,                   -- 事件类型
    department_id INTEGER NOT NULL,             -- 部门ID
    approver_id INTEGER NOT NULL,               -- 审批人ID
    approval_level INTEGER NOT NULL,            -- 审批级别
    amount_threshold REAL,                      -- 金额阈值（超过此金额需要该级审批）
    is_active BOOLEAN DEFAULT 1,                -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (approver_id) REFERENCES users (id)
);

-- 附件表
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_event_id INTEGER NOT NULL,         -- 业务事件ID
    file_name TEXT NOT NULL,                    -- 文件名
    file_path TEXT NOT NULL,                    -- 文件路径
    file_type TEXT NOT NULL,                    -- 文件类型
    file_size INTEGER NOT NULL,                 -- 文件大小（字节）
    uploaded_by INTEGER NOT NULL,               -- 上传人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_event_id) REFERENCES business_events (id),
    FOREIGN KEY (uploaded_by) REFERENCES users (id)
);

-- 系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                            -- 操作用户ID
    action TEXT NOT NULL,                       -- 操作类型
    target_type TEXT NOT NULL,                  -- 操作对象类型
    target_id INTEGER,                          -- 操作对象ID
    details TEXT,                               -- 详细信息
    ip_address TEXT,                            -- IP地址
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 报表配置表
CREATE TABLE IF NOT EXISTS report_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_name TEXT NOT NULL,                  -- 报表名称
    report_type TEXT NOT NULL,                  -- 报表类型：财务/业务/预算
    sql_query TEXT NOT NULL,                    -- SQL查询语句
    description TEXT,                           -- 描述
    created_by INTEGER NOT NULL,                -- 创建人
    is_active BOOLEAN DEFAULT 1,                -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- 初始化数据

-- 添加系统管理员账户
INSERT OR IGNORE INTO users (username, password, role, department, email)
VALUES ('admin', 'admin', '管理员', '系统管理', 'admin@example.com');

-- 添加普通用户账户
INSERT OR IGNORE INTO users (username, password, role, department, email)
VALUES ('zhangsan', 'password123', '财务人员', '财务部', 'zhangsan@example.com');

INSERT OR IGNORE INTO users (username, password, role, department, email)
VALUES ('lisi', 'password123', '业务人员', '业务部', 'lisi@example.com');

INSERT OR IGNORE INTO users (username, password, role, department, email)
VALUES ('wangwu', 'password123', '技术人员', '技术部', 'wangwu@example.com');

-- 添加示例部门
INSERT OR IGNORE INTO departments (name, code)
VALUES ('系统管理', 'SYS001');

INSERT OR IGNORE INTO departments (name, code)
VALUES ('财务部', 'FIN001');

INSERT OR IGNORE INTO departments (name, code)
VALUES ('业务部', 'BUS001');

INSERT OR IGNORE INTO departments (name, code)
VALUES ('技术部', 'TEC001');

-- 添加示例客户
INSERT OR IGNORE INTO customers (name, code, contact_person, contact_phone, address, email)
VALUES ('北京科技有限公司', 'CUST001', '张经理', '13800138001', '北京市海淀区中关村', 'contact@bjtech.com');

INSERT OR IGNORE INTO customers (name, code, contact_person, contact_phone, address, email)
VALUES ('上海贸易有限公司', 'CUST002', '李总监', '13900139002', '上海市浦东新区张江', 'info@shtrading.com');

INSERT OR IGNORE INTO customers (name, code, contact_person, contact_phone, address, email)
VALUES ('广州电子科技公司', 'CUST003', '王董事', '13700137003', '广州市天河区珠江新城', 'service@gzelec.com');

-- 添加示例预算
INSERT OR IGNORE INTO budgets (department_id, year, month, account_subject_id, amount, used_amount, created_by)
VALUES (2, 2023, 4, 1, 100000.00, 25000.00, 1);

INSERT OR IGNORE INTO budgets (department_id, year, month, account_subject_id, amount, used_amount, created_by)
VALUES (3, 2023, 4, 1, 200000.00, 75000.00, 1);

INSERT OR IGNORE INTO budgets (department_id, year, month, account_subject_id, amount, used_amount, created_by)
VALUES (4, 2023, 4, 1, 150000.00, 50000.00, 1);

-- 添加示例会计科目
INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('1001', '库存现金', '借');

INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('1002', '银行存款', '借');

INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('2001', '应付账款', '贷');

INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('2002', '预收账款', '贷');

INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('4001', '主营业务收入', '贷');

INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('5001', '主营业务成本', '借');

INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('6001', '管理费用', '借');

INSERT OR IGNORE INTO account_subjects (code, name, direction)
VALUES ('6602', '销售费用', '借'); 
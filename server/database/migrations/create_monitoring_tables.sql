-- 创建项目表
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                         -- 项目名称
    code TEXT UNIQUE,                           -- 项目编码
    customer_id INTEGER,                        -- 客户ID
    manager_id INTEGER,                         -- 项目经理ID
    start_date DATE NOT NULL,                   -- 开始日期
    end_date DATE,                              -- 计划结束日期
    actual_end_date DATE,                       -- 实际结束日期
    budget REAL NOT NULL,                       -- 项目预算
    status TEXT NOT NULL,                       -- 状态：规划中/进行中/已完成/已暂停
    progress REAL DEFAULT 0,                    -- 进度百分比(0-100)
    description TEXT,                           -- 描述
    created_by INTEGER NOT NULL,                -- 创建人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建项目里程碑表
CREATE TABLE IF NOT EXISTS project_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                -- 项目ID
    name TEXT NOT NULL,                         -- 里程碑名称
    description TEXT,                           -- 描述
    planned_date DATE NOT NULL,                 -- 计划日期
    actual_date DATE,                           -- 实际日期
    status TEXT NOT NULL,                       -- 状态：未开始/进行中/已完成/已延期
    weight REAL DEFAULT 0,                      -- 权重(0-100)
    created_by INTEGER NOT NULL,                -- 创建人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- 创建预警规则表
CREATE TABLE IF NOT EXISTS alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                         -- 规则名称
    description TEXT,                           -- 描述
    indicator TEXT NOT NULL,                    -- 指标：预算超支/毛利率/回款逾期等
    condition TEXT NOT NULL,                    -- 条件：大于/小于/等于
    threshold REAL NOT NULL,                    -- 阈值
    severity TEXT NOT NULL,                     -- 严重程度：低/中/高
    is_active BOOLEAN DEFAULT 1,                -- 是否启用
    notify_roles TEXT NOT NULL,                 -- 通知角色(JSON格式)
    created_by INTEGER NOT NULL,                -- 创建人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建预警记录表
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,                   -- 规则ID
    target_type TEXT NOT NULL,                  -- 目标类型：项目/业务事件/财务记录
    target_id INTEGER NOT NULL,                 -- 目标ID
    current_value REAL NOT NULL,                -- 当前值
    threshold REAL NOT NULL,                    -- 阈值
    status TEXT NOT NULL,                       -- 状态：未处理/已处理/已忽略
    handled_by INTEGER,                         -- 处理人
    handled_at TIMESTAMP,                       -- 处理时间
    remarks TEXT,                               -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES alert_rules (id)
);

-- 创建通知记录表
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                   -- 用户ID
    alert_id INTEGER,                           -- 预警ID
    message TEXT NOT NULL,                      -- 消息内容
    type TEXT NOT NULL,                         -- 类型：预警/系统/任务
    is_read BOOLEAN DEFAULT 0,                  -- 是否已读
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建仪表盘配置表
CREATE TABLE IF NOT EXISTS dashboard_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                   -- 用户ID
    name TEXT NOT NULL,                         -- 配置名称
    layout TEXT NOT NULL,                       -- 布局配置(JSON格式)
    is_default BOOLEAN DEFAULT 0,               -- 是否默认
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 
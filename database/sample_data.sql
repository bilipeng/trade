-- 业财融合管理系统示例数据
-- 用于初始化系统以便测试和演示

-- 清空现有数据（如果需要）
-- 请谨慎执行以下语句，它们会删除所有现有数据
-- 取消注释以下语句可以清空所有表
-- DELETE FROM report_configs;
-- DELETE FROM system_logs;
-- DELETE FROM attachments;
-- DELETE FROM approval_configs;
-- DELETE FROM approvals;
-- DELETE FROM budgets;
-- DELETE FROM financial_records;
-- DELETE FROM business_events;
-- DELETE FROM customers;
-- DELETE FROM account_subjects;
-- DELETE FROM departments;
-- DELETE FROM users;

-- 添加用户数据
INSERT OR IGNORE INTO users (username, password, role, department, email, phone) VALUES
('admin', 'admin', '管理员', '系统管理', 'admin@example.com', '13800000001'),
('zhangsan', 'password123', '财务', '财务部', 'zhangsan@example.com', '13800000002'),
('lisi', 'password123', '业务', '业务部', 'lisi@example.com', '13800000003'),
('wangwu', 'password123', '业务', '业务部', 'wangwu@example.com', '13800000004'),
('zhaoliu', 'password123', '财务', '财务部', 'zhaoliu@example.com', '13800000005'),
('qianqi', 'password123', '审批', '技术部', 'qianqi@example.com', '13800000006'),
('sunba', 'password123', '管理员', '业务部', 'sunba@example.com', '13800000007'),
('zhoujiu', 'password123', '审批', '财务部', 'zhoujiu@example.com', '13800000008');

-- 部门数据
-- 假设admin用户ID为1，sunba用户ID为7，zhoujiu用户ID为8
INSERT OR IGNORE INTO departments (name, code, parent_id, manager_id) VALUES
('系统管理', 'SYS001', NULL, 1),
('财务部', 'FIN001', NULL, 8),
('业务部', 'BUS001', NULL, 7),
('技术部', 'TEC001', NULL, 6),
('销售组', 'BUS101', 3, 3),
('市场组', 'BUS102', 3, 4),
('研发组', 'TEC101', 4, 6),
('财务核算组', 'FIN101', 2, 2),
('预算管理组', 'FIN102', 2, 5);

-- 客户数据
INSERT OR IGNORE INTO customers (name, code, contact_person, contact_phone, contact_email, address, email) VALUES
('北京科技有限公司', 'CUST001', '王经理', '13911112222', 'wang@bjtech.com', '北京市海淀区中关村南大街5号', 'contact@bjtech.com'),
('上海贸易有限公司', 'CUST002', '张总', '13922223333', 'zhang@shtr.com', '上海市浦东新区陆家嘴金融中心', 'info@shtrading.com'),
('广州电子科技公司', 'CUST003', '李工', '13933334444', 'li@gzel.com', '广州市天河区珠江新城', 'service@gzelec.com'),
('深圳软件开发公司', 'CUST004', '赵博士', '13944445555', 'zhao@szsw.com', '深圳市南山区科技园', 'info@szsoftware.com'),
('杭州网络科技有限公司', 'CUST005', '钱总', '13955556666', 'qian@hznet.com', '杭州市西湖区余杭塘路', 'support@hznetwork.com');

-- 会计科目数据（除了初始化已有的）
INSERT OR IGNORE INTO account_subjects (code, name, parent_code, direction) VALUES
('1001001', '人民币现金', '1001', '借'),
('1001002', '美元现金', '1001', '借'),
('1002001', '工商银行', '1002', '借'),
('1002002', '建设银行', '1002', '借'),
('4001001', '产品销售收入', '4001', '贷'),
('4001002', '服务收入', '4001', '贷'),
('5001001', '原材料成本', '5001', '借'),
('5001002', '人工成本', '5001', '借'),
('6001001', '办公费用', '6001', '借'),
('6001002', '差旅费用', '6001', '借'),
('6602001', '广告费', '6602', '借'),
('6602002', '业务招待费', '6602', '借');

-- 业务事件数据（假设部门ID 1-4，客户ID 1-5，创建者ID 1-8）
INSERT OR IGNORE INTO business_events (event_type, project_name, project_code, customer_id, amount, event_date, description, department_id, created_by, status) VALUES
('销售', '软件开发项目', 'PRJ001', 1, 100000.00, '2023-04-15', '为北京科技有限公司开发管理系统', 3, 3, '已完成'),
('采购', '设备采购', 'PRJ002', NULL, 50000.00, '2023-05-20', '购买办公设备', 4, 6, '已审批'),
('合同', '技术服务合同', 'PRJ003', 3, 200000.00, '2023-06-10', '为广州电子提供技术服务', 3, 4, '待审批'),
('报销', '出差报销', 'PRJ004', NULL, 5000.00, '2023-07-05', '出差上海费用报销', 2, 5, '已审批'),
('销售', '网站建设项目', 'PRJ005', 5, 80000.00, '2023-08-12', '为杭州网络开发企业网站', 3, 3, '已完成'),
('采购', '原材料采购', 'PRJ006', 2, 30000.00, '2023-09-18', '采购生产原材料', 3, 4, '待审批'),
('合同', '年度维护合同', 'PRJ007', 4, 150000.00, '2023-10-22', '深圳软件系统维护合同', 4, 6, '已审批'),
('报销', '招待费用', 'PRJ008', NULL, 3000.00, '2023-11-15', '客户招待费用', 3, 4, '已拒绝'),
('销售', '培训服务', 'PRJ009', 1, 50000.00, '2023-12-05', '为北京科技提供技术培训', 3, 3, '待审批'),
('合同', '咨询服务', 'PRJ010', 5, 120000.00, '2024-01-10', '为杭州网络提供咨询服务', 3, 4, '已审批');

-- 财务记录数据（假设业务事件ID 1-10，创建者ID为财务人员2和5）
INSERT OR IGNORE INTO financial_records (business_event_id, account_code, account_name, amount, direction, record_date, fiscal_year, fiscal_period, description, created_by) VALUES
(1, '4001002', '服务收入', 100000.00, '收入', '2023-04-20', 2023, 4, '软件开发收入', 2),
(1, '1002001', '工商银行', 100000.00, '收入', '2023-04-20', 2023, 4, '收到软件开发款', 2),
(2, '6001001', '办公费用', 50000.00, '支出', '2023-05-25', 2023, 5, '办公设备采购', 5),
(2, '1002002', '建设银行', 50000.00, '支出', '2023-05-25', 2023, 5, '支付设备款', 5),
(4, '6001002', '差旅费用', 5000.00, '支出', '2023-07-10', 2023, 7, '员工出差费用', 2),
(4, '1001001', '人民币现金', 5000.00, '支出', '2023-07-10', 2023, 7, '支付差旅费', 2),
(5, '4001002', '服务收入', 80000.00, '收入', '2023-08-15', 2023, 8, '网站建设收入', 5),
(5, '1002001', '工商银行', 80000.00, '收入', '2023-08-15', 2023, 8, '收到网站建设款', 5),
(7, '4001002', '服务收入', 150000.00, '收入', '2023-10-25', 2023, 10, '系统维护收入', 2),
(7, '1002001', '工商银行', 150000.00, '收入', '2023-10-25', 2023, 10, '收到系统维护款', 2);

-- 预算数据（使用部门ID 1-9，科目ID 1-12）
INSERT OR IGNORE INTO budgets (department_id, year, month, account_subject_id, amount, used_amount, created_by) VALUES
(2, 2024, 1, 1, 50000.00, 10000.00, 8),
(2, 2024, 1, 3, 500000.00, 120000.00, 8),
(2, 2024, 1, 9, 20000.00, 5000.00, 8),
(3, 2024, 1, 10, 30000.00, 8000.00, 7),
(3, 2024, 1, 11, 100000.00, 25000.00, 7),
(3, 2024, 1, 12, 50000.00, 15000.00, 7),
(4, 2024, 1, 9, 15000.00, 3000.00, 6),
(4, 2024, 1, 7, 80000.00, 30000.00, 6),
(5, 2024, 1, 11, 50000.00, 12000.00, 7),
(8, 2024, 1, 9, 10000.00, 2000.00, 8);

-- 审批流程数据（使用业务事件ID 1-10，审批人ID 6-8）
INSERT OR IGNORE INTO approvals (business_event_id, approver_id, approval_level, status, comment, approval_date) VALUES
(1, 7, 1, '已通过', '同意软件开发项目', '2023-04-16 10:30:00'),
(2, 6, 1, '已通过', '设备采购必要，同意', '2023-05-21 14:45:00'),
(3, 7, 1, '待审批', NULL, NULL),
(4, 8, 1, '已通过', '差旅费用合理', '2023-07-06 09:15:00'),
(5, 7, 1, '已通过', '同意网站建设项目', '2023-08-13 11:20:00'),
(6, 7, 1, '待审批', NULL, NULL),
(7, 6, 1, '已通过', '维护合同重要，同意', '2023-10-23 16:30:00'),
(8, 7, 1, '已拒绝', '招待费用过高，不符合规定', '2023-11-16 13:45:00'),
(9, 7, 1, '待审批', NULL, NULL),
(10, 7, 1, '已通过', '咨询服务项目有价值', '2024-01-11 10:00:00');

-- 审批流程配置
INSERT OR IGNORE INTO approval_configs (event_type, department_id, approver_id, approval_level, amount_threshold, is_active) VALUES
('销售', 3, 7, 1, 10000.00, 1),
('销售', 3, 8, 2, 100000.00, 1),
('采购', 3, 7, 1, 10000.00, 1),
('采购', 4, 6, 1, 10000.00, 1),
('采购', 2, 8, 2, 50000.00, 1),
('合同', 3, 7, 1, 0.00, 1),
('合同', 4, 6, 1, 0.00, 1),
('报销', 2, 8, 1, 1000.00, 1),
('报销', 3, 7, 1, 1000.00, 1);

-- 附件数据（使用业务事件ID 1-10，上传者ID 1-8）
INSERT OR IGNORE INTO attachments (business_event_id, file_name, file_path, file_type, file_size, uploaded_by) VALUES
(1, '软件开发合同.pdf', '/uploads/contracts/contract_1.pdf', 'application/pdf', 1024000, 3),
(1, '软件需求说明书.docx', '/uploads/documents/requirements_1.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 512000, 3),
(2, '设备清单.xlsx', '/uploads/documents/equipment_list.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 256000, 6),
(3, '技术服务方案.pdf', '/uploads/documents/service_plan.pdf', 'application/pdf', 768000, 4),
(4, '出差报销单.pdf', '/uploads/receipts/travel_expense.pdf', 'application/pdf', 102400, 5),
(5, '网站设计方案.pdf', '/uploads/documents/website_design.pdf', 'application/pdf', 1536000, 3),
(7, '维护合同.pdf', '/uploads/contracts/maintenance_contract.pdf', 'application/pdf', 819200, 6),
(10, '咨询服务合同.pdf', '/uploads/contracts/consulting_contract.pdf', 'application/pdf', 1228800, 4);

-- 系统日志数据
INSERT OR IGNORE INTO system_logs (user_id, action, target_type, target_id, details, ip_address) VALUES
(1, '登录', '系统', NULL, '管理员登录系统', '192.168.1.100'),
(2, '创建', '财务记录', 1, '创建财务记录', '192.168.1.101'),
(3, '创建', '业务事件', 1, '创建销售项目', '192.168.1.102'),
(4, '创建', '业务事件', 3, '创建技术服务合同', '192.168.1.103'),
(5, '修改', '预算', 1, '修改财务部预算', '192.168.1.101'),
(6, '审批', '业务事件', 2, '审批设备采购', '192.168.1.104'),
(7, '拒绝', '业务事件', 8, '拒绝报销申请', '192.168.1.105'),
(8, '创建', '审批配置', 1, '创建审批流程', '192.168.1.106'),
(1, '导出', '报表', NULL, '导出财务报表', '192.168.1.100'),
(2, '上传', '附件', 1, '上传合同文件', '192.168.1.101');

-- 报表配置数据
INSERT OR IGNORE INTO report_configs (report_name, report_type, sql_query, description, created_by, is_active) VALUES
('月度销售报表', '业务', 'SELECT strftime(''%Y-%m'', event_date) as month, SUM(amount) as total_amount FROM business_events WHERE event_type = ''销售'' GROUP BY month ORDER BY month DESC', '按月统计销售金额', 1, 1),
('部门预算执行情况', '预算', 'SELECT d.name as department, SUM(b.amount) as budget_amount, SUM(b.used_amount) as used_amount, ROUND(SUM(b.used_amount) * 100.0 / SUM(b.amount), 2) as usage_rate FROM budgets b JOIN departments d ON b.department_id = d.id WHERE b.year = 2024 AND b.month = 1 GROUP BY b.department_id', '2024年1月各部门预算执行情况', 1, 1),
('审批统计报表', '业务', 'SELECT a.status, COUNT(*) as count FROM approvals a GROUP BY a.status', '按状态统计审批数量', 1, 1),
('财务收支明细', '财务', 'SELECT record_date, account_name, amount, direction FROM financial_records ORDER BY record_date DESC', '财务收支明细记录', 1, 1),
('客户业务统计', '业务', 'SELECT c.name as customer, COUNT(b.id) as event_count, SUM(b.amount) as total_amount FROM business_events b JOIN customers c ON b.customer_id = c.id GROUP BY b.customer_id', '各客户业务统计', 1, 1); 
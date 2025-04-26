# 业财看板MVP实施方案

## 1. 功能概述

业财看板MVP版本将实现一个简单的项目财务概览功能，展示业务事件与财务数据的关联，帮助用户快速了解项目的财务状况。

## 2. 实现方案

### 2.1 数据库扩展

利用现有数据库结构，不需要创建新表，只需添加一个视图来关联业务事件和财务数据：

```sql
-- 创建业务财务关联视图
CREATE VIEW IF NOT EXISTS business_finance_view AS
SELECT 
    be.id AS business_id,
    be.project_name,
    be.project_code,
    be.event_type,
    be.amount AS business_amount,
    be.status AS business_status,
    be.event_date,
    be.department_id,
    d.name AS department_name,
    c.name AS customer_name,
    SUM(CASE WHEN fr.direction = '收入' THEN fr.amount ELSE 0 END) AS income_amount,
    SUM(CASE WHEN fr.direction = '支出' THEN fr.amount ELSE 0 END) AS expense_amount,
    COUNT(fr.id) AS finance_record_count
FROM 
    business_events be
LEFT JOIN 
    departments d ON be.department_id = d.id
LEFT JOIN 
    customers c ON be.customer_id = c.id
LEFT JOIN 
    financial_transactions fr ON be.id = fr.business_event_id
GROUP BY 
    be.id;
```

### 2.2 后端API

添加一个简单的API端点来获取业财看板数据：

```python
@app.get("/dashboard/business-finance")
async def get_business_finance_dashboard(
    department_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """获取业财看板数据"""
    conn = get_db_connection()
  
    # 构建查询条件
    query = "SELECT * FROM business_finance_view WHERE 1=1"
    params = []
  
    if department_id:
        query += " AND department_id = ?"
        params.append(department_id)
  
    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)
  
    if start_date:
        query += " AND event_date >= ?"
        params.append(start_date)
  
    if end_date:
        query += " AND event_date <= ?"
        params.append(end_date)
  
    # 执行查询
    results = conn.execute(query, params).fetchall()
    conn.close()
  
    # 计算汇总数据
    total_business_amount = sum(r['business_amount'] for r in results)
    total_income = sum(r['income_amount'] for r in results)
    total_expense = sum(r['expense_amount'] for r in results)
  
    # 按部门分组
    dept_summary = {}
    for r in results:
        dept_id = r['department_id']
        if dept_id not in dept_summary:
            dept_summary[dept_id] = {
                'department_name': r['department_name'],
                'business_amount': 0,
                'income_amount': 0,
                'expense_amount': 0,
                'count': 0
            }
      
        dept_summary[dept_id]['business_amount'] += r['business_amount']
        dept_summary[dept_id]['income_amount'] += r['income_amount']
        dept_summary[dept_id]['expense_amount'] += r['expense_amount']
        dept_summary[dept_id]['count'] += 1
  
    # 按事件类型分组
    type_summary = {}
    for r in results:
        event_type = r['event_type']
        if event_type not in type_summary:
            type_summary[event_type] = {
                'business_amount': 0,
                'income_amount': 0,
                'expense_amount': 0,
                'count': 0
            }
      
        type_summary[event_type]['business_amount'] += r['business_amount']
        type_summary[event_type]['income_amount'] += r['income_amount']
        type_summary[event_type]['expense_amount'] += r['expense_amount']
        type_summary[event_type]['count'] += 1
  
    return {
        "detail_data": [dict(r) for r in results],
        "summary": {
            "total_business_amount": total_business_amount,
            "total_income": total_income,
            "total_expense": total_expense,
            "profit": total_income - total_expense,
            "record_count": len(results)
        },
        "department_summary": dept_summary,
        "type_summary": type_summary
    }
```

### 2.3 前端实现

在客户端添加一个简单的业财看板界面：

```python
class BusinessFinanceDashboard(QWidget):
    """业财看板"""
  
    def __init__(self, token, user_data):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.init_ui()
        self.load_data()
  
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
      
        # 标题与工具栏
        top_layout = QHBoxLayout()
        title_label = QLabel("业财看板")
        title_label.setProperty("class", "view-title")
        top_layout.addWidget(title_label)
      
        top_layout.addStretch()
      
        # 筛选控件
        self.department_combo = QComboBox()
        self.department_combo.addItem("全部部门", None)
        self.department_combo.currentIndexChanged.connect(self.filter_data)
      
        self.type_combo = QComboBox()
        self.type_combo.addItem("全部类型", None)
        self.type_combo.addItems(["合同", "销售", "采购", "报销"])
        self.type_combo.currentIndexChanged.connect(self.filter_data)
      
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        self.date_start.dateChanged.connect(self.filter_data)
      
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.dateChanged.connect(self.filter_data)
      
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_data)
      
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("部门:"))
        filter_layout.addWidget(self.department_combo)
        filter_layout.addWidget(QLabel("类型:"))
        filter_layout.addWidget(self.type_combo)
        filter_layout.addWidget(QLabel("开始日期:"))
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("结束日期:"))
        filter_layout.addWidget(self.date_end)
        filter_layout.addWidget(self.refresh_btn)
      
        top_layout.addLayout(filter_layout)
        main_layout.addLayout(top_layout)
      
        # 摘要卡片区域
        summary_layout = QHBoxLayout()
      
        # 业务金额卡片
        self.business_card = QGroupBox("业务总金额")
        business_layout = QVBoxLayout(self.business_card)
        self.business_amount_label = QLabel("¥0.00")
        self.business_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.business_amount_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1976D2;")
        business_layout.addWidget(self.business_amount_label)
        summary_layout.addWidget(self.business_card)
      
        # 收入卡片
        self.income_card = QGroupBox("总收入")
        income_layout = QVBoxLayout(self.income_card)
        self.income_amount_label = QLabel("¥0.00")
        self.income_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.income_amount_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        income_layout.addWidget(self.income_amount_label)
        summary_layout.addWidget(self.income_card)
      
        # 支出卡片
        self.expense_card = QGroupBox("总支出")
        expense_layout = QVBoxLayout(self.expense_card)
        self.expense_amount_label = QLabel("¥0.00")
        self.expense_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.expense_amount_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #F44336;")
        expense_layout.addWidget(self.expense_amount_label)
        summary_layout.addWidget(self.expense_card)
      
        # 利润卡片
        self.profit_card = QGroupBox("利润")
        profit_layout = QVBoxLayout(self.profit_card)
        self.profit_amount_label = QLabel("¥0.00")
        self.profit_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profit_amount_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800;")
        profit_layout.addWidget(self.profit_amount_label)
        summary_layout.addWidget(self.profit_card)
      
        main_layout.addLayout(summary_layout)
      
        # 创建选项卡
        self.tabs = QTabWidget()
      
        # 详细数据表格
        self.detail_tab = QWidget()
        detail_layout = QVBoxLayout(self.detail_tab)
      
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(8)
        self.detail_table.setHorizontalHeaderLabels([
            "项目名称", "项目编号", "类型", "部门", "客户", 
            "业务金额", "收入", "支出"
        ])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        detail_layout.addWidget(self.detail_table)
      
        self.tabs.addTab(self.detail_tab, "详细数据")
      
        # 部门统计选项卡
        self.dept_tab = QWidget()
        dept_layout = QVBoxLayout(self.dept_tab)
      
        self.dept_table = QTableWidget()
        self.dept_table.setColumnCount(5)
        self.dept_table.setHorizontalHeaderLabels([
            "部门", "业务数量", "业务金额", "收入", "支出"
        ])
        self.dept_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dept_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        dept_layout.addWidget(self.dept_table)
      
        self.tabs.addTab(self.dept_tab, "部门统计")
      
        # 类型统计选项卡
        self.type_tab = QWidget()
        type_layout = QVBoxLayout(self.type_tab)
      
        self.type_table = QTableWidget()
        self.type_table.setColumnCount(5)
        self.type_table.setHorizontalHeaderLabels([
            "类型", "业务数量", "业务金额", "收入", "支出"
        ])
        self.type_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.type_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        type_layout.addWidget(self.type_table)
      
        self.tabs.addTab(self.type_tab, "类型统计")
      
        main_layout.addWidget(self.tabs)
  
    def load_departments(self):
        """加载部门数据"""
        try:
            response = requests.get(
                "http://localhost:8000/departments",
                headers={"Authorization": f"Bearer {self.token}"}
            )
          
            if response.status_code == 200:
                departments = response.json()
              
                # 保存当前选择
                current_index = self.department_combo.currentIndex()
              
                # 清空并重新添加
                self.department_combo.clear()
                self.department_combo.addItem("全部部门", None)
              
                for dept in departments:
                    self.department_combo.addItem(dept["name"], dept["id"])
              
                # 恢复选择
                if current_index < self.department_combo.count():
                    self.department_combo.setCurrentIndex(current_index)
            else:
                QMessageBox.warning(self, "加载失败", "无法加载部门数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载部门数据时发生错误: {str(e)}")
  
    def load_data(self):
        """加载业财看板数据"""
        try:
            # 构建查询参数
            params = {}
          
            if self.department_combo.currentData():
                params["department_id"] = self.department_combo.currentData()
          
            if self.type_combo.currentData():
                params["event_type"] = self.type_combo.currentText()
          
            params["start_date"] = self.date_start.date().toString("yyyy-MM-dd")
            params["end_date"] = self.date_end.date().toString("yyyy-MM-dd")
          
            # 发送请求
            response = requests.get(
                "http://localhost:8000/dashboard/business-finance",
                params=params,
                headers={"Authorization": f"Bearer {self.token}"}
            )
          
            if response.status_code == 200:
                data = response.json()
                self.display_data(data)
            else:
                QMessageBox.warning(self, "加载失败", "无法加载业财看板数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据时发生错误: {str(e)}")
  
    def filter_data(self):
        """根据筛选条件过滤数据"""
        self.load_data()
  
    def display_data(self, data):
        """显示业财看板数据"""
        # 更新摘要卡片
        summary = data["summary"]
        self.business_amount_label.setText(f"¥{summary['total_business_amount']:,.2f}")
        self.income_amount_label.setText(f"¥{summary['total_income']:,.2f}")
        self.expense_amount_label.setText(f"¥{summary['total_expense']:,.2f}")
        self.profit_amount_label.setText(f"¥{summary['profit']:,.2f}")
      
        # 更新详细数据表格
        detail_data = data["detail_data"]
        self.detail_table.setRowCount(len(detail_data))
      
        for row, item in enumerate(detail_data):
            self.detail_table.setItem(row, 0, QTableWidgetItem(item["project_name"]))
            self.detail_table.setItem(row, 1, QTableWidgetItem(item["project_code"] or ""))
            self.detail_table.setItem(row, 2, QTableWidgetItem(item["event_type"]))
            self.detail_table.setItem(row, 3, QTableWidgetItem(item["department_name"]))
            self.detail_table.setItem(row, 4, QTableWidgetItem(item["customer_name"] or ""))
            self.detail_table.setItem(row, 5, QTableWidgetItem(f"¥{item['business_amount']:,.2f}"))
            self.detail_table.setItem(row, 6, QTableWidgetItem(f"¥{item['income_amount']:,.2f}"))
            self.detail_table.setItem(row, 7, QTableWidgetItem(f"¥{item['expense_amount']:,.2f}"))
      
        # 更新部门统计表格
        dept_summary = data["department_summary"]
        self.dept_table.setRowCount(len(dept_summary))
      
        for row, (dept_id, dept_data) in enumerate(dept_summary.items()):
            self.dept_table.setItem(row, 0, QTableWidgetItem(dept_data["department_name"]))
            self.dept_table.setItem(row, 1, QTableWidgetItem(str(dept_data["count"])))
            self.dept_table.setItem(row, 2, QTableWidgetItem(f"¥{dept_data['business_amount']:,.2f}"))
            self.dept_table.setItem(row, 3, QTableWidgetItem(f"¥{dept_data['income_amount']:,.2f}"))
            self.dept_table.setItem(row, 4, QTableWidgetItem(f"¥{dept_data['expense_amount']:,.2f}"))
      
        # 更新类型统计表格
        type_summary = data["type_summary"]
        self.type_table.setRowCount(len(type_summary))
      
        for row, (event_type, type_data) in enumerate(type_summary.items()):
            self.type_table.setItem(row, 0, QTableWidgetItem(event_type))
            self.type_table.setItem(row, 1, QTableWidgetItem(str(type_data["count"])))
            self.type_table.setItem(row, 2, QTableWidgetItem(f"¥{type_data['business_amount']:,.2f}"))
            self.type_table.setItem(row, 3, QTableWidgetItem(f"¥{type_data['income_amount']:,.2f}"))
            self.type_table.setItem(row, 4, QTableWidgetItem(f"¥{type_data['expense_amount']:,.2f}"))
```

## 3. 集成到主界面

在主窗口中添加业财看板选项卡：

```python
# 在MainWindow类的init_ui方法中添加
self.dashboard_view = BusinessFinanceDashboard(self.token, self.user_data)
self.content_tabs.addTab(self.dashboard_view, "业财看板")
```

## 4. 实施步骤

1. 在数据库中创建业务财务关联视图
2. 在后端添加业财看板API
3. 在前端实现业财看板界面
4. 将业财看板集成到主界面

## 5. 测试方案

1. 创建几个测试业务事件和关联的财务记录
2. 启动系统，进入业财看板
3. 验证数据显示是否正确
4. 测试筛选功能
5. 测试不同选项卡的数据展示

## 6. 后续扩展

这个MVP版本实现了基本的业财看板功能，后续可以扩展：

1. 添加图表展示，如柱状图、饼图等
2. 实现数据导出功能
3. 添加更多的数据分析指标
4. 实现预警规则配置
5. 添加通知功能

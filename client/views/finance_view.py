import sys
import os
import json
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QLineEdit, QDateEdit, QFormLayout, QDialog, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QDate

class FinancialRecordView(QWidget):
    """财务记录管理视图"""
    
    def __init__(self, token, user_data):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.account_subjects = []
        self.business_events = []
        self.init_ui()
        self.load_account_subjects()
        self.load_business_events()
        self.load_data()
    
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题与工具栏
        top_layout = QHBoxLayout()
        title_label = QLabel("财务记录管理")
        title_label.setProperty("class", "view-title")
        top_layout.addWidget(title_label)
        
        top_layout.addStretch()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索项目名称...")
        self.search_input.textChanged.connect(self.search_data)
        self.search_input.setMaximumWidth(200)
        top_layout.addWidget(self.search_input)
        
        # 新建按钮
        self.add_button = QPushButton("新建财务记录")
        self.add_button.clicked.connect(self.show_add_dialog)
        top_layout.addWidget(self.add_button)
        
        main_layout.addLayout(top_layout)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 待处理业务选项卡
        self.pending_tab = QWidget()
        pending_layout = QVBoxLayout(self.pending_tab)
        
        # 待处理业务列表标题
        pending_header = QHBoxLayout()
        pending_title = QLabel("待处理已审批业务")
        pending_title.setProperty("class", "section-title")
        pending_header.addWidget(pending_title)
        
        pending_header.addStretch()
        
        # 刷新待处理按钮
        refresh_pending_btn = QPushButton("刷新")
        refresh_pending_btn.clicked.connect(self.load_business_events)
        pending_header.addWidget(refresh_pending_btn)
        
        pending_layout.addLayout(pending_header)
        
        # 待处理业务表格
        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(6)
        self.pending_table.setHorizontalHeaderLabels(["业务ID", "事件类型", "项目名称", "金额", "审批日期", "操作"])
        self.pending_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pending_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pending_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        pending_layout.addWidget(self.pending_table)
        
        # 财务记录选项卡
        self.records_tab = QWidget()
        records_layout = QVBoxLayout(self.records_tab)
        
        # 财务记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "业务项目", "科目", "金额", "方向", "日期", "财年/期间", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        records_layout.addWidget(self.table)
        
        # 添加选项卡
        self.tabs.addTab(self.pending_tab, "待处理业务")
        self.tabs.addTab(self.records_tab, "财务记录")
        
        main_layout.addWidget(self.tabs)
    
    def load_account_subjects(self):
        """加载会计科目数据"""
        try:
            response = requests.get(
                "http://localhost:8000/account_subjects",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                self.account_subjects = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载会计科目数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载会计科目数据时发生错误: {str(e)}")
    
    def load_business_events(self):
        """加载已审批的业务事件数据"""
        try:
            response = requests.get(
                "http://localhost:8000/business_events",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                # 只保留已审批但未创建财务记录的业务事件
                all_events = response.json()
                self.business_events = []
                
                for event in all_events:
                    if event["status"] == "已审批":
                        # 检查是否已有财务记录
                        has_finance = False
                        try:
                            # 查询关联的财务记录
                            fin_response = requests.get(
                                f"http://localhost:8000/business_events/{event['id']}/related",
                                headers={"Authorization": f"Bearer {self.token}"}
                            )
                            
                            if fin_response.status_code == 200:
                                related_data = fin_response.json()
                                has_finance = len(related_data.get("financial_records", [])) > 0
                        except:
                            pass
                        
                        if not has_finance:
                            self.business_events.append(event)
                
                # 更新待处理业务表格
                self.display_pending_events()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载业务事件数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载业务事件数据时发生错误: {str(e)}")
    
    def display_pending_events(self):
        """显示待处理业务事件"""
        self.pending_table.setRowCount(0)
        
        for row, item in enumerate(self.business_events):
            self.pending_table.insertRow(row)
            
            # 设置各列数据
            self.pending_table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.pending_table.setItem(row, 1, QTableWidgetItem(item["event_type"]))
            self.pending_table.setItem(row, 2, QTableWidgetItem(item["project_name"]))
            
            # 金额列
            amount_item = QTableWidgetItem(f"¥{item['amount']:,.2f}")
            self.pending_table.setItem(row, 3, amount_item)
            
            # 审批日期（使用创建日期）
            date_str = item.get("approved_at", item.get("created_at", ""))
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                except:
                    formatted_date = date_str
            else:
                formatted_date = ""
                
            self.pending_table.setItem(row, 4, QTableWidgetItem(formatted_date))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            # 创建财务记录按钮
            create_btn = QPushButton("创建财务记录")
            create_btn.setProperty("class", "primary")
            create_btn.clicked.connect(lambda _, event_id=item["id"]: self.create_from_business(event_id))
            btn_layout.addWidget(create_btn)
            
            # 查看详情按钮
            view_btn = QPushButton("查看详情")
            view_btn.clicked.connect(lambda _, event_id=item["id"]: self.view_business_detail(event_id))
            btn_layout.addWidget(view_btn)
            
            self.pending_table.setCellWidget(row, 5, btn_widget)
    
    def load_data(self):
        """加载财务记录数据"""
        try:
            response = requests.get(
                "http://localhost:8000/financial_records",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                self.data = response.json()
                self.display_data(self.data)
            else:
                QMessageBox.warning(self, "加载失败", "无法加载财务记录数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据时发生错误: {str(e)}")
    
    def display_data(self, data):
        """显示数据到表格"""
        self.table.setRowCount(0)
        
        for row, item in enumerate(data):
            self.table.insertRow(row)
            
            # 设置各列数据
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            
            # 项目名称（从业务事件获取）
            self.table.setItem(row, 1, QTableWidgetItem(item.get("project_name", "")))
            
            # 科目
            self.table.setItem(row, 2, QTableWidgetItem(item["account_name"]))
            
            # 金额
            amount_item = QTableWidgetItem(f"¥{item['amount']:,.2f}")
            self.table.setItem(row, 3, amount_item)
            
            # 方向
            direction_item = QTableWidgetItem(item["direction"])
            if item["direction"] == "收入":
                direction_item.setForeground(Qt.GlobalColor.green)
            else:
                direction_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 4, direction_item)
            
            # 日期
            self.table.setItem(row, 5, QTableWidgetItem(item["record_date"]))
            
            # 财年/期间
            self.table.setItem(row, 6, QTableWidgetItem(f"{item['fiscal_year']}/{item['fiscal_period']}"))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            # 详情按钮
            detail_btn = QPushButton("详情")
            detail_btn.clicked.connect(lambda _, record_id=item["id"]: self.show_detail(record_id))
            btn_layout.addWidget(detail_btn)
            
            # 查看业务事件按钮
            if "business_event_id" in item and item["business_event_id"]:
                view_business_btn = QPushButton("查看业务")
                view_business_btn.setProperty("class", "link-button")
                view_business_btn.clicked.connect(lambda _, b_id=item["business_event_id"]: self.view_business_detail(b_id))
                btn_layout.addWidget(view_business_btn)
            
            self.table.setCellWidget(row, 7, btn_widget)
    
    def search_data(self):
        """搜索数据"""
        search_text = self.search_input.text().lower()
        
        filtered_data = []
        for item in self.data:
            project_name = item.get("project_name", "").lower()
            account_name = item["account_name"].lower()
            
            if search_text in project_name or search_text in account_name:
                filtered_data.append(item)
        
        self.display_data(filtered_data)
    
    def show_add_dialog(self):
        """显示添加财务记录对话框"""
        if not self.business_events and not self.tabs.currentIndex() == 0:
            QMessageBox.warning(self, "无可用业务事件", "没有已审批的业务事件可以创建财务记录")
            return
            
        dialog = FinancialRecordDialog(self.token, self.user_data, 
                                      self.account_subjects, self.business_events)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.load_business_events()  # 刷新待处理业务
    
    def create_from_business(self, business_id):
        """从业务事件创建财务记录"""
        # 查找业务事件
        event_data = None
        for event in self.business_events:
            if event["id"] == business_id:
                event_data = event
                break
        
        if not event_data:
            QMessageBox.warning(self, "数据错误", "找不到指定的业务事件")
            return
        
        # 创建财务记录
        dialog = FinancialRecordDialog(self.token, self.user_data, 
                                      self.account_subjects, [event_data], 
                                      preselect_business=business_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.load_business_events()  # 刷新待处理业务
            
            # 切换到财务记录选项卡
            self.tabs.setCurrentIndex(1)
    
    def view_business_detail(self, business_id):
        """查看业务事件详情"""
        try:
            response = requests.get(
                f"http://localhost:8000/business_events/{business_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                event_data = response.json()
                dialog = BusinessEventViewDialog(event_data)
                dialog.exec()
            else:
                QMessageBox.warning(self, "查询失败", "无法获取业务事件详情")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查询详情时发生错误: {str(e)}")
    
    def show_detail(self, record_id):
        """显示财务记录详情"""
        try:
            response = requests.get(
                f"http://localhost:8000/financial_records/{record_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                record_data = response.json()
                
                # 查询关联的业务事件
                event_data = None
                if "business_event_id" in record_data and record_data["business_event_id"]:
                    event_response = requests.get(
                        f"http://localhost:8000/business_events/{record_data['business_event_id']}",
                        headers={"Authorization": f"Bearer {self.token}"}
                    )
                    
                    if event_response.status_code == 200:
                        event_data = event_response.json()
                
                dialog = FinancialRecordDetailDialog(record_data, event_data)
                dialog.exec()
            else:
                QMessageBox.warning(self, "查询失败", "无法获取财务记录详情")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查询详情时发生错误: {str(e)}")

class FinancialRecordDialog(QDialog):
    """财务记录添加对话框"""
    
    def __init__(self, token, user_data, account_subjects, business_events, preselect_business=None):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.account_subjects = account_subjects
        self.business_events = business_events
        self.preselect_business = preselect_business
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("添加财务记录")
        self.setMinimumWidth(550)
        
        layout = QVBoxLayout(self)
        
        # 添加标题
        title_label = QLabel("创建财务记录")
        title_label.setProperty("class", "dialog-title")
        layout.addWidget(title_label)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 关联业务事件
        self.event_combo = QComboBox()
        self.event_combo.setMinimumWidth(300)
        self.event_combo.addItem("- 请选择业务事件 -", None)
        
        # 添加业务事件选项
        for event in self.business_events:
            display_text = f"{event['id']} - {event['project_name']} (¥{event['amount']:,.2f})"
            self.event_combo.addItem(display_text, event["id"])
        
        self.update_amount_from_event()
        self.event_combo.currentIndexChanged.connect(self.update_amount_from_event)
        
        # 预选业务事件
        if self.preselect_business:
            for i in range(self.event_combo.count()):
                if self.event_combo.itemData(i) == self.preselect_business:
                    self.event_combo.setCurrentIndex(i)
                    break
        
        # 会计科目
        self.account_combo = QComboBox()
        self.account_combo.addItem("- 请选择科目 -", None)
        
        # 添加科目选项
        for subject in self.account_subjects:
            self.account_combo.addItem(f"{subject['code']} - {subject['name']}", subject["code"])
        
        self.account_combo.currentIndexChanged.connect(self.update_account_info)
        form_layout.addRow("会计科目:", self.account_combo)
        
        # 科目编码
        self.account_code_input = QLineEdit()
        self.account_code_input.setReadOnly(True)
        form_layout.addRow("科目编码:", self.account_code_input)
        
        # 科目名称
        self.account_name_input = QLineEdit()
        self.account_name_input.setReadOnly(True)
        form_layout.addRow("科目名称:", self.account_name_input)
        
        # 收支方向
        self.direction_combo = QComboBox()
        self.direction_combo.addItem("支出", "支出")
        self.direction_combo.addItem("收入", "收入")
        form_layout.addRow("收支方向:", self.direction_combo)
        
        # 金额
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 10000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" 元")
        self.amount_input.setSpecialValueText(" ")
        form_layout.addRow("金额:", self.amount_input)
        
        # 记录日期
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("记录日期:", self.date_input)
        
        # 财年
        current_year = datetime.now().year
        self.fiscal_year_input = QSpinBox()
        self.fiscal_year_input.setRange(2000, 2100)
        self.fiscal_year_input.setValue(current_year)
        form_layout.addRow("财年:", self.fiscal_year_input)
        
        # 会计期间
        current_month = datetime.now().month
        self.fiscal_period_input = QSpinBox()
        self.fiscal_period_input.setRange(1, 12)
        self.fiscal_period_input.setValue(current_month)
        form_layout.addRow("会计期间:", self.fiscal_period_input)
        
        # 描述
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("请输入描述信息...")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("描述:", self.description_input)
        
        # 添加项目名称（仅用于展示）
        self.project_name_label = QLabel()
        form_layout.addRow("项目名称:", self.project_name_label)
        
        layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_data)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def update_account_info(self):
        """更新科目信息"""
        selected_code = self.account_combo.currentData()
        
        if not selected_code:
            self.account_code_input.clear()
            self.account_name_input.clear()
            return
        
        # 查找选中的科目
        for subject in self.account_subjects:
            if subject["code"] == selected_code:
                self.account_code_input.setText(subject["code"])
                self.account_name_input.setText(subject["name"])
                
                # 设置默认收支方向
                if "默认方向" in subject and subject["默认方向"]:
                    direction_index = self.direction_combo.findText(subject["默认方向"])
                    if direction_index >= 0:
                        self.direction_combo.setCurrentIndex(direction_index)
                
                break
    
    def update_amount_from_event(self):
        """从业务事件更新金额"""
        selected_id = self.event_combo.currentData()
        
        if not selected_id:
            self.amount_input.setValue(0)
            self.project_name_label.setText("")
            self.description_input.clear()
            return
        
        # 查找选中的业务事件
        for event in self.business_events:
            if event["id"] == selected_id:
                # 设置金额
                self.amount_input.setValue(event["amount"])
                
                # 设置项目名称
                self.project_name_label.setText(event["project_name"])
                
                # 设置描述
                if "description" in event and event["description"]:
                    self.description_input.setText(event["description"])
                else:
                    self.description_input.setText(f"业务事件 {event['id']} 的财务记录")
                
                # 设置日期
                try:
                    event_date = QDate.fromString(event["event_date"], "yyyy-MM-dd")
                    if event_date.isValid():
                        self.date_input.setDate(event_date)
                except:
                    pass
                
                # 根据业务类型自动选择科目
                event_type = event["event_type"]
                recommend_subject = None
                
                if event_type == "固定资产采购":
                    # 查找固定资产相关科目
                    for subject in self.account_subjects:
                        if "固定资产" in subject["name"]:
                            recommend_subject = subject["code"]
                            break
                elif event_type == "费用报销":
                    # 查找费用相关科目
                    for subject in self.account_subjects:
                        if "费用" in subject["name"]:
                            recommend_subject = subject["code"]
                            break
                
                if recommend_subject:
                    subject_index = self.account_combo.findData(recommend_subject)
                    if subject_index >= 0:
                        self.account_combo.setCurrentIndex(subject_index)
                
                break
    
    def save_data(self):
        """保存数据"""
        # 验证输入
        account_code = self.account_code_input.text()
        if not account_code:
            QMessageBox.warning(self, "输入错误", "请选择会计科目")
            return
        
        business_event_id = self.event_combo.currentData()
        if not business_event_id:
            QMessageBox.warning(self, "输入错误", "请选择关联业务事件")
            return
        
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "输入错误", "请输入有效金额")
            return
        
        # 构建数据
        data = {
            "business_event_id": business_event_id,
            "account_code": account_code,
            "account_name": self.account_name_input.text(),
            "amount": amount,
            "direction": self.direction_combo.currentData(),
            "record_date": self.date_input.date().toString("yyyy-MM-dd"),
            "fiscal_year": self.fiscal_year_input.value(),
            "fiscal_period": self.fiscal_period_input.value(),
            "description": self.description_input.toPlainText(),
        }
        
        try:
            # 发送请求
            response = requests.post(
                "http://localhost:8000/financial_records",
                json=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                QMessageBox.information(self, "添加成功", f"财务记录已添加，ID: {result['id']}")
                
                # 更新业务事件状态为已入账
                try:
                    status_response = requests.post(
                        f"http://localhost:8000/business_events/{business_event_id}/status",
                        json={"status": "已入账"},
                        headers={"Authorization": f"Bearer {self.token}"}
                    )
                except:
                    # 忽略状态更新错误
                    pass
                
                self.accept()
            else:
                QMessageBox.warning(self, "添加失败", f"无法添加财务记录: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存数据时发生错误: {str(e)}")

class FinancialRecordDetailDialog(QDialog):
    """财务记录详情对话框"""
    
    def __init__(self, record_data, event_data=None):
        super().__init__()
        self.record_data = record_data
        self.event_data = event_data
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("财务记录详情")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 创建基本信息组
        info_group = QGroupBox("财务记录信息")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("记录ID:", QLabel(str(self.record_data["id"])))
        info_layout.addRow("会计科目:", QLabel(f"{self.record_data['account_name']} ({self.record_data['account_code']})"))
        
        # 金额与方向
        amount_label = QLabel(f"¥{self.record_data['amount']:,.2f}")
        if self.record_data["direction"] == "收入":
            amount_label.setProperty("class", "income-amount")
        else:
            amount_label.setProperty("class", "expense-amount")
        
        info_layout.addRow(f"{self.record_data['direction']}金额:", amount_label)
        
        info_layout.addRow("记账日期:", QLabel(self.record_data["record_date"]))
        info_layout.addRow("财年/期间:", QLabel(f"{self.record_data['fiscal_year']}/{self.record_data['fiscal_period']}"))
        
        created_at = datetime.fromisoformat(self.record_data["created_at"].replace('Z', '+00:00'))
        info_layout.addRow("创建时间:", QLabel(created_at.strftime("%Y-%m-%d %H:%M:%S")))
        
        if self.record_data["description"]:
            desc_label = QLabel(self.record_data["description"])
            desc_label.setWordWrap(True)
            info_layout.addRow("描述:", desc_label)
            
        layout.addWidget(info_group)
        
        # 如果有关联的业务事件，显示业务事件信息
        if self.event_data:
            event_group = QGroupBox("关联业务事件")
            event_layout = QFormLayout(event_group)
            
            event_layout.addRow("事件ID:", QLabel(str(self.event_data["id"])))
            event_layout.addRow("事件类型:", QLabel(self.event_data["event_type"]))
            event_layout.addRow("项目名称:", QLabel(self.event_data["project_name"]))
            
            if self.event_data["project_code"]:
                event_layout.addRow("项目编号:", QLabel(self.event_data["project_code"]))
                
            event_layout.addRow("业务日期:", QLabel(self.event_data["event_date"]))
            
            layout.addWidget(event_group)
        
        # 关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout) 
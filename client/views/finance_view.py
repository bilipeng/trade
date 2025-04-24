import sys
import os
import json
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QLineEdit, QDateEdit, QFormLayout, QDialog, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QTabWidget,
                           QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from views.business_view import BusinessEventDetailDialog

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
        self.search_input.textChanged.connect(self.handle_top_search)
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

        # 添加工具栏
        toolbar = QHBoxLayout()

        # 添加刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(refresh_btn)

        # 添加搜索框
        self.records_search_input = QLineEdit()
        self.records_search_input.setPlaceholderText("搜索项目名称...")
        self.records_search_input.textChanged.connect(self.search_records)
        self.records_search_input.setMaximumWidth(200)
        toolbar.addWidget(self.records_search_input)

        # 添加过滤下拉框
        self.records_filter_combo = QComboBox()
        self.records_filter_combo.addItem("全部类型", "")
        self.records_filter_combo.addItem("合同", "合同")
        self.records_filter_combo.addItem("销售", "销售")
        self.records_filter_combo.addItem("采购", "采购")
        self.records_filter_combo.addItem("报销", "报销")
        self.records_filter_combo.currentIndexChanged.connect(self.filter_records)
        toolbar.addWidget(self.records_filter_combo)

        records_layout.addLayout(toolbar)

        # 创建业务事件树形视图
        self.records_tree = QTreeWidget()
        self.records_tree.setHeaderLabels(["业务ID", "项目名称", "事件类型", "总金额", "收入", "支出", "净额", "操作"])
        self.records_tree.setColumnWidth(0, 80)  # 业务ID列宽
        self.records_tree.setColumnWidth(1, 200)  # 项目名称列宽
        self.records_tree.setColumnWidth(2, 100)  # 事件类型列宽
        self.records_tree.setColumnWidth(3, 100)  # 总金额列宽
        self.records_tree.setColumnWidth(4, 100)  # 收入列宽
        self.records_tree.setColumnWidth(5, 100)  # 支出列宽
        self.records_tree.setColumnWidth(6, 100)  # 净额列宽
        self.records_tree.setColumnWidth(7, 150)  # 操作列宽
        self.records_tree.setAlternatingRowColors(True)
        self.records_tree.setIndentation(20)
        self.records_tree.setExpandsOnDoubleClick(True)

        records_layout.addWidget(self.records_tree)

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
                # 保留已审批和执行中的业务事件
                all_events = response.json()
                self.business_events = []

                for event in all_events:
                    if event["status"] in ["已审批", "执行中"]:
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
            create_btn = QPushButton("财务处理")
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
            # 显示加载中状态
            self.records_tree.clear()
            loading_item = QTreeWidgetItem(["加载中...", "", "", "", "", "", "", ""])
            self.records_tree.addTopLevelItem(loading_item)

            # 获取所有财务交易记录
            response = requests.get(
                "http://localhost:8000/financial_transactions",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.data = response.json()

                # 获取所有业务事件
                business_response = requests.get(
                    "http://localhost:8000/business_events",
                    headers={"Authorization": f"Bearer {self.token}"}
                )

                if business_response.status_code == 200:
                    business_events = business_response.json()

                    # 创建业务事件ID到事件数据的映射
                    self.business_map = {event["id"]: event for event in business_events}

                    # 按业务事件分组财务记录
                    self.grouped_data = {}
                    for record in self.data:
                        business_id = record.get("business_event_id")
                        if business_id:
                            if business_id not in self.grouped_data:
                                self.grouped_data[business_id] = []
                            self.grouped_data[business_id].append(record)

                    # 显示分组后的数据
                    self.display_grouped_data(self.grouped_data)
                else:
                    QMessageBox.warning(self, "加载失败", "无法加载业务事件数据")
            else:
                QMessageBox.warning(self, "加载失败", "无法加载财务记录数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据时发生错误: {str(e)}")

    def display_grouped_data(self, grouped_data):
        """显示按业务事件分组的财务记录"""
        # 清空树形视图
        self.records_tree.clear()

        # 如果没有数据，显示提示信息
        if not grouped_data:
            empty_item = QTreeWidgetItem(["暂无财务记录", "", "", "", "", "", "", ""])
            self.records_tree.addTopLevelItem(empty_item)
            return

        # 按业务事件ID排序（降序，最新的在前面）
        sorted_business_ids = sorted(grouped_data.keys(), reverse=True)

        for business_id in sorted_business_ids:
            records = grouped_data[business_id]

            # 获取业务事件信息
            business_event = self.business_map.get(business_id, {})
            project_name = business_event.get("project_name", "未知项目")
            event_type = business_event.get("event_type", "未知类型")

            # 计算财务汇总信息
            total_income = sum(record["amount"] for record in records if record["direction"] == "收入")
            total_expense = sum(record["amount"] for record in records if record["direction"] == "支出")
            net_amount = total_income - total_expense

            # 创建业务事件顶级项
            business_item = QTreeWidgetItem()
            business_item.setText(0, str(business_id))
            business_item.setText(1, project_name)
            business_item.setText(2, event_type)
            business_item.setText(3, f"¥{business_event.get('amount', 0):,.2f}")
            business_item.setText(4, f"¥{total_income:,.2f}")
            business_item.setText(5, f"¥{total_expense:,.2f}")
            business_item.setText(6, f"¥{net_amount:,.2f}")

            # 设置颜色
            if net_amount >= 0:
                business_item.setForeground(6, Qt.GlobalColor.green)
            else:
                business_item.setForeground(6, Qt.GlobalColor.red)

            # 添加操作按钮
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(2, 2, 2, 2)

            # 查看详情按钮
            detail_btn = QPushButton("查看详情")
            detail_btn.clicked.connect(lambda _, b_id=business_id: self.view_business_detail(b_id))
            button_layout.addWidget(detail_btn)

            # 添加财务记录按钮（如果业务事件状态允许）
            if business_event.get("status") in ["已审批", "执行中"]:
                add_record_btn = QPushButton("添加记录")
                add_record_btn.clicked.connect(lambda _, b_id=business_id: self.create_from_business(b_id))
                button_layout.addWidget(add_record_btn)

            # 完成业务按钮（如果业务事件状态为执行中）
            if business_event.get("status") == "执行中":
                complete_btn = QPushButton("完成业务")
                complete_btn.clicked.connect(lambda _, b_id=business_id: self.complete_business(b_id))
                button_layout.addWidget(complete_btn)

            # 设置操作列的自定义部件
            self.records_tree.addTopLevelItem(business_item)
            self.records_tree.setItemWidget(business_item, 7, button_widget)

            # 添加财务记录子项
            for record in records:
                record_item = QTreeWidgetItem(business_item)
                record_item.setText(0, str(record["id"]))
                record_item.setText(1, record.get("description", ""))
                record_item.setText(2, record["account_name"])

                # 金额和方向
                if record["direction"] == "收入":
                    record_item.setText(4, f"¥{record['amount']:,.2f}")
                    record_item.setText(5, "")
                    record_item.setForeground(4, Qt.GlobalColor.green)
                else:
                    record_item.setText(4, "")
                    record_item.setText(5, f"¥{record['amount']:,.2f}")
                    record_item.setForeground(5, Qt.GlobalColor.red)

                record_item.setText(6, "")  # 净额列留空

                # 添加记录操作按钮
                record_button_widget = QWidget()
                record_button_layout = QHBoxLayout(record_button_widget)
                record_button_layout.setContentsMargins(2, 2, 2, 2)

            # 详情按钮
                record_detail_btn = QPushButton("详情")
                record_detail_btn.clicked.connect(lambda _, r_id=record["id"]: self.show_detail(r_id))
                record_button_layout.addWidget(record_detail_btn)

                self.records_tree.setItemWidget(record_item, 7, record_button_widget)

    def search_records(self):
        """搜索财务记录"""
        search_text = self.records_search_input.text().lower()
        filter_type = self.records_filter_combo.currentData()

        # 如果没有搜索文本和过滤条件，显示所有数据
        if not search_text and not filter_type:
            self.display_grouped_data(self.grouped_data)
            return

        # 创建过滤后的分组数据
        filtered_data = {}

        for business_id, records in self.grouped_data.items():
            # 获取业务事件信息
            business_event = self.business_map.get(business_id, {})
            project_name = business_event.get("project_name", "").lower()
            event_type = business_event.get("event_type", "")

            # 应用过滤条件
            type_match = not filter_type or event_type == filter_type
            name_match = not search_text or search_text in project_name

            if type_match and name_match:
                filtered_data[business_id] = records

        # 显示过滤后的数据
        self.display_grouped_data(filtered_data)

    def filter_records(self):
        """按事件类型过滤财务记录"""
        self.search_records()  # 复用搜索方法

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

        # 打开业务事件管理对话框
        dialog = BusinessEventManagerDialog(self.token, self.user_data, business_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.load_business_events()  # 刷新待处理业务

            # 切换到财务记录选项卡
            self.tabs.setCurrentIndex(1)

    def view_business_detail(self, business_id):
        """查看业务事件详情"""
        try:
            # 直接打开业务事件管理对话框
            dialog = BusinessEventManagerDialog(self.token, self.user_data, business_id)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查询详情时发生错误: {str(e)}")

    def show_detail(self, record_id):
        """显示财务记录详情"""
        try:
            # 查找记录
            record_data = None
            for business_id, records in self.grouped_data.items():
                for record in records:
                    if record["id"] == record_id:
                        record_data = record
                        break
                if record_data:
                    break

            if not record_data:
                QMessageBox.warning(self, "查询失败", "无法找到指定的财务记录")
                return

            # 如果有关联的业务事件，获取业务事件详情
            event_data = None
            if "business_event_id" in record_data and record_data["business_event_id"]:
                try:
                    event_response = requests.get(
                        f"http://localhost:8000/business_events/{record_data['business_event_id']}",
                        headers={"Authorization": f"Bearer {self.token}"}
                    )
                    if event_response.status_code == 200:
                        event_data = event_response.json()
                except:
                    pass

            # 使用FinancialTransactionDetailDialog替代FinancialRecordDetailDialog
            dialog = FinancialTransactionDetailDialog(record_data)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查询详情时发生错误: {str(e)}")

    def highlight_record(self, record_id):
        """高亮显示指定的财务记录"""
        # 切换到财务记录选项卡
        if hasattr(self, "tabs"):
            self.tabs.setCurrentIndex(1)  # 切换到财务记录选项卡

        # 刷新数据
        self.load_data()

        # 查找并高亮显示对应的记录
        # 先查找包含这个记录的业务事件
        for business_id, records in self.grouped_data.items():
            for record in records:
                if record["id"] == record_id:
                    # 找到记录所在的业务事件
                    # 查找业务事件项
                    for i in range(self.records_tree.topLevelItemCount()):
                        business_item = self.records_tree.topLevelItem(i)
                        if business_item.text(0) == str(business_id):
                            # 展开业务事件项
                            business_item.setExpanded(True)

                            # 查找记录项
                            for j in range(business_item.childCount()):
                                record_item = business_item.child(j)
                                if record_item.text(0) == str(record_id):
                                    # 选中记录项
                                    self.records_tree.setCurrentItem(record_item)
                                    self.records_tree.scrollToItem(record_item)
                                    
                                    # 显示详情
                                    self.show_detail(record_id)
                                    return

                            # 如果没找到具体记录项，至少选中业务事件项
                            self.records_tree.setCurrentItem(business_item)
                            self.records_tree.scrollToItem(business_item)
                            return

    def complete_business(self, business_id):
        """完成业务事件"""
        try:
            # 获取业务事件详情
            response = requests.get(
                f"http://localhost:8000/business_events/{business_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                business_data = response.json()

                # 确认是否完成业务
                reply = QMessageBox.question(
                    self, "确认操作",
                    f"确定要将业务事件 '{business_data['project_name']}' 标记为已完成吗？完成后将不能再添加财务记录。",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # 调用完成业务API
                    complete_response = requests.post(
                        f"http://localhost:8000/business_events/{business_id}/complete",
                        headers={"Authorization": f"Bearer {self.token}"}
                    )

                    if complete_response.status_code == 200:
                        QMessageBox.information(self, "操作成功", "业务事件已标记为已完成")

                        # 刷新数据
                        self.load_data()

                        # 显示财务汇总对话框
                        records = self.grouped_data.get(business_id, [])
                        summary_dialog = FinancialTransactionSummaryDialog(business_data, records)
                        summary_dialog.exec()
                    else:
                        QMessageBox.warning(self, "操作失败", f"无法完成业务事件: {complete_response.text}")
            else:
                QMessageBox.warning(self, "查询失败", "无法获取业务事件详情")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"完成业务事件时发生错误: {str(e)}")

    def handle_top_search(self):
        """处理顶部搜索框的搜索"""
        # 将顶部搜索框的文本同步到记录搜索框
        if hasattr(self, 'records_search_input'):
            self.records_search_input.setText(self.search_input.text())
            # 如果当前是财务记录选项卡，则自动执行搜索
            if self.tabs.currentIndex() == 1:
                self.search_records()

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

        # 将update_amount_from_event调用移到这里，确保所有UI元素都已创建
        self.update_amount_from_event()

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
        # 检查必要的属性是否已创建
        if not hasattr(self, 'amount_input') or not hasattr(self, 'project_name_label') or not hasattr(self, 'description_input'):
            # 如果属性尚未创建，则直接返回
            return

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
        try:
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
                "transaction_date": self.date_input.date().toString("yyyy-MM-dd"),
                "fiscal_year": self.fiscal_year_input.value(),
                "fiscal_period": self.fiscal_period_input.value(),
                "description": self.description_input.toPlainText(),
                "created_by": self.user_data["id"]
            }

            print(f"准备发送的数据: {data}")  # 调试输出

            # 发送请求
            response = requests.post(
                "http://localhost:8000/financial_transactions",
                json=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )

            print(f"响应状态码: {response.status_code}")  # 调试输出
            print(f"响应内容: {response.text}")  # 调试输出

            if response.status_code == 200:
                result = response.json()
                QMessageBox.information(self, "添加成功", f"财务记录已添加，ID: {result['id']}")

                # 更新业务事件状态为已入账
                try:
                    # 获取关联的审批ID
                    related_response = requests.get(
                        f"http://localhost:8000/business_events/{business_event_id}/related",
                        headers={"Authorization": f"Bearer {self.token}"}
                    )

                    if related_response.status_code == 200:
                        related_data = related_response.json()
                        approvals = related_data.get("approvals", [])

                        if approvals:
                            # 获取最新的审批ID
                            approval_id = approvals[0]["id"]

                            # 更新业务事件状态
                            status_response = requests.post(
                                f"http://localhost:8000/approvals/{approval_id}/update-business-status",
                                json={"status": "已入账", "remarks": "财务记录已创建"},
                                headers={"Authorization": f"Bearer {self.token}"}
                            )
                            print(f"状态更新响应: {status_response.status_code}, {status_response.text}")
                except Exception as e:
                    print(f"获取审批ID或更新状态错误: {str(e)}")
                    # 记录错误，但不影响主流程
                    pass

                # 刷新财务视图数据
                main_window = self.window()
                if main_window and hasattr(main_window, "finance_view") and hasattr(main_window.finance_view, "load_data"):
                    main_window.finance_view.load_data()
                    main_window.finance_view.load_business_events()  # 刷新待处理业务列表

                self.accept()
            else:
                QMessageBox.warning(self, "添加失败", f"无法添加财务记录: {response.text}")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"保存数据时发生错误: {str(e)}")
            print(f"错误详情: {error_details}")
            QMessageBox.warning(self, "错误", f"保存数据时发生错误: {str(e)}")

class FinancialTransactionDialog(QDialog):
    """财务交易记录对话框"""

    def __init__(self, token, user_data, business_id, account_subjects):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.business_id = business_id
        self.account_subjects = account_subjects
        self.business_data = None
        self.init_data()
        self.init_ui()

    def init_data(self):
        """初始化业务事件数据"""
        try:
            response = requests.get(
                f"http://localhost:8000/business_events/{self.business_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.business_data = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载业务事件数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载业务事件数据时发生错误: {str(e)}")

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("添加财务交易记录")
        self.setMinimumWidth(550)

        layout = QVBoxLayout(self)

        # 添加标题
        title_label = QLabel("创建财务交易记录")
        title_label.setProperty("class", "dialog-title")
        layout.addWidget(title_label)

        # 业务信息组
        if self.business_data:
            info_group = QGroupBox("业务信息")
            info_layout = QFormLayout(info_group)

            info_layout.addRow("业务ID:", QLabel(str(self.business_data["id"])))
            info_layout.addRow("项目名称:", QLabel(self.business_data["project_name"]))
            info_layout.addRow("事件类型:", QLabel(self.business_data["event_type"]))
            info_layout.addRow("总金额:", QLabel(f"¥{self.business_data['amount']:,.2f}"))

            layout.addWidget(info_group)

        # 交易记录信息
        form_layout = QFormLayout()

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
        form_layout.addRow("交易日期:", self.date_input)

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

    def save_data(self):
        """保存数据"""
        try:
            # 验证输入
            account_code = self.account_code_input.text()
            if not account_code:
                QMessageBox.warning(self, "输入错误", "请选择会计科目")
                return

            amount = self.amount_input.value()
            if amount <= 0:
                QMessageBox.warning(self, "输入错误", "请输入有效金额")
                return

            # 构建数据
            data = {
                "business_event_id": self.business_id,
                "account_code": account_code,
                "account_name": self.account_name_input.text(),
                "amount": amount,
                "direction": self.direction_combo.currentData(),
                "transaction_date": self.date_input.date().toString("yyyy-MM-dd"),
                "fiscal_year": self.fiscal_year_input.value(),
                "fiscal_period": self.fiscal_period_input.value(),
                "description": self.description_input.toPlainText(),
                "created_by": self.user_data["id"]
            }

            # 发送请求
            response = requests.post(
                "http://localhost:8000/financial_transactions",
                json=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                result = response.json()
                QMessageBox.information(self, "添加成功", f"财务交易记录已添加，ID: {result['id']}")
                self.accept()
            else:
                QMessageBox.warning(self, "添加失败", f"无法添加财务交易记录: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存数据时发生错误: {str(e)}")

class BusinessEventManagerDialog(QDialog):
    """业务事件管理对话框"""

    def __init__(self, token, user_data, business_id):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.business_id = business_id
        self.business_data = None
        self.transactions = []
        self.departments = []
        self.account_subjects = []
        self.setWindowTitle("业务事件财务管理")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.load_data()

    def load_data(self):
        """加载业务事件数据和交易记录"""
        try:
            # 加载业务事件详情
            response = requests.get(
                f"http://localhost:8000/business_events/{self.business_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.business_data = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载业务事件数据")
                self.reject()
                return

            # 加载部门数据
            departments_response = requests.get(
                "http://localhost:8000/departments",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if departments_response.status_code == 200:
                self.departments = departments_response.json()

            # 加载会计科目
            subjects_response = requests.get(
                "http://localhost:8000/account_subjects",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if subjects_response.status_code == 200:
                self.account_subjects = subjects_response.json()

            # 加载财务交易记录
            transactions_response = requests.get(
                f"http://localhost:8000/business_events/{self.business_id}/financial_transactions",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if transactions_response.status_code == 200:
                self.transactions = transactions_response.json()

            self.init_ui()

        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据时发生错误: {str(e)}")
            self.reject()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 创建选项卡
        tabs = QTabWidget()

        # 业务详情选项卡
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)

        # 业务信息组
        info_group = QGroupBox("业务基本信息")
        info_layout = QFormLayout(info_group)

        info_layout.addRow("业务ID:", QLabel(str(self.business_data["id"])))

        if "project_code" in self.business_data and self.business_data["project_code"]:
            info_layout.addRow("项目编号:", QLabel(self.business_data["project_code"]))

        info_layout.addRow("事件类型:", QLabel(self.business_data["event_type"]))
        info_layout.addRow("项目名称:", QLabel(self.business_data["project_name"]))

        # 创建突出显示的金额标签
        amount_label = QLabel(f"¥{self.business_data['amount']:,.2f}")
        amount_label.setProperty("class", "amount-label")
        info_layout.addRow("总金额:", amount_label)

        info_layout.addRow("业务日期:", QLabel(self.business_data["event_date"]))

        # 获取部门名称
        department_name = "未知"
        for dept in self.departments:
            if dept["id"] == self.business_data["department_id"]:
                department_name = dept["name"]
                break

        info_layout.addRow("所属部门:", QLabel(department_name))

        status_label = QLabel(self.business_data["status"])
        status_label.setProperty("class", "status-" + self.business_data["status"])
        info_layout.addRow("当前状态:", status_label)

        if "description" in self.business_data and self.business_data["description"]:
            desc_text = QTextEdit()
            desc_text.setPlainText(self.business_data["description"])
            desc_text.setReadOnly(True)
            desc_text.setMaximumHeight(80)
            info_layout.addRow("描述:", desc_text)

        details_layout.addWidget(info_group)

        # 财务交易记录选项卡
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)

        # 添加工具栏
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("财务交易记录"))
        toolbar.addStretch()

        # 添加财务交易按钮
        add_transaction_btn = QPushButton("添加财务交易")
        add_transaction_btn.clicked.connect(self.add_transaction)
        toolbar.addWidget(add_transaction_btn)

        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_transactions)
        toolbar.addWidget(refresh_btn)

        # 完成业务按钮（仅在执行中状态显示）
        if self.business_data["status"] == "执行中":
            complete_btn = QPushButton("完成业务")
            complete_btn.setProperty("class", "primary")
            complete_btn.clicked.connect(self.complete_business)
            toolbar.addWidget(complete_btn)

        transactions_layout.addLayout(toolbar)

        # 财务交易表格
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels(["ID", "科目", "金额", "方向", "交易日期", "财年/期间", "操作"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        transactions_layout.addWidget(self.transactions_table)

        # 显示交易记录
        self.display_transactions()

        # 添加选项卡
        tabs.addTab(details_tab, "业务详情")
        tabs.addTab(transactions_tab, "财务交易记录")

        layout.addWidget(tabs)

        # 关闭按钮
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def display_transactions(self):
        """显示财务交易记录"""
        self.transactions_table.setRowCount(0)

        for row, item in enumerate(self.transactions):
            self.transactions_table.insertRow(row)

            # 设置各列数据
            self.transactions_table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(f"{item['account_name']} ({item['account_code']})"))

            # 金额列
            amount_item = QTableWidgetItem(f"¥{item['amount']:,.2f}")
            self.transactions_table.setItem(row, 2, amount_item)

            # 方向
            direction_item = QTableWidgetItem(item["direction"])
            if item["direction"] == "收入":
                direction_item.setForeground(Qt.GlobalColor.green)
            else:
                direction_item.setForeground(Qt.GlobalColor.red)
            self.transactions_table.setItem(row, 3, direction_item)

            # 交易日期
            self.transactions_table.setItem(row, 4, QTableWidgetItem(item["transaction_date"]))

            # 财年/期间
            self.transactions_table.setItem(row, 5, QTableWidgetItem(f"{item['fiscal_year']}/{item['fiscal_period']}"))

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            # 详情按钮
            detail_btn = QPushButton("详情")
            detail_btn.clicked.connect(lambda _, t_id=item["id"]: self.show_transaction_detail(t_id))
            btn_layout.addWidget(detail_btn)

            self.transactions_table.setCellWidget(row, 6, btn_widget)

    def add_transaction(self):
        """添加财务交易记录"""
        dialog = FinancialTransactionDialog(
            self.token,
            self.user_data,
            self.business_id,
            self.account_subjects
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_transactions()
            # 刷新业务事件数据
            self.load_data()

    def refresh_transactions(self):
        """刷新财务交易记录"""
        try:
            response = requests.get(
                f"http://localhost:8000/business_events/{self.business_id}/financial_transactions",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.transactions = response.json()
                self.display_transactions()

                # 刷新业务事件状态
                event_response = requests.get(
                    f"http://localhost:8000/business_events/{self.business_id}",
                    headers={"Authorization": f"Bearer {self.token}"}
                )

                if event_response.status_code == 200:
                    self.business_data = event_response.json()
                    # 如果状态改变，重新加载UI
                    self.init_ui()
            else:
                QMessageBox.warning(self, "刷新失败", "无法刷新财务交易记录")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"刷新交易记录时发生错误: {str(e)}")

    def show_transaction_detail(self, transaction_id):
        """显示财务交易详情"""
        # 查找交易记录
        transaction = None
        for item in self.transactions:
            if item["id"] == transaction_id:
                transaction = item
                break

        if not transaction:
            QMessageBox.warning(self, "查询失败", "找不到指定的交易记录")
            return

        # 显示详情对话框
        dialog = FinancialTransactionDetailDialog(transaction)
        dialog.exec()

    def complete_business(self):
        """完成业务事件"""
        # 检查是否有交易记录
        if not self.transactions:
            QMessageBox.warning(self, "操作失败", "业务事件至少需要一条财务交易记录才能标记为已完成")
            return

        reply = QMessageBox.question(
            self, "确认操作",
            "确定要将此业务事件标记为已完成吗？完成后将不能再添加财务交易记录。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.post(
                    f"http://localhost:8000/business_events/{self.business_id}/complete",
                    headers={"Authorization": f"Bearer {self.token}"}
                )

                if response.status_code == 200:
                    QMessageBox.information(self, "操作成功", "业务事件已标记为已完成")

                    # 刷新交易记录和业务数据
                    self.refresh_transactions()

                    # 显示财务交易汇总对话框
                    summary_dialog = FinancialTransactionSummaryDialog(self.business_data, self.transactions)
                    summary_dialog.exec()

                    # 关闭当前对话框
                    self.accept()
                else:
                    QMessageBox.warning(self, "操作失败", f"无法完成业务事件: {response.text}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"完成业务事件时发生错误: {str(e)}")

class FinancialTransactionDetailDialog(QDialog):
    """财务交易记录详情对话框"""

    def __init__(self, transaction_data):
        super().__init__()
        self.transaction_data = transaction_data
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("财务交易记录详情")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # 创建基本信息组
        info_group = QGroupBox("交易记录信息")
        info_layout = QFormLayout(info_group)

        info_layout.addRow("交易ID:", QLabel(str(self.transaction_data["id"])))
        info_layout.addRow("会计科目:", QLabel(f"{self.transaction_data['account_name']} ({self.transaction_data['account_code']})"))

        # 金额与方向
        amount_label = QLabel(f"¥{self.transaction_data['amount']:,.2f}")
        if self.transaction_data["direction"] == "收入":
            amount_label.setProperty("class", "income-amount")
        else:
            amount_label.setProperty("class", "expense-amount")

        info_layout.addRow(f"{self.transaction_data['direction']}金额:", amount_label)

        info_layout.addRow("交易日期:", QLabel(self.transaction_data["transaction_date"]))
        info_layout.addRow("财年/期间:", QLabel(f"{self.transaction_data['fiscal_year']}/{self.transaction_data['fiscal_period']}"))

        if "transaction_type" in self.transaction_data:
            info_layout.addRow("交易类型:", QLabel(self.transaction_data["transaction_type"]))

        if "payment_method" in self.transaction_data:
            info_layout.addRow("支付方式:", QLabel(self.transaction_data["payment_method"]))

        created_at = datetime.fromisoformat(self.transaction_data["created_at"].replace('Z', '+00:00'))
        info_layout.addRow("创建时间:", QLabel(created_at.strftime("%Y-%m-%d %H:%M:%S")))

        if self.transaction_data.get("description"):
            desc_label = QLabel(self.transaction_data["description"])
            desc_label.setWordWrap(True)
            info_layout.addRow("描述:", desc_label)

        layout.addWidget(info_group)

        # 如果有附加信息，显示附加信息
        if "additional_info" in self.transaction_data and self.transaction_data["additional_info"]:
            additional_group = QGroupBox("附加信息")
            additional_layout = QFormLayout(additional_group)

            for key, value in self.transaction_data["additional_info"].items():
                if value:  # 只显示非空值
                    label = QLabel(str(value))
                    label.setWordWrap(True)
                    additional_layout.addRow(f"{key}:", label)

            layout.addWidget(additional_group)

        # 关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

class FinancialTransactionSummaryDialog(QDialog):
    """财务交易汇总对话框"""

    def __init__(self, business_data, transactions):
        super().__init__()
        self.business_data = business_data
        self.transactions = transactions
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("财务交易汇总")
        self.setMinimumWidth(600)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("业务事件财务交易汇总")
        title_label.setProperty("class", "dialog-title")
        layout.addWidget(title_label)

        # 业务信息组
        info_group = QGroupBox("业务信息")
        info_layout = QFormLayout(info_group)

        info_layout.addRow("业务ID:", QLabel(str(self.business_data["id"])))
        info_layout.addRow("项目名称:", QLabel(self.business_data["project_name"]))
        info_layout.addRow("事件类型:", QLabel(self.business_data["event_type"]))

        # 创建突出显示的金额标签
        amount_label = QLabel(f"¥{self.business_data['amount']:,.2f}")
        amount_label.setProperty("class", "amount-label")
        info_layout.addRow("总金额:", amount_label)

        layout.addWidget(info_group)

        # 交易汇总组
        summary_group = QGroupBox("交易汇总")
        summary_layout = QVBoxLayout(summary_group)

        # 计算汇总数据
        total_income = sum(t["amount"] for t in self.transactions if t["direction"] == "收入")
        total_expense = sum(t["amount"] for t in self.transactions if t["direction"] == "支出")
        net_amount = total_income - total_expense

        # 创建汇总表格
        summary_table = QTableWidget()
        summary_table.setColumnCount(2)
        summary_table.setRowCount(3)
        summary_table.setHorizontalHeaderLabels(["项目", "金额"])
        summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 设置表格数据
        summary_table.setItem(0, 0, QTableWidgetItem("总收入"))
        income_item = QTableWidgetItem(f"¥{total_income:,.2f}")
        income_item.setForeground(Qt.GlobalColor.green)
        summary_table.setItem(0, 1, income_item)

        summary_table.setItem(1, 0, QTableWidgetItem("总支出"))
        expense_item = QTableWidgetItem(f"¥{total_expense:,.2f}")
        expense_item.setForeground(Qt.GlobalColor.red)
        summary_table.setItem(1, 1, expense_item)

        summary_table.setItem(2, 0, QTableWidgetItem("净额"))
        net_item = QTableWidgetItem(f"¥{net_amount:,.2f}")
        if net_amount >= 0:
            net_item.setForeground(Qt.GlobalColor.green)
        else:
            net_item.setForeground(Qt.GlobalColor.red)
        summary_table.setItem(2, 1, net_item)

        summary_layout.addWidget(summary_table)

        layout.addWidget(summary_group)

        # 交易明细组
        details_group = QGroupBox("交易明细")
        details_layout = QVBoxLayout(details_group)

        # 创建交易明细表格
        details_table = QTableWidget()
        details_table.setColumnCount(5)
        details_table.setHorizontalHeaderLabels(["ID", "科目", "金额", "方向", "交易日期"])
        details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        details_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 设置表格数据
        details_table.setRowCount(len(self.transactions))
        for row, item in enumerate(self.transactions):
            details_table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            details_table.setItem(row, 1, QTableWidgetItem(f"{item['account_name']} ({item['account_code']})"))

            # 金额列
            amount_item = QTableWidgetItem(f"¥{item['amount']:,.2f}")
            details_table.setItem(row, 2, amount_item)

            # 方向
            direction_item = QTableWidgetItem(item["direction"])
            if item["direction"] == "收入":
                direction_item.setForeground(Qt.GlobalColor.green)
            else:
                direction_item.setForeground(Qt.GlobalColor.red)
            details_table.setItem(row, 3, direction_item)

            # 交易日期
            details_table.setItem(row, 4, QTableWidgetItem(item["transaction_date"]))

        details_layout.addWidget(details_table)

        layout.addWidget(details_group)

        # 关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
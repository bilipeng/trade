import sys
import os
import json
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QLineEdit, QDateEdit, QFormLayout, QDialog, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QDate

class BusinessEventView(QWidget):
    """业务事件管理视图"""

    def __init__(self, token, user_data):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.departments = []
        self.init_ui()
        self.load_departments()
        self.load_data()

    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 标题与工具栏
        top_layout = QHBoxLayout()
        title_label = QLabel("业务事件管理")
        title_label.setProperty("class", "view-title")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索项目名称...")
        self.search_input.textChanged.connect(self.search_data)
        self.search_input.setMaximumWidth(200)
        top_layout.addWidget(self.search_input)

        # 过滤下拉框
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("全部状态", "")
        self.filter_combo.addItem("新建", "新建")
        self.filter_combo.addItem("待审批", "待审批")
        self.filter_combo.addItem("审批中", "审批中")
        self.filter_combo.addItem("已审批", "已审批")
        self.filter_combo.addItem("已入账", "已入账")
        self.filter_combo.addItem("已完成", "已完成")
        self.filter_combo.addItem("已拒绝", "已拒绝")
        self.filter_combo.currentIndexChanged.connect(self.filter_data)
        top_layout.addWidget(self.filter_combo)

        # 新建按钮
        self.add_button = QPushButton("新建业务事件")
        self.add_button.clicked.connect(self.show_add_dialog)
        top_layout.addWidget(self.add_button)

        main_layout.addLayout(top_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # 增加了2列：审批ID和财务ID
        self.table.setHorizontalHeaderLabels(["ID", "事件类型", "项目名称", "金额", "日期", "状态", "审批ID", "财务ID", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

    def load_departments(self):
        """加载部门数据"""
        try:
            response = requests.get(
                "http://localhost:8000/departments",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.departments = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载部门数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载部门数据时发生错误: {str(e)}")

    def load_data(self):
        """加载业务事件数据"""
        try:
            response = requests.get(
                "http://localhost:8000/business_events",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.data = response.json()
                self.display_data(self.data)
            else:
                QMessageBox.warning(self, "加载失败", "无法加载业务事件数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据时发生错误: {str(e)}")

    def display_data(self, data):
        """显示数据到表格"""
        self.table.setRowCount(0)

        for row, item in enumerate(data):
            self.table.insertRow(row)

            # 设置各列数据
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["event_type"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["project_name"]))
            self.table.setItem(row, 3, QTableWidgetItem(f"¥{item['amount']:,.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(item["event_date"]))

            # 状态单元格 - 优化状态显示
            status_label = QLabel(item["status"])
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 根据状态设置样式类
            if item["status"] == "新建":
                status_label.setProperty("class", "status-new")
            elif item["status"] == "待审批":
                status_label.setProperty("class", "status-pending")
            elif item["status"] == "审批中":
                status_label.setProperty("class", "status-processing")
            elif item["status"] == "已审批":
                status_label.setProperty("class", "status-approved")
            elif item["status"] == "已入账":
                status_label.setProperty("class", "status-recorded")
            elif item["status"] == "已完成":
                status_label.setProperty("class", "status-completed")
            elif item["status"] == "已拒绝":
                status_label.setProperty("class", "status-rejected")

            # 将状态标签添加到单元格中
            status_cell = QWidget()
            status_layout = QHBoxLayout(status_cell)
            status_layout.setContentsMargins(2, 2, 2, 2)
            status_layout.addWidget(status_label)
            self.table.setCellWidget(row, 5, status_cell)

            # 添加审批ID列
            approval_btn = QPushButton("查看") if "approval_id" in item and item["approval_id"] else QTableWidgetItem("-")
            if isinstance(approval_btn, QPushButton):
                approval_btn.setProperty("class", "link-button")
                approval_btn.clicked.connect(lambda _, a_id=item["approval_id"]: self.view_approval(a_id))
                approval_cell = QWidget()
                approval_layout = QHBoxLayout(approval_cell)
                approval_layout.setContentsMargins(2, 2, 2, 2)
                approval_layout.addWidget(approval_btn)
                self.table.setCellWidget(row, 6, approval_cell)
            else:
                self.table.setItem(row, 6, approval_btn)

            # 添加财务ID列
            finance_btn = QPushButton("查看") if "finance_id" in item and item["finance_id"] else QTableWidgetItem("-")
            if isinstance(finance_btn, QPushButton):
                finance_btn.setProperty("class", "link-button")
                finance_btn.clicked.connect(lambda _, f_id=item["finance_id"]: self.view_finance(f_id))
                finance_cell = QWidget()
                finance_layout = QHBoxLayout(finance_cell)
                finance_layout.setContentsMargins(2, 2, 2, 2)
                finance_layout.addWidget(finance_btn)
                self.table.setCellWidget(row, 7, finance_cell)
            else:
                self.table.setItem(row, 7, finance_btn)

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            # 详情按钮
            detail_btn = QPushButton("详情")
            detail_btn.setMaximumWidth(50)
            detail_btn.clicked.connect(lambda _, item_id=item["id"]: self.show_detail(item_id))
            btn_layout.addWidget(detail_btn)

            # 如果状态是"已审批"且没有关联财务记录，添加"创建财务记录"按钮
            if item["status"] == "已审批" and not ("finance_id" in item and item["finance_id"]):
                create_finance_btn = QPushButton("创建财务记录")
                create_finance_btn.setProperty("class", "primary")
                create_finance_btn.clicked.connect(lambda _, b_id=item["id"]: self.create_finance_record(b_id))
                btn_layout.addWidget(create_finance_btn)

            # 如果状态是"新建"或"待审批"，添加"提交审批"按钮
            if item["status"] in ["新建", "待审批"]:
                submit_btn = QPushButton("提交审批")
                submit_btn.setProperty("class", "secondary")
                submit_btn.clicked.connect(lambda _, b_id=item["id"]: self.submit_to_approval(b_id))
                btn_layout.addWidget(submit_btn)

            self.table.setCellWidget(row, 8, btn_widget)

    def search_data(self):
        """搜索数据"""
        search_text = self.search_input.text().lower()
        status_filter = self.filter_combo.currentData()

        filtered_data = []
        for item in self.data:
            project_name_match = search_text in item["project_name"].lower()
            status_match = not status_filter or item["status"] == status_filter

            if project_name_match and status_match:
                filtered_data.append(item)

        self.display_data(filtered_data)

    def filter_data(self):
        """按状态过滤数据"""
        self.search_data()

    def show_add_dialog(self):
        """显示添加业务事件对话框"""
        dialog = BusinessEventDialog(self.token, self.user_data, self.departments)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def show_detail(self, item_id):
        """显示业务事件详情"""
        try:
            response = requests.get(
                f"http://localhost:8000/business_events/{item_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                event_data = response.json()
                dialog = BusinessEventDetailDialog(event_data, self.departments)
                dialog.exec()
            else:
                QMessageBox.warning(self, "查询失败", "无法获取业务事件详情")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查询详情时发生错误: {str(e)}")

    def view_approval(self, approval_id):
        """查看关联的审批记录"""
        try:
            # 获取审批记录详情
            response = requests.get(
                f"http://localhost:8000/approvals/{approval_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                approval_data = response.json()

                # 找到主窗口
                main_window = self.window()
                if main_window and hasattr(main_window, "content_tabs") and hasattr(main_window, "approval_view"):
                    # 切换到审批管理选项卡
                    main_window.switch_to_approval_view(approval_id)
                else:
                    QMessageBox.information(self, "提示", "请手动切换到审批管理界面查看详情")
            else:
                QMessageBox.warning(self, "查询失败", f"无法获取审批记录: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查看审批记录时发生错误: {str(e)}")

    def view_finance(self, finance_id):
        """查看关联的财务记录"""
        try:
            # 获取财务记录详情
            response = requests.get(
                f"http://localhost:8000/financial_records/{finance_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                finance_data = response.json()

                # 找到主窗口
                main_window = self.window()
                if main_window and hasattr(main_window, "content_tabs") and hasattr(main_window, "finance_view"):
                    # 切换到财务管理选项卡
                    main_window.switch_to_finance_view()

                    # 高亮显示对应的财务记录
                    main_window.finance_view.highlight_record(finance_id)
                else:
                    QMessageBox.information(self, "提示", "请手动切换到财务管理界面查看详情")
            else:
                QMessageBox.warning(self, "查询失败", f"无法获取财务记录: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查看财务记录时发生错误: {str(e)}")

    def create_finance_record(self, business_id):
        """为已审批的业务事件创建财务记录"""
        try:
            # 获取业务事件详情
            response = requests.get(
                f"http://localhost:8000/business_events/{business_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                event_data = response.json()

                # 找到主窗口
                main_window = self.window()
                if main_window and hasattr(main_window, "content_tabs") and hasattr(main_window, "finance_view"):
                    # 切换到财务管理选项卡
                    main_window.switch_to_finance_view()

                    # 调用财务视图的创建记录方法，传入业务事件数据
                    main_window.finance_view.create_from_business(business_id)
                else:
                    QMessageBox.information(self, "提示", "请手动切换到财务管理界面创建财务记录")
            else:
                QMessageBox.warning(self, "查询失败", f"无法获取业务事件详情: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"创建财务记录时发生错误: {str(e)}")

    def submit_to_approval(self, business_id):
        """提交业务事件至审批流程"""
        try:
            print(f"提交业务事件 {business_id} 到审批流程")

            # 调用新API将业务事件提交到审批流程
            response = requests.post(
                f"http://localhost:8000/business_events/{business_id}/submit-to-approval",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                # 自动刷新当前视图数据
                self.load_data()

                reply = QMessageBox.question(
                    self, "提交成功",
                    "业务事件已成功提交到审批流程，是否立即跳转到审批管理界面？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # 发出信号，让主窗口切换到审批管理界面
                    # 此处需要根据具体的信号实现调整
                    # 如果您的BusinessEventView类中没有定义信号，可以通过其他方式实现界面切换
                    # 例如，可以通过主窗口提供的方法进行切换
                    main_window = self.window()
                    if main_window and hasattr(main_window, "switch_to_approval_view"):
                        main_window.switch_to_approval_view(None)  # 切换到审批管理界面
                        # 刷新审批视图数据
                        if hasattr(main_window.approval_view, "load_data"):
                            main_window.approval_view.load_data()
                    else:
                        QMessageBox.information(self, "提示", "请手动切换到审批管理界面并刷新数据")
            else:
                QMessageBox.warning(self, "提交失败", f"提交到审批流程失败: {response.text}")
        except Exception as e:
            print(f"提交过程中发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"提交过程中发生错误: {str(e)}")

class BusinessEventDialog(QDialog):
    """业务事件添加对话框"""

    def __init__(self, token, user_data, departments):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.departments = departments
        self.customers = []  # 添加客户列表
        self.init_ui()
        self.load_customers()  # 加载客户数据

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("添加业务事件")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # 表单布局
        form_layout = QFormLayout()

        # 事件类型
        self.event_type_combo = QComboBox()
        self.event_type_combo.addItems(["合同", "销售", "采购", "报销"])
        form_layout.addRow("事件类型:", self.event_type_combo)

        # 客户下拉菜单
        self.customer_combo = QComboBox()
        self.customer_combo.addItem("-- 请选择客户 --", None)  # 添加默认选项
        self.customer_combo.currentIndexChanged.connect(self.on_customer_changed)
        form_layout.addRow("客户:", self.customer_combo)

        # 项目名称
        self.project_name_input = QLineEdit()
        form_layout.addRow("项目名称:", self.project_name_input)

        # 金额
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setSingleStep(100)
        self.amount_input.setSuffix(" 元")
        form_layout.addRow("金额:", self.amount_input)

        # 日期
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("日期:", self.date_input)

        # 部门
        self.department_combo = QComboBox()
        for dept in self.departments:
            self.department_combo.addItem(dept["name"], dept["id"])
        form_layout.addRow("所属部门:", self.department_combo)

        # 描述
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("描述:", self.description_input)

        layout.addLayout(form_layout)

        # 加载数据
        self.load_customers()  # 加载客户数据

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_data)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def load_customers(self):
        """加载客户数据"""
        try:
            response = requests.get(
                "http://localhost:8000/customers",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.customers = response.json()
                # 清空下拉菜单（保留默认选项）
                while self.customer_combo.count() > 1:
                    self.customer_combo.removeItem(1)
                # 添加客户到下拉菜单
                for customer in self.customers:
                    self.customer_combo.addItem(customer["name"], customer["id"])

                # 添加"添加新客户"选项
                self.customer_combo.addItem("+ 添加新客户", "add_new")
            else:
                QMessageBox.warning(self, "加载失败", "无法加载客户数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载客户数据时发生错误: {str(e)}")

    def on_customer_changed(self):
        """处理客户选择变更"""
        selected_data = self.customer_combo.currentData()

        if selected_data == "add_new":
            # 打开添加新客户对话框
            dialog = CustomerDialog(self.token)
            if dialog.exec() == QDialog.DialogCode.Accepted and dialog.customer_id:
                # 重新加载客户列表
                self.load_customers()

                # 选中新添加的客户
                for i in range(self.customer_combo.count()):
                    if self.customer_combo.itemData(i) == dialog.customer_id:
                        self.customer_combo.setCurrentIndex(i)
                        break
            else:
                # 如果用户取消，恢复到默认选项
                self.customer_combo.setCurrentIndex(0)

    def save_data(self):
        """保存数据"""
        # 输入验证
        if not self.project_name_input.text():
            QMessageBox.warning(self, "输入错误", "请输入项目名称")
            return

        # 构造请求数据
        data = {
            "event_type": self.event_type_combo.currentText(),
            "project_name": self.project_name_input.text(),
            "amount": self.amount_input.value(),
            "event_date": self.date_input.date().toString("yyyy-MM-dd"),
            "department_id": self.department_combo.currentData(),
            "created_by": self.user_data["id"],
            "description": self.description_input.toPlainText()
        }

        # 如果选择了客户，添加客户ID
        customer_id = self.customer_combo.currentData()
        if customer_id:
            data["customer_id"] = customer_id

        print("准备发送的数据:", data)

        try:
            response = requests.post(
                "http://localhost:8000/business_events",
                json=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )

            # 添加调试代码，输出API响应
            print("API响应状态码:", response.status_code)
            print("API响应内容:", response.text)

            if response.status_code == 200:
                try:
                    result = response.json()
                    print("解析后的结果:", result)  # 添加解析后的结果输出

                    # 检查返回的所有字段
                    for key, value in result.items():
                        print(f"返回字段: {key} = {value}")

                    # 提取事务编号
                    if "transaction_code" in result:
                        transaction_code = result["transaction_code"]
                    else:
                        transaction_code = "未生成 (字段不存在)"
                        print("警告: 响应中没有transaction_code字段")

                    QMessageBox.information(self, "成功", f"业务事件创建成功\n事务编号: {transaction_code}")
                    self.accept()
                except Exception as json_error:
                    print(f"JSON解析错误: {str(json_error)}")
                    QMessageBox.warning(self, "数据错误", f"解析返回数据时出错: {str(json_error)}")
            else:
                QMessageBox.warning(self, "失败", f"业务事件创建失败: {response.text}")
        except Exception as e:
            print(f"请求错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"创建业务事件时发生错误: {str(e)}")

class BusinessEventDetailDialog(QDialog):
    """业务事件详情对话框"""

    def __init__(self, event_data, departments):
        super().__init__()
        self.event_data = event_data
        self.departments = departments
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("业务事件详情")
        self.setMinimumWidth(600)

        layout = QVBoxLayout(self)

        # 添加流程进度指示器
        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout(progress_group)

        # 流程步骤标签
        steps_layout = QHBoxLayout()
        steps = ["业务创建", "审批处理", "财务处理", "完成"]
        step_labels = []

        for step in steps:
            label = QLabel(step)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            steps_layout.addWidget(label)
            step_labels.append(label)

        progress_layout.addLayout(steps_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        # 设置当前进度
        current_progress = 0
        if self.event_data["status"] == "新建":
            current_progress = 25
            step_labels[0].setStyleSheet("font-weight: bold; color: #1976D2;")
        elif self.event_data["status"] in ["待审批", "审批中"]:
            current_progress = 50
            step_labels[1].setStyleSheet("font-weight: bold; color: #1976D2;")
        elif self.event_data["status"] == "已审批":
            current_progress = 75
            step_labels[2].setStyleSheet("font-weight: bold; color: #1976D2;")
        elif self.event_data["status"] in ["已入账", "已完成"]:
            current_progress = 100
            step_labels[3].setStyleSheet("font-weight: bold; color: #1976D2;")

        self.progress_bar.setValue(current_progress)

        # 如果审批被拒绝，设置特殊样式
        if self.event_data["status"] == "已拒绝":
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #E53935; }")
            step_labels[1].setStyleSheet("font-weight: bold; color: #E53935;")

        layout.addWidget(progress_group)

        # 基本信息
        info_group = QGroupBox("基本信息")
        form_layout = QFormLayout(info_group)

        # 显示各项信息
        form_layout.addRow("事件ID:", QLabel(str(self.event_data["id"])))

        # 显示事务编号（即 project_code）
        if "project_code" in self.event_data and self.event_data["project_code"]:
            form_layout.addRow("事务编号:", QLabel(self.event_data["project_code"]))

        form_layout.addRow("事件类型:", QLabel(self.event_data["event_type"]))
        form_layout.addRow("项目名称:", QLabel(self.event_data["project_name"]))
        form_layout.addRow("金额:", QLabel(f"¥{self.event_data['amount']:,.2f}"))
        form_layout.addRow("业务日期:", QLabel(self.event_data["event_date"]))

        # 查找部门名称
        department_name = "未知部门"
        for dept in self.departments:
            if dept["id"] == self.event_data["department_id"]:
                department_name = dept["name"]
                break

        form_layout.addRow("所属部门:", QLabel(department_name))
        form_layout.addRow("当前状态:", QLabel(self.event_data["status"]))

        if "description" in self.event_data and self.event_data["description"]:
            desc_label = QLabel(self.event_data["description"])
            desc_label.setWordWrap(True)
            form_layout.addRow("描述:", desc_label)

        # 相关信息
        if "created_at" in self.event_data:
            created_at = datetime.fromisoformat(self.event_data["created_at"].replace('Z', '+00:00'))
            form_layout.addRow("创建时间:", QLabel(created_at.strftime("%Y-%m-%d %H:%M:%S")))

        layout.addWidget(info_group)

        # 关联信息
        related_group = QGroupBox("关联信息")
        related_layout = QFormLayout(related_group)

        # 审批信息
        if "approval_id" in self.event_data and self.event_data["approval_id"]:
            approval_info = QLabel(f"审批ID: {self.event_data['approval_id']}")
            related_layout.addRow("审批信息:", approval_info)
        else:
            related_layout.addRow("审批信息:", QLabel("暂无关联审批信息"))

        # 财务信息
        if "finance_id" in self.event_data and self.event_data["finance_id"]:
            finance_info = QLabel(f"财务记录ID: {self.event_data['finance_id']}")
            related_layout.addRow("财务信息:", finance_info)
        else:
            related_layout.addRow("财务信息:", QLabel("暂无关联财务信息"))

        layout.addWidget(related_group)

        # 状态历史
        if "status_history" in self.event_data and self.event_data["status_history"]:
            history_group = QGroupBox("状态变更历史")
            history_layout = QVBoxLayout(history_group)

            history_table = QTableWidget()
            history_table.setColumnCount(4)
            history_table.setHorizontalHeaderLabels(["时间", "状态", "操作人", "备注"])
            history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            history_records = self.event_data["status_history"]
            history_table.setRowCount(len(history_records))

            for row, record in enumerate(history_records):
                history_table.setItem(row, 0, QTableWidgetItem(record["timestamp"]))
                history_table.setItem(row, 1, QTableWidgetItem(record["status"]))
                history_table.setItem(row, 2, QTableWidgetItem(record["operator"]))
                history_table.setItem(row, 3, QTableWidgetItem(record.get("remarks", "")))

            history_layout.addWidget(history_table)
            layout.addWidget(history_group)

        # 按钮
        button_layout = QHBoxLayout()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

class CustomerDialog(QDialog):
    """客户添加对话框"""

    def __init__(self, token):
        super().__init__()
        self.token = token
        self.customer_id = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("添加新客户")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # 表单布局
        form_layout = QFormLayout()

        # 客户名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入客户名称")
        form_layout.addRow("客户名称:", self.name_input)

        # 联系人
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("请输入联系人姓名")
        form_layout.addRow("联系人:", self.contact_input)

        # 电话
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入联系电话")
        form_layout.addRow("联系电话:", self.phone_input)

        # 地址
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("请输入地址")
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("地址:", self.address_input)

        # 备注
        self.remarks_input = QTextEdit()
        self.remarks_input.setPlaceholderText("请输入备注信息")
        self.remarks_input.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remarks_input)

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

    def save_data(self):
        """保存数据"""
        # 验证输入
        if not self.name_input.text():
            QMessageBox.warning(self, "输入错误", "请输入客户名称")
            return

        # 构建数据
        data = {
            "name": self.name_input.text(),
            "code": None,  # 客户编码可以为空
            "contact_person": self.contact_input.text(),
            "contact_phone": self.phone_input.text(),
            "contact_email": "",  # 联系邮箱为空
            "address": self.address_input.toPlainText(),
            "email": self.remarks_input.toPlainText()  # 将备注字段作为email
        }

        try:
            # 发送请求
            response = requests.post(
                "http://localhost:8000/customers",
                json=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                result = response.json()
                self.customer_id = result["id"]
                QMessageBox.information(self, "添加成功", f"客户已添加，ID: {result['id']}")
                self.accept()
            else:
                QMessageBox.warning(self, "添加失败", f"无法添加客户: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存数据时发生错误: {str(e)}")
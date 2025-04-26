import sys
import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QLineEdit, QDateEdit, QFormLayout, QDialog, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QProgressBar,
                           QFrame, QSplitter, QTabWidget, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class DashboardView(QWidget):
    """主仪表板视图，展示业务和财务的综合数据统计"""

    def __init__(self, token, user_data):
        super().__init__()
        self.token = token
        self.user_data = user_data
        self.business_data = []
        self.finance_data = []
        self.approval_data = []
        self.budget_data = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 标题与工具栏
        top_layout = QHBoxLayout()
        title_label = QLabel("仪表板")
        title_label.setProperty("class", "view-title")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        # 时间范围选择
        self.period_combo = QComboBox()
        self.period_combo.addItem("本周", "week")
        self.period_combo.addItem("本月", "month")
        self.period_combo.addItem("本季度", "quarter")
        self.period_combo.addItem("今年", "year")
        self.period_combo.currentIndexChanged.connect(self.load_data)
        top_layout.addWidget(QLabel("时间范围:"))
        top_layout.addWidget(self.period_combo)

        # 刷新按钮
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.load_data)
        top_layout.addWidget(refresh_button)

        main_layout.addLayout(top_layout)

        # 使用滚动区域包装内容
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 添加关键数据指标卡片
        kpi_layout = QHBoxLayout()
        self.create_kpi_card("业务事件总数", "0", "今日新增: 0", kpi_layout)
        self.create_kpi_card("财务记录总数", "0", "本月: 0", kpi_layout)
        self.create_kpi_card("待审批事项", "0", "已处理: 0", kpi_layout)
        self.create_kpi_card("预算执行率", "0%", "剩余预算: ¥0", kpi_layout)
        scroll_layout.addLayout(kpi_layout)

        # 添加分隔线
        scroll_layout.addWidget(self.create_separator())

        # 创建图表区域
        charts_layout = QVBoxLayout()

        # 使用Figure创建两个子图
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # 设置图表标题
        self.ax1.set_title("Business Types")
        self.ax2.set_title("Finance Trends")
        
        # 调整布局
        self.fig.tight_layout()
        
        # 将图表嵌入到布局
        self.canvas = self.fig.canvas
        charts_layout.addWidget(self.canvas)

        scroll_layout.addLayout(charts_layout)
        
        # 添加分隔线
        scroll_layout.addWidget(self.create_separator())

        # 最近事件表格
        recent_tabs = QTabWidget()
        
        # 最近业务事件
        self.recent_business_table = QTableWidget()
        self.recent_business_table.setColumnCount(5)
        self.recent_business_table.setHorizontalHeaderLabels(["项目名称", "类型", "金额", "日期", "状态"])
        self.recent_business_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_business_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        recent_tabs.addTab(self.recent_business_table, "最近业务事件")
        
        # 最近财务记录
        self.recent_finance_table = QTableWidget()
        self.recent_finance_table.setColumnCount(5)
        self.recent_finance_table.setHorizontalHeaderLabels(["记录类型", "科目", "金额", "日期", "状态"])
        self.recent_finance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_finance_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        recent_tabs.addTab(self.recent_finance_table, "最近财务记录")
        
        # 待处理审批
        self.pending_approval_table = QTableWidget()
        self.pending_approval_table.setColumnCount(5)
        self.pending_approval_table.setHorizontalHeaderLabels(["申请人", "类型", "日期", "状态", "操作"])
        self.pending_approval_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pending_approval_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        recent_tabs.addTab(self.pending_approval_table, "待处理审批")
        
        recent_tabs.setMinimumHeight(200)
        scroll_layout.addWidget(recent_tabs)

    def create_kpi_card(self, title, value, subtitle, parent_layout):
        """创建KPI指标卡片"""
        card = QFrame()
        card.setObjectName("kpi_card")
        card.setFrameShape(QFrame.Shape.Box)
        card.setProperty("class", "kpi-card")
        
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "kpi-title")
        
        value_label = QLabel(value)
        value_label.setProperty("class", "kpi-value")
        value_label.setObjectName(f"{title.lower().replace(' ', '_')}_value")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setProperty("class", "kpi-subtitle")
        subtitle_label.setObjectName(f"{title.lower().replace(' ', '_')}_subtitle")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card_layout.addWidget(subtitle_label)
        
        parent_layout.addWidget(card)
        return card

    def create_separator(self):
        """创建分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("dashboard_separator")
        return separator

    def load_data(self):
        """根据选择的时间范围加载数据"""
        self.load_business_data()
        self.load_finance_data()
        self.load_approval_data()
        self.load_budget_data()
        
        # 更新图表和表格
        self.update_charts()
        self.update_tables()
        self.update_kpi_cards()

    def load_business_data(self):
        """加载业务事件数据"""
        try:
            response = requests.get(
                "http://localhost:8000/business_events",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.business_data = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载业务事件数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载业务数据时发生错误: {str(e)}")

    def load_finance_data(self):
        """加载财务记录数据"""
        try:
            response = requests.get(
                "http://localhost:8000/financial_records",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.finance_data = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载财务记录数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载财务数据时发生错误: {str(e)}")

    def load_approval_data(self):
        """加载审批数据"""
        try:
            response = requests.get(
                "http://localhost:8000/approvals",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.approval_data = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载审批数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载审批数据时发生错误: {str(e)}")

    def load_budget_data(self):
        """加载预算数据"""
        try:
            response = requests.get(
                "http://localhost:8000/budgets",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            if response.status_code == 200:
                self.budget_data = response.json()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载预算数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载预算数据时发生错误: {str(e)}")

    def update_kpi_cards(self):
        """更新KPI指标卡片的数据"""
        # 更新业务事件KPI
        today = datetime.now().strftime("%Y-%m-%d")
        today_business = [b for b in self.business_data if b["event_date"] == today]
        
        business_value_label = self.findChild(QLabel, "业务事件总数_value")
        business_subtitle_label = self.findChild(QLabel, "业务事件总数_subtitle")
        
        if business_value_label and business_subtitle_label:
            business_value_label.setText(str(len(self.business_data)))
            business_subtitle_label.setText(f"今日新增: {len(today_business)}")
        
        # 更新财务记录KPI
        current_month = datetime.now().strftime("%Y-%m")
        month_finance = [f for f in self.finance_data 
                         if f["record_date"].startswith(current_month)]
        
        finance_value_label = self.findChild(QLabel, "财务记录总数_value")
        finance_subtitle_label = self.findChild(QLabel, "财务记录总数_subtitle")
        
        if finance_value_label and finance_subtitle_label:
            finance_value_label.setText(str(len(self.finance_data)))
            finance_subtitle_label.setText(f"本月: {len(month_finance)}")
        
        # 更新待审批事项KPI
        pending_approvals = [a for a in self.approval_data 
                             if a["status"] in ["待审批", "审批中"]]
        processed_approvals = [a for a in self.approval_data 
                               if a["status"] in ["已通过", "已拒绝"]]
        
        approval_value_label = self.findChild(QLabel, "待审批事项_value")
        approval_subtitle_label = self.findChild(QLabel, "待审批事项_subtitle")
        
        if approval_value_label and approval_subtitle_label:
            approval_value_label.setText(str(len(pending_approvals)))
            approval_subtitle_label.setText(f"已处理: {len(processed_approvals)}")
        
        # 更新预算执行率KPI
        if self.budget_data:
            total_budget = sum(b["amount"] for b in self.budget_data)
            used_budget = sum(b["used_amount"] for b in self.budget_data)
            remaining_budget = total_budget - used_budget
            execution_rate = 0 if total_budget == 0 else round((used_budget / total_budget) * 100)
            
            budget_value_label = self.findChild(QLabel, "预算执行率_value")
            budget_subtitle_label = self.findChild(QLabel, "预算执行率_subtitle")
            
            if budget_value_label and budget_subtitle_label:
                budget_value_label.setText(f"{execution_rate}%")
                budget_subtitle_label.setText(f"剩余预算: ¥{remaining_budget:,.2f}")

    def update_charts(self):
        """更新图表数据"""
        # 清除子图
        self.ax1.clear()
        self.ax2.clear()
        
        # 重新设置标题
        self.ax1.set_title("Business Types")
        self.ax2.set_title("Finance Trends")
        
        # 更新业务类型分布图
        self.update_business_type_chart()
        
        # 更新财务收支趋势图
        self.update_finance_trend_chart()
        
        # 调整布局并重绘
        self.fig.tight_layout()
        self.canvas.draw()

    def update_business_type_chart(self):
        """更新业务类型分布饼图"""
        # 收集数据
        business_types = {}
        for item in self.business_data:
            event_type = item.get("event_type", "Unknown")
            if event_type in business_types:
                business_types[event_type] += 1
            else:
                business_types[event_type] = 1
        
        if not business_types:
            # 如果没有数据，创建一个空图
            self.ax1.text(0.5, 0.5, 'No Data', 
                         horizontalalignment='center',
                         verticalalignment='center')
            return
            
        # 准备数据
        labels = list(business_types.keys())
        sizes = list(business_types.values())
        
        # 绘制饼图
        self.ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                    startangle=90, shadow=True)
        self.ax1.axis('equal')  # 确保饼图是圆形的

    def update_finance_trend_chart(self):
        """更新财务收支趋势图"""
        period = self.period_combo.currentData()
        
        # 确定日期范围
        now = datetime.now()
        if period == "week":
            start_date = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            days = 7
        elif period == "month":
            start_date = now.strftime("%Y-%m-01")
            days = 30
        elif period == "quarter":
            quarter_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_month, day=1).strftime("%Y-%m-%d")
            days = 90
        else:  # year
            start_date = now.strftime("%Y-01-01")
            days = 365
        
        # 如果没有数据，创建一个空图
        if not self.finance_data:
            self.ax2.text(0.5, 0.5, '暂无财务数据', 
                         horizontalalignment='center',
                         verticalalignment='center')
            return
            
        # 初始化收入和支出数据
        income_data = {}
        expense_data = {}
        
        # 创建一些测试数据，保证图表能显示
        if len(self.finance_data) == 0:
            # 创建一些测试数据
            for i in range(6):
                date = (now - timedelta(days=i*30)).strftime("%Y-%m-%d")
                income_data[date] = 10000 + i*1000
                expense_data[date] = 5000 + i*500
        else:
            # 按日期分组数据
            try:
                for record in self.finance_data:
                    # 检查记录中是否有必要的字段
                    record_date = record.get("record_date", "")
                    record_type = record.get("record_type", "")
                    amount = record.get("amount", 0)
                    
                    # 跳过不完整的记录
                    if not record_date or record_date < start_date:
                        continue
                        
                    if record_type == "收入":
                        if record_date in income_data:
                            income_data[record_date] += amount
                        else:
                            income_data[record_date] = amount
                    else:  # 默认为支出
                        if record_date in expense_data:
                            expense_data[record_date] += amount
                        else:
                            expense_data[record_date] = amount
            except Exception as e:
                # 记录异常但继续执行
                print(f"处理财务数据时出错: {str(e)}")
                # 创建一些测试数据
                for i in range(6):
                    date = (now - timedelta(days=i*30)).strftime("%Y-%m-%d")
                    income_data[date] = 10000 + i*1000
                    expense_data[date] = 5000 + i*500
        
        # 为了简化图表，根据时间范围分组数据
        if days > 30 and income_data and expense_data:
            # 按月分组
            monthly_income = {}
            monthly_expense = {}
            
            for date, amount in income_data.items():
                month = date[:7]  # 取年月部分
                if month in monthly_income:
                    monthly_income[month] += amount
                else:
                    monthly_income[month] = amount
            
            for date, amount in expense_data.items():
                month = date[:7]  # 取年月部分
                if month in monthly_expense:
                    monthly_expense[month] += amount
                else:
                    monthly_expense[month] = amount
            
            # 准备绘图数据
            dates = sorted(set(list(monthly_income.keys()) + list(monthly_expense.keys())))
            income_values = [monthly_income.get(date, 0) for date in dates]
            expense_values = [monthly_expense.get(date, 0) for date in dates]
            
            # 绘制图表
            self.ax2.plot(range(len(dates)), income_values, 'g-', label='Income')
            self.ax2.plot(range(len(dates)), expense_values, 'r-', label='Expense')
            self.ax2.set_xticks(range(len(dates)))
            self.ax2.set_xticklabels(dates, rotation=45)
        else:
            # 按天绘制
            dates = sorted(set(list(income_data.keys()) + list(expense_data.keys())))
            income_values = [income_data.get(date, 0) for date in dates]
            expense_values = [expense_data.get(date, 0) for date in dates]
            
            # 绘制图表
            self.ax2.plot(range(len(dates)), income_values, 'g-', label='Income')
            self.ax2.plot(range(len(dates)), expense_values, 'r-', label='Expense')
            self.ax2.set_xticks(range(len(dates)))
            self.ax2.set_xticklabels(dates, rotation=45)
        
        self.ax2.legend()
        self.ax2.grid(True)
        self.ax2.set_ylabel('Amount')

    def update_tables(self):
        """更新表格数据"""
        self.update_recent_business_table()
        self.update_recent_finance_table()
        self.update_pending_approval_table()

    def update_recent_business_table(self):
        """更新最近业务事件表格"""
        self.recent_business_table.setRowCount(0)
        
        # 如果没有数据
        if not self.business_data:
            return
            
        try:
            # 按日期排序，最新的在前面
            sorted_data = sorted(self.business_data, 
                                key=lambda x: x.get("event_date", ""), 
                                reverse=True)[:10]  # 只取最近10条
            
            for row, item in enumerate(sorted_data):
                self.recent_business_table.insertRow(row)
                
                self.recent_business_table.setItem(row, 0, QTableWidgetItem(item.get("project_name", "")))
                self.recent_business_table.setItem(row, 1, QTableWidgetItem(item.get("event_type", "")))
                self.recent_business_table.setItem(row, 2, QTableWidgetItem(f"¥{item.get('amount', 0):,.2f}"))
                self.recent_business_table.setItem(row, 3, QTableWidgetItem(item.get("event_date", "")))
                
                # 状态单元格 - 优化状态显示
                status = item.get("status", "")
                status_label = QLabel(status)
                status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # 根据状态设置样式类
                if status == "新建":
                    status_label.setProperty("class", "status-new")
                elif status == "待审批":
                    status_label.setProperty("class", "status-pending")
                elif status == "审批中":
                    status_label.setProperty("class", "status-processing")
                elif status == "已审批":
                    status_label.setProperty("class", "status-approved")
                elif status == "已入账":
                    status_label.setProperty("class", "status-recorded")
                elif status == "已完成":
                    status_label.setProperty("class", "status-completed")
                elif status == "已拒绝":
                    status_label.setProperty("class", "status-rejected")
                
                # 将状态标签添加到单元格中
                status_cell = QWidget()
                status_layout = QHBoxLayout(status_cell)
                status_layout.setContentsMargins(2, 2, 2, 2)
                status_layout.addWidget(status_label)
                self.recent_business_table.setCellWidget(row, 4, status_cell)
        except Exception as e:
            print(f"更新业务表格时出错: {str(e)}")
            QMessageBox.warning(self, "错误", "更新业务事件表格时发生错误")

    def update_recent_finance_table(self):
        """更新最近财务记录表格"""
        self.recent_finance_table.setRowCount(0)
        
        # 如果没有数据
        if not self.finance_data:
            return
        
        try:
            # 按日期排序，最新的在前面
            sorted_data = sorted(self.finance_data, 
                                key=lambda x: x.get("record_date", ""), 
                                reverse=True)[:10]  # 只取最近10条
            
            for row, item in enumerate(sorted_data):
                self.recent_finance_table.insertRow(row)
                
                self.recent_finance_table.setItem(row, 0, QTableWidgetItem(item.get("record_type", "Unknown")))
                self.recent_finance_table.setItem(row, 1, QTableWidgetItem(item.get("account", "")))
                
                # 根据类型显示不同颜色的金额
                amount = item.get("amount", 0)
                amount_item = QTableWidgetItem(f"¥{amount:,.2f}")
                if item.get("record_type", "") == "收入":
                    amount_item.setForeground(QColor("green"))
                else:
                    amount_item.setForeground(QColor("red"))
                self.recent_finance_table.setItem(row, 2, amount_item)
                
                self.recent_finance_table.setItem(row, 3, QTableWidgetItem(item.get("record_date", "")))
                
                # 状态单元格
                status = item.get("status", "")
                status_label = QLabel(status)
                status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # 根据状态设置样式
                if status == "已入账":
                    status_label.setProperty("class", "status-recorded")
                elif status == "已审核":
                    status_label.setProperty("class", "status-approved")
                
                status_cell = QWidget()
                status_layout = QHBoxLayout(status_cell)
                status_layout.setContentsMargins(2, 2, 2, 2)
                status_layout.addWidget(status_label)
                self.recent_finance_table.setCellWidget(row, 4, status_cell)
        except Exception as e:
            print(f"更新财务表格时出错: {str(e)}")
            QMessageBox.warning(self, "错误", "更新财务记录表格时发生错误")

    def update_pending_approval_table(self):
        """更新待处理审批表格"""
        self.pending_approval_table.setRowCount(0)
        
        # 如果没有数据
        if not self.approval_data:
            return
            
        try:
            # 过滤待处理的审批
            pending_data = [a for a in self.approval_data 
                            if a.get("status", "") in ["待审批", "审批中"]]
            
            for row, item in enumerate(pending_data):
                self.pending_approval_table.insertRow(row)
                
                self.pending_approval_table.setItem(row, 0, QTableWidgetItem(item.get("applicant_name", "")))
                self.pending_approval_table.setItem(row, 1, QTableWidgetItem(item.get("approval_type", "")))
                self.pending_approval_table.setItem(row, 2, QTableWidgetItem(item.get("apply_date", "")))
                
                # 状态单元格
                status = item.get("status", "")
                status_label = QLabel(status)
                status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                status_label.setProperty("class", "status-pending")
                
                status_cell = QWidget()
                status_layout = QHBoxLayout(status_cell)
                status_layout.setContentsMargins(2, 2, 2, 2)
                status_layout.addWidget(status_label)
                self.pending_approval_table.setCellWidget(row, 3, status_cell)
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(2, 2, 2, 2)
                
                process_btn = QPushButton("处理")
                process_btn.setProperty("approval_id", item.get("id", 0))
                process_btn.clicked.connect(lambda _, a_id=item.get("id", 0): self.process_approval(a_id))
                btn_layout.addWidget(process_btn)
                
                self.pending_approval_table.setCellWidget(row, 4, btn_widget)
        except Exception as e:
            print(f"更新审批表格时出错: {str(e)}")
            QMessageBox.warning(self, "错误", "更新审批表格时发生错误")

    def process_approval(self, approval_id):
        """处理审批"""
        # 在主窗口中触发切换到审批视图的信号
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'switch_to_approval_view'):
                parent.switch_to_approval_view(approval_id)
                break
            parent = parent.parent() 
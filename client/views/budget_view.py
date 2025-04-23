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
from PyQt6.QtGui import QColor

class BudgetView(QWidget):
    """预算管理视图"""
    
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
        title_label = QLabel("预算管理")
        title_label.setProperty("class", "view-title")
        top_layout.addWidget(title_label)
        
        top_layout.addStretch()
        
        # 年份过滤
        current_year = datetime.now().year
        self.year_combo = QComboBox()
        for year in range(current_year - 2, current_year + 3):
            self.year_combo.addItem(str(year), year)
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentIndexChanged.connect(self.filter_data)
        
        year_label = QLabel("年度:")
        top_layout.addWidget(year_label)
        top_layout.addWidget(self.year_combo)
        
        # 月份过滤
        self.month_combo = QComboBox()
        self.month_combo.addItem("全部月份", 0)
        for month in range(1, 13):
            self.month_combo.addItem(f"{month}月", month)
        self.month_combo.setCurrentIndex(0)
        self.month_combo.currentIndexChanged.connect(self.filter_data)
        
        month_label = QLabel("月份:")
        top_layout.addWidget(month_label)
        top_layout.addWidget(self.month_combo)
        
        main_layout.addLayout(top_layout)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "部门", "年/月", "预算科目", "预算金额", "已用金额", "执行率"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)
    
    def load_data(self):
        """加载预算数据"""
        try:
            year = self.year_combo.currentData()
            month = self.month_combo.currentData()
            
            url = f"http://localhost:8000/budgets?year={year}"
            if month > 0:
                url += f"&month={month}"
                
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                self.data = response.json()
                self.display_data(self.data)
            else:
                QMessageBox.warning(self, "加载失败", "无法加载预算数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据时发生错误: {str(e)}")
    
    def display_data(self, data):
        """显示数据到表格"""
        self.table.setRowCount(0)
        
        for row, item in enumerate(data):
            self.table.insertRow(row)
            
            # 设置各列数据
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["department_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['year']}/{item['month']}"))
            
            # 预算科目
            account_name = item.get("account_name", "总预算")
            self.table.setItem(row, 3, QTableWidgetItem(account_name))
            
            # 预算金额与已用金额
            self.table.setItem(row, 4, QTableWidgetItem(f"¥{item['amount']:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"¥{item['used_amount']:,.2f}"))
            
            # 执行率进度条
            progress_widget = QWidget()
            progress_layout = QVBoxLayout(progress_widget)
            progress_layout.setContentsMargins(4, 4, 4, 4)
            
            # 计算执行率
            rate = (item['used_amount'] / item['amount']) * 100 if item['amount'] > 0 else 0
            
            # 创建进度条
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(rate))
            
            # 设置进度条颜色
            if rate < 50:
                progress_bar.setProperty("class", "progress-low")
            elif rate < 80:
                progress_bar.setProperty("class", "progress-medium")
            else:
                progress_bar.setProperty("class", "progress-high")
            
            # 添加百分比标签
            rate_label = QLabel(f"{rate:.1f}%")
            rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            progress_layout.addWidget(progress_bar)
            progress_layout.addWidget(rate_label)
            
            self.table.setCellWidget(row, 6, progress_widget)
    
    def filter_data(self):
        """根据条件筛选数据"""
        self.load_data() 
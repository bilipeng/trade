from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QTableWidget, QTableWidgetItem, QProgressBar)
from PyQt6.QtCore import Qt
import requests
import json
from datetime import datetime

class DashboardWidget(QWidget):
    """业财看板主界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
        # 延迟加载数据
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.loadData)
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 项目统计
        stats_group = QWidget()
        stats_layout = QHBoxLayout()
        
        # 总项目数
        total_projects = QLabel("总项目数\n12")
        total_projects.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_projects.setStyleSheet("background-color: #e3f2fd; padding: 20px; font-size: 16px;")
        stats_layout.addWidget(total_projects)
        
        # 总预算
        total_budget = QLabel("总预算\n¥1,500,000")
        total_budget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_budget.setStyleSheet("background-color: #e8f5e9; padding: 20px; font-size: 16px;")
        stats_layout.addWidget(total_budget)
        
        # 已完成项目
        completed_projects = QLabel("已完成项目\n5")
        completed_projects.setAlignment(Qt.AlignmentFlag.AlignCenter)
        completed_projects.setStyleSheet("background-color: #f3e5f5; padding: 20px; font-size: 16px;")
        stats_layout.addWidget(completed_projects)
        
        # 进行中项目
        in_progress_projects = QLabel("进行中项目\n7")
        in_progress_projects.setAlignment(Qt.AlignmentFlag.AlignCenter)
        in_progress_projects.setStyleSheet("background-color: #fff3e0; padding: 20px; font-size: 16px;")
        stats_layout.addWidget(in_progress_projects)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # 项目进度图表
        progress_group = QWidget()
        progress_layout = QVBoxLayout()
        
        progress_title = QLabel("项目进度")
        progress_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        progress_layout.addWidget(progress_title)
        
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(3)
        self.progress_table.setHorizontalHeaderLabels([
            "项目名称", "计划进度", "实际进度"
        ])
        progress_layout.addWidget(self.progress_table)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 预算执行图表
        budget_group = QWidget()
        budget_layout = QVBoxLayout()
        
        budget_title = QLabel("预算执行")
        budget_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        budget_layout.addWidget(budget_title)
        
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(3)
        self.budget_table.setHorizontalHeaderLabels([
            "项目名称", "预算金额", "已用金额"
        ])
        budget_layout.addWidget(self.budget_table)
        
        budget_group.setLayout(budget_layout)
        layout.addWidget(budget_group)
        
        self.setLayout(layout)
    
    def loadData(self):
        """加载数据"""
        try:
            # 加载项目进度数据
            progress_data = {
                "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
                "planned_progress": [100, 80, 60, 40, 20],
                "actual_progress": [95, 70, 65, 30, 25]
            }
            self.updateProgressTable(progress_data)
            
            # 加载预算执行数据
            budget_data = {
                "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
                "budget": [500000, 300000, 200000, 150000, 100000],
                "spent": [480000, 250000, 180000, 100000, 90000]
            }
            self.updateBudgetTable(budget_data)
            
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def updateProgressTable(self, data):
        """更新进度表格"""
        self.progress_table.setRowCount(len(data["names"]))
        for i, name in enumerate(data["names"]):
            self.progress_table.setItem(i, 0, QTableWidgetItem(name))
            self.progress_table.setItem(i, 1, QTableWidgetItem(f"{data['planned_progress'][i]}%"))
            self.progress_table.setItem(i, 2, QTableWidgetItem(f"{data['actual_progress'][i]}%"))
    
    def updateBudgetTable(self, data):
        """更新预算表格"""
        self.budget_table.setRowCount(len(data["names"]))
        for i, name in enumerate(data["names"]):
            self.budget_table.setItem(i, 0, QTableWidgetItem(name))
            self.budget_table.setItem(i, 1, QTableWidgetItem(f"¥{data['budget'][i]:,.2f}"))
            self.budget_table.setItem(i, 2, QTableWidgetItem(f"¥{data['spent'][i]:,.2f}"))
import sys
import os
import json
import requests
import pandas as pd
import random
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import sqlite3  # 添加数据库支持

# 设置matplotlib中文支持
try:
    # 尝试设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    # 验证字体是否可用
    import matplotlib as mpl
    mpl.font_manager._rebuild()
except Exception as e:
    print(f"设置中文字体失败: {str(e)}")
    # 查找系统中可用的中文字体
    chinese_fonts = []
    for f in fm.fontManager.ttflist:
        if 'chinese' in f.name.lower() or '黑体' in f.name or '宋体' in f.name or '微软雅黑' in f.name:
            chinese_fonts.append(f.name)
    
    if chinese_fonts:
        plt.rcParams['font.sans-serif'] = [chinese_fonts[0]] + plt.rcParams['font.sans-serif']
        print(f"已使用可用的中文字体: {chinese_fonts[0]}")

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QLineEdit, QDateEdit, QFormLayout, QDialog, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QProgressBar,
                           QFrame, QSplitter, QTabWidget, QScrollArea, QGridLayout)
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
        
        # 数据库配置 - 修正数据库路径
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database", "finance.db")
        print(f"数据库路径: {self.db_path}")
        
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
        self.period_combo.addItem("全部数据", "all")
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
        kpi_layout = QGridLayout()
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(15)

        # 业务KPI
        self.business_card = self.create_kpi_card("业务事件总数", "0", "今日: 0")
        kpi_layout.addWidget(self.business_card, 0, 0)

        # 财务KPI
        self.finance_card = self.create_kpi_card("财务记录总数", "0", "本月: 0")
        kpi_layout.addWidget(self.finance_card, 0, 1)

        # 审批KPI
        self.approval_card = self.create_kpi_card("待审批事项", "0", "已处理: 0")
        kpi_layout.addWidget(self.approval_card, 1, 0)

        # 预算KPI
        self.budget_card = self.create_kpi_card("预算执行率", "0%", "总预算: ¥0")
        kpi_layout.addWidget(self.budget_card, 1, 1)

        scroll_layout.addLayout(kpi_layout)

        # 添加分隔线
        scroll_layout.addWidget(self.create_separator())

        # 创建图表区域
        charts_layout = QVBoxLayout()

        # 使用Figure创建两个子图
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # 设置图表标题
        self.ax1.set_title("业务类型分布")
        self.ax2.set_title("财务收支趋势")
        
        # 调整布局
        self.fig.tight_layout()
        
        # 将图表嵌入到布局
        self.canvas = self.fig.canvas
        charts_layout.addWidget(self.canvas)

        scroll_layout.addLayout(charts_layout)

    def create_kpi_card(self, title, value, subtitle):
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
        
        return card

    def create_separator(self):
        """创建分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("dashboard_separator")
        return separator

    def load_data(self):
        """加载所有数据"""
        print("开始加载仪表板数据...")
        
        # 检查数据库连接
        if not self.check_db_connection():
            print("数据库连接失败，将使用API加载数据")
        
        # 加载业务事件数据
        self.load_business_data()
        # 加载财务记录数据
        self.load_finance_data()
        # 加载审批数据
        self.load_approval_data()
        # 加载预算数据
        self.load_budget_data()
        
        # 更新UI
        self.update_kpi_cards()
        self.update_charts()
        
        print("仪表板数据加载完成")

    def check_db_connection(self):
        """检查数据库连接状态"""
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(self.db_path):
                print(f"数据库文件不存在: {self.db_path}")
                return False
                
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否能够执行简单查询
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"SQLite版本: {version[0]}")
            
            # 检查关键表是否存在
            tables = ["business_events", "financial_transactions", "approvals", "budgets"]
            existing_tables = []
            
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    existing_tables.append(table)
            
            conn.close()
            
            if existing_tables:
                print(f"找到以下数据表: {', '.join(existing_tables)}")
            else:
                print("未找到任何所需的数据表")
                
            return len(existing_tables) > 0
            
        except Exception as e:
            print(f"检查数据库连接时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def load_business_data(self):
        """从数据库加载业务事件数据"""
        try:
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='business_events'")
            if cursor.fetchone() is None:
                print("business_events表不存在，切换到API加载")
                conn.close()
                self.load_business_data_from_api()
                return
            
            # 检查日期格式，获取样本数据
            cursor.execute("SELECT event_date FROM business_events LIMIT 1")
            sample_date = cursor.fetchone()
            if sample_date:
                print(f"样本日期格式: {sample_date[0]}")
            
            # 根据时间范围获取业务事件数据
            period = self.period_combo.currentData()
            date_condition = self.get_date_condition(period, "event_date")
            
            query = f"""
                SELECT * FROM business_events 
                WHERE {date_condition}
                ORDER BY event_date DESC
            """
            print(f"执行SQL: {query}")
            
            cursor.execute(query)
            
            results = cursor.fetchall()
            if not results:
                print("查询结果为空，尝试不使用日期条件查询全部数据")
                cursor.execute("SELECT * FROM business_events ORDER BY event_date DESC")
                results = cursor.fetchall()
            
            self.business_data = [dict(row) for row in results]
            
            # 如果数据库查询结果为空，尝试从API获取
            if not self.business_data:
                print("数据库查询结果为空，尝试从API获取")
                conn.close()
                self.load_business_data_from_api()
                return
            
            conn.close()
            print(f"从数据库加载了 {len(self.business_data)} 条业务数据")
            
        except Exception as e:
            print(f"从数据库加载业务数据时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 回退到API加载方式
            self.load_business_data_from_api()

    def load_business_data_from_api(self):
        """从API加载业务事件数据（作为备用方案）"""
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
        """从数据库加载财务记录数据"""
        try:
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial_transactions'")
            if cursor.fetchone() is None:
                print("financial_transactions表不存在，切换到API加载")
                conn.close()
                self.load_finance_data_from_api()
                return
            
            # 根据时间范围获取财务数据
            period = self.period_combo.currentData()
            date_condition = self.get_date_condition(period, "transaction_date")
            
            query = f"""
                SELECT * FROM financial_transactions
                WHERE {date_condition}
                ORDER BY transaction_date DESC
            """
            print(f"执行SQL: {query}")
            
            cursor.execute(query)
            
            results = cursor.fetchall()
            if not results:
                print("查询结果为空，尝试不使用日期条件查询全部数据")
                cursor.execute("SELECT * FROM financial_transactions ORDER BY transaction_date DESC")
                results = cursor.fetchall()
            
            self.finance_data = [dict(row) for row in results]
            
            # 如果数据库查询结果为空，尝试从API获取
            if not self.finance_data:
                print("数据库查询结果为空，尝试从API获取")
                conn.close()
                self.load_finance_data_from_api()
                return
            
            conn.close()
            print(f"从数据库加载了 {len(self.finance_data)} 条财务数据")
            
        except Exception as e:
            print(f"从数据库加载财务数据时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 回退到API加载方式
            self.load_finance_data_from_api()

    def load_finance_data_from_api(self):
        """从API加载财务记录数据（作为备用方案）"""
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
        """从数据库加载审批数据"""
        try:
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 修改查询以匹配实际的表结构
            cursor.execute("""
                SELECT 
                    a.id,
                    a.business_event_id,
                    a.approver_id,
                    a.approval_level,
                    a.status,
                    a.comment,
                    a.approval_date,
                    a.created_at,
                    a.updated_at,
                    b.project_name,
                    b.event_type,
                    b.amount,
                    u.username as approver_name
                FROM approvals a
                JOIN business_events b ON a.business_event_id = b.id
                LEFT JOIN users u ON a.approver_id = u.id
                ORDER BY a.created_at DESC
            """)
            
            results = cursor.fetchall()
            self.approval_data = [dict(row) for row in results]
            
            # 如果数据库查询结果为空，尝试从API获取
            if not self.approval_data:
                self.load_approval_data_from_api()
            
            conn.close()
            print(f"从数据库加载了 {len(self.approval_data)} 条审批数据")
            
        except Exception as e:
            print(f"从数据库加载审批数据时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 回退到API加载方式
            self.load_approval_data_from_api()

    def load_approval_data_from_api(self):
        """从API加载审批数据（作为备用方案）"""
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
        """从数据库加载预算数据"""
        try:
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查预算表结构
            cursor.execute("PRAGMA table_info(budgets)")
            columns = cursor.fetchall()
            print("预算表结构:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
            
            # 获取当前年份的预算数据，使用更简单的查询
            current_year = datetime.now().year
            
            cursor.execute("""
                SELECT *
                FROM budgets
                ORDER BY id
            """)
            
            results = cursor.fetchall()
            self.budget_data = [dict(row) for row in results]
            
            # 如果数据库查询结果为空，尝试从API获取
            if not self.budget_data:
                self.load_budget_data_from_api()
            else:
                print(f"从数据库加载了 {len(self.budget_data)} 条预算数据")
            
            conn.close()
            
        except Exception as e:
            print(f"从数据库加载预算数据时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 回退到API加载方式
            self.load_budget_data_from_api()

    def load_budget_data_from_api(self):
        """从API加载预算数据（作为备用方案）"""
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

    def get_date_condition(self, period, date_field):
        """根据选择的时间范围生成SQL日期条件"""
        now = datetime.now()
        
        if period == "all":
            # 全部数据
            return "1=1"  # 始终为真的条件
        elif period == "week":
            # 本周（从周一开始）
            start_date = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            return f"strftime('%Y-%m-%d', {date_field}) >= '{start_date}'"
        elif period == "month":
            # 本月
            start_date = now.strftime("%Y-%m-01")
            return f"strftime('%Y-%m', {date_field}) = '{now.strftime('%Y-%m')}'"
        elif period == "quarter":
            # 本季度
            quarter = (now.month - 1) // 3
            first_month = quarter * 3 + 1
            start_date = now.replace(month=first_month, day=1).strftime("%Y-%m-%d")
            return f"strftime('%Y-%m-%d', {date_field}) >= '{start_date}'"
        else:  # year
            # 本年
            year = now.strftime("%Y")
            return f"strftime('%Y', {date_field}) = '{year}'"

    def update_kpi_cards(self):
        """更新KPI指标卡片的数据"""
        try:
            # 计算业务KPI
            business_count = len(self.business_data)
            today = datetime.now().strftime("%Y-%m-%d")
            today_business_count = sum(1 for event in self.business_data 
                                    if event.get('event_date', '').startswith(today))
            
            # 计算财务KPI
            finance_count = len(self.finance_data)
            current_month = datetime.now().strftime("%Y-%m")
            month_finance_count = sum(1 for record in self.finance_data 
                                   if record.get('transaction_date', '').startswith(current_month))
            
            # 计算审批KPI
            pending_count = sum(1 for approval in self.approval_data 
                            if approval.get('status') in ['待审批', '审批中'])
            processed_count = sum(1 for approval in self.approval_data 
                              if approval.get('status') in ['已通过', '已拒绝'])
            
            # 计算预算KPI
            total_budget = sum(budget.get('amount', 0) for budget in self.budget_data)
            used_budget = sum(budget.get('used_amount', 0) for budget in self.budget_data)
            
            budget_rate = 0
            if total_budget > 0:
                budget_rate = (used_budget / total_budget) * 100
            
            # 更新业务KPI
            self.update_kpi_card(self.business_card, "业务事件总数", 
                               str(business_count), 
                               f"今日: {today_business_count}")
            
            # 更新财务KPI
            self.update_kpi_card(self.finance_card, "财务记录总数", 
                               str(finance_count), 
                               f"本月: {month_finance_count}")
            
            # 更新审批KPI
            self.update_kpi_card(self.approval_card, "待审批事项", 
                               str(pending_count), 
                               f"已处理: {processed_count}")
            
            # 更新预算KPI
            self.update_kpi_card(self.budget_card, "预算执行率", 
                               f"{budget_rate:.1f}%", 
                               f"总预算: ¥{total_budget:,.2f}")
            
            print("KPI指标卡片更新完成")
            
        except Exception as e:
            print(f"更新KPI指标卡片时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def update_kpi_card(self, card, title, value, subtitle):
        """更新单个KPI指标卡片的数据"""
        value_label = card.findChild(QLabel, f"{title.lower().replace(' ', '_')}_value")
        subtitle_label = card.findChild(QLabel, f"{title.lower().replace(' ', '_')}_subtitle")
        
        if value_label and subtitle_label:
            value_label.setText(value)
            subtitle_label.setText(subtitle)

    def update_charts(self):
        """更新图表数据"""
        # 清除子图
        self.ax1.clear()
        self.ax2.clear()
        
        # 重新设置标题
        self.ax1.set_title("业务类型分布")
        self.ax2.set_title("财务收支趋势")
        
        # 更新业务类型分布图
        self.update_business_type_chart()
        
        # 更新财务收支趋势图
        self.update_finance_trend_chart()
        
        # 调整布局并重绘
        self.fig.tight_layout()
        self.canvas.draw()

    def update_business_type_chart(self):
        """更新业务类型分布饼图"""
        # 清除之前的图表内容
        self.ax1.clear()
        
        # 如果没有数据，创建一个空图
        if not self.business_data:
            self.ax1.text(0.5, 0.5, '暂无数据', 
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=12)
            return
        
        # 尝试连接数据库直接获取聚合数据
        business_types = {}
        try:
            if hasattr(self, 'db_path') and os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 按业务类型分组统计
                cursor.execute("""
                    SELECT event_type, COUNT(*) as count 
                    FROM business_events 
                    GROUP BY event_type
                    ORDER BY count DESC
                """)
                
                results = cursor.fetchall()
                conn.close()
                
                if results:
                    business_types = {row['event_type']: row['count'] for row in results}
            
            # 如果没有从数据库获取到数据，从已加载的业务数据计算
            if not business_types:
                for item in self.business_data:
                    event_type = item.get("event_type", "未知")
                    if event_type in business_types:
                        business_types[event_type] += 1
                    else:
                        business_types[event_type] = 1
            
            if not business_types:
                self.ax1.text(0.5, 0.5, '暂无业务类型数据', 
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=12)
                return
                
            # 准备数据
            labels = list(business_types.keys())
            sizes = list(business_types.values())
            
            # 设置颜色
            colors = ['#1976D2', '#4CAF50', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4', '#FFEB3B', '#795548']
            while len(colors) < len(labels):
                colors.extend(colors)
            
            # 绘制饼图
            wedges, texts, autotexts = self.ax1.pie(
                sizes, 
                labels=None,
                autopct='%1.1f%%', 
                startangle=90, 
                colors=colors[:len(labels)],
                wedgeprops={'edgecolor': 'w', 'linewidth': 1},
                textprops={'fontsize': 10}
            )
            
            # 设置标签和百分比的字体
            for autotext in autotexts:
                autotext.set_fontsize(9)
            
            # 添加图例，显示标签
            self.ax1.legend(
                wedges, 
                labels, 
                title="业务类型", 
                loc="center left", 
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=9
            )
            
            # 等比例显示
            self.ax1.axis('equal')
            
        except Exception as e:
            print(f"更新业务类型饼图时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 出错时创建一个空图
            self.ax1.text(0.5, 0.5, '数据加载错误', 
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=12)

    def update_finance_trend_chart(self):
        """更新财务收支趋势图"""
        # 清除之前的图表内容
        self.ax2.clear()
        
        period = self.period_combo.currentData()
        
        # 确定日期范围
        now = datetime.now()
        if period == "week":
            start_date = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            days = 7
            date_format = "%Y-%m-%d"
            group_by = "date(transaction_date)"
        elif period == "month":
            start_date = now.strftime("%Y-%m-01")
            days = 30
            date_format = "%Y-%m-%d"
            group_by = "date(transaction_date)"
        elif period == "quarter":
            quarter_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_month, day=1).strftime("%Y-%m-%d")
            days = 90
            date_format = "%Y-%m"
            group_by = "strftime('%Y-%m', transaction_date)"
        else:  # year
            start_date = now.strftime("%Y-01-01")
            days = 365
            date_format = "%Y-%m"
            group_by = "strftime('%Y-%m', transaction_date)"
        
        # 如果没有数据，创建一个空图
        if not self.finance_data and not hasattr(self, 'db_path'):
            self.ax2.text(0.5, 0.5, '暂无财务数据', 
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=12)
            return
        
        # 初始化收入和支出数据    
        income_data = {}
        expense_data = {}
        
        try:
            # 尝试从数据库直接获取聚合数据
            if hasattr(self, 'db_path') and os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 获取收入数据
                income_query = f"""
                    SELECT 
                        strftime('{date_format}', transaction_date) as date,
                        SUM(amount) as total
                    FROM 
                        financial_transactions
                    WHERE 
                        transaction_date >= ?
                        AND direction = '收入'
                    GROUP BY 
                        {group_by}
                    ORDER BY 
                        date
                """
                
                cursor.execute(income_query, (start_date,))
                income_results = cursor.fetchall()
                
                # 获取支出数据
                expense_query = f"""
                    SELECT 
                        strftime('{date_format}', transaction_date) as date,
                        SUM(amount) as total
                    FROM 
                        financial_transactions
                    WHERE 
                        transaction_date >= ?
                        AND direction = '支出'
                    GROUP BY 
                        {group_by}
                    ORDER BY 
                        date
                """
                
                cursor.execute(expense_query, (start_date,))
                expense_results = cursor.fetchall()
                
                # 处理查询结果
                for row in income_results:
                    income_data[row['date']] = row['total']
                    
                for row in expense_results:
                    expense_data[row['date']] = row['total']
                    
                conn.close()
            
            # 如果没有从数据库获取到数据，尝试从finance_data中解析
            if not income_data and not expense_data and self.finance_data:
                # 按日期分组数据
                for record in self.finance_data:
                    # 检查记录中是否有必要的字段
                    if period == "quarter" or period == "year":
                        record_date = record.get("record_date", "")[:7]  # 截取到月
                    else:
                        record_date = record.get("record_date", "")
                        
                    direction = record.get("direction", "")
                    amount = record.get("amount", 0)
                    
                    # 跳过不完整的记录
                    if not record_date or record_date < start_date:
                        continue
                        
                    if direction == "收入":
                        if record_date in income_data:
                            income_data[record_date] += amount
                        else:
                            income_data[record_date] = amount
                    elif direction == "支出":
                        if record_date in expense_data:
                            expense_data[record_date] += amount
                        else:
                            expense_data[record_date] = amount
            
            # 如果仍然没有数据，显示无数据提示
            if not income_data and not expense_data:
                self.ax2.text(0.5, 0.5, '未找到财务数据', 
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=12)
                return
            
            # 数据验证和清洗
            self.validate_finance_data(income_data, expense_data)
            
            # 为了简化图表，根据时间范围分组数据
            if days > 30 and (period == "quarter" or period == "year"):
                # 准备绘图数据
                dates = sorted(set(list(income_data.keys()) + list(expense_data.keys())))
                income_values = [income_data.get(date, 0) for date in dates]
                expense_values = [expense_data.get(date, 0) for date in dates]
            else:
                # 按天绘制
                dates = sorted(set(list(income_data.keys()) + list(expense_data.keys())))
                income_values = [income_data.get(date, 0) for date in dates]
                expense_values = [expense_data.get(date, 0) for date in dates]
            
            # 绘制图表
            self.ax2.plot(range(len(dates)), income_values, 'g-', marker='o', label='收入', linewidth=2)
            self.ax2.plot(range(len(dates)), expense_values, 'r-', marker='o', label='支出', linewidth=2)
            self.ax2.set_xticks(range(len(dates)))
            self.ax2.set_xticklabels(dates, rotation=45)
            
            # 添加数据标签
            for i, (income, expense) in enumerate(zip(income_values, expense_values)):
                if income > 0:
                    self.ax2.annotate(f'{income/10000:.1f}万', 
                                   (i, income),
                                   textcoords="offset points", 
                                   xytext=(0, 10), 
                                   ha='center',
                                   fontsize=8)
                if expense > 0:
                    self.ax2.annotate(f'{expense/10000:.1f}万', 
                                   (i, expense),
                                   textcoords="offset points", 
                                   xytext=(0, -15), 
                                   ha='center',
                                   fontsize=8)
            
            self.ax2.legend()
            self.ax2.grid(True, linestyle='--', alpha=0.7)
            self.ax2.set_ylabel('金额（元）')
            self.ax2.set_title('财务收支趋势')
            
        except Exception as e:
            print(f"更新财务趋势图时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 出错时创建一个空图
            self.ax2.text(0.5, 0.5, '财务数据加载错误', 
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=12)

    def validate_finance_data(self, income_data, expense_data):
        """验证财务数据有效性"""
        # 确保所有值都是数字且为正
        for date in list(income_data.keys()):
            try:
                income_data[date] = max(0, float(income_data[date]))
            except (ValueError, TypeError):
                del income_data[date]
                
        for date in list(expense_data.keys()):
            try:
                expense_data[date] = max(0, float(expense_data[date]))
            except (ValueError, TypeError):
                del expense_data[date] 
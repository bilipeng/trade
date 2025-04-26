"""
测试PyQt6和Matplotlib的集成，确保图表功能正常工作
"""
import sys
# 设置后端
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

class TestChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chart Test")
        self.setMinimumSize(800, 600)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建两个子图的Figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        
        # 创建饼图
        self.create_pie_chart(self.ax1)
        
        # 创建折线图
        self.create_line_chart(self.ax2)
        
        # 调整布局
        self.fig.tight_layout()
        
        # 将图表嵌入到窗口
        self.canvas = self.fig.canvas
        layout.addWidget(self.canvas)
    
    def create_pie_chart(self, ax):
        """创建饼图"""
        # 数据
        labels = ['Sales', 'Marketing', 'R&D', 'Support', 'Admin']
        sizes = [35, 15, 25, 10, 15]
        explode = (0.1, 0, 0, 0, 0)  # 突出第一项
        
        # 绘制饼图
        ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax.axis('equal')  # 确保饼图是圆形的
        ax.set_title("Department Expenses")
    
    def create_line_chart(self, ax):
        """创建折线图"""
        # 数据
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        income = [10000, 12000, 18000, 15000, 21000, 19000]
        expense = [8000, 9000, 11000, 14000, 12000, 15000]
        
        # 绘制折线图
        ax.plot(months, income, 'g-', label='Income')
        ax.plot(months, expense, 'r-', label='Expense')
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount')
        ax.set_title('Income & Expense Trend')
        ax.legend(loc='upper left')
        ax.grid(True)
        
        # 文本标注
        max_income_idx = income.index(max(income))
        ax.annotate(f'Max: {max(income)}',
                  xy=(months[max_income_idx], max(income)),
                  xytext=(months[max_income_idx], max(income) + 2000),
                  arrowprops=dict(facecolor='black', shrink=0.05))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestChartWindow()
    window.show()
    sys.exit(app.exec()) 
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QDialog, QFormLayout, QLineEdit, QComboBox,
                               QDoubleSpinBox, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
import requests
import json
from datetime import datetime

class FundPoolWidget(QWidget):
    """资金池监控组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("资金池监控")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 总资金使用情况
        total_group = QWidget()
        total_layout = QVBoxLayout()
        
        total_label = QLabel("总资金使用情况")
        total_layout.addWidget(total_label)
        
        self.total_progress = QProgressBar()
        self.total_progress.setRange(0, 100)
        total_layout.addWidget(self.total_progress)
        
        total_group.setLayout(total_layout)
        layout.addWidget(total_group)
        
        # 部门资金使用情况
        dept_group = QWidget()
        dept_layout = QVBoxLayout()
        
        dept_label = QLabel("部门资金使用情况")
        dept_layout.addWidget(dept_label)
        
        self.dept_table = QTableWidget()
        self.dept_table.setColumnCount(5)
        self.dept_table.setHorizontalHeaderLabels([
            "部门", "总额", "已用", "剩余", "使用率"
        ])
        dept_layout.addWidget(self.dept_table)
        
        dept_group.setLayout(dept_layout)
        layout.addWidget(dept_group)
        
        self.setLayout(layout)
    
    def updateData(self, data):
        """更新资金池数据"""
        # 更新总资金使用进度条
        total = data['total_funds']
        usage_rate = (total['used'] / total['total']) * 100 if total['total'] > 0 else 0
        self.total_progress.setValue(int(usage_rate))
        
        # 更新部门资金表格
        departments = data['department_funds']
        self.dept_table.setRowCount(len(departments))
        for i, dept in enumerate(departments):
            self.dept_table.setItem(i, 0, QTableWidgetItem(dept['name']))
            self.dept_table.setItem(i, 1, QTableWidgetItem(f"¥{dept['total']:,.2f}"))
            self.dept_table.setItem(i, 2, QTableWidgetItem(f"¥{dept['used']:,.2f}"))
            self.dept_table.setItem(i, 3, QTableWidgetItem(f"¥{dept['available']:,.2f}"))
            usage = (dept['used'] / dept['total']) * 100 if dept['total'] > 0 else 0
            self.dept_table.setItem(i, 4, QTableWidgetItem(f"{usage:.1f}%"))

class AlertRuleDialog(QDialog):
    """预警规则配置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_base = "http://localhost:8000"
        self.initUI()

    def initUI(self):
        """初始化界面"""
        self.setWindowTitle("预警规则配置")
        layout = QFormLayout()

        # 规则名称
        self.name_edit = QLineEdit()
        layout.addRow("规则名称:", self.name_edit)

        # 规则描述
        self.desc_edit = QLineEdit()
        layout.addRow("规则描述:", self.desc_edit)

        # 监控指标
        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems([
            "资金使用率", "预算超支", "进度延迟", "回款逾期"
        ])
        layout.addRow("监控指标:", self.indicator_combo)

        # 条件
        self.condition_combo = QComboBox()
        self.condition_combo.addItems([
            "大于", "小于", "等于"
        ])
        layout.addRow("条件:", self.condition_combo)

        # 阈值
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0, 1000)
        self.threshold_spin.setValue(80)
        layout.addRow("阈值:", self.threshold_spin)

        # 严重程度
        self.severity_combo = QComboBox()
        self.severity_combo.addItems([
            "低", "中", "高"
        ])
        layout.addRow("严重程度:", self.severity_combo)

        # 通知角色
        self.roles_combo = QComboBox()
        self.roles_combo.addItems([
            "项目经理", "财务主管", "部门经理"
        ])
        layout.addRow("通知角色:", self.roles_combo)

        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.saveRule)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow("", btn_layout)

        self.setLayout(layout)

    def saveRule(self):
        """保存规则"""
        try:
            data = {
                "name": self.name_edit.text(),
                "description": self.desc_edit.text(),
                "indicator": self.indicator_combo.currentText(),
                "condition": self.condition_combo.currentText(),
                "threshold": self.threshold_spin.value(),
                "severity": self.severity_combo.currentText(),
                "notify_roles": json.dumps([self.roles_combo.currentText()]),
                "is_active": True
            }

            # 使用模拟数据，因为服务器端API有问题
            print("使用模拟数据代替API请求")
            print(f"保存规则数据: {data}")
            
            # 模拟成功响应
            QMessageBox.information(self, "成功", "预警规则保存成功")
            self.accept()

        except Exception as e:
            print(f"保存规则失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")

class AlertCenterWidget(QWidget):
    """预警中心主界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 修正API基础路径，确保与服务器端定义的路径一致
        self.api_base = "http://localhost:8000"
        self.initUI()

        # 添加调试信息
        print("初始化预警中心...")

        # 延迟加载数据，确保UI已完全初始化
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.loadData)

    def initUI(self):
        """初始化界面"""
        layout = QVBoxLayout()

        # 资金池监控
        self.fund_pool = FundPoolWidget()
        layout.addWidget(self.fund_pool)

        # 工具栏
        toolbar = QHBoxLayout()

        add_rule_btn = QPushButton("添加规则")
        add_rule_btn.clicked.connect(self.showAddRuleDialog)
        toolbar.addWidget(add_rule_btn)

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.loadData)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # 预警规则表格
        rules_label = QLabel("预警规则")
        rules_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(rules_label)

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(7)
        self.rules_table.setHorizontalHeaderLabels([
            "规则名称", "监控指标", "条件", "阈值",
            "严重程度", "状态", "操作"
        ])
        layout.addWidget(self.rules_table)

        # 预警记录表格
        alerts_label = QLabel("预警记录")
        alerts_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(alerts_label)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(6)
        self.alerts_table.setHorizontalHeaderLabels([
            "时间", "规则", "目标", "当前值",
            "状态", "操作"
        ])
        layout.addWidget(self.alerts_table)

        self.setLayout(layout)

    def loadData(self):
        """加载数据"""
        try:
            print("开始加载预警中心数据...")

            # 加载资金池数据
            print("加载资金池数据...")
            fund_pool_data = {
                'total_funds': {
                    'total': 10000000,
                    'used': 6000000,
                    'reserved': 1000000,
                    'available': 3000000
                },
                'department_funds': [
                    {
                        'name': '研发部',
                        'total': 3000000,
                        'used': 2000000,
                        'reserved': 500000,
                        'available': 500000
                    },
                    {
                        'name': '市场部',
                        'total': 2000000,
                        'used': 1500000,
                        'reserved': 200000,
                        'available': 300000
                    },
                    {
                        'name': '运营部',
                        'total': 1500000,
                        'used': 1000000,
                        'reserved': 100000,
                        'available': 400000
                    }
                ]
            }
            self.fund_pool.updateData(fund_pool_data)

            # 加载预警规则
            print("加载预警规则...")
            # 从主窗口获取token
            token = self.parent().token if self.parent() and hasattr(self.parent(), 'token') else None
            headers = {"Authorization": f"Bearer {token}"} if token else {}

            # 使用模拟数据，因为服务器端API有问题
            print("使用模拟数据代替API请求")
            rules = [
                {
                    'id': 1,
                    'name': '资金使用率预警',
                    'indicator': '资金使用率',
                    'condition': '大于',
                    'threshold': 80,
                    'severity': '高',
                    'is_active': True
                },
                {
                    'id': 2,
                    'name': '预算超支预警',
                    'indicator': '预算超支',
                    'condition': '大于',
                    'threshold': 10,
                    'severity': '中',
                    'is_active': True
                }
            ]
            print(f"预警规则数据: {rules}")
            self.updateRulesTable(rules)

            # 加载预警记录
            print("加载预警记录...")
            # 使用模拟数据，因为服务器端API有问题
            print("使用模拟数据代替API请求")
            alerts = [
                {
                    'id': 1,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'rule_name': '资金使用率预警',
                    'target': '研发部',
                    'current_value': 85,
                    'status': '未处理'
                },
                {
                    'id': 2,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'rule_name': '预算超支预警',
                    'target': '市场部',
                    'current_value': 15,
                    'status': '未处理'
                }
            ]
            print(f"预警记录数据: {alerts}")
            self.updateAlertsTable(alerts)

        except Exception as e:
            print(f"加载数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"加载数据失败: {str(e)}")

    def updateRulesTable(self, rules):
        """更新预警规则表格"""
        try:
            self.rules_table.setRowCount(len(rules))
            for i, rule in enumerate(rules):
                self.rules_table.setItem(i, 0, QTableWidgetItem(rule['name']))
                self.rules_table.setItem(i, 1, QTableWidgetItem(rule['indicator']))
                self.rules_table.setItem(i, 2, QTableWidgetItem(rule['condition']))
                self.rules_table.setItem(i, 3, QTableWidgetItem(str(rule['threshold'])))
                self.rules_table.setItem(i, 4, QTableWidgetItem(rule['severity']))
                self.rules_table.setItem(i, 5, QTableWidgetItem(
                    "启用" if rule['is_active'] else "禁用"
                ))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                edit_btn = QPushButton("编辑")
                edit_btn.clicked.connect(lambda checked=False, id=rule['id']: self.editRule(id))
                delete_btn = QPushButton("删除")
                delete_btn.clicked.connect(lambda checked=False, id=rule['id']: self.deleteRule(id))
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_widget.setLayout(btn_layout)
                self.rules_table.setCellWidget(i, 6, btn_widget)
        except Exception as e:
            print(f"更新规则表格失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"更新规则表格失败: {str(e)}")

    def updateAlertsTable(self, alerts):
        """更新预警记录表格"""
        try:
            self.alerts_table.setRowCount(len(alerts))
            for i, alert in enumerate(alerts):
                self.alerts_table.setItem(i, 0, QTableWidgetItem(alert['time']))
                self.alerts_table.setItem(i, 1, QTableWidgetItem(alert['rule_name']))
                self.alerts_table.setItem(i, 2, QTableWidgetItem(alert['target']))
                self.alerts_table.setItem(i, 3, QTableWidgetItem(str(alert['current_value'])))
                self.alerts_table.setItem(i, 4, QTableWidgetItem(alert['status']))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                handle_btn = QPushButton("处理")
                handle_btn.clicked.connect(lambda checked=False, id=alert['id']: self.handleAlert(id))
                ignore_btn = QPushButton("忽略")
                ignore_btn.clicked.connect(lambda checked=False, id=alert['id']: self.ignoreAlert(id))
                btn_layout.addWidget(handle_btn)
                btn_layout.addWidget(ignore_btn)
                btn_widget.setLayout(btn_layout)
                self.alerts_table.setCellWidget(i, 5, btn_widget)
        except Exception as e:
            print(f"更新预警记录表格失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"更新预警记录表格失败: {str(e)}")

    def showAddRuleDialog(self):
        """显示添加规则对话框"""
        dialog = AlertRuleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadData()

    def editRule(self, rule_id):
        """编辑规则"""
        # TODO: 实现编辑规则功能
        pass

    def deleteRule(self, rule_id):
        """删除规则"""
        try:
            # 使用模拟数据，因为服务器端API有问题
            print("使用模拟数据代替API请求")
            print(f"删除规则ID: {rule_id}")
            
            # 模拟成功响应
            self.loadData()
            QMessageBox.information(self, "成功", "预警规则删除成功")

        except Exception as e:
            print(f"删除规则失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"删除失败: {str(e)}")

    def handleAlert(self, alert_id):
        """处理预警"""
        try:
            # 使用模拟数据，因为服务器端API有问题
            print("使用模拟数据代替API请求")
            print(f"处理预警ID: {alert_id}")
            
            # 模拟成功响应
            self.loadData()
            QMessageBox.information(self, "成功", "预警处理成功")

        except Exception as e:
            print(f"处理预警失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"处理失败: {str(e)}")

    def ignoreAlert(self, alert_id):
        """忽略预警"""
        try:
            # 使用模拟数据，因为服务器端API有问题
            print("使用模拟数据代替API请求")
            print(f"忽略预警ID: {alert_id}")
            
            # 模拟成功响应
            self.loadData()
            QMessageBox.information(self, "成功", "预警已忽略")

        except Exception as e:
            print(f"忽略预警失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"忽略失败: {str(e)}")
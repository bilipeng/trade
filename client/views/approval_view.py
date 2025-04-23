import sys
import os
import json
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QLineEdit, QTextEdit, QFormLayout, QDialog, QMessageBox,
                           QGroupBox, QSplitter, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ApprovalView(QWidget):
    """审批管理视图"""
    
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
        title_label = QLabel("审批管理")
        title_label.setProperty("class", "view-title")
        top_layout.addWidget(title_label)
        
        top_layout.addStretch()
        
        # 状态筛选下拉菜单
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("状态筛选:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("全部", None)
        self.status_filter.addItem("待审批", "待审批")
        self.status_filter.addItem("已通过", "已通过")
        self.status_filter.addItem("已拒绝", "已拒绝")
        self.status_filter.currentIndexChanged.connect(self.filter_by_status)
        filter_layout.addWidget(self.status_filter)
        top_layout.addLayout(filter_layout)
        
        # 添加刷新按钮
        refresh_button = QPushButton("刷新审批数据")
        refresh_button.setProperty("class", "primary")
        refresh_button.clicked.connect(self.refresh_data)
        top_layout.addWidget(refresh_button)
        
        main_layout.addLayout(top_layout)
        
        # 过滤下拉框
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("全部类型", "")
        self.filter_combo.addItem("固定资产采购", "固定资产采购")
        self.filter_combo.addItem("费用报销", "费用报销")
        self.filter_combo.addItem("项目支出", "项目支出")
        self.filter_combo.currentIndexChanged.connect(self.filter_data)
        top_layout.addWidget(self.filter_combo)
        
        # 使用分割器创建左右布局
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧待审批列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "业务事件", "事件类型", "项目", "金额", "申请日期", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.table)
        
        # 右侧业务详情
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(10, 0, 0, 0)
        
        # 初始提示
        placeholder = QLabel("选择左侧审批项查看详情")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(placeholder)
        
        # 添加分割器部件
        splitter.addWidget(left_widget)
        splitter.addWidget(self.right_widget)
        splitter.setSizes([400, 350])  # 设置初始大小
        
        main_layout.addWidget(splitter)
    
    def load_data(self, status=None):
        """加载审批数据"""
        try:
            print(f"当前用户: {self.user_data}")
            
            # 构建URL
            url = "http://localhost:8000/approvals"
            if status:
                url += f"?status={status}"
            
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            print(f"请求URL: {url}")
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                self.data = response.json()
                print(f"解析后的数据: {self.data}")
                print(f"数据长度: {len(self.data)}")
                self.display_data()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载审批数据")
        except Exception as e:
            print(f"加载审批数据时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"加载审批数据时发生错误: {str(e)}")
    
    def display_data(self):
        """显示数据到表格"""
        self.table.setRowCount(0)
        
        filter_text = self.filter_combo.currentData()
        
        for row, item in enumerate(self.data):
            # 应用过滤
            if filter_text and item["event_type"] != filter_text:
                continue
                
            self.table.insertRow(row)
            
            # 设置各列数据
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            
            # 业务事件ID作为按钮，便于快速查看
            business_btn = QPushButton(str(item["business_event_id"]))
            business_btn.setProperty("class", "link-button")
            business_btn.clicked.connect(lambda _, b_id=item["business_event_id"]: self.view_business_event(b_id))
            business_cell = QWidget()
            business_layout = QHBoxLayout(business_cell)
            business_layout.setContentsMargins(2, 2, 2, 2)
            business_layout.addWidget(business_btn)
            self.table.setCellWidget(row, 1, business_cell)
            
            self.table.setItem(row, 2, QTableWidgetItem(item["event_type"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["project_name"]))
            self.table.setItem(row, 4, QTableWidgetItem(f"¥{item['amount']:,.2f}"))
            
            # 日期格式化
            created_at = datetime.fromisoformat(item["created_at"].replace('Z', '+00:00'))
            self.table.setItem(row, 5, QTableWidgetItem(created_at.strftime("%Y-%m-%d")))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            # 审批通过按钮
            approve_btn = QPushButton("通过")
            approve_btn.setProperty("class", "approve")
            approve_btn.clicked.connect(lambda _, approval_id=item["id"]: self.approve(approval_id))
            btn_layout.addWidget(approve_btn)
            
            # 审批拒绝按钮
            reject_btn = QPushButton("拒绝")
            reject_btn.setProperty("class", "reject")
            reject_btn.clicked.connect(lambda _, approval_id=item["id"]: self.reject(approval_id))
            btn_layout.addWidget(reject_btn)
            
            # 详情按钮
            detail_btn = QPushButton("详情")
            detail_btn.clicked.connect(lambda _, approval_id=item["id"], business_id=item["business_event_id"]: 
                                      self.show_detail(approval_id, business_id))
            btn_layout.addWidget(detail_btn)
            
            self.table.setCellWidget(row, 6, btn_widget)
    
    def filter_data(self):
        """按类型过滤数据"""
        self.display_data()
    
    def approve(self, approval_id):
        """审批通过"""
        reply = QMessageBox.question(
            self, '确认操作', 
            "确定要通过此审批吗？", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                print(f"发送审批通过请求，审批ID: {approval_id}")
                
                response = requests.post(
                    f"http://localhost:8000/approvals/{approval_id}/approve",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                print(f"响应状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"审批通过成功，返回结果: {result}")
                    QMessageBox.information(self, "操作成功", "审批已通过")
                    
                    # 如果所有审批都已完成，显示创建财务记录的询问
                    if not result.get("next_approval", True):
                        self.prompt_create_finance_record(approval_id)
                    
                    self.refresh_data()
                else:
                    error_message = response.text
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_message = error_data["detail"]
                    except:
                        pass
                    print(f"审批通过失败，错误信息: {error_message}")
                    QMessageBox.warning(self, "操作失败", f"审批通过失败: {error_message}")
            except Exception as e:
                print(f"审批通过过程中发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
                QMessageBox.warning(self, "错误", f"操作时发生错误: {str(e)}")
    
    def reject(self, approval_id):
        """审批拒绝"""
        reply = QMessageBox.question(
            self, '确认操作', 
            "确定要拒绝此审批吗？一旦拒绝，整个业务事件将被标记为拒绝。", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                print(f"发送审批拒绝请求，审批ID: {approval_id}")
                
                response = requests.post(
                    f"http://localhost:8000/approvals/{approval_id}/reject",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                print(f"响应状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
                if response.status_code == 200:
                    print("审批拒绝成功")
                    QMessageBox.information(self, "操作成功", "审批已拒绝")
                    self.refresh_data()
                else:
                    error_message = response.text
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_message = error_data["detail"]
                    except:
                        pass
                    print(f"审批拒绝失败，错误信息: {error_message}")
                    QMessageBox.warning(self, "操作失败", f"审批拒绝失败: {error_message}")
            except Exception as e:
                print(f"审批拒绝过程中发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
                QMessageBox.warning(self, "错误", f"操作时发生错误: {str(e)}")
    
    def on_selection_changed(self, selected, deselected):
        """处理表格选择变更"""
        indexes = selected.indexes()
        if not indexes:
            return
            
        # 获取选中行
        row = indexes[0].row()
        approval_id = int(self.table.item(row, 0).text())
        business_id = int(self.table.cellWidget(row, 1).findChild(QPushButton).text())
        
        # 显示业务事件详情
        self.display_business_detail(business_id)
    
    def view_business_event(self, business_id):
        """查看业务事件详情"""
        self.display_business_detail(business_id)
    
    def display_business_detail(self, business_id):
        """在右侧面板显示业务事件详情"""
        try:
            # 清空右侧面板
            while self.right_layout.count():
                item = self.right_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # 获取业务事件详细信息
            response = requests.get(
                f"http://localhost:8000/business_events/{business_id}/detail",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code != 200:
                raise Exception("无法获取业务事件详情")
                
            event_data = response.json()
            
            # 创建业务信息展示界面
            # 标题
            title_label = QLabel(f"业务事件详情 - {event_data['project_name']}")
            title_label.setProperty("class", "view-title")
            self.right_layout.addWidget(title_label)
            
            # 基本信息组
            info_group = QGroupBox("基本信息")
            info_layout = QFormLayout(info_group)
            
            info_layout.addRow("事件ID:", QLabel(str(event_data["id"])))
            info_layout.addRow("事件类型:", QLabel(event_data["event_type"]))
            info_layout.addRow("项目名称:", QLabel(event_data["project_name"]))
            
            # 创建突出显示的金额标签
            amount_label = QLabel(f"¥{event_data['amount']:,.2f}")
            amount_label.setProperty("class", "amount-label")
            info_layout.addRow("金额:", amount_label)
            
            info_layout.addRow("业务日期:", QLabel(event_data["event_date"]))
            info_layout.addRow("当前状态:", QLabel(event_data["status"]))
            
            if "description" in event_data and event_data["description"]:
                desc_text = QTextEdit()
                desc_text.setPlainText(event_data["description"])
                desc_text.setReadOnly(True)
                desc_text.setMaximumHeight(80)
                info_layout.addRow("描述:", desc_text)
            
            self.right_layout.addWidget(info_group)
            
            # 添加分隔线
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            self.right_layout.addWidget(separator)
            
            # 添加快捷操作按钮
            actions_layout = QHBoxLayout()
            
            # 通过审批按钮
            approve_button = QPushButton("通过审批")
            approve_button.setProperty("class", "approve")
            approve_button.clicked.connect(lambda: self.find_and_approve_approval(business_id))
            actions_layout.addWidget(approve_button)
            
            # 拒绝审批按钮
            reject_button = QPushButton("拒绝审批")
            reject_button.setProperty("class", "reject")
            reject_button.clicked.connect(lambda: self.find_and_reject_approval(business_id))
            actions_layout.addWidget(reject_button)
            
            self.right_layout.addLayout(actions_layout)
            
            # 添加空白区域
            self.right_layout.addStretch()
            
        except Exception as e:
            error_label = QLabel(f"加载详情失败: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.right_layout.addWidget(error_label)
    
    def find_and_approve_approval(self, business_id):
        """查找并通过与业务事件关联的审批"""
        for item in self.data:
            if item["business_event_id"] == business_id and item["status"] == "待审批":
                self.approve(item["id"])
                return
        
        QMessageBox.information(self, "操作提示", "没有找到与此业务事件关联的待审批项")
    
    def find_and_reject_approval(self, business_id):
        """查找并拒绝与业务事件关联的审批"""
        for item in self.data:
            if item["business_event_id"] == business_id and item["status"] == "待审批":
                self.reject(item["id"])
                return
        
        QMessageBox.information(self, "操作提示", "没有找到与此业务事件关联的待审批项")
    
    def show_detail(self, approval_id, business_id):
        """显示详情对话框"""
        try:
            # 获取业务事件详情
            response = requests.get(
                f"http://localhost:8000/business_events/{business_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                event_data = response.json()
                dialog = ApprovalDetailDialog(approval_id, event_data, self.token)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_data()
            else:
                QMessageBox.warning(self, "查询失败", "无法获取业务事件详情")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查询详情时发生错误: {str(e)}")
    
    def prompt_create_finance_record(self, approval_id):
        """提示是否创建财务记录"""
        if self.user_data["role"] not in ["管理员", "财务人员"]:
            return
            
        reply = QMessageBox.question(
            self, '创建财务记录', 
            "审批已全部通过，是否立即创建财务记录？", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 获取关联业务事件ID
                for item in self.data:
                    if item["id"] == approval_id:
                        business_id = item["business_event_id"]
                        self.create_finance_record(business_id)
                        break
            except Exception as e:
                QMessageBox.warning(self, "错误", f"创建财务记录时发生错误: {str(e)}")
    
    def create_finance_record(self, business_id):
        """创建财务记录"""
        QMessageBox.information(self, "功能开发中", f"为业务事件 ID: {business_id} 创建财务记录功能正在开发中")
        # 此处待实现财务记录创建功能
    
    def refresh_data(self):
        """刷新数据"""
        # 先加载所有待审批记录
        self.load_data("待审批")
        if len(self.data) > 0:
            QMessageBox.information(self, "刷新成功", f"找到 {len(self.data)} 条待审批记录")
        else:
            # 如果没有待审批记录，加载所有记录
            self.load_data()
            QMessageBox.information(self, "刷新成功", "审批数据已刷新")

    def filter_by_status(self):
        """按状态筛选"""
        status = self.status_filter.currentData()
        self.load_data(status)

    def load_business_approvals(self, business_id):
        """加载特定业务事件的审批任务"""
        try:
            response = requests.get(
                f"http://localhost:8000/business_events/{business_id}/approvals",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            print(f"查询业务事件 {business_id} 的审批任务")
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                approvals = response.json()
                if approvals and len(approvals) > 0:
                    QMessageBox.information(self, "查询结果", f"找到 {len(approvals)} 条审批记录")
                    self.data = approvals
                    self.display_data()
                    return True
                else:
                    QMessageBox.warning(self, "查询结果", "没有找到审批记录")
                    return False
            else:
                QMessageBox.warning(self, "查询失败", "无法获取审批记录")
                return False
        except Exception as e:
            print(f"查询审批记录时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"查询审批记录时发生错误: {str(e)}")
            return False

class ApprovalDetailDialog(QDialog):
    """审批详情对话框"""
    
    def __init__(self, approval_id, event_data, token):
        super().__init__()
        self.approval_id = approval_id
        self.event_data = event_data
        self.token = token
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("审批详情")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # 显示业务事件详情
        form_layout = QFormLayout()
        
        # 添加标题
        title_label = QLabel(f"审批详情 - {self.event_data['project_name']}")
        title_label.setProperty("class", "dialog-title")
        layout.addWidget(title_label)
        
        # 基本信息组
        info_group = QGroupBox("业务信息")
        info_form = QFormLayout(info_group)
        
        info_form.addRow("业务ID:", QLabel(str(self.event_data["id"])))
        info_form.addRow("事件类型:", QLabel(self.event_data["event_type"]))
        info_form.addRow("项目名称:", QLabel(self.event_data["project_name"]))
        info_form.addRow("项目编码:", QLabel(self.event_data.get("project_code", "无")))
        
        # 金额使用突出显示
        amount_label = QLabel(f"¥{self.event_data['amount']:,.2f}")
        amount_label.setProperty("class", "amount-label")
        info_form.addRow("金额:", amount_label)
        
        info_form.addRow("业务日期:", QLabel(self.event_data["event_date"]))
        
        # 当前状态
        status_label = QLabel(self.event_data["status"])
        if self.event_data["status"] == "待审批":
            status_label.setProperty("class", "status-pending-label")
        elif self.event_data["status"] == "已审批":
            status_label.setProperty("class", "status-approved-label")
        elif self.event_data["status"] == "已拒绝":
            status_label.setProperty("class", "status-rejected-label")
        info_form.addRow("当前状态:", status_label)
        
        layout.addWidget(info_group)
        
        # 描述信息
        if "description" in self.event_data and self.event_data["description"]:
            desc_group = QGroupBox("详细描述")
            desc_layout = QVBoxLayout(desc_group)
            
            desc_text = QTextEdit()
            desc_text.setPlainText(self.event_data["description"])
            desc_text.setReadOnly(True)
            desc_layout.addWidget(desc_text)
            
            layout.addWidget(desc_group)
        
        # 审批决定区域
        decision_group = QGroupBox("审批决定")
        decision_layout = QVBoxLayout(decision_group)
        
        # 添加审批意见输入框
        self.remarks_input = QTextEdit()
        self.remarks_input.setPlaceholderText("请输入审批意见...")
        self.remarks_input.setMaximumHeight(100)
        decision_layout.addWidget(QLabel("审批意见:"))
        decision_layout.addWidget(self.remarks_input)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.approve_button = QPushButton("通过审批")
        self.approve_button.setProperty("class", "approve-btn")
        self.approve_button.clicked.connect(self.approve)
        
        self.reject_button = QPushButton("拒绝审批")
        self.reject_button.setProperty("class", "reject-btn")
        self.reject_button.clicked.connect(self.reject_approval)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.approve_button)
        button_layout.addWidget(self.reject_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        
        decision_layout.addLayout(button_layout)
        layout.addWidget(decision_group)
        
    def approve(self):
        """审批通过"""
        try:
            remarks = self.remarks_input.toPlainText()
            
            # 调用更新状态接口
            status_response = requests.post(
                f"http://localhost:8000/approvals/{self.approval_id}/update-business-status",
                json={"status": "已审批", "remarks": remarks},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if status_response.status_code != 200:
                QMessageBox.warning(self, "状态更新失败", "无法更新业务事件状态")
            
            # 调用审批通过接口
            response = requests.post(
                f"http://localhost:8000/approvals/{self.approval_id}/approve",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "操作成功", "审批已通过")
                self.accept()
            else:
                QMessageBox.warning(self, "操作失败", f"审批通过失败: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"操作时发生错误: {str(e)}")
    
    def reject_approval(self):
        """审批拒绝"""
        try:
            remarks = self.remarks_input.toPlainText()
            
            # 调用更新状态接口
            status_response = requests.post(
                f"http://localhost:8000/approvals/{self.approval_id}/update-business-status",
                json={"status": "已拒绝", "remarks": remarks},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if status_response.status_code != 200:
                QMessageBox.warning(self, "状态更新失败", "无法更新业务事件状态")
            
            # 调用审批拒绝接口
            response = requests.post(
                f"http://localhost:8000/approvals/{self.approval_id}/reject",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "操作成功", "审批已拒绝")
                self.accept()
            else:
                QMessageBox.warning(self, "操作失败", f"审批拒绝失败: {response.text}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"操作时发生错误: {str(e)}") 
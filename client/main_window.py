import sys
import os
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                           QMessageBox, QStatusBar, QToolBar, QSizePolicy, QFrame,
                           QTabWidget, QToolButton, QMenu, QSplitter, QDialog, QFormLayout,
                           QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette, QPixmap

# 导入其他模块
from views.business_view import BusinessEventView
from views.finance_view import FinancialRecordView
from views.approval_view import ApprovalView
from views.budget_view import BudgetView
from login import LoginWindow

class MainWindow(QMainWindow):
    """主窗口类"""
    logout_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("FinanceApp", "BizFinanceSystem")
        self.user_data = None
        self.token = None
        
        # 检查是否已有token，如果有尝试自动登录
        token = self.settings.value("access_token", "")
        if token:
            self.try_auto_login(token)
        else:
            self.show_login()
            
    def try_auto_login(self, token):
        """尝试使用保存的token自动登录"""
        try:
            response = requests.get(
                "http://localhost:8000/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.login_successful({
                    "user": user_data,
                    "token": token
                })
            else:
                self.show_login()
        except:
            self.show_login()
    
    def show_login(self):
        """显示登录窗口"""
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.login_successful)
        self.login_window.show()
        
    def login_successful(self, data):
        """登录成功后的处理"""
        self.user_data = data["user"]
        self.token = data["token"]
        
        # 如果登录窗口存在，关闭它
        if hasattr(self, 'login_window') and self.login_window is not None:
            self.login_window.close()
            self.login_window = None
            
        # 初始化主界面
        self.init_ui()
        self.show()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("业财融合管理系统")
        self.setMinimumSize(1280, 900)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 使用分割器
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # 侧边导航栏
        self.nav_widget = QWidget()
        self.nav_widget.setObjectName("nav_widget")
        
        nav_layout = QVBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # 添加系统标题
        title_widget = QWidget()
        title_widget.setObjectName("title_widget")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(15, 20, 15, 20)
        
        # 使用水平布局来放置图标和标题
        title_header = QHBoxLayout()
        # 添加应用图标
        icon_label = QLabel()
        icon_label.setObjectName("app_icon")
        # 尝试加载图标，如果找不到则使用文本占位符
        try:
            pixmap = QPixmap("ui/assets/logo.png")
            icon_label.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
        except:
            icon_label.setText("📊")
            icon_label.setStyleSheet("font-size: 24px;")
        
        title_header.addWidget(icon_label)
        
        title_label = QLabel("业财融合管理系统")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_header.addWidget(title_label, 1)
        title_layout.addLayout(title_header)
        
        # 添加版本标签
        version_label = QLabel("V1.0.0")
        version_label.setObjectName("version_label")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(version_label)
        
        nav_layout.addWidget(title_widget)
        
        # 用户信息区域
        user_widget = QWidget()
        user_layout = QVBoxLayout(user_widget)
        user_layout.setContentsMargins(15, 20, 15, 20)
        
        # 添加用户头像标签
        user_avatar_label = QLabel("👤")  # 使用Emoji作为简单头像
        user_avatar_label.setObjectName("user_avatar_label")
        user_avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_avatar_label.setFixedSize(70, 70)
        
        user_header_layout = QHBoxLayout()
        user_header_layout.addStretch()
        user_header_layout.addWidget(user_avatar_label)
        user_header_layout.addStretch()
        user_layout.addLayout(user_header_layout)
        
        # 添加用户名和角色
        username_label = QLabel(f"{self.user_data['username']}")
        username_label.setObjectName("username_label")
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        role_label = QLabel(f"{self.user_data['role']}")
        role_label.setObjectName("role_label")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        user_layout.addWidget(username_label)
        user_layout.addWidget(role_label)
        nav_layout.addWidget(user_widget)
        
        # 添加分隔线
        separator = QFrame()
        separator.setObjectName("nav_separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(2)
        nav_layout.addWidget(separator)
        
        # 导航菜单标题
        nav_title = QLabel("功能导航")
        nav_title.setObjectName("nav_title")
        nav_layout.addWidget(nav_title)
        
        # 导航按钮
        self.create_nav_button("业务管理", "📊", "查看和管理业务数据", nav_layout, 0)
        
        # 根据角色显示导航项
        if self.user_data['role'] in ['管理员', '财务人员']:
            self.create_nav_button("财务管理", "💰", "管理公司财务记录和报表", nav_layout, 1)
            
        if self.user_data['role'] in ['管理员', '业务人员', '部门主管']:
            self.create_nav_button("审批管理", "✓", "处理待审批的业务和财务请求", nav_layout, 2)
            
        if self.user_data['role'] in ['管理员', '财务人员']:
            self.create_nav_button("预算管理", "📈", "监控和管理部门预算", nav_layout, 3)
            
        # 添加占位空间
        nav_layout.addStretch()
        
        # 添加设置按钮
        settings_btn = QPushButton("⚙ 系统设置")
        settings_btn.setObjectName("settings_btn")
        settings_btn.setToolTip("调整系统设置和个人偏好")
        settings_btn.clicked.connect(self.show_settings_dialog)
        nav_layout.addWidget(settings_btn)
        
        # 添加退出按钮
        logout_btn = QPushButton("🚪 退出登录")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setToolTip("退出当前账号并返回登录界面")
        logout_btn.clicked.connect(self.logout)
        nav_layout.addWidget(logout_btn)
        
        # 添加版权信息
        copyright_label = QLabel("© 2023 业财融合系统")
        copyright_label.setObjectName("copyright_label")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(copyright_label)
        
        # 添加导航栏到分割器
        self.main_splitter.addWidget(self.nav_widget)
        
        # 创建内容区域
        content_container = QWidget()
        content_container.setObjectName("content_container")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 添加内容标题栏
        self.header_widget = QWidget()
        self.header_widget.setObjectName("header_widget")
        self.header_widget.setFixedHeight(70)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.header_title = QLabel("业务管理")
        self.header_title.setObjectName("header_title")
        header_layout.addWidget(self.header_title)
        
        # 添加右侧用户信息和快捷操作
        header_layout.addStretch()
        
        # 添加快捷操作工具栏
        quick_actions = QToolBar()
        quick_actions.setObjectName("quick_actions")
        quick_actions.setIconSize(QSize(24, 24))
        
        # 添加刷新按钮
        refresh_action = QAction("🔄 刷新", self)
        refresh_action.setToolTip("刷新当前视图数据")
        refresh_action.triggered.connect(self.refresh_current_view)
        quick_actions.addAction(refresh_action)
        
        # 添加帮助按钮
        help_action = QAction("❓ 帮助", self) 
        help_action.setToolTip("获取功能帮助")
        help_action.triggered.connect(self.show_help)
        quick_actions.addAction(help_action)
        
        # 添加通知按钮
        notif_btn = QToolButton()
        notif_btn.setText("🔔")
        notif_btn.setToolTip("查看通知")
        notif_btn.setObjectName("notif_btn")
        quick_actions.addWidget(notif_btn)
        
        header_layout.addWidget(quick_actions)
        content_layout.addWidget(self.header_widget)
        
        # 创建选项卡式内容区域
        self.content_tabs = QTabWidget()
        self.content_tabs.setObjectName("content_tabs")
        self.content_tabs.setTabsClosable(False)
        self.content_tabs.setMovable(True)
        self.content_tabs.setDocumentMode(True)
        
        # 添加内容页面到选项卡
        self.business_view = BusinessEventView(self.token, self.user_data)
        self.content_tabs.addTab(self.business_view, "业务数据")
        
        if self.user_data['role'] in ['管理员', '财务人员']:
            self.finance_view = FinancialRecordView(self.token, self.user_data)
            self.content_tabs.addTab(self.finance_view, "财务记录")
        
        if self.user_data['role'] in ['管理员', '业务人员', '部门主管']:
            self.approval_view = ApprovalView(self.token, self.user_data)
            self.content_tabs.addTab(self.approval_view, "审批流程")
        
        if self.user_data['role'] in ['管理员', '财务人员']:
            self.budget_view = BudgetView(self.token, self.user_data)
            self.content_tabs.addTab(self.budget_view, "预算分析")
        
        # 添加选项卡区域到布局
        content_layout.addWidget(self.content_tabs)
        
        # 添加内容区域到分割器
        self.main_splitter.addWidget(content_container)
        
        # 设置分割器比例
        self.main_splitter.setSizes([260, 1020])
        self.main_splitter.setCollapsible(0, False)  # 防止导航栏被完全折叠
        
        # 设置状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 添加系统状态指示
        system_status = QLabel("系统就绪")
        system_status.setObjectName("status_system")
        
        server_status = QLabel("服务器: 已连接")
        server_status.setObjectName("status_server")
        
        user_status = QLabel(f"用户: {self.user_data['username']} ({self.user_data['role']})")
        user_status.setObjectName("status_user")
        
        # 添加到状态栏
        self.statusBar.addWidget(system_status)
        self.statusBar.addWidget(server_status)
        self.statusBar.addPermanentWidget(user_status)  # 永久显示在右侧
        
        # 连接选项卡切换信号
        self.content_tabs.currentChanged.connect(self.on_tab_changed)
        
        # 默认显示业务管理视图
        self.content_tabs.setCurrentIndex(0)
    
    def create_nav_button(self, text, icon, tooltip, layout, index):
        """创建导航按钮"""
        button = QPushButton(f"{icon} {text}")
        button.setProperty("class", "NavButton")  # 设置类属性用于CSS样式选择器
        button.setCheckable(True)
        button.setToolTip(tooltip)  # 添加工具提示
        
        # 连接点击事件
        button.clicked.connect(lambda: self.change_page(index, button, text))
        button.setObjectName(f"nav_{text}")
        layout.addWidget(button)
        
        # 默认选中第一个按钮
        if index == 0:
            button.setChecked(True)
            
        return button
    
    def change_page(self, index, button, title):
        """改变页面显示"""
        # 取消选中其他按钮
        for child in self.nav_widget.findChildren(QPushButton):
            if child.property("class") == "NavButton" and child != button:
                child.setChecked(False)
        
        # 设置当前按钮为选中状态
        button.setChecked(True)
        
        # 更新头部标题
        self.header_title.setText(title)
        
        # 切换到相应的选项卡
        if index == 0:
            self.content_tabs.setCurrentWidget(self.business_view)
        elif index == 1 and hasattr(self, 'finance_view'):
            self.content_tabs.setCurrentWidget(self.finance_view)
        elif index == 2 and hasattr(self, 'approval_view'):
            self.content_tabs.setCurrentWidget(self.approval_view)
        elif index == 3 and hasattr(self, 'budget_view'):
            self.content_tabs.setCurrentWidget(self.budget_view)
    
    def on_tab_changed(self, index):
        """处理选项卡切换事件"""
        # 获取当前选项卡的标题
        tab_title = self.content_tabs.tabText(index)
        
        # 找到对应的导航按钮并选中
        if tab_title == "业务数据":
            nav_button = self.findChild(QPushButton, "nav_业务管理")
            if nav_button:
                self.change_page(0, nav_button, "业务管理")
        elif tab_title == "财务记录":
            nav_button = self.findChild(QPushButton, "nav_财务管理")
            if nav_button:
                self.change_page(1, nav_button, "财务管理")
        elif tab_title == "审批流程":
            nav_button = self.findChild(QPushButton, "nav_审批管理")
            if nav_button:
                self.change_page(2, nav_button, "审批管理")
        elif tab_title == "预算分析":
            nav_button = self.findChild(QPushButton, "nav_预算管理")
            if nav_button:
                self.change_page(3, nav_button, "预算管理")
    
    def logout(self):
        """退出登录"""
        reply = QMessageBox.question(
            self, 
            '确认退出', 
            '确定要退出登录吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清除token
            self.settings.remove("access_token")
            
            # 关闭当前窗口并显示登录窗口
            self.close()
            self.show_login()
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        # 如果是由于退出登录导致的关闭，直接接受
        if not hasattr(self, 'login_window') or self.login_window is None:
            reply = QMessageBox.question(
                self, 
                '确认退出', 
                '确定要退出应用程序吗？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def refresh_current_view(self):
        """刷新当前视图的数据"""
        current_widget = self.content_tabs.currentWidget()
        
        if hasattr(current_widget, "load_data"):
            try:
                # 显示刷新中的状态
                self.statusBar.showMessage("正在刷新数据...", 2000)
                
                # 调用当前视图的load_data方法
                current_widget.load_data()
                
                # 更新状态栏
                self.statusBar.showMessage("数据刷新成功", 2000)
            except Exception as e:
                self.statusBar.showMessage(f"刷新失败: {str(e)}", 3000)
                QMessageBox.warning(self, "刷新失败", f"刷新数据时发生错误: {str(e)}")
        else:
            self.statusBar.showMessage("当前视图不支持刷新", 2000)

    def switch_to_business_view(self):
        """切换到业务管理视图"""
        if hasattr(self, "business_view"):
            self.content_tabs.setCurrentWidget(self.business_view)
            nav_button = self.findChild(QPushButton, "nav_业务管理")
            if nav_button:
                self.change_page(0, nav_button, "业务管理")

    def switch_to_finance_view(self):
        """切换到财务管理视图"""
        if hasattr(self, "finance_view"):
            self.content_tabs.setCurrentWidget(self.finance_view)
            nav_button = self.findChild(QPushButton, "nav_财务管理")
            if nav_button:
                self.change_page(1, nav_button, "财务管理")

    def switch_to_approval_view(self, approval_id=None):
        """切换到审批管理视图"""
        if hasattr(self, "approval_view"):
            self.content_tabs.setCurrentWidget(self.approval_view)
            nav_button = self.findChild(QPushButton, "nav_审批管理")
            if nav_button:
                self.change_page(2, nav_button, "审批管理")
            
            # 如果提供了审批ID，高亮显示对应的审批记录
            if approval_id and hasattr(self.approval_view, "highlight_approval"):
                self.approval_view.highlight_approval(approval_id)

    def switch_to_budget_view(self):
        """切换到预算管理视图"""
        if hasattr(self, "budget_view"):
            self.content_tabs.setCurrentWidget(self.budget_view)
            nav_button = self.findChild(QPushButton, "nav_预算管理")
            if nav_button:
                self.change_page(3, nav_button, "预算管理")

    def show_help(self):
        """显示帮助信息"""
        # 获取当前视图
        current_widget = self.content_tabs.currentWidget()
        help_title = "系统帮助"
        help_content = "这是业财融合管理系统的帮助信息。"
        
        # 根据当前视图显示不同的帮助信息
        if isinstance(current_widget, BusinessEventView):
            help_title = "业务管理帮助"
            help_content = """
            <h3>业务管理模块使用指南</h3>
            <p>业务管理模块用于创建和管理业务事件，包括合同、销售、采购和报销等类型的业务活动。</p>
            <h4>主要功能：</h4>
            <ul>
                <li><b>新建业务事件</b>：点击"新建业务事件"按钮，填写相关信息后保存。</li>
                <li><b>查看详情</b>：点击操作列中的"详情"按钮，查看业务事件的详细信息。</li>
                <li><b>提交审批</b>：对于"新建"状态的业务事件，可以点击"提交审批"按钮将其提交到审批流程。</li>
                <li><b>创建财务记录</b>：对于"已审批"状态的业务事件，可以点击"创建财务记录"按钮创建对应的财务记录。</li>
            </ul>
            <h4>搜索和筛选：</h4>
            <p>可以使用顶部的搜索框搜索项目名称，使用状态下拉框筛选不同状态的业务事件。</p>
            """
        elif isinstance(current_widget, FinancialRecordView):
            help_title = "财务管理帮助"
            help_content = """
            <h3>财务管理模块使用指南</h3>
            <p>财务管理模块用于创建和管理财务记录，将业务事件转化为财务数据。</p>
            <h4>主要功能：</h4>
            <ul>
                <li><b>新建财务记录</b>：点击"新建财务记录"按钮，选择关联的业务事件，填写财务信息后保存。</li>
                <li><b>查看详情</b>：点击操作列中的"详情"按钮，查看财务记录的详细信息。</li>
                <li><b>待处理业务</b>：在"待处理业务"选项卡中，可以查看已审批但尚未创建财务记录的业务事件。</li>
            </ul>
            <h4>注意事项：</h4>
            <p>创建财务记录时，需要选择正确的会计科目和收支方向，确保财务数据的准确性。</p>
            """
        elif isinstance(current_widget, ApprovalView):
            help_title = "审批管理帮助"
            help_content = """
            <h3>审批管理模块使用指南</h3>
            <p>审批管理模块用于处理业务事件的审批流程。</p>
            <h4>主要功能：</h4>
            <ul>
                <li><b>审批通过</b>：点击"通过"按钮，对业务事件进行审批通过操作。</li>
                <li><b>审批拒绝</b>：点击"拒绝"按钮，对业务事件进行审批拒绝操作。</li>
                <li><b>查看详情</b>：点击"详情"按钮，查看审批记录的详细信息。</li>
            </ul>
            <h4>审批流程：</h4>
            <p>业务事件提交审批后，会根据审批配置分配给相应的审批人。审批通过后，业务事件状态变为"已审批"，可以创建财务记录。</p>
            """
        elif isinstance(current_widget, BudgetView):
            help_title = "预算管理帮助"
            help_content = """
            <h3>预算管理模块使用指南</h3>
            <p>预算管理模块用于管理和监控各部门的预算使用情况。</p>
            <h4>主要功能：</h4>
            <ul>
                <li><b>预算编制</b>：设置各部门的预算金额。</li>
                <li><b>预算执行</b>：查看各部门的预算使用情况。</li>
                <li><b>预算分析</b>：分析预算执行情况，生成报表。</li>
            </ul>
            <h4>注意事项：</h4>
            <p>预算管理需要与财务记录关联，确保预算使用情况的准确性。</p>
            """
        
        # 创建帮助对话框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(help_title)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(help_content)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def show_settings_dialog(self):
        """显示系统设置对话框"""
        # 创建一个简单的设置对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("系统设置")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 添加设置选项
        form_layout = QFormLayout()
        
        # 主题设置
        theme_combo = QComboBox()
        theme_combo.addItems(["默认主题", "暗色主题", "浅色主题"])
        form_layout.addRow("界面主题:", theme_combo)
        
        # 字体大小设置
        font_size_combo = QComboBox()
        font_size_combo.addItems(["小", "中", "大"])
        font_size_combo.setCurrentIndex(1)  # 默认选中"中"
        form_layout.addRow("字体大小:", font_size_combo)
        
        # 自动刷新设置
        auto_refresh_check = QCheckBox("启用")
        form_layout.addRow("自动刷新:", auto_refresh_check)
        
        layout.addLayout(form_layout)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("保存")
        save_button.clicked.connect(dialog.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 保存设置
            self.settings.setValue("theme", theme_combo.currentText())
            self.settings.setValue("font_size", font_size_combo.currentText())
            self.settings.setValue("auto_refresh", auto_refresh_check.isChecked())
            
            QMessageBox.information(self, "设置已保存", "系统设置已保存，部分设置可能需要重启应用后生效")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局样式
    app.setStyle("Fusion")
    
    # 加载外部样式表
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "styles.css")
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    
    window = MainWindow()
    sys.exit(app.exec()) 
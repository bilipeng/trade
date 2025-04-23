import sys
import requests
import json
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                           QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
                           QCheckBox, QMainWindow, QFrame)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont

class LoginWindow(QWidget):
    """登录窗口"""
    login_success = pyqtSignal(dict)  # 登录成功信号，传递用户信息
    
    def __init__(self):
        super().__init__()
        
        self.settings = QSettings("FinanceApp", "BizFinanceSystem")
        self.init_ui()
        
    def init_ui(self):
        # 设置窗口
        self.setWindowTitle('业财融合管理系统 - 登录')
        self.setFixedSize(450, 600)
        self.setWindowIcon(QIcon('client/ui/assets/logo.png'))
        self.setObjectName("login_window")
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # 添加logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join('client', 'ui', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            # 如果找不到logo，使用文本替代
            logo_label = QLabel("💼")
            logo_label.setObjectName("logo_label")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        main_layout.addLayout(logo_layout)
        
        # 标题
        title_label = QLabel("业财融合管理系统")
        title_label.setObjectName("title_label_login")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("用户登录")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # 添加表单容器
        form_container = QFrame()
        form_container.setObjectName("form_container")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 25, 20, 25)
        form_layout.setSpacing(15)
        
        # 用户名
        username_label = QLabel("用户名")
        username_label.setObjectName("username_label_login")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setClearButtonEnabled(True)
        form_layout.addWidget(self.username_input)
        
        # 密码
        password_label = QLabel("密码")
        password_label.setObjectName("password_label")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setClearButtonEnabled(True)
        form_layout.addWidget(self.password_input)
        
        # 记住密码
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("记住密码")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        # 添加忘记密码链接
        forgot_password = QLabel("忘记密码?")
        forgot_password.setObjectName("forgot_password")
        remember_layout.addWidget(forgot_password)
        
        form_layout.addLayout(remember_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setObjectName("login_separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        form_layout.addWidget(separator)
        
        # 登录按钮
        self.login_button = QPushButton("登 录")
        self.login_button.setObjectName("loginButton")
        self.login_button.setFixedHeight(50)
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)
        
        # 显示系统默认用户信息
        default_users_info = QLabel("""<html>系统默认用户: <br>
                                    admin (管理员) <br>
                                    zhangsan (财务人员) <br>
                                    lisi (业务人员) <br>
                                    密码均为：admin 或 password123</html>""")
        default_users_info.setObjectName("default_users_info")
        default_users_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(default_users_info)
        
        main_layout.addWidget(form_container)
        
        # 读取保存的用户名密码
        if self.settings.value("remember_password", False, type=bool):
            self.remember_checkbox.setChecked(True)
            self.username_input.setText(self.settings.value("username", ""))
            self.password_input.setText(self.settings.value("password", ""))
        
        # 版本信息
        version_layout = QHBoxLayout()
        version_label = QLabel("© 2023 业财融合系统 v1.0.0")
        version_label.setObjectName("version_label_login")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_layout.addStretch()
        version_layout.addWidget(version_label)
        version_layout.addStretch()
        main_layout.addLayout(version_layout)
        
        self.setLayout(main_layout)
        
        # 设置Tab顺序
        self.username_input.setFocus()
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.remember_checkbox)
        self.setTabOrder(self.remember_checkbox, self.login_button)
        
        # 按Enter键登录
        self.username_input.returnPressed.connect(self.focus_password)
        self.password_input.returnPressed.connect(self.login)
    
    def focus_password(self):
        """当用户名输入完成后自动切换到密码输入框"""
        self.password_input.setFocus()
        
    def login(self):
        """登录处理"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "登录失败", "用户名和密码不能为空")
            return
        
        # 保存用户名密码设置
        if self.remember_checkbox.isChecked():
            self.settings.setValue("username", username)
            self.settings.setValue("password", password)
            self.settings.setValue("remember_password", True)
        else:
            self.settings.setValue("remember_password", False)
            self.settings.remove("username")
            self.settings.remove("password")
        
        # 添加登录中提示
        self.login_button.setEnabled(False)
        self.login_button.setText("登录中...")
        
        # 发送登录请求
        try:
            response = requests.post(
                "http://localhost:8000/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            self.login_button.setEnabled(True)
            self.login_button.setText("登 录")
            
            if response.status_code == 200:
                # 登录成功
                token_data = response.json()
                
                # 获取用户信息
                user_response = requests.get(
                    "http://localhost:8000/users/me",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"}
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    # 保存token
                    self.settings.setValue("access_token", token_data['access_token'])
                    
                    # 发送登录成功信号
                    self.login_success.emit({
                        "user": user_data,
                        "token": token_data['access_token']
                    })
            else:
                # 登录失败
                error_msg = "用户名或密码错误"
                if response.status_code != 401:
                    error_msg = f"服务器错误 ({response.status_code})"
                
                QMessageBox.warning(self, "登录失败", error_msg)
                
        except requests.exceptions.ConnectionError:
            self.login_button.setEnabled(True)
            self.login_button.setText("登 录")
            QMessageBox.critical(self, "连接错误", "无法连接到服务器，请检查网络连接和服务器状态")
        except Exception as e:
            self.login_button.setEnabled(True)
            self.login_button.setText("登 录")
            QMessageBox.critical(self, "错误", f"登录过程中发生错误: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 加载样式表
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "styles.css")
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
        
    window = LoginWindow()
    window.show()
    sys.exit(app.exec()) 
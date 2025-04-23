import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow

if __name__ == "__main__":
    # 添加当前目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("业财融合管理系统")
    
    # 设置应用图标
    icon_path = os.path.join(current_dir, "ui", "assets", "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 设置全局样式
    app.setStyle("Fusion")
    
    # 加载外部样式表
    style_path = os.path.join(current_dir, "ui", "styles.css")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    
    # 创建并显示主窗口
    window = MainWindow()
    
    # 运行应用
    sys.exit(app.exec()) 
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from PyQt6.QtCore import Qt

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
    
    # 加载外部样式表 - 使用深色主题
    style_path = os.path.join(current_dir, "ui", "styles.css")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    
    # 为Qt应用设置深色模式标志
    try:
        # 尝试设置高DPI图像属性，不同版本的PyQt可能有不同的属性名
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        elif hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    except AttributeError:
        # 如果属性不存在，忽略错误
        print("警告：无法设置高DPI图像属性，可能会影响在高分辨率显示器上的显示效果。")
    
    # 创建并显示主窗口
    window = MainWindow()
    
    # 运行应用
    sys.exit(app.exec()) 
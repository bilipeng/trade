#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库清理工具 - 强制删除数据库文件，解决锁定问题
"""

import os
import sys
import time
import shutil
import sqlite3
import subprocess
from pathlib import Path

# 定义路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_PATH = os.path.join(DATA_DIR, 'finance.db')

def main():
    print("=" * 50)
    print("业财融合管理系统 - 数据库清理工具")
    print("=" * 50)
    print()
    
    # 确保data目录存在
    if not os.path.exists(DATA_DIR):
        print(f"目录不存在，创建目录: {DATA_DIR}")
        os.makedirs(DATA_DIR)
    
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        print("无需清理，可以直接初始化新数据库。")
        return True
    
    print(f"发现数据库文件: {DB_PATH}")
    
    # 尝试关闭所有连接
    print("尝试关闭数据库连接...")
    try:
        # 尝试使用临时连接强制关闭
        temp_conn = sqlite3.connect(DB_PATH)
        temp_conn.close()
        print("数据库连接已关闭")
    except:
        print("无法关闭现有连接，将尝试强制删除")
    
    # 在Windows上尝试终止可能使用数据库的进程
    if os.name == 'nt':
        try:
            print("尝试停止所有Python进程...")
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Python进程已停止")
            time.sleep(1)  # 给系统一点时间
        except:
            print("无法停止Python进程，继续尝试删除...")
    
    # 尝试删除文件
    print(f"尝试删除数据库文件: {DB_PATH}")
    
    success = False
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        try:
            # 创建备份
            if attempt == 1:
                try:
                    backup_path = f"{DB_PATH}.bak.{int(time.time())}"
                    shutil.copy2(DB_PATH, backup_path)
                    print(f"已创建备份: {backup_path}")
                except:
                    print("无法创建备份，继续尝试删除...")
            
            # 尝试删除
            os.remove(DB_PATH)
            print(f"成功删除数据库文件!")
            success = True
            break
        except Exception as e:
            print(f"尝试 {attempt}/{max_attempts} 失败: {e}")
            if attempt < max_attempts:
                print(f"等待2秒后重试...")
                time.sleep(2)
    
    if success:
        print("数据库文件已成功删除，可以进行初始化操作。")
        return True
    else:
        print("无法删除数据库文件，请确保没有程序正在使用它。")
        print("建议手动关闭所有相关应用后再试。")
        return False

if __name__ == "__main__":
    success = main()
    # 退出码 - 0表示成功
    sys.exit(0 if success else 1) 
 
 
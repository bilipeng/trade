#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
业财融合管理系统 - 数据库初始化工具
用于创建数据库结构并导入示例数据
"""

import os
import sys
import sqlite3
import shutil
import time
from datetime import datetime

# 定义路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_PATH = os.path.join(DATA_DIR, 'finance.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
SAMPLE_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_data.sql')

def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"已创建目录: {directory}")

def execute_sql_file(conn, cursor, file_path, continue_on_error=True):
    """执行SQL文件中的语句"""
    print(f"正在执行SQL文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("尝试使用executescript方法执行完整SQL脚本...")
        try:
            # 首先尝试使用executescript执行整个脚本
            conn.executescript(content)
            conn.commit()
            print("SQL脚本执行成功!")
            return len(content.split(';')) - 1, 0  # 大致估计执行的语句数
        except sqlite3.Error as e:
            print(f"整体执行失败: {str(e)}")
            print("回退，尝试逐条执行...")
            conn.rollback()
            
            # 如果整体执行失败，尝试逐条执行
            # 分割SQL语句
            statements = []
            current_statement = []
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('--'):  # 跳过空行和注释
                    continue
                    
                current_statement.append(line)
                if line.endswith(';'):
                    statements.append(' '.join(current_statement))
                    current_statement = []
            
            # 如果最后一条语句没有分号，也添加进来
            if current_statement:
                statements.append(' '.join(current_statement))
                
            # 执行SQL语句
            success_count = 0
            error_count = 0
            
            print(f"找到 {len(statements)} 条SQL语句")
            
            for i, statement in enumerate(statements):
                if not statement.strip():
                    continue
                    
                try:
                    cursor.execute(statement)
                    success_count += 1
                    if (i + 1) % 10 == 0:  # 每执行10条显示一次进度
                        print(f"进度: {i+1}/{len(statements)}")
                except sqlite3.Error as e:
                    error_count += 1
                    print(f"执行SQL出错 ({i+1}/{len(statements)}): {str(e)}")
                    print(f"问题语句: {statement[:150]}..." if len(statement) > 150 else f"问题语句: {statement}")
                    
                    if not continue_on_error:
                        choice = input("是否继续执行? (y/n): ")
                        if choice.lower() != 'y':
                            raise
            
            conn.commit()
            print(f"SQL逐条执行完成: 成功 {success_count} 条, 失败 {error_count} 条")
            return success_count, error_count
            
    except Exception as e:
        conn.rollback()
        print(f"执行SQL文件出错: {str(e)}")
        return 0, 0

def initialize_database(auto_yes=False):
    """初始化数据库
    
    Args:
        auto_yes: 是否自动回答'是'进行初始化和导入样例数据
    """
    print("=" * 50)
    print("业财融合管理系统 - 数据库初始化工具")
    print("=" * 50)
    print()
    
    # 确保data目录存在
    ensure_dir(DATA_DIR)
    
    # 检查数据库文件是否已存在
    if os.path.exists(DB_PATH):
        if auto_yes:
            choice = 'y'
            print(f"数据库文件 {DB_PATH} 已存在。自动执行重新初始化...")
        else:
            print(f"数据库文件 {DB_PATH} 已存在。是否重新初始化? (y/n): ", end="")
            choice = input().strip().lower()
        
        if choice != 'y':
            print("操作已取消。")
            return False
        
        # 备份现有数据库
        backup_path = f"{DB_PATH}.bak.{int(time.time())}"
        try:
            shutil.copy2(DB_PATH, backup_path)
            print(f"已备份现有数据库到 {backup_path}")
        except Exception as e:
            print(f"备份数据库失败: {str(e)}")
            print("操作已取消。")
            return False
    
    # 连接到数据库
    try:
        print(f"连接到数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 执行schema.sql创建表结构
        print("正在创建数据库表结构...")
        success, errors = execute_sql_file(conn, cursor, SCHEMA_PATH, continue_on_error=True)
        if success > 0:
            print("数据库架构创建成功完成。")
            
            # 询问是否导入示例数据
            if auto_yes:
                choice = 'y'
                print("自动执行导入示例数据...")
            else:
                print("是否导入示例数据? (y/n): ", end="")
                choice = input().strip().lower()
            
            if choice == 'y':
                # 执行sample_data.sql导入示例数据
                print("正在导入示例数据...")
                execute_sql_file(conn, cursor, SAMPLE_DATA_PATH, continue_on_error=True)
                print("示例数据导入成功完成！")
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
        print()
        print("数据库初始化全部完成！")
        return True
        
    except Exception as e:
        print(f"初始化数据库时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        # 自动模式
        initialize_database(auto_yes=True)
    else:
        # 交互模式
        initialize_database() 
 
 
import sqlite3

def add_approval_configs():
    """添加审批配置"""
    try:
        conn = sqlite3.connect('database/finance.db')
        cursor = conn.cursor()
        
        # 检查当前审批配置
        cursor.execute("SELECT COUNT(*) FROM approval_configs")
        count = cursor.fetchone()[0]
        print(f"当前审批配置数量: {count}")
        
        if count == 0:
            # 添加管理员审批配置 (假设ID为1)
            cursor.execute('''
                INSERT INTO approval_configs 
                (event_type, department_id, approver_id, approval_level, amount_threshold, is_active)
                VALUES
                ("销售", 3, 1, 1, 0.0, 1),
                ("采购", 4, 1, 1, 0.0, 1),
                ("合同", 3, 1, 1, 0.0, 1),
                ("报销", 2, 1, 1, 0.0, 1)
            ''')
            
            # 添加审批人员审批配置
            cursor.execute('''
                INSERT INTO approval_configs 
                (event_type, department_id, approver_id, approval_level, amount_threshold, is_active)
                VALUES
                ("销售", 3, 10, 2, 1000.0, 1),
                ("采购", 4, 10, 2, 1000.0, 1),
                ("合同", 3, 10, 2, 1000.0, 1),
                ("报销", 2, 12, 2, 500.0, 1)
            ''')
            
            # 针对系统管理部门添加配置
            cursor.execute('''
                INSERT INTO approval_configs 
                (event_type, department_id, approver_id, approval_level, amount_threshold, is_active)
                VALUES
                ("销售", 1, 1, 1, 0.0, 1),
                ("采购", 1, 1, 1, 0.0, 1),
                ("合同", 1, 1, 1, 0.0, 1),
                ("报销", 1, 1, 1, 0.0, 1)
            ''')
            
            conn.commit()
            print("已成功添加审批配置")
            
            # 验证添加结果
            cursor.execute("SELECT COUNT(*) FROM approval_configs")
            count = cursor.fetchone()[0]
            print(f"添加后审批配置数量: {count}")
        else:
            print("已存在审批配置，不需要添加")
        
        conn.close()
        return True
    except Exception as e:
        print(f"添加审批配置时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    add_approval_configs() 
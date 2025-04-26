from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
from functools import wraps
import jwt

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS
app.config['SECRET_KEY'] = 'your-secret-key'  # 在生产环境中应该使用环境变量

# 数据库连接
def get_db_connection():
    conn = sqlite3.connect(
        os.path.join(os.path.dirname(__file__), '..', 'database', 'finance.db'),
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    conn.row_factory = sqlite3.Row
    return conn

# 认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '无效的认证令牌格式'}), 401
        
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # 这里可以添加用户验证逻辑
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '认证令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的认证令牌'}), 401

        return f(*args, **kwargs)
    return decorated

# 登录接口
@app.route('/token', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': '缺少认证信息'}), 401
    
    # 这里应该查询数据库验证用户，这里简化处理
    if auth.username == "admin" and auth.password == "password":
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'expires_in': 24 * 3600
        })
    
    return jsonify({'message': '认证失败'}), 401

# 用户信息接口
@app.route('/users/me', methods=['GET'])
@token_required
def get_current_user():
    # 模拟用户数据
    return jsonify({
        'id': 1,
        'username': 'admin',
        'role': '管理员',
        'department': '系统管理',
        'email': 'admin@example.com'
    })

# 部门接口
@app.route('/departments', methods=['GET'])
@token_required
def get_departments():
    conn = get_db_connection()
    departments = conn.execute('SELECT * FROM departments').fetchall()
    conn.close()
    return jsonify([dict(dept) for dept in departments])

# 业务事件接口
@app.route('/business_events', methods=['GET', 'POST'])
@token_required
def business_events():
    conn = get_db_connection()
    
    if request.method == 'GET':
        events = conn.execute('''
            SELECT be.*, d.name as department_name, c.name as customer_name
            FROM business_events be
            LEFT JOIN departments d ON be.department_id = d.id
            LEFT JOIN customers c ON be.customer_id = c.id
            ORDER BY be.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(event) for event in events])
    
    elif request.method == 'POST':
        data = request.json
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO business_events (
                project_name, project_code, event_type, amount, event_date,
                description, department_id, customer_id, created_by, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['project_name'],
            data.get('project_code'),
            data['event_type'],
            data['amount'],
            data['event_date'],
            data.get('description'),
            data['department_id'],
            data.get('customer_id'),
            data['created_by'],
            'pending'
        ))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'id': event_id, 'message': '业务事件创建成功'})

# 科目接口
@app.route('/account_subjects', methods=['GET'])
@token_required
def get_account_subjects():
    conn = get_db_connection()
    subjects = conn.execute('SELECT * FROM account_subjects').fetchall()
    conn.close()
    return jsonify([dict(subj) for subj in subjects])

# 财务交易接口
@app.route('/financial_transactions', methods=['GET', 'POST'])
@token_required
def financial_transactions():
    conn = get_db_connection()
    
    if request.method == 'GET':
        transactions = conn.execute('''
            SELECT ft.*, be.project_name, be.event_type
            FROM financial_transactions ft
            JOIN business_events be ON ft.business_event_id = be.id
            ORDER BY ft.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(tx) for tx in transactions])
    
    elif request.method == 'POST':
        data = request.json
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO financial_transactions (
                business_event_id, account_subject_id, amount, direction,
                transaction_date, description, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['business_event_id'],
            data['account_subject_id'],
            data['amount'],
            data['direction'],
            data['transaction_date'],
            data.get('description'),
            data['created_by']
        ))
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'id': tx_id, 'message': '财务交易创建成功'})

# 审批接口
@app.route('/approvals', methods=['GET', 'POST'])
@token_required
def approvals():
    conn = get_db_connection()
    
    if request.method == 'GET':
        approvals = conn.execute('''
            SELECT a.*, be.project_name, be.event_type, be.amount, u.username as approver_name
            FROM approvals a
            JOIN business_events be ON a.business_event_id = be.id
            LEFT JOIN users u ON a.approver_id = u.id
            ORDER BY a.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(approval) for approval in approvals])
    
    elif request.method == 'POST':
        data = request.json
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO approvals (
                business_event_id, approver_id, approval_level,
                status, comment
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            data['business_event_id'],
            data['approver_id'],
            data['approval_level'],
            'pending',
            data.get('comment')
        ))
        approval_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'id': approval_id, 'message': '审批创建成功'})

# 预算接口
@app.route('/budgets', methods=['GET'])
@token_required
def get_budgets():
    year = request.args.get('year', datetime.now().year)
    conn = get_db_connection()
    budgets = conn.execute('''
        SELECT b.*, d.name as department_name
        FROM budgets b
        JOIN departments d ON b.department_id = d.id
        WHERE b.year = ?
    ''', (year,)).fetchall()
    conn.close()
    return jsonify([dict(budget) for budget in budgets])

# 业财看板API
@app.route('/api/projects/stats', methods=['GET'])
@token_required
def get_project_stats():
    """获取项目统计数据"""
    # 模拟数据
    return jsonify({
        "total_projects": 12,
        "total_budget": 1500000.00,
        "completed_projects": 5,
        "in_progress_projects": 7
    })

@app.route('/api/alerts/stats', methods=['GET'])
@token_required
def get_alert_stats():
    """获取预警统计数据"""
    # 模拟数据
    return jsonify({
        "total_alerts": 8,
        "unhandled_alerts": 3,
        "high_priority_alerts": 2,
        "medium_priority_alerts": 4,
        "low_priority_alerts": 2
    })

@app.route('/api/projects/progress', methods=['GET'])
@token_required
def get_project_progress():
    """获取项目进度数据"""
    # 模拟数据
    return jsonify({
        "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
        "planned_progress": [100, 80, 60, 40, 20],
        "actual_progress": [95, 70, 65, 30, 25]
    })

@app.route('/api/projects/budget', methods=['GET'])
@token_required
def get_project_budget():
    """获取项目预算数据"""
    # 模拟数据
    return jsonify({
        "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
        "budget": [500000, 300000, 200000, 150000, 100000],
        "spent": [480000, 250000, 180000, 100000, 90000]
    })

@app.route('/api/alert-rules', methods=['GET'])
@token_required
def get_alert_rules():
    """获取预警规则列表"""
    # 模拟数据
    return jsonify([
        {
            "id": 1,
            "name": "预算超支预警",
            "indicator": "预算超支",
            "condition": "大于",
            "threshold": 10.0,
            "severity": "高",
            "is_active": True
        },
        {
            "id": 2,
            "name": "进度延迟预警",
            "indicator": "进度延迟",
            "condition": "大于",
            "threshold": 15.0,
            "severity": "中",
            "is_active": True
        },
        {
            "id": 3,
            "name": "回款逾期预警",
            "indicator": "回款逾期",
            "condition": "大于",
            "threshold": 30.0,
            "severity": "高",
            "is_active": True
        }
    ])

@app.route('/api/alerts', methods=['GET'])
@token_required
def get_alerts():
    """获取预警记录列表"""
    # 模拟数据
    return jsonify([
        {
            "id": 1,
            "time": "2023-06-15 10:30:00",
            "rule_name": "预算超支预警",
            "target": "项目A",
            "current_value": 12.5,
            "status": "未处理"
        },
        {
            "id": 2,
            "time": "2023-06-14 15:45:00",
            "rule_name": "进度延迟预警",
            "target": "项目B",
            "current_value": 18.2,
            "status": "未处理"
        },
        {
            "id": 3,
            "time": "2023-06-13 09:15:00",
            "rule_name": "回款逾期预警",
            "target": "项目C",
            "current_value": 45.0,
            "status": "未处理"
        }
    ])

@app.route('/api/alert-rules/<int:rule_id>', methods=['DELETE'])
@token_required
def delete_alert_rule(rule_id):
    """删除预警规则"""
    # 模拟删除成功
    return jsonify({"message": "预警规则删除成功"})

@app.route('/api/alerts/<int:alert_id>/handle', methods=['POST'])
@token_required
def handle_alert(alert_id):
    """处理预警"""
    # 模拟处理成功
    return jsonify({"message": "预警处理成功"})

@app.route('/api/alerts/<int:alert_id>/ignore', methods=['POST'])
@token_required
def ignore_alert(alert_id):
    """忽略预警"""
    # 模拟忽略成功
    return jsonify({"message": "预警已忽略"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

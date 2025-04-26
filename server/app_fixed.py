from flask import Flask, jsonify, request, g
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
import jwt

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS
app.config['SECRET_KEY'] = 'your-secret-key'  # 在生产环境中应该使用环境变量
app.config['TOKEN_EXPIRE_HOURS'] = 24

# 认证装饰器
def token_required(f):
    from functools import wraps
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
            g.current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '认证令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的认证令牌'}), 401

        return f(*args, **kwargs)
    return decorated

# 登录路由
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': '缺少认证信息'}), 401
    
    # 这里应该查询数据库验证用户，这里简化处理
    if auth.username == "admin" and auth.password == "password":
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.utcnow() + timedelta(hours=app.config['TOKEN_EXPIRE_HOURS'])
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'expires_in': app.config['TOKEN_EXPIRE_HOURS'] * 3600
        })
    
    return jsonify({'message': '认证失败'}), 401

# 数据库连接
def get_db_connection():
    try:
        conn = sqlite3.connect(
            os.path.join(os.path.dirname(__file__), '..', 'database', 'finance.db'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"数据库连接错误: {str(e)}")
        return None

# 财务交易接口
@app.route('/api/financial_transactions', methods=['GET'])
@token_required
def get_financial_transactions():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ft.*, be.project_name, be.event_type
            FROM financial_transactions ft
            JOIN business_events be ON ft.business_event_id = be.id
            ORDER BY ft.created_at DESC
        """)
        transactions = cursor.fetchall()
        return jsonify([dict(tx) for tx in transactions])
    finally:
        conn.close()

# 业财看板API
@app.route('/api/dashboard/business-finance', methods=['GET'])
@token_required
def get_business_finance():
    # 模拟数据
    return jsonify({
        'revenue': 1000000,
        'expenses': 800000,
        'profit': 200000,
        'growth_rate': 15.5
    })

# 预警中心API
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

@app.route('/api/alert-rules', methods=['GET', 'POST', 'DELETE'])
@token_required
def alert_rules():
    if request.method == 'GET':
        # 获取预警规则列表
        return jsonify([
            {'id': 1, 'name': '收入异常预警', 'condition': 'revenue < 1000000'},
            {'id': 2, 'name': '支出异常预警', 'condition': 'expenses > 1000000'}
        ])
    elif request.method == 'POST':
        # 创建新预警规则
        data = request.json
        return jsonify({'message': '预警规则创建成功', 'rule_id': 3})
    elif request.method == 'DELETE':
        # 删除预警规则
        rule_id = request.args.get('id')
        return jsonify({'message': f'预警规则 {rule_id} 删除成功'})

@app.route('/api/alerts', methods=['GET', 'POST'])
@token_required
def alerts():
    if request.method == 'GET':
        # 获取预警列表
        return jsonify([
            {'id': 1, 'rule_id': 1, 'message': '收入低于预期', 'status': 'active'},
            {'id': 2, 'rule_id': 2, 'message': '支出超出预算', 'status': 'handled'}
        ])
    elif request.method == 'POST':
        # 处理预警
        data = request.json
        return jsonify({'message': '预警处理成功'})

# 示例受保护的API端点
@app.route('/api/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': '这是一个受保护的API端点'})

# 健康检查
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

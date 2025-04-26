from flask import Blueprint, jsonify, request, g
import sqlite3
import os
from datetime import datetime
from auth_utils import token_required
import traceback

api = Blueprint('api', __name__)

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

# 统一的错误处理装饰器
def handle_errors(f):
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({
                'error': '服务器内部错误',
                'message': str(e)
            }), 500
    return decorated

# 注意：修改了装饰器的顺序，将路由装饰器放在最外层
@api.route('/financial_transactions', methods=['GET'])
@token_required
@handle_errors
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
@api.route('/dashboard/business-finance', methods=['GET'])
@token_required
@handle_errors
def get_business_finance():
    # 模拟数据
    return jsonify({
        'revenue': 1000000,
        'expenses': 800000,
        'profit': 200000,
        'growth_rate': 15.5
    })

# 预警中心API
@api.route('/projects/stats', methods=['GET'])
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

@api.route('/alerts/stats', methods=['GET'])
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

@api.route('/projects/progress', methods=['GET'])
@token_required
def get_project_progress():
    """获取项目进度数据"""
    # 模拟数据
    return jsonify({
        "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
        "planned_progress": [100, 80, 60, 40, 20],
        "actual_progress": [95, 70, 65, 30, 25]
    })

@api.route('/projects/budget', methods=['GET'])
@token_required
def get_project_budget():
    """获取项目预算数据"""
    # 模拟数据
    return jsonify({
        "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
        "budget": [500000, 300000, 200000, 150000, 100000],
        "spent": [480000, 250000, 180000, 100000, 90000]
    })

@api.route('/alert-rules', methods=['GET', 'POST', 'DELETE'])
@token_required
@handle_errors
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

@api.route('/alerts', methods=['GET', 'POST'])
@token_required
@handle_errors
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

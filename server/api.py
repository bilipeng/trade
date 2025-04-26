from flask import Blueprint, jsonify, request, g
from .auth import token_required
import sqlite3
import os
import traceback

api_bp = Blueprint('api', __name__)

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

@api_bp.route('/financial_transactions', methods=['GET'])
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

@api_bp.route('/projects/stats', methods=['GET'])
@token_required
def get_project_stats():
    """获取项目统计数据"""
    return jsonify({
        "total_projects": 12,
        "total_budget": 1500000.00,
        "completed_projects": 5,
        "in_progress_projects": 7
    })

@api_bp.route('/alerts/stats', methods=['GET'])
@token_required
def get_alert_stats():
    """获取预警统计数据"""
    return jsonify({
        "total_alerts": 8,
        "unhandled_alerts": 3,
        "high_priority_alerts": 2,
        "medium_priority_alerts": 4,
        "low_priority_alerts": 2
    })

@api_bp.route('/projects/progress', methods=['GET'])
@token_required
def get_project_progress():
    """获取项目进度数据"""
    return jsonify({
        "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
        "planned_progress": [100, 80, 60, 40, 20],
        "actual_progress": [95, 70, 65, 30, 25]
    })

@api_bp.route('/projects/budget', methods=['GET'])
@token_required
def get_project_budget():
    """获取项目预算数据"""
    return jsonify({
        "names": ["项目A", "项目B", "项目C", "项目D", "项目E"],
        "budget": [500000, 300000, 200000, 150000, 100000],
        "spent": [480000, 250000, 180000, 100000, 90000]
    })

@api_bp.route('/alert-rules', methods=['GET', 'POST', 'DELETE'])
@token_required
@handle_errors
def alert_rules():
    if request.method == 'GET':
        return jsonify([
            {'id': 1, 'name': '收入异常预警', 'condition': 'revenue < 1000000'},
            {'id': 2, 'name': '支出异常预警', 'condition': 'expenses > 1000000'}
        ])
    elif request.method == 'POST':
        data = request.json
        return jsonify({'message': '预警规则创建成功', 'rule_id': 3})
    elif request.method == 'DELETE':
        rule_id = request.args.get('id')
        return jsonify({'message': f'预警规则 {rule_id} 删除成功'})

@api_bp.route('/alerts', methods=['GET', 'POST'])
@token_required
@handle_errors
def alerts():
    if request.method == 'GET':
        return jsonify([
            {'id': 1, 'rule_id': 1, 'message': '收入低于预期', 'status': 'active'},
            {'id': 2, 'rule_id': 2, 'message': '支出超出预算', 'status': 'handled'}
        ])
    elif request.method == 'POST':
        data = request.json
        return jsonify({'message': '预警处理成功'}) 
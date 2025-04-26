from flask import Blueprint, request, jsonify
from .auth import verify_user, create_user, user_exists
from .auth_utils import token_required, generate_token, TOKEN_EXPIRE_HOURS

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """注册新用户"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    if user_exists(username):
        return jsonify({'message': '用户名已存在'}), 409
        
    if create_user(username, password):
        return jsonify({'message': '注册成功'}), 201
    else:
        return jsonify({'message': '注册失败'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    if verify_user(username, password):
        token = generate_token(username, TOKEN_EXPIRE_HOURS)
        return jsonify({
            'message': '登录成功',
            'token': token,
            'expires_in': TOKEN_EXPIRE_HOURS * 3600
        })
    else:
        return jsonify({'message': '用户名或密码错误'}), 401

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify(current_user):
    """验证token"""
    return jsonify({'message': 'token有效'}) 
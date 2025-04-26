from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta
from .auth import create_user, verify_password, get_user

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# JWT配置
SECRET_KEY = 'your-secret-key'  # 在生产环境中应使用安全的密钥
TOKEN_EXPIRATION = 24  # token有效期(小时)

def generate_token(username):
    """生成JWT token"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    """验证token的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '无效的token格式'}), 401
        
        if not token:
            return jsonify({'message': '缺少token'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = get_user(data['username'])
            if not current_user:
                return jsonify({'message': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的token'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """注册新用户"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    if create_user(username, password):
        return jsonify({'message': '注册成功'}), 201
    else:
        return jsonify({'message': '用户名已存在'}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    if verify_password(username, password):
        token = generate_token(username)
        return jsonify({
            'token': token,
            'expires_in': TOKEN_EXPIRATION * 3600
        }), 200
    else:
        return jsonify({'message': '用户名或密码错误'}), 401

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """验证token"""
    return jsonify({'message': 'token有效', 'username': current_user[1]}), 200 
from functools import wraps
from flask import jsonify, request, g
import jwt
from datetime import datetime, timedelta

# JWT配置
SECRET_KEY = 'your-secret-key'  # 在生产环境中应该使用环境变量
TOKEN_EXPIRE_HOURS = 24

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
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '认证令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的认证令牌'}), 401

        return f(*args, **kwargs)
    return decorated

def generate_token(username, expire_hours=24):
    """生成JWT token"""
    payload = {
        'user': username,
        'exp': datetime.utcnow() + timedelta(hours=expire_hours)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256') 
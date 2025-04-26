import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request, g, current_app
import hashlib
import sqlite3
import os

DB_PATH = 'users.db'

def init_auth_db():
    """初始化认证数据库"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

def hash_password(password):
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    """根据用户名获取用户信息"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, password):
    """创建新用户"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                 (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_password(username, password):
    """验证用户密码"""
    user = get_user(username)
    if user:
        return user[2] == hash_password(password)
    return False

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
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
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
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_user(username, password):
    """验证用户凭据"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?',
             (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def user_exists(username):
    """检查用户是否存在"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user is not None

# 初始化数据库并创建默认管理员用户
init_auth_db()
if not verify_password('admin', 'admin123'):
    create_user('admin', 'admin123') 
from flask import Flask, jsonify, request
from flask_cors import CORS
from .config import Config
from .api import api_bp
from .auth import init_auth_db, verify_user, generate_token

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 登录路由
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        if verify_user(username, password):
            token = generate_token(username, app.config['TOKEN_EXPIRE_HOURS'])
            return jsonify({
                'token': token,
                'expires_in': app.config['TOKEN_EXPIRE_HOURS'] * 3600
            })
        
        return jsonify({'message': '用户名或密码错误'}), 401
    
    # 健康检查
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok'})
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # 初始化数据库
    init_auth_db()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
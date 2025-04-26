class Config:
    SECRET_KEY = 'your-secret-key'  # 在生产环境中应该使用环境变量
    TOKEN_EXPIRE_HOURS = 24
    DATABASE_PATH = 'database/app.db' 
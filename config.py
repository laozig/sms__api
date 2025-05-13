import os

class Config:
    """应用配置类"""
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///sms_api.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库连接池配置 - 使用标准的SQLAlchemy引擎参数
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 1800,  # 30分钟后回收连接
        'pool_pre_ping': True  # 使用前测试连接是否有效
    }
    
    # JWT配置
    JWT_EXPIRATION_DAYS = 30
    
    # 应用端口
    PORT = int(os.environ.get('PORT', 5000))


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境应该使用环境变量设置的强密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 生产环境推荐使用更可靠的数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    
    # 生产环境数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 30,
        'max_overflow': 50,
        'pool_timeout': 60,
        'pool_recycle': 1800,
        'pool_pre_ping': True
    }


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 
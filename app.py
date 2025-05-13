from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler
from models import db, User, Project, PhoneNumber, BlacklistedPhone
from config import config

# 配置日志
def configure_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/sms_api.log', maxBytes=10240, backupCount=10, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SMS API启动')

def create_app(config_name='default'):
    """
    创建Flask应用实例
    
    参数:
    - config_name: 配置类型名称，可选值：development, production, testing, default
    
    返回:
    - app: Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    CORS(app)  # 启用CORS支持跨域请求
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 配置日志
    configure_logging(app)
    
    # 初始化数据库实例
    db.init_app(app)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': '资源未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error('服务器错误: %s', str(error))
        return jsonify({'error': '服务器内部错误'}), 500
    
    # 添加静态文件路由
    @app.route('/')
    def index():
        return app.send_static_file('ty.html')
    
    @app.route('/api-docs')
    def api_docs():
        return app.send_static_file('index.html')
    
    @app.route('/index.html')
    def index_html():
        return app.send_static_file('index.html')
    
    # 导入并注册路由
    from routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    return app

# 创建数据库表
def create_tables(app):
    with app.app_context():
        db.create_all()
        app.logger.info("数据库表创建成功")

# 主入口
if __name__ == '__main__':
    # 获取配置模式
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # 创建应用
    app = create_app(config_name)
    
    # 创建数据库表
    create_tables(app)
    
    # 开发环境使用Flask内置服务器
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
    
# 生产环境建议使用Gunicorn启动
# 命令: gunicorn -w 4 -b 0.0.0.0:5000 app:create_app\('production'\) --timeout 120 --preload
#   -w: 工作进程数，建议设置为 CPU核心数 * 2 + 1
#   --timeout: 请求超时时间(秒)
#   --access-logfile: 访问日志文件路径，例如 --access-logfile logs/access.log
#   --error-logfile: 错误日志文件路径，例如 --error-logfile logs/error.log
#   --preload: 预加载应用提高性能 
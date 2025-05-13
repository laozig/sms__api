import datetime
from flask_sqlalchemy import SQLAlchemy

# 初始化一个空的SQLAlchemy对象，稍后再用app对象初始化它
db = SQLAlchemy()

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    security_question = db.Column(db.String(200), nullable=False)
    token = db.Column(db.String(500), nullable=True)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # 手机号关联
    phone_numbers = db.relationship('PhoneNumber', backref='user', lazy=True)
    blacklisted_phones = db.relationship('BlacklistedPhone', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """将用户信息转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'token': self.token,
            'balance': self.balance
        }

# 项目模型
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, default=0.1)  # 项目价格
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self):
        """将项目信息转换为字典"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'amount': self.amount
        }

# 手机号模型
class PhoneNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Integer, default=1)  # 1=有效，0=已使用
    carrier_type = db.Column(db.Integer, default=0)  # 0=不限，1=移动，2=联通，3=电信
    number_type = db.Column(db.Integer, default=0)  # 0=不限，1=正常，2=虚拟
    frozen_amount = db.Column(db.Float, default=0.0)  # 冻结的余额
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<PhoneNumber {self.phone}>'
    
    def to_dict(self):
        """将手机号码信息转换为字典"""
        return {
            'phone': self.phone,
            'project_id': self.project_id,
            'carrier_type': self.carrier_type,
            'number_type': self.number_type,
            'status': self.status,
            'frozen_amount': self.frozen_amount
        }

# 黑名单手机号模型
class BlacklistedPhone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<BlacklistedPhone {self.phone}>' 
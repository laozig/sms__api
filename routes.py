from flask import Blueprint, request, jsonify, current_app
import random
import string
import jwt
import datetime
from models import db, User, Project, PhoneNumber, BlacklistedPhone
from async_util import run_async
from phone_utils import generate_random_phone, get_carrier_type, get_number_type, is_valid_phone
from sqlalchemy.orm import sessionmaker

# 创建蓝图
api = Blueprint('api', __name__)

# 根路由 - 为测试添加
@api.route('/', methods=['GET'])
def index():
    """
    API根路由
    
    返回API服务基本信息
    
    参数: 无
    
    返回:
    - name: API名称
    - version: API版本
    - status: 服务状态
    """
    return jsonify({
        'name': 'SMS API服务',
        'version': '1.0.0',
        'status': 'running'
    }), 200

# 用户注册API
@api.route('/register', methods=['GET'])
def register():
    """
    用户注册接口
    
    注册新用户账号，要求提供用户名、密码、邮箱和安全问题。
    注册成功后返回用户信息和token。
    
    参数:
    - username: 用户名，必填，唯一
    - password: 密码，必填
    - email: 邮箱，必填，唯一
    - security_question: 安全问题及答案，必填
    
    返回:
    - success: 操作是否成功
    - message: 操作结果描述
    - user: 用户信息(注册成功时)
    """
    # 从URL参数获取数据
    username = request.args.get('username')
    password = request.args.get('password')
    email = request.args.get('email')
    security_question = request.args.get('security_question')
    
    # 检查是否提供了所有必要的字段
    if not all([username, password, email, security_question]):
        return jsonify({'success': False, 'message': '缺少必要的注册信息'}), 400
    
    # 检查用户名是否存在
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    # 检查邮箱是否存在
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已存在'}), 400
    
    # 生成token
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=current_app.config['JWT_EXPIRATION_DAYS'])
    }, current_app.config['SECRET_KEY'])
    
    # 创建新用户
    new_user = User(
        username=username,
        password=password,  # 明文存储密码（按需求）
        email=email,
        security_question=security_question,
        token=token,
        balance=0.0
    )
    
    # 将用户添加到数据库
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '注册成功',
        'user': {
            'username': username,
            'email': email,
            'token': token,
            'balance': 0.0
        }
    }), 201

# 用户登录API
@api.route('/login', methods=['GET'])
def login():
    """
    用户登录接口
    
    验证用户名和密码，成功后返回用户信息和更新的token。
    
    参数:
    - username: 用户名，必填
    - password: 密码，必填
    
    返回:
    - success: 操作是否成功
    - message: 操作结果描述
    - user: 用户信息(登录成功时)，包含用户名、邮箱、token和余额
    """
    # 从URL参数获取数据
    username = request.args.get('username')
    password = request.args.get('password')
    
    # 检查是否提供了所有必要的字段
    if not all([username, password]):
        return jsonify({'success': False, 'message': '缺少必要的登录信息'}), 400
    
    # 查询用户
    user = User.query.filter_by(username=username).first()
    
    # 验证用户是否存在及密码是否正确
    if not user or user.password != password:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    # 更新token
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=current_app.config['JWT_EXPIRATION_DAYS'])
    }, current_app.config['SECRET_KEY'])
    
    user.token = token
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'user': {
            'username': username,
            'email': user.email,
            'token': token,
            'balance': user.balance
        }
    }), 200

# 充值API
@api.route('/recharge', methods=['GET'])
def recharge():
    """
    用户充值接口
    
    根据token验证用户身份，为用户账户充值指定金额。
    充值成功后更新数据库中的用户余额。
    
    参数:
    - token: 用户登录后获取的token，必填
    - amount: 充值金额，必填，必须大于0
    
    返回:
    - success: 操作是否成功
    - message: 操作结果描述
    - balance: 充值后的余额(充值成功时)
    - username: 用户名(充值成功时)
    """
    # 从URL参数获取数据
    token = request.args.get('token')
    amount_str = request.args.get('amount')
    
    # 检查是否提供了所有必要的字段
    if not all([token, amount_str]):
        return jsonify({'success': False, 'message': '缺少必要的充值信息'}), 400
    
    # 验证amount是否为有效的数字
    try:
        amount = float(amount_str)
    except ValueError:
        return jsonify({'success': False, 'message': '充值金额必须是有效的数字'}), 400
    
    # 验证金额是否大于0
    if amount <= 0:
        return jsonify({'success': False, 'message': '充值金额必须大于0'}), 400
    
    # 查找具有该token的用户
    user = User.query.filter_by(token=token).first()
    
    # 验证token是否有效
    if not user:
        return jsonify({'success': False, 'message': '无效的token，请重新登录'}), 401
    
    try:
        # 验证token有效期
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        # 检查token是否过期在jwt.decode中已经处理
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'token已过期，请重新登录'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': '无效的token格式'}), 401
    
    # 更新用户余额
    user.balance += amount
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '充值成功',
        'username': user.username,
        'balance': user.balance
    }), 200

# 测试路由
@api.route('/test', methods=['GET'])
def test():
    """
    API测试接口
    
    用于测试API服务是否正常运行。
    
    参数: 无
    
    返回:
    - message: 连接状态描述
    """
    return jsonify({'message': 'API 连接成功'}), 200

# 查询余额API
@api.route('/balance', methods=['GET'])
def check_balance():
    """
    查询余额接口
    
    根据token验证用户身份，查询用户账户余额。
    
    参数:
    - token: 用户登录后获取的token，必填
    
    返回:
    - success: 操作是否成功
    - message: 操作结果描述
    - username: 用户名(查询成功时)
    - balance: 用户余额(查询成功时)
    """
    # 从URL参数获取token
    token = request.args.get('token')
    
    # 检查是否提供了token
    if not token:
        return jsonify({'success': False, 'message': '缺少必要的token信息'}), 400
    
    # 直接查询用户，不使用异步方式
    user = User.query.filter_by(token=token).first()
    
    # 验证token是否有效
    if not user:
        return jsonify({'success': False, 'message': '无效的token，请重新登录'}), 401
    
    try:
        # 验证token有效期
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        # 检查token是否过期在jwt.decode中已经处理
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'token已过期，请重新登录'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': '无效的token格式'}), 401
    
    # 返回用户余额信息
    return jsonify({
        'success': True,
        'message': '查询成功',
        'username': user.username,
        'balance': user.balance
    }), 200

# 修改密码API
@api.route('/change_password', methods=['GET'])
def change_password():
    """
    修改密码接口
    
    验证旧密码、新密码和密保问题，修改成功后原token会作废，需要重新登录获取新token。
    
    参数:
    - username: 用户名，必填
    - old_password: 旧密码，必填
    - new_password: 新密码，必填
    - security_answer: 密保问题答案，必填
    
    返回:
    - success: 操作是否成功
    - message: 操作结果描述
    """
    # 从URL参数获取数据
    username = request.args.get('username')
    old_password = request.args.get('old_password')
    new_password = request.args.get('new_password')
    security_answer = request.args.get('security_answer')
    
    # 检查是否提供了所有必要的字段
    if not all([username, old_password, new_password, security_answer]):
        return jsonify({'success': False, 'message': '缺少必要的修改密码信息'}), 400
    
    # 查询用户
    user = User.query.filter_by(username=username).first()
    
    # 验证用户是否存在
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    # 验证旧密码是否正确
    if user.password != old_password:
        return jsonify({'success': False, 'message': '旧密码不正确'}), 401
    
    # 验证密保问题答案是否正确
    # 从数据库中提取问题部分（格式：问题? 答案）
    stored_question_answer = user.security_question
    try:
        # 分割问题和答案
        question_parts = stored_question_answer.split('?')
        if len(question_parts) < 2:
            return jsonify({'success': False, 'message': '密保问题格式错误'}), 500
        
        # 提取答案部分，去除前导空格
        stored_answer = question_parts[1].strip()
        
        # 验证答案是否匹配
        if stored_answer != security_answer:
            return jsonify({'success': False, 'message': '密保问题答案不正确'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证密保问题时出错: {str(e)}'}), 500
    
    # 更新密码
    user.password = new_password
    
    # 使原token作废（设置为空或生成一个无效token）
    user.token = ""
    
    # 保存更改到数据库
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '密码修改成功，请重新登录获取新token'
    }), 200

# 项目搜索API
@api.route('/search_projects', methods=['GET'])
def search_projects():
    """
    项目搜索接口
    
    根据项目ID或项目名称搜索项目，支持模糊搜索。
    
    参数:
    - project_id: 项目ID，可选，精确匹配
    - name: 项目名称，可选，支持模糊搜索
    - token: 用户登录后获取的token，必填
    
    返回:
    - success: 操作是否成功
    - message: 操作结果描述
    - projects: 项目列表(搜索成功时)
    """
    # 从URL参数获取数据
    project_id = request.args.get('project_id')
    name = request.args.get('name')
    token = request.args.get('token')
    
    # 检查是否提供了token
    if not token:
        return jsonify({'success': False, 'message': '缺少必要的token信息'}), 400
    
    # 验证token是否有效
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'success': False, 'message': '无效的token，请重新登录'}), 401
    
    try:
        # 验证token有效期
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'token已过期，请重新登录'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': '无效的token格式'}), 401
    
    # 构建查询
    query = Project.query
    
    # 按项目ID搜索（精确匹配）
    if project_id:
        query = query.filter(Project.project_id == project_id)
    
    # 按项目名称搜索（模糊匹配）
    if name:
        query = query.filter(Project.name.like(f'%{name}%'))
    
    # 执行查询
    projects = query.all()
    
    # 将结果转换为字典列表
    result = [project.to_dict() for project in projects]
    
    # 修改所有项目的金额为固定值0.1
    for project_dict in result:
        project_dict['amount'] = 0.1
    
    # 返回结果
    if result:
        return jsonify({
            'success': True,
            'message': '搜索成功',
            'projects': result
        }), 200
    else:
        return jsonify({
            'success': True,
            'message': '没有找到匹配的项目',
            'projects': []
        }), 200

# 获取手机号码API
@api.route('/get_phone', methods=['GET'])
def get_phone():
    """
    获取手机号码接口
    
    根据项目ID获取一个随机可用的手机号码。
    获取成功后会锁定号码并冻结相应金额。
    
    参数:
    - token: 用户登录后获取的token，必填
    - project_id: 项目ID，必填
    - carrier_type: 运营商类型，可选，默认0(不限)，可选值1=移动，2=联通，3=电信
    - number_type: 号码类型，可选，默认0(不限)，可选值1=普通，2=虚拟
    
    返回成功:
    - stat: true
    - message: "ok"
    - code: 1
    - data: 手机号码
    
    返回失败:
    - stat: false
    - message: 错误原因
    - code: 错误代码
    - data: null
    """
    # 从URL参数获取数据
    token = request.args.get('token')
    project_id = request.args.get('project_id')
    carrier_type = request.args.get('carrier_type', '0')
    number_type = request.args.get('number_type', '0')
    
    # 检查是否提供了token和project_id
    if not token or not project_id:
        return jsonify({
            'stat': False,
            'message': '缺少必要的参数',
            'code': -1,
            'data': None
        }), 400
    
    # 使用异步任务处理
    result = run_async(lambda: async_get_phone(token, project_id, carrier_type, number_type))
    
    # 提取状态码并从结果中移除
    status_code = result.pop('status_code', 200)
    
    # 返回结果
    return jsonify(result), status_code

# 获取指定手机号码API
@api.route('/get_specified_phone', methods=['GET'])
def get_specified_phone():
    """
    获取指定手机号码接口
    
    根据项目ID和指定的手机号码获取手机号码。
    获取成功时会冻结用户余额，冻结金额为项目价格。
    此接口可以获取黑名单中的手机号，并将其从黑名单中移除。
    
    参数:
    - token: 用户登录后获取的token，必填
    - project_id: 项目ID，必填
    - phone: 指定的手机号码，必填
    - carrier_type: 运营商类型，可选，0不限，1移动，2联通，3电信，默认0
    - number_type: 号段类型，可选，0不限，1正常，2虚拟，默认0
    
    返回成功:
    - stat: true
    - message: "ok"
    - code: 1
    - data: 手机号码
    
    返回失败:
    - stat: false
    - message: 错误原因
    - code: -1
    - data: null
    """
    # 从URL参数获取数据
    token = request.args.get('token')
    project_id = request.args.get('project_id')
    phone = request.args.get('phone')
    carrier_type = int(request.args.get('carrier_type', 0))
    number_type = int(request.args.get('number_type', 0))
    
    # 检查是否提供了token、project_id和phone
    if not token or not project_id or not phone:
        return jsonify({
            'stat': False,
            'message': '缺少必要的参数',
            'code': -1,
            'data': None
        }), 400
    
    # 验证token是否有效
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({
            'stat': False,
            'message': '无效的token，请重新登录',
            'code': -1,
            'data': None
        }), 401
    
    try:
        # 验证token有效期
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({
            'stat': False,
            'message': 'token已过期，请重新登录',
            'code': -1,
            'data': None
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            'stat': False,
            'message': '无效的token格式',
            'code': -1,
            'data': None
        }), 401
    
    # 检查项目是否存在
    project = Project.query.filter_by(project_id=project_id).first()
    if not project:
        return jsonify({
            'stat': False,
            'message': '无效的项目ID',
            'code': -1,
            'data': None
        }), 404
    
    # 检查用户余额是否足够
    project_amount = project.amount  # 项目价格
    if user.balance < project_amount:
        return jsonify({
            'stat': False,
            'message': '账户余额不足',
            'code': -2,
            'data': None
        }), 200
    
    # 验证手机号是否有效
    if not is_valid_phone(phone):
        return jsonify({
            'stat': False,
            'message': '无效的手机号码格式',
            'code': -1,
            'data': None
        }), 400
    
    # 自动检测手机号的运营商和号段类型
    detected_carrier_type = get_carrier_type(phone)
    detected_number_type = get_number_type(phone)
    
    # 如果用户指定了运营商类型和号段类型，则验证手机号是否匹配
    if carrier_type != 0 and carrier_type != detected_carrier_type:
        return jsonify({
            'stat': False,
            'message': '手机号与指定的运营商类型不匹配',
            'code': -1,
            'data': None
        }), 400
    
    if number_type != 0 and number_type != detected_number_type:
        return jsonify({
            'stat': False,
            'message': '手机号与指定的号段类型不匹配',
            'code': -1,
            'data': None
        }), 400
    
    # 检查手机号是否已被其他用户占用
    existing_phone = PhoneNumber.query.filter_by(phone=phone).first()
    if existing_phone:
        return jsonify({
            'stat': False,
            'message': '该手机号已被使用',
            'code': -1,
            'data': None
        }), 200
    
    # 检查手机号是否在黑名单中，如果在则从黑名单中移除
    blacklisted_phone = BlacklistedPhone.query.filter_by(phone=phone).first()
    if blacklisted_phone:
        # 移除黑名单记录
        db.session.delete(blacklisted_phone)
    
    # 扣除用户余额并创建冻结记录
    user.balance -= project_amount
    
    # 创建新的手机号码记录，包含冻结金额
    new_phone = PhoneNumber(
        phone=phone,
        user_id=user.id,
        project_id=project_id,
        carrier_type=detected_carrier_type,
        number_type=detected_number_type,
        frozen_amount=project_amount
    )
    
    # 保存到数据库
    db.session.add(new_phone)
    db.session.commit()
    
    # 返回成功响应
    return jsonify({
        'stat': True,
        'message': 'ok',
        'code': 1,
        'data': phone
    }), 200

# 获取短信验证码API
@api.route('/get_sms_code', methods=['GET'])
def get_sms_code():
    """
    获取短信验证码接口
    
    通过手机号获取短信验证码，需要指定项目ID。
    每个手机号每分钟最多请求3次，每个IP每分钟最多请求50次。
    
    参数:
    - token: 用户登录后获取的token，必填
    - project_id: 项目ID，必填
    - phone: 手机号码，必填
    
    返回成功:
    - message: "ok"
    - code: 验证码(有短信时)或空(无短信时)
    - data: 短信详细信息
    
    返回失败:
    - message: 错误原因
    - code: -1
    - data: null
    """
    # 从URL参数获取数据
    token = request.args.get('token')
    project_id = request.args.get('project_id')
    phone = request.args.get('phone')
    
    # 检查是否提供了token、project_id和phone
    if not all([token, project_id, phone]):
        return jsonify({
            'message': '缺少必要的参数',
            'code': -1,
            'data': None
        }), 400
    
    # 使用异步任务处理
    result = run_async(lambda: async_get_sms_code(token, project_id, phone))
    
    # 提取状态码并从结果中移除
    status_code = result.pop('status_code', 200)
    
    # 返回结果
    return jsonify(result), status_code

# 释放手机号码API
@api.route('/release_phone', methods=['GET'])
def release_phone():
    """
    释放手机号码接口
    
    释放用户之前获取的手机号码，如果该号码尚未使用，将退还冻结的余额。
    释放成功后将手机号与用户解除绑定，允许其他用户获取该号码。
    
    参数:
    - token: 用户登录后获取的token，必填
    - project_id: 项目ID，必填
    - phone: 手机号码，必填
    
    返回成功:
    - message: "ok"
    - data: []
    
    返回失败:
    - message: 错误原因
    - code: -1
    - data: null
    """
    # 从URL参数获取数据
    token = request.args.get('token')
    project_id = request.args.get('project_id')
    phone = request.args.get('phone')
    
    # 检查是否提供了token、project_id和phone
    if not token or not project_id or not phone:
        return jsonify({
            'message': '缺少必要的参数',
            'code': -1,
            'data': None
        }), 400
    
    # 使用异步任务处理
    result = run_async(lambda: async_release_phone(token, project_id, phone))
    
    # 提取状态码并从结果中移除
    status_code = result.pop('status_code', 200)
    
    # 返回结果
    return jsonify(result), status_code

# 加黑手机号码API
@api.route('/blacklist_phone', methods=['GET'])
def blacklist_phone():
    """
    加黑手机号码接口
    
    将手机号码加入黑名单，表示该号码存在问题不应再次使用。
    加黑后的手机号不会再分配给任何用户。
    
    参数:
    - token: 用户登录后获取的token，必填
    - project_id: 项目ID，必填
    - phone: 手机号码，必填
    
    返回成功:
    - message: "ok"
    - data: []
    
    返回失败:
    - message: 错误原因
    - code: -1
    - data: null
    """
    # 从URL参数获取数据
    token = request.args.get('token')
    project_id = request.args.get('project_id')
    phone = request.args.get('phone')
    
    # 检查是否提供了token、project_id和phone
    if not token or not project_id or not phone:
        return jsonify({
            'message': '缺少必要的参数',
            'code': -1,
            'data': None
        }), 400
    
    # 使用异步任务处理
    result = run_async(lambda: async_blacklist_phone(token, project_id, phone))
    
    # 提取状态码并从结果中移除
    status_code = result.pop('status_code', 200)
    
    # 返回结果
    return jsonify(result), status_code

# 异步处理释放手机号请求
def async_release_phone(token, project_id, phone):
    """异步处理释放手机号的请求"""
    from flask import current_app
    
    # 创建独立会话
    Session = sessionmaker(bind=db.engine)  # 使用全局db.engine而不是app
    session = Session()
    
    try:
        # 验证token是否有效
        user = session.query(User).filter_by(token=token).first()
        if not user:
            return {
                'message': '无效的token，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        try:
            # 验证token有效期
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {
                'message': 'token已过期，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        except jwt.InvalidTokenError:
            return {
                'message': '无效的token格式',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        # 查找手机号记录
        phone_record = session.query(PhoneNumber).filter_by(phone=phone, user_id=user.id, project_id=project_id).first()
        
        if not phone_record:
            return {
                'message': '该手机号不存在或不属于当前用户',
                'code': -1,
                'data': None,
                'status_code': 404
            }
        
        # 如果手机号有冻结金额，退还给用户
        if phone_record.frozen_amount > 0:
            user.balance += phone_record.frozen_amount
            print(f"退还用户({user.username})冻结金额: {phone_record.frozen_amount}")
        
        # 删除手机号记录
        session.delete(phone_record)
        session.commit()
        
        return {
            'message': 'ok',
            'data': [],
            'status_code': 200
        }
    except Exception as e:
        session.rollback()
        print(f"释放手机号异常: {str(e)}")
        return {
            'message': '释放手机号时发生错误',
            'code': -1,
            'data': None,
            'status_code': 500
        }
    finally:
        session.close()

# 异步处理加黑手机号请求
def async_blacklist_phone(token, project_id, phone):
    """异步处理加黑手机号的请求"""
    from flask import current_app
    
    # 创建独立会话
    Session = sessionmaker(bind=db.engine)  # 使用全局db.engine而不是app
    session = Session()
    
    try:
        # 验证token是否有效
        user = session.query(User).filter_by(token=token).first()
        if not user:
            return {
                'message': '无效的token，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        try:
            # 验证token有效期
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {
                'message': 'token已过期，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        except jwt.InvalidTokenError:
            return {
                'message': '无效的token格式',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        # 检查手机号是否存在
        if not is_valid_phone(phone):
            return {
                'message': '无效的手机号码格式',
                'code': -1,
                'data': None,
                'status_code': 400
            }
        
        # 查找手机号记录
        phone_record = session.query(PhoneNumber).filter_by(phone=phone, user_id=user.id).first()
        
        # 检查是否已经在黑名单中
        existing_blacklist = session.query(BlacklistedPhone).filter_by(phone=phone, project_id=project_id).first()
        if existing_blacklist:
            return {
                'message': '该手机号已在黑名单中',
                'code': -1,
                'data': None,
                'status_code': 409
            }
        
        # 添加到黑名单
        blacklisted_phone = BlacklistedPhone(
            phone=phone,
            user_id=user.id,
            project_id=project_id
        )
        session.add(blacklisted_phone)
        
        # 如果手机号在用户的手机号列表中，释放它
        if phone_record:
            # 如果手机号有冻结金额，退还给用户
            if phone_record.frozen_amount > 0:
                user.balance += phone_record.frozen_amount
                print(f"退还用户({user.username})冻结金额: {phone_record.frozen_amount}")
            
            # 删除手机号记录
            session.delete(phone_record)
        
        session.commit()
        
        return {
            'message': 'ok',
            'data': [],
            'status_code': 200
        }
    except Exception as e:
        session.rollback()
        print(f"加黑手机号异常: {str(e)}")
        return {
            'message': '加黑手机号时发生错误',
            'code': -1,
            'data': None,
            'status_code': 500
        }
    finally:
        session.close()

# 异步处理获取手机号请求
def async_get_phone(token, project_id, carrier_type, number_type):
    """异步获取手机号功能"""
    from flask import current_app
    
    # 创建独立会话
    Session = sessionmaker(bind=db.engine)  # 使用全局db.engine而不是app
    session = Session()
    
    try:
        # 验证token是否有效
        user = session.query(User).filter_by(token=token).first()
        if not user:
            return {
                'stat': False,
                'message': '无效的token，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        try:
            # 验证token有效期
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {
                'stat': False,
                'message': 'token已过期，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        except jwt.InvalidTokenError:
            return {
                'stat': False,
                'message': '无效的token格式',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        # 检查项目是否存在
        project = session.query(Project).filter_by(project_id=project_id).first()
        if not project:
            return {
                'stat': False,
                'message': '无效的项目ID',
                'code': -1,
                'data': None,
                'status_code': 404
            }
        
        # 检查用户余额是否足够
        project_amount = project.amount  # 项目价格
        if user.balance < project_amount:
            return {
                'stat': False,
                'message': '账户余额不足',
                'code': -2,  # 使用不同的错误码区分余额不足
                'data': None,
                'status_code': 200
            }
        
        # 检查黑名单手机号
        blacklisted_phones = session.query(BlacklistedPhone.phone).filter_by(project_id=project_id).all()
        blacklisted_phones = [bp[0] for bp in blacklisted_phones]
        
        # 已分配给当前用户的手机号
        user_phones = session.query(PhoneNumber.phone).filter_by(
            user_id=user.id, 
            project_id=project_id, 
            status=1
        ).all()
        user_phones = [up[0] for up in user_phones]
        
        # 获取手机号(尝试3次)
        phone = None
        for _ in range(3):
            # 生成随机手机号
            phone = generate_random_phone(
                carrier_type=int(carrier_type),
                number_type=int(number_type)
            )
            
            # 检查是否在黑名单中
            if phone in blacklisted_phones:
                continue
            
            # 检查是否已分配
            if phone in user_phones:
                continue
            
            # 检查是否已被其他用户使用
            existing_phone = session.query(PhoneNumber).filter_by(phone=phone).first()
            if existing_phone:
                continue
            
            # 找到可用手机号
            break
        else:
            # 尝试3次都失败
            return {
                'stat': False,
                'message': '没有可用号码',
                'code': -3,
                'data': None,
                'status_code': 200
            }
        
        # 冻结用户余额
        user.balance -= project_amount
        
        # 创建手机号记录
        new_phone = PhoneNumber(
            phone=phone,
            user_id=user.id,
            project_id=project_id,
            carrier_type=int(carrier_type),
            number_type=int(number_type),
            frozen_amount=project_amount,
            status=1  # 有效状态
        )
        
        # 保存到数据库
        session.add(new_phone)
        session.commit()
        
        return {
            'stat': True,
            'message': 'ok',
            'code': 1,
            'data': phone,
            'status_code': 200
        }
    except Exception as e:
        session.rollback()
        print(f"获取手机号异常: {str(e)}")
        return {
            'stat': False,
            'message': '获取手机号时发生错误',
            'code': -1,
            'data': None,
            'status_code': 500
        }
    finally:
        session.close()

# 异步处理获取短信验证码请求
def async_get_sms_code(token, project_id, phone):
    """异步获取短信验证码"""
    from flask import current_app
    
    # 创建独立会话
    Session = sessionmaker(bind=db.engine)  # 使用全局db.engine而不是app
    session = Session()
    
    try:
        # 验证token是否有效
        user = session.query(User).filter_by(token=token).first()
        if not user:
            return {
                'stat': False,
                'message': '无效的token，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        try:
            # 验证token有效期
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {
                'stat': False,
                'message': 'token已过期，请重新登录',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        except jwt.InvalidTokenError:
            return {
                'stat': False,
                'message': '无效的token格式',
                'code': -1,
                'data': None,
                'status_code': 401
            }
        
        # 检查手机号是否存在且属于当前用户
        phone_record = session.query(PhoneNumber).filter_by(phone=phone, user_id=user.id).first()
        if not phone_record:
            return {
                'stat': False,
                'message': '该手机号不存在或不属于当前用户',
                'code': -1,
                'data': None,
                'status_code': 404
            }
        
        # 检查项目ID是否匹配
        if phone_record.project_id != project_id:
            return {
                'stat': False,
                'message': '该手机号与项目ID不匹配',
                'code': -1,
                'data': None,
                'status_code': 400
            }
        
        # 模拟短信接收过程
        # 有70%的概率接收到短信验证码
        if random.random() < 0.7:
            # 生成6位数字验证码
            verification_code = ''.join(random.choices('0123456789', k=6))
            
            # 模拟短信内容
            sms_content = f"【酷狗音乐】您的登录验证码{verification_code}。如非本人操作，请不要把验证码泄露给任何人。"
            
            # 更新手机号状态，将冻结余额正式扣除
            if phone_record.frozen_amount > 0:
                # 已经扣除了余额，现在只需标记为已使用即可
                phone_record.status = 0  # 标记为已使用
                phone_record.frozen_amount = 0  # 清除冻结金额
                session.commit()
            
            # 返回验证码信息
            return {
                'stat': True,
                'message': 'ok',
                'code': verification_code,
                'data': [{
                    'project_id': project_id,
                    'modle': sms_content,
                    'phone': phone,
                    'project_type': '1'
                }],
                'status_code': 200
            }
        else:
            # 没有收到短信
            return {
                'stat': True,
                'message': 'ok',
                'code': '',  # 空验证码
                'data': [],
                'status_code': 200
            }
    except Exception as e:
        session.rollback()
        print(f"获取短信验证码异常: {str(e)}")
        return {
            'stat': False,
            'message': '获取短信验证码时发生错误',
            'code': -1,
            'data': None,
            'status_code': 500
        }
    finally:
        session.close() 
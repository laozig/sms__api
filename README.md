# SMS API 服务

SMS API是一个用于管理短信验证码的API服务，提供手机号码获取、短信验证码验证等功能。

## 功能特点

- 用户管理：注册、登录、密码修改
- 充值功能：用户余额管理
- 手机号码管理：获取手机号、释放手机号、黑名单管理
- 短信验证码：获取指定手机号的验证码
- 高并发支持：使用SQLAlchemy连接池和异步处理机制

## 技术栈

- Python 3.6+
- Flask：Web框架
- SQLAlchemy：ORM和数据库连接池
- JWT：身份验证
- SQLite/MySQL/PostgreSQL：数据库支持

## 项目结构

```
sms_api/
├── app.py              # 应用主入口
├── config.py           # 配置文件
├── models.py           # 数据库模型
├── routes.py           # API路由
├── async_util.py       # 异步工具
├── phone_utils.py      # 手机号工具
└── logs/               # 日志目录
```

## 环境配置搭建

### 系统要求

- Python 3.6或更高版本
- pip包管理器
- 虚拟环境(可选但推荐)

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/laozig/sms__api.git
cd sms_api
```

2. **创建并激活虚拟环境**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置数据库**

默认使用SQLite数据库，无需额外配置。如需使用其他数据库，请修改config.py中的相应配置。

```python
# 使用MySQL示例
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/sms_api'

# 使用PostgreSQL示例
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/sms_api'
```

5. **环境变量设置（可选）**

```bash
# Windows PowerShell
$env:DATABASE_URI = "sqlite:///sms_api.db"
$env:SECRET_KEY = "your_secure_secret_key"
$env:FLASK_CONFIG = "development"

# Windows CMD
set DATABASE_URI=sqlite:///sms_api.db
set SECRET_KEY=your_secure_secret_key
set FLASK_CONFIG=development

# macOS/Linux
export DATABASE_URI=sqlite:///sms_api.db
export SECRET_KEY=your_secure_secret_key
export FLASK_CONFIG=development
```

### 配置文件详解

`config.py`文件包含以下配置选项:

- **SECRET_KEY**: 用于会话签名和token生成的密钥
- **SQLALCHEMY_DATABASE_URI**: 数据库连接URI
- **SQLALCHEMY_POOL_SIZE**: 数据库连接池大小
- **SQLALCHEMY_MAX_OVERFLOW**: 连接池溢出连接数
- **PORT**: 应用监听端口

## 使用说明

### 启动服务

```bash
# 开发环境
python app.py

# 生产环境
export FLASK_CONFIG=production
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app\('production'\) --timeout 120 --preload
```

### 使用API

所有API都遵循RESTful设计原则，主要通过GET请求提供服务。

#### 1. 用户注册

```
GET /api/register?username=testuser&password=testpassword&email=test@example.com&security_question=测试问题?%20测试答案
```

成功响应:
```json
{
  "success": true,
  "message": "用户注册成功",
  "user": {
    "id": 123,
    "username": "testuser",
    "email": "test@example.com",
    "balance": 0.0,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### 2. 用户登录

```
GET /api/login?username=testuser&password=testpassword
```

成功响应:
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "id": 123,
    "username": "testuser",
    "email": "test@example.com",
    "balance": 100.0,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### 3. 获取手机号

```
GET /api/get_phone?token=YOUR_TOKEN&project_id=123456&carrier_type=0&number_type=0
```

成功响应:
```json
{
  "stat": true,
  "message": "获取手机号成功",
  "code": 0,
  "data": "13812345678"
}
```

#### 4. 获取短信验证码

```
GET /api/get_sms_code?token=YOUR_TOKEN&project_id=123456&phone=13812345678
```

成功响应:
```json
{
  "message": "获取验证码成功",
  "code": 0,
  "data": "【淘宝】您的验证码是123456，5分钟内有效。如非本人操作，请忽略本短信。"
}
```

## 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查数据库URI配置是否正确
   - 确认数据库服务是否运行
   - 验证用户名和密码是否有效

2. **API返回未授权错误**
   - 检查token是否过期(有效期24小时)
   - 验证token是否完整无误
   - 确认使用了正确的token参数名

3. **日志文件乱码**
   - 确保app.py中的日志配置使用UTF-8编码
   - 使用支持UTF-8的文本编辑器查看日志

### 日志查看

日志保存在`logs/sms_api.log`文件中，可以通过以下命令查看:

```bash
# 查看最后100行日志
tail -n 100 logs/sms_api.log

# 实时查看日志更新
tail -f logs/sms_api.log
```

## 生产环境部署建议

1. 使用gunicorn启动多进程服务
2. 配置nginx作为前端代理
3. 使用更可靠的数据库如MySQL或PostgreSQL
4. 开启SSL/TLS加密
5. 实施IP限流保护

## 许可证

MIT 
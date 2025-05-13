# 接码平台 API 文档

## 基本信息

- 基础URL: `http://localhost:5000/api`
- 所有API均使用 `GET` 请求方式
- 响应格式: JSON

## API 列表

| 接口名称 | 接口路径 | 描述 |
|---------|---------|------|
| [注册](#用户注册) | `/register` | 注册新用户 |
| [登录](#用户登录) | `/login` | 用户登录 |
| [充值](#用户充值) | `/recharge` | 账户充值 |
| [查询余额](#查询余额) | `/balance` | 查询账户余额 |
| [修改密码](#修改密码) | `/change_password` | 修改用户密码 |
| [项目搜索](#项目搜索) | `/search_projects` | 搜索项目信息 |
| [获取手机号码](#获取手机号码) | `/get_phone` | 获取随机手机号码 |
| [获取指定手机号码](#获取指定手机号码) | `/get_specified_phone` | 获取指定的手机号码 |
| [获取短信验证码](#获取短信验证码) | `/get_sms_code` | 获取手机短信验证码 |
| [释放手机号码](#释放手机号码) | `/release_phone` | 释放已获取的手机号码 |
| [加黑手机号码](#加黑手机号码) | `/blacklist_phone` | 将手机号码加入黑名单 |
| [测试连接](#测试连接) | `/test` | 测试API连接 |

## 详细文档

### 用户注册

注册新用户账号。

**请求URL**:
```
GET /api/register
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| email | string | 是 | 邮箱地址 |
| security_question | string | 是 | 安全问题及答案 |

**请求示例**:
```
GET /api/register?username=testuser&password=password123&email=test@example.com&security_question=What%20is%20your%20favorite%20color%3F%20Blue
```

**成功响应** (状态码: 201):
```json
{
  "success": true,
  "message": "注册成功",
  "user": {
    "username": "testuser",
    "email": "test@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "balance": 0.0
  }
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "success": false,
  "message": "缺少必要的注册信息"
}
```

2. 用户名已存在 (状态码: 400):
```json
{
  "success": false,
  "message": "用户名已存在"
}
```

3. 邮箱已存在 (状态码: 400):
```json
{
  "success": false,
  "message": "邮箱已存在"
}
```

### 用户登录

用户登录接口，验证用户名和密码。

**请求URL**:
```
GET /api/login
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**:
```
GET /api/login?username=testuser&password=password123
```

**成功响应** (状态码: 200):
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "username": "testuser",
    "email": "test@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "balance": 0.0
  }
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "success": false,
  "message": "缺少必要的登录信息"
}
```

2. 用户名或密码错误 (状态码: 401):
```json
{
  "success": false,
  "message": "用户名或密码错误"
}
```

### 用户充值

为用户账户充值金额，需要使用登录获取的token进行身份验证。

**请求URL**:
```
GET /api/recharge
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |
| amount | number | 是 | 充值金额，必须大于0 |

**请求示例**:
```
GET /api/recharge?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&amount=100.50
```

**成功响应** (状态码: 200):
```json
{
  "success": true,
  "message": "充值成功",
  "username": "testuser",
  "balance": 100.50
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "success": false,
  "message": "缺少必要的充值信息"
}
```

2. 无效的金额 (状态码: 400):
```json
{
  "success": false,
  "message": "充值金额必须是有效的数字"
}
```

3. 金额必须大于0 (状态码: 400):
```json
{
  "success": false,
  "message": "充值金额必须大于0"
}
```

4. 无效的token (状态码: 401):
```json
{
  "success": false,
  "message": "无效的token，请重新登录"
}
```

5. token已过期 (状态码: 401):
```json
{
  "success": false,
  "message": "token已过期，请重新登录"
}
```

### 查询余额

查询用户账户余额，需要使用登录获取的token进行身份验证。

**请求URL**:
```
GET /api/balance
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |

**成功响应** (状态码: 200):
```json
{
  "success": true,
  "message": "查询成功",
  "username": "testuser",
  "balance": 100.50
}
```

**错误响应**:

1. 无效的token (状态码: 401):
```json
{
  "success": false,
  "message": "无效的token，请重新登录"
}
```

### 修改密码

修改用户密码，需要提供用户名、旧密码、新密码和密保问题答案。修改成功后原token会作废，需要重新登录获取新token。

**请求URL**:
```
GET /api/change_password
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| username | string | 是 | 用户名 |
| old_password | string | 是 | 旧密码 |
| new_password | string | 是 | 新密码 |
| security_answer | string | 是 | 密保问题答案 |

**请求示例**:
```
GET /api/change_password?username=testuser&old_password=password123&new_password=newpassword456&security_answer=Blue
```

**成功响应** (状态码: 200):
```json
{
  "success": true,
  "message": "密码修改成功，请重新登录获取新token"
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "success": false,
  "message": "缺少必要的修改密码信息"
}
```

2. 用户不存在 (状态码: 404):
```json
{
  "success": false,
  "message": "用户不存在"
}
```

3. 旧密码不正确 (状态码: 401):
```json
{
  "success": false,
  "message": "旧密码不正确"
}
```

4. 密保问题答案不正确 (状态码: 401):
```json
{
  "success": false,
  "message": "密保问题答案不正确"
}
```

### 项目搜索

搜索项目信息，支持按项目ID或项目名称搜索（包括模糊搜索）。需要使用登录获取的token进行身份验证。

**请求URL**:
```
GET /api/search_projects
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |
| project_id | string | 否 | 项目ID（6位数字），精确匹配 |
| name | string | 否 | 项目名称，支持模糊搜索 |

**注意**: 必须提供 `project_id` 或 `name` 中的至少一个参数。

**请求示例**:
```
GET /api/search_projects?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&project_id=123456
```

或者:
```
GET /api/search_projects?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&name=智能管理
```

**成功响应** (状态码: 200):
```json
{
  "success": true,
  "message": "搜索成功",
  "projects": [
    {
      "project_id": "123456",
      "name": "智能管理系统",
      "amount": 1500.50
    },
    {
      "project_id": "234567",
      "name": "智能监控平台",
      "amount": 2300.75
    }
  ]
}
```

**搜索无结果响应** (状态码: 200):
```json
{
  "success": true,
  "message": "没有找到匹配的项目",
  "projects": []
}
```

**错误响应**:

1. 缺少token (状态码: 400):
```json
{
  "success": false,
  "message": "缺少必要的token信息"
}
```

2. 无效的token (状态码: 401):
```json
{
  "success": false,
  "message": "无效的token，请重新登录"
}
```

3. 缺少搜索参数 (状态码: 400):
```json
{
  "success": false,
  "message": "请提供项目ID或项目名称进行搜索"
}
```

### 获取手机号码

根据指定的项目ID、运营商类型和号段类型获取一个随机手机号码。获取成功时将冻结用户余额，冻结金额为项目的价格。

**请求URL**:
```
GET /api/get_phone
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |
| project_id | string | 是 | 项目ID |
| carrier_type | int | 否 | 运营商类型：0不限，1移动，2联通，3电信，默认0 |
| number_type | int | 否 | 号段类型：0不限，1正常，2虚拟，默认0 |

**请求示例**:
```
GET /api/get_phone?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&project_id=123456&carrier_type=1&number_type=1
```

**成功响应** (状态码: 200):
```json
{
  "stat": true,
  "message": "ok",
  "code": 1,
  "data": "13888888888"
}
```

**失败响应** (状态码: 200):

1. 没有可用号码:
```json
{
  "stat": false,
  "message": "没有可用号码",
  "code": -1,
  "data": null
}
```

2. 余额不足:
```json
{
  "stat": false,
  "message": "账户余额不足",
  "code": -2,
  "data": null
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "stat": false,
  "message": "缺少必要的参数",
  "code": -1,
  "data": null
}
```

2. 无效的token (状态码: 401):
```json
{
  "stat": false,
  "message": "无效的token，请重新登录",
  "code": -1,
  "data": null
}
```

3. 无效的项目ID (状态码: 404):
```json
{
  "stat": false,
  "message": "无效的项目ID",
  "code": -1,
  "data": null
}
```

4. 无效的运营商类型 (状态码: 400):
```json
{
  "stat": false,
  "message": "无效的运营商类型",
  "code": -1,
  "data": null
}
```

5. 无效的号段类型 (状态码: 400):
```json
{
  "stat": false,
  "message": "无效的号段类型",
  "code": -1,
  "data": null
}
```

**注意事项**:
- 获取号码成功后，系统会从用户余额中扣除项目价格的金额，并将其作为冻结金额记录
- 用户余额不足时将无法获取号码
- 冻结的金额将用于后续接收短信验证码的服务

### 获取指定手机号码

根据项目ID获取指定的手机号码。获取成功时将冻结用户余额，冻结金额为项目的价格。

**请求URL**:
```
GET /api/get_specified_phone
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |
| project_id | string | 是 | 项目ID |
| phone | string | 是 | 指定的手机号码 |
| carrier_type | int | 否 | 运营商类型：0不限，1移动，2联通，3电信，默认0 |
| number_type | int | 否 | 号段类型：0不限，1正常，2虚拟，默认0 |

**请求示例**:
```
GET /api/get_specified_phone?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&project_id=123456&phone=13888888888
```

**成功响应** (状态码: 200):
```json
{
  "stat": true,
  "message": "ok",
  "code": 1,
  "data": "13888888888"
}
```

**失败响应** (状态码: 200):

1. 该手机号已被使用:
```json
{
  "stat": false,
  "message": "该手机号已被使用",
  "code": -1,
  "data": null
}
```

2. 余额不足:
```json
{
  "stat": false,
  "message": "账户余额不足",
  "code": -2,
  "data": null
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "stat": false,
  "message": "缺少必要的参数",
  "code": -1,
  "data": null
}
```

2. 无效的token (状态码: 401):
```json
{
  "stat": false,
  "message": "无效的token，请重新登录",
  "code": -1,
  "data": null
}
```

3. 无效的手机号码格式 (状态码: 400):
```json
{
  "stat": false,
  "message": "无效的手机号码格式",
  "code": -1,
  "data": null
}
```

4. 手机号与指定的运营商类型不匹配 (状态码: 400):
```json
{
  "stat": false,
  "message": "手机号与指定的运营商类型不匹配",
  "code": -1,
  "data": null
}
```

5. 手机号与指定的号段类型不匹配 (状态码: 400):
```json
{
  "stat": false,
  "message": "手机号与指定的号段类型不匹配",
  "code": -1,
  "data": null
}
```

6. 无效的项目ID (状态码: 404):
```json
{
  "stat": false,
  "message": "无效的项目ID",
  "code": -1,
  "data": null
}
```

**注意事项**:
- 获取指定号码成功后，系统会从用户余额中扣除项目价格的金额，并将其作为冻结金额记录
- 用户余额不足时将无法获取号码
- 系统会自动检测手机号的运营商和号段类型，确保与指定参数匹配
- 如果手机号已被使用，将无法再次获取
- 冻结的金额将用于后续接收短信验证码的服务

### 获取短信验证码

根据项目ID和手机号获取短信验证码。获取成功时会将之前冻结的余额正式扣除。

**请求URL**:
```
GET /api/get_sms_code
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |
| project_id | string | 是 | 项目ID |
| phone | string | 是 | 手机号码 |

**请求示例**:
```
GET /api/get_sms_code?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&project_id=123456&phone=13888888888
```

**成功响应(有验证码)** (状态码: 200):
```json
{
  "message": "ok",
  "code": "807272",
  "data": [{
    "project_id": "123456",
    "modle": "【酷狗音乐】您的登录验证码807272。如非本人操作，请不要把验证码泄露给任何人。",
    "phone": "13888888888",
    "project_type": "1"
  }]
}
```

**成功响应(无验证码)** (状态码: 200):
```json
{
  "message": "ok",
  "data": []
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "message": "缺少必要的参数",
  "code": -1,
  "data": null
}
```

2. 无效的token (状态码: 401):
```json
{
  "message": "无效的token，请重新登录",
  "code": -1,
  "data": null
}
```

3. 该手机号不存在或不属于当前用户 (状态码: 404):
```json
{
  "message": "该手机号不存在或不属于当前用户",
  "code": -1,
  "data": null
}
```

4. 该手机号与项目ID不匹配 (状态码: 400):
```json
{
  "message": "该手机号与项目ID不匹配",
  "code": -1,
  "data": null
}
```

5. 请求过于频繁 (状态码: 429):
```json
{
  "message": "请求过于频繁，请在2秒后重试",
  "code": -1,
  "data": null
}
```

**注意事项**:
- 接口有访问频率限制，同一手机号最快3秒访问一次
- 获取验证码成功后，系统会将之前冻结的余额正式扣除，手机号状态更新为已使用
- 验证码为随机生成的6位数字，可能不同请求会得到不同验证码
- 此接口可能返回空数据，表示尚未收到验证码，请稍后再试

### 释放手机号码

释放用户之前获取的手机号码，如果该号码尚未使用，将退还冻结的余额。释放成功后会彻底解除手机号与用户的绑定。

**请求URL**:
```
GET /api/release_phone
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |
| project_id | string | 是 | 项目ID |
| phone | string | 是 | 手机号码 |

**请求示例**:
```
GET /api/release_phone?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&project_id=123456&phone=13888888888
```

**成功响应** (状态码: 200):
```json
{
  "message": "ok",
  "data": []
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "message": "缺少必要的参数",
  "code": -1,
  "data": null
}
```

2. 无效的token (状态码: 401):
```json
{
  "message": "无效的token，请重新登录",
  "code": -1,
  "data": null
}
```

3. 该手机号不存在或不属于当前用户 (状态码: 404):
```json
{
  "message": "该手机号不存在或不属于当前用户",
  "code": -1,
  "data": null
}
```

4. 该手机号与项目ID不匹配 (状态码: 400):
```json
{
  "message": "该手机号与项目ID不匹配",
  "code": -1,
  "data": null
}
```

**注意事项**:
- 释放手机号成功后，如果该手机号尚未使用（未获取验证码），系统会将冻结的余额退还给用户
- 若手机号已经使用（已获取验证码），则不会有余额退还
- 释放成功后，该手机号记录将从数据库中彻底删除，与用户完全解除绑定关系
- 释放后的手机号可以被任何用户（包括原用户）重新获取
- 重复释放同一个手机号将返回404错误，因为第一次释放后该号码记录已不存在

### 加黑手机号码

将用户之前获取的手机号码加入黑名单，使其不会再被随机分配(除非指定获取)。加黑成功后如果该号码尚未使用，将退还冻结的余额并解除与用户的绑定。

**请求URL**:
```
GET /api/blacklist_phone
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| token | string | 是 | 用户登录后获取的token |
| project_id | string | 是 | 项目ID |
| phone | string | 是 | 手机号码 |

**请求示例**:
```
GET /api/blacklist_phone?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&project_id=123456&phone=13888888888
```

**成功响应** (状态码: 200):
```json
{
  "message": "ok",
  "data": []
}
```

**错误响应**:

1. 缺少必要参数 (状态码: 400):
```json
{
  "message": "缺少必要的参数",
  "code": -1,
  "data": null
}
```

2. 无效的token (状态码: 401):
```json
{
  "message": "无效的token，请重新登录",
  "code": -1,
  "data": null
}
```

3. 该手机号不存在或不属于当前用户 (状态码: 404):
```json
{
  "message": "该手机号不存在或不属于当前用户",
  "code": -1,
  "data": null
}
```

4. 该手机号与项目ID不匹配 (状态码: 400):
```json
{
  "message": "该手机号与项目ID不匹配",
  "code": -1,
  "data": null
}
```

5. 手机号已在黑名单中 (状态码: 400):
```json
{
  "message": "该手机号已在黑名单中",
  "code": -1,
  "data": null
}
```

**注意事项**:
- 加黑手机号成功后，该号码将不会再被随机分配给任何用户
- 如果该手机号尚未使用（未获取验证码），系统会将冻结的余额退还给用户
- 已加黑的手机号仍然可以通过指定取号API（`get_specified_phone`）获取
- 加黑操作会从用户的手机号列表中删除该号码，并将其加入系统黑名单
- 黑名单是全局性的，即所有用户在随机获取号码时都不会获取到黑名单中的号码

### 测试连接

测试API服务器连接状态。

**请求URL**:
```
GET /api/test
```

**请求参数**: 无

**成功响应** (状态码: 200):
```json
{
  "message": "API 连接成功"
}
```

## 测试账号

为方便测试，系统提供了一个预设的测试账号：

| 字段 | 值 |
|------|-----|
| 用户名 | testapi |
| 密码 | test123456 |
| 邮箱 | testapi@example.com |

可以使用此账号进行API测试。

## 错误码说明

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 

## 性能优化说明

为应对高并发场景，API服务采用以下优化策略：

1. 异步处理：关键操作使用异步方式处理，提高并发能力
2. 连接池：数据库连接使用连接池技术，减少连接创建开销
3. 缓存机制：对频繁访问的数据进行缓存，减轻数据库负担
4. 负载均衡：通过负载均衡分散请求压力
5. 请求限流：防止过多请求导致系统崩溃 
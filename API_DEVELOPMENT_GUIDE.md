# 接码平台API开发指南

本文档提供了添加新API和维护现有API的最佳实践和标准。请所有开发者遵循这些指南，确保API的一致性和可维护性。

## API设计原则

1. **简单性**: API应该易于理解和使用
2. **一致性**: 所有API应该遵循相同的命名和结构约定
3. **文档化**: 每个API必须有完整的文档
4. **错误处理**: 所有可能的错误状态都应该被考虑和处理

## 命名约定

- API路径使用小写单词，多个单词之间用下划线连接，如 `/user_info`
- 处理函数名应该与路径保持一致
- 请求参数名使用小写驼峰式命名，如 `userName`

## 请求方式

- 所有API都使用GET请求方式
- 参数通过URL参数传递（Query String）

## 响应格式

所有API响应都应该使用以下标准格式：

```json
{
  "success": true/false,             // 操作是否成功
  "message": "操作结果描述",          // 操作结果的描述信息
  "data": {                          // 返回的数据(可选)
    // 具体数据字段
  }
}
```

## 错误处理

- 所有错误响应都应该包含有意义的错误信息
- 使用适当的HTTP状态码
  - 200: OK
  - 201: Created
  - 400: Bad Request
  - 401: Unauthorized
  - 404: Not Found
  - 500: Internal Server Error

## 代码注释格式

每个API函数都应该包含详细的文档字符串，格式如下：

```python
@api.route('/example', methods=['GET'])
def example():
    """
    简短的API描述（一句话）
    
    详细的API描述，包括该API的用途和任何需要说明的重要信息。
    
    参数:
    - param1: 参数1的描述，包括类型、是否必填等
    - param2: 参数2的描述
    
    返回:
    - success: 操作是否成功
    - message: 操作结果描述
    - data: 返回的数据结构描述
    """
    # 函数实现
```

## 添加新API的步骤

1. 在routes.py中添加新的路由和处理函数
2. 按照上述格式添加详细的文档注释
3. 实现API功能
4. 编写测试代码
5. 更新API文档：运行 `python update_api_docs.py`
6. 修改生成的文档，添加更详细的信息
7. 确认无误后替换现有的API_DOCS.md文件

## API文档模板

每个API在文档中应包含以下部分：

```markdown
### API名称

简短描述

**请求URL**:
```
GET /api/path
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|-----|------|
| param1 | string | 是 | 参数1描述 |
| param2 | number | 否 | 参数2描述 |

**请求示例**:
```
GET /api/path?param1=value1&param2=value2
```

**成功响应** (状态码: 200):
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 数据字段
  }
}
```

**错误响应**:

1. 错误情况1 (状态码: xxx):
```json
{
  "success": false,
  "message": "错误描述"
}
```
```

## 示例

以用户登录API为例：

```python
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
    # 实现代码
```

对应的API文档：

```markdown
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
```

## 结论

遵循这些指南将确保接码平台API的一致性、可用性和可维护性。随着项目的发展，这些指南也可能会更新。 
import sqlite3

def get_all_users():
    """获取所有用户记录"""
    conn = sqlite3.connect('sms_api.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    
    conn.close()
    return users

def print_user_info(user):
    """打印用户信息"""
    print(f"ID: {user[0]}")
    print(f"用户名: {user[1]}")
    print(f"密码: {user[2]}")
    print(f"邮箱: {user[3]}")
    print(f"安全问题: {user[4]}")
    if user[5]:
        print(f"Token: {user[5][:20]}...")
    else:
        print("Token: 无")
    print(f"余额: {user[6]}")
    print("-" * 50)

def check_db():
    """检查数据库中的用户记录"""
    users = get_all_users()
    
    print("查询用户表中的所有记录...")
    if not users:
        print("数据库中没有用户记录")
    else:
        print(f"共找到 {len(users)} 条用户记录:")
        for i, user in enumerate(users):
            print(f"记录 {i+1}:")
            print_user_info(user) 
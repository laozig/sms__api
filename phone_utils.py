import random

# 手机号码前缀(前三位)
# 移动号段
CHINA_MOBILE_PREFIX = [
    '134', '135', '136', '137', '138', '139',
    '150', '151', '152', '157', '158', '159',
    '182', '183', '184', '187', '188', '178',
    '147', '172', '198'
]

# 联通号段
CHINA_UNICOM_PREFIX = [
    '130', '131', '132', '155', '156',
    '185', '186', '166', '145', '175',
    '176', '171', '166'
]

# 电信号段
CHINA_TELECOM_PREFIX = [
    '133', '153', '177', '173', '180',
    '181', '189', '199', '149'
]

# 虚拟运营商号段
VIRTUAL_PREFIX = [
    '170', '171', '165', '167', '162', 
    '174', '191', '192', '195', '196', 
    '197', '198', '199'
]

def generate_random_phone(carrier_type=0, number_type=0):
    """
    生成随机手机号码
    
    参数:
    - carrier_type: 运营商类型，0不限，1移动，2联通，3电信
    - number_type: 号段类型，0不限，1正常，2虚拟
    
    返回:
    - 生成的随机手机号码
    """
    # 选择运营商前缀
    if carrier_type == 0:  # 不限运营商
        if number_type == 0:  # 不限号段类型
            # 随机选择所有运营商的所有号段
            all_prefixes = CHINA_MOBILE_PREFIX + CHINA_UNICOM_PREFIX + CHINA_TELECOM_PREFIX
            prefix = random.choice(all_prefixes)
        elif number_type == 1:  # 正常号段
            # 排除虚拟号段
            normal_prefixes = [p for p in (CHINA_MOBILE_PREFIX + CHINA_UNICOM_PREFIX + CHINA_TELECOM_PREFIX) 
                               if p not in VIRTUAL_PREFIX]
            prefix = random.choice(normal_prefixes)
        else:  # 虚拟号段
            prefix = random.choice(VIRTUAL_PREFIX)
    elif carrier_type == 1:  # 移动
        if number_type == 0 or number_type == 1:  # 不限或正常号段
            # 移动非虚拟号段
            normal_mobile = [p for p in CHINA_MOBILE_PREFIX if p not in VIRTUAL_PREFIX]
            prefix = random.choice(normal_mobile)
        else:  # 虚拟号段
            # 移动虚拟号段
            virtual_mobile = [p for p in VIRTUAL_PREFIX if p in CHINA_MOBILE_PREFIX]
            # 如果没有符合条件的号段，使用普通移动号段
            if not virtual_mobile:
                prefix = random.choice(CHINA_MOBILE_PREFIX)
            else:
                prefix = random.choice(virtual_mobile)
    elif carrier_type == 2:  # 联通
        if number_type == 0 or number_type == 1:  # 不限或正常号段
            # 联通非虚拟号段
            normal_unicom = [p for p in CHINA_UNICOM_PREFIX if p not in VIRTUAL_PREFIX]
            prefix = random.choice(normal_unicom)
        else:  # 虚拟号段
            # 联通虚拟号段
            virtual_unicom = [p for p in VIRTUAL_PREFIX if p in CHINA_UNICOM_PREFIX]
            # 如果没有符合条件的号段，使用普通联通号段
            if not virtual_unicom:
                prefix = random.choice(CHINA_UNICOM_PREFIX)
            else:
                prefix = random.choice(virtual_unicom)
    elif carrier_type == 3:  # 电信
        if number_type == 0 or number_type == 1:  # 不限或正常号段
            # 电信非虚拟号段
            normal_telecom = [p for p in CHINA_TELECOM_PREFIX if p not in VIRTUAL_PREFIX]
            prefix = random.choice(normal_telecom)
        else:  # 虚拟号段
            # 电信虚拟号段
            virtual_telecom = [p for p in VIRTUAL_PREFIX if p in CHINA_TELECOM_PREFIX]
            # 如果没有符合条件的号段，使用普通电信号段
            if not virtual_telecom:
                prefix = random.choice(CHINA_TELECOM_PREFIX)
            else:
                prefix = random.choice(virtual_telecom)
    
    # 生成后8位随机数字
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    
    # 组合前缀和后缀生成完整手机号
    phone = prefix + suffix
    
    return phone

def is_valid_phone(phone):
    """
    验证手机号码是否有效
    
    参数:
    - phone: 手机号码
    
    返回:
    - 是否有效
    """
    # 检查长度
    if len(phone) != 11:
        return False
    
    # 检查是否全为数字
    if not phone.isdigit():
        return False
    
    # 检查前三位是否为有效运营商前缀
    prefix = phone[:3]
    if prefix not in (CHINA_MOBILE_PREFIX + CHINA_UNICOM_PREFIX + CHINA_TELECOM_PREFIX):
        return False
    
    return True

def get_carrier_type(phone):
    """
    获取手机号码的运营商类型
    
    参数:
    - phone: 手机号码
    
    返回:
    - 1: 移动, 2: 联通, 3: 电信, 0: 未知
    """
    if not is_valid_phone(phone):
        return 0
    
    prefix = phone[:3]
    
    if prefix in CHINA_MOBILE_PREFIX:
        return 1
    elif prefix in CHINA_UNICOM_PREFIX:
        return 2
    elif prefix in CHINA_TELECOM_PREFIX:
        return 3
    else:
        return 0

def get_number_type(phone):
    """
    获取手机号码的号段类型
    
    参数:
    - phone: 手机号码
    
    返回:
    - 1: 正常号段, 2: 虚拟号段, 0: 未知
    """
    if not is_valid_phone(phone):
        return 0
    
    prefix = phone[:3]
    
    if prefix in VIRTUAL_PREFIX:
        return 2
    else:
        return 1 
import threading
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

# 全局线程池，增加最大工作线程数以处理更高的并发
thread_pool = ThreadPoolExecutor(max_workers=50)

def run_async(func):
    """
    运行异步函数并等待结果
    
    参数:
    - func: 异步函数
    
    返回:
    - 函数结果
    """
    result = func()
    return result

def run_in_thread(func):
    """
    在线程池中运行函数
    
    参数:
    - func: 需要在线程中执行的函数
    
    返回:
    - 函数执行的Future
    """
    return thread_pool.submit(func)

# 数据库连接池管理
class DBConnectionPool:
    """
    数据库连接池管理类
    
    管理SQLAlchemy数据库连接池配置
    """
    @staticmethod
    def configure(app, pool_size=20, max_overflow=30, timeout=60):
        """
        配置SQLAlchemy数据库连接池
        
        参数:
        - app: Flask应用实例
        - pool_size: 连接池大小
        - max_overflow: 最大溢出连接数
        - timeout: 连接超时时间(秒)
        """
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': pool_size,
            'max_overflow': max_overflow,
            'pool_timeout': timeout,
            'pool_recycle': 1800,  # 30分钟后回收连接
            'pool_pre_ping': True  # 使用前测试连接是否有效
        }

class AsyncDatabase:
    """
    异步数据库操作工具类
    
    提供异步方式执行数据库操作的方法
    """
    
    @staticmethod
    async def execute_query(query_func, *args, **kwargs):
        """
        异步执行数据库查询
        
        参数:
        - query_func: 查询函数
        - args, kwargs: 传递给查询函数的参数
        
        返回:
        - 查询结果
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            thread_pool, 
            functools.partial(query_func, *args, **kwargs)
        )
    
    @staticmethod
    async def execute_transaction(transaction_func, *args, **kwargs):
        """
        异步执行数据库事务
        
        参数:
        - transaction_func: 事务函数
        - args, kwargs: 传递给事务函数的参数
        
        返回:
        - 事务执行结果
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            thread_pool, 
            functools.partial(transaction_func, *args, **kwargs)
        )

class RateLimiter:
    """
    请求限流器
    
    控制API请求速率，防止系统过载
    """
    
    def __init__(self, max_calls, time_frame):
        """
        初始化限流器
        
        参数:
        - max_calls: 时间窗口内最大请求数
        - time_frame: 时间窗口(秒)
        """
        self.max_calls = max_calls
        self.time_frame = time_frame
        self.calls = {}  # 改为字典存储，key为客户端标识
        self.lock = threading.Lock()
    
    def try_acquire(self, client_id=None):
        """
        尝试获取请求许可
        
        参数:
        - client_id: 客户端标识(IP地址、用户ID等)
        
        返回:
        - 是否允许请求
        """
        current_time = asyncio.get_event_loop().time()
        
        with self.lock:
            # 为每个客户端单独计数
            if client_id not in self.calls:
                self.calls[client_id] = []
            
            # 移除过期的请求记录
            self.calls[client_id] = [call_time for call_time in self.calls[client_id] 
                                    if current_time - call_time < self.time_frame]
            
            # 检查是否超过限制
            if len(self.calls[client_id]) >= self.max_calls:
                return False
            
            # 记录新请求
            self.calls[client_id].append(current_time)
            return True

# 全局API速率限制器
api_rate_limiter = RateLimiter(max_calls=100, time_frame=60)  # 每个客户端每分钟100个请求

# 请求并发控制函数
def concurrency_control(max_concurrent=50):
    """
    并发控制装饰器
    
    限制函数的并发执行数量
    
    参数:
    - max_concurrent: 最大并发数
    
    返回:
    - 装饰后的函数
    """
    semaphore = threading.Semaphore(max_concurrent)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            acquired = semaphore.acquire(blocking=False)
            if not acquired:
                return {
                    'message': '服务器繁忙，请稍后再试',
                    'code': -1,
                    'data': None,
                    'status_code': 503  # Service Unavailable
                }
            
            try:
                return func(*args, **kwargs)
            finally:
                semaphore.release()
        
        return wrapper
    
    return decorator 
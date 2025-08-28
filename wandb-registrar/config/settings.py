import os
import urllib.parse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# TempMailHub API配置
TEMPMAILHUB_API_URL = os.getenv('TEMPMAILHUB_API_URL', 'https://tempmailhub.xjtuglory.workers.dev')
TEMPMAILHUB_API_KEY = os.getenv('TEMPMAILHUB_API_KEY', '')

# Mail.tm API配置（已弃用）
MAIL_TM_API_URL = os.getenv('MAIL_TM_API_URL', 'https://api.mail.tm')

# 注册后配置 - 使用动态生成的随机名称
def get_random_full_name():
    """获取随机生成的全名"""
    from utils.random_generator import generate_random_string
    return generate_random_string(4, 10)

def get_random_company_name():
    """获取随机生成的公司名"""
    from utils.random_generator import generate_random_string
    return generate_random_string(4, 10)

# 默认配置
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3

# 注册执行次数配置
REGISTRATION_COUNT = int(os.getenv('REGISTRATION_COUNT', 1))

# Headless模式配置
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'true').lower() in ('true', '1', 'yes')

# Visual Debug Mode
VISUAL_DEBUG_ENABLED = os.getenv('VISUAL_DEBUG_ENABLED', 'false').lower() in ('true', '1', 'yes')


# 代理配置
PROXY_URL = os.getenv('PROXY_URL', None)


def parse_proxy_url(proxy_url):
    """解析代理URL并返回代理配置字典"""
    if not proxy_url:
        return None
    
    parsed = urllib.parse.urlparse(proxy_url)
    
    proxy_config = {
        'scheme': parsed.scheme,
        'hostname': parsed.hostname,
        'port': parsed.port,
        'username': parsed.username,
        'password': parsed.password
    }
    
    return proxy_config
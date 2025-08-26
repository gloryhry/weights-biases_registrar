import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Mail.tm API配置
MAIL_TM_API_URL = os.getenv('MAIL_TM_API_URL', 'https://api.mail.tm')

# 注册后配置
FULL_NAME = os.getenv('FULL_NAME', 'Zhi Yang')
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Linux Do')

# 默认配置
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
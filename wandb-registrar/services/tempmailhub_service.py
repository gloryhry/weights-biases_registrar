import requests
import time
import logging
import re
from config.settings import TEMPMAILHUB_API_URL, TEMPMAILHUB_API_KEY, DEFAULT_TIMEOUT, PROXY_URL, parse_proxy_url

class TempMailHubClient:
    """TempMailHub API客户端"""
    
    def __init__(self):
        self.base_url = TEMPMAILHUB_API_URL
        self.api_key = TEMPMAILHUB_API_KEY
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # 配置API Key认证
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        # 配置SSL适配器以处理SSL问题
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 配置代理
        if PROXY_URL:
            proxy_config = parse_proxy_url(PROXY_URL)
            if proxy_config:
                proxies = {
                    'http': PROXY_URL,
                    'https': PROXY_URL
                }
                self.session.proxies.update(proxies)
                self.logger.info(f"已配置代理: {PROXY_URL}")
    
    def create_account(self, username=None, provider='mailtm'):
        """创建临时邮箱账户"""
        try:
            payload = {
                'provider': provider
            }
            
            # 如果提供了用户名前缀，则使用
            if username:
                payload['prefix'] = username
            
            self.logger.info(f"正在创建账户，请求参数: {payload}")
            
            response = self.session.post(
                f"{self.base_url}/api/mail/create",
                json=payload,
                timeout=DEFAULT_TIMEOUT
            )
            
            self.logger.info(f"API响应状态码: {response.status_code}")
            self.logger.info(f"API响应内容: {response.text}")
            
            # 检查是否是429错误（请求过于频繁）
            if response.status_code == 429:
                self.logger.warning("请求过于频繁，等待60秒后重试")
                time.sleep(60)
                # 重新尝试一次
                response = self.session.post(
                    f"{self.base_url}/api/mail/create",
                    json=payload,
                    timeout=DEFAULT_TIMEOUT
                )
                self.logger.info(f"重试后API响应状态码: {response.status_code}")
                self.logger.info(f"重试后API响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    account = result.get('data', {})
                    self.logger.info(f"成功创建邮箱账户: {account.get('address')}")
                    return account
                else:
                    self.logger.error(f"创建账户失败: {result.get('message', 'Unknown error')}")
                    return None
            else:
                self.logger.error(f"创建账户失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建账户时发生错误: {str(e)}")
            return None
    
    def get_messages(self, email, access_token=None, limit=20):
        """获取邮件列表"""
        try:
            payload = {
                'address': email,
                'limit': limit
            }
            
            # 如果提供了access_token，则添加到payload中（仅Mail.tm需要）
            if access_token:
                payload['accessToken'] = access_token
            
            response = self.session.post(
                f"{self.base_url}/api/mail/list",
                json=payload,
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('data', [])
                else:
                    self.logger.error(f"获取邮件列表失败: {result.get('message', 'Unknown error')}")
                    return None
            else:
                self.logger.error(f"获取邮件列表失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取邮件列表时发生错误: {str(e)}")
            return None
    
    def get_message_content(self, email, message_id, access_token=None):
        """获取邮件详情内容"""
        try:
            payload = {
                'address': email,
                'id': message_id
            }
            
            # 如果提供了access_token，则添加到payload中（仅Mail.tm需要）
            if access_token:
                payload['accessToken'] = access_token
            
            response = self.session.post(
                f"{self.base_url}/api/mail/content",
                json=payload,
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('data', {})
                else:
                    self.logger.error(f"获取邮件详情失败: {result.get('message', 'Unknown error')}")
                    return None
            else:
                self.logger.error(f"获取邮件详情失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取邮件详情时发生错误: {str(e)}")
            return None
    
    def get_verification_link(self, email, access_token=None):
        """获取Wandb验证链接"""
        try:
            # 轮询邮件（最多等待5分钟）
            max_attempts = 30
            for attempt in range(max_attempts):
                messages = self.get_messages(email, access_token)
                if messages:
                    for message in messages:
                        # 查找来自 support@wandb.com 的验证邮件
                        from_address = message.get('from', {}).get('email', '').lower()
                        if 'support@wandb.com' in from_address:
                            # 获取邮件详情
                            message_id = message.get('id')
                            if message_id:
                                message_detail = self.get_message_content(email, message_id, access_token)
                                if message_detail:
                                    self.logger.info(f"收到来自 {from_address} 的邮件，主题: {message_detail.get('subject', '')}")
                                    
                                    # 提取验证链接
                                    text_content = message_detail.get('textContent', '')
                                    # 匹配包含 wandb.auth0.com 的完整链接
                                    links = re.findall(r'https?://wandb\.auth0\.com[^\s<>"\)]+', text_content)
                                    if links:
                                        verification_link = links[0]
                                        self.logger.info(f"找到验证链接: {verification_link}")
                                        return verification_link
                
                # 等待10秒后重试
                time.sleep(10)
            
            self.logger.warning("未找到验证邮件")
            return None
            
        except Exception as e:
            self.logger.error(f"获取验证链接时发生错误: {str(e)}")
            return None
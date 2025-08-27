import requests
import time
import logging
import random
from config.settings import MAIL_TM_API_URL, DEFAULT_TIMEOUT, PROXY_URL, parse_proxy_url

class MailTMApiClient:
    """Mail.tm API客户端"""
    
    def __init__(self):
        self.base_url = MAIL_TM_API_URL
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
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
    
    def _get_domains(self, max_retries=3):
        """获取域名列表，包含重试机制"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    f"{self.base_url}/domains",
                    timeout=DEFAULT_TIMEOUT
                )
                
                if response.status_code == 200:
                    domains = response.json().get('hydra:member', [])
                    # 过滤出激活的域名
                    active_domains = [d for d in domains if d.get('isActive')]
                    return active_domains
                else:
                    self.logger.warning(f"获取域名列表失败 (尝试 {attempt + 1}/{max_retries}): {response.status_code} - {response.text}")
                    
            except Exception as e:
                self.logger.warning(f"获取域名列表时发生错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            
            # 如果不是最后一次尝试，等待一段时间再重试
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
        
        self.logger.error("获取域名列表失败，已达到最大重试次数")
        return None
    
    def _get_random_domain(self):
        """获取一个随机的激活域名"""
        domains = self._get_domains()
        if domains is None:
            return None
        
        if not domains:
            self.logger.error("没有找到可用的激活域名")
            return None
        
        # 随机选择一个域名
        selected_domain = random.choice(domains)
        self.logger.info(f"随机选择域名: {selected_domain.get('domain')}")
        return selected_domain
    
    def create_account(self, username, password):
        """创建临时邮箱账户，使用动态获取的域名"""
        try:
            # 获取随机域名
            domain_info = self._get_random_domain()
            if not domain_info:
                self.logger.error("无法获取有效的域名")
                return None
            
            domain = domain_info.get('domain')
            domain_id = domain_info.get('@id')
            
            # 创建账户
            account_data = {
                'address': f"{username}@{domain}",
                'password': password
            }
            
            response = self.session.post(
                f"{self.base_url}/accounts",
                json=account_data,
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 201:
                account = response.json()
                self.logger.info(f"成功创建邮箱账户: {account['address']}")
                return account
            else:
                self.logger.error(f"创建账户失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建账户时发生错误: {str(e)}")
            return None
    
    def get_token(self, email, password):
        """获取账户访问令牌"""
        try:
            auth_data = {
                'address': email,
                'password': password
            }
            
            response = self.session.post(
                f"{self.base_url}/token",
                json=auth_data,
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 200:
                token = response.json().get('token')
                self.session.headers['Authorization'] = f"Bearer {token}"
                self.logger.info("成功获取访问令牌")
                return token
            else:
                self.logger.error(f"获取令牌失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取令牌时发生错误: {str(e)}")
            return None
    
    def get_messages(self, page=1):
        """获取邮件列表"""
        try:
            response = self.session.get(
                f"{self.base_url}/messages?page={page}",
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"获取邮件列表失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取邮件列表时发生错误: {str(e)}")
            return None
    
    def get_verification_link(self, email, password):
        """获取Wandb验证链接"""
        try:
            # 获取访问令牌
            token = self.get_token(email, password)
            if not token:
                return None
            
            # 轮询邮件（最多等待5分钟）
            max_attempts = 30
            for attempt in range(max_attempts):
                messages_data = self.get_messages()
                if messages_data and 'hydra:member' in messages_data:
                    messages = messages_data['hydra:member']
                    for message in messages:
                        # 查找来自 support@wandb.com 的验证邮件
                        from_address = message.get('from', {}).get('address', '').lower()
                        if 'support@wandb.com' in from_address:
                            # 获取邮件详情
                            message_id = message.get('@id', '').split('/')[-1]
                            if message_id:
                                detail_response = self.session.get(
                                    f"{self.base_url}/messages/{message_id}",
                                    timeout=DEFAULT_TIMEOUT
                                )
                                
                                if detail_response.status_code == 200:
                                    message_detail = detail_response.json()
                                    self.logger.info(f"收到来自 {from_address} 的邮件，内容: {message_detail.get('text', '')}")
                                    # 提取验证链接
                                    text_content = message_detail.get('text', '')
                                    import re
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
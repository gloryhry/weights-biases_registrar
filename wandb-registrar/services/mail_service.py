import requests
import time
import logging
from config.settings import MAIL_TM_API_URL, DEFAULT_TIMEOUT

class MailTMApiClient:
    """Mail.tm API客户端"""
    
    def __init__(self):
        self.base_url = MAIL_TM_API_URL
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def create_account(self, username, password, domain):
        """创建临时邮箱账户"""
        try:
            # 检查域名是否存在
            domain_response = self.session.get(
                f"{self.base_url}/domains?page=1",
                timeout=DEFAULT_TIMEOUT
            )
            
            domain_id = None
            if domain_response.status_code == 200:
                domains = domain_response.json().get('hydra:member', [])
                for d in domains:
                    if d.get('domain') == domain and d.get('isActive'):
                        domain_id = d.get('@id')
                        break
            
            if not domain_id:
                self.logger.error(f"域名 {domain} 不存在或未激活")
                return None
            
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
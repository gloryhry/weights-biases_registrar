import time
import logging
import re
from services.mail_service import MailTMApiClient
from services.browser_service import BrowserAutomation
from utils.password_generator import generate_secure_password
from utils.logger import setup_logger
from config.settings import MAIL_TM_DOMAIN, DEFAULT_RETRY_ATTEMPTS, FULL_NAME, COMPANY_NAME

class RegistrationOrchestrator:
    """注册流程协调器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.mail_client = MailTMApiClient()
        self.browser_service = BrowserAutomation()
    
    def execute_registration(self, headless=True):
        """执行完整注册流程"""
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            try:
                self.logger.info(f"开始第 {attempt + 1} 次注册尝试")
                
                # 生成随机邮箱用户名和密码
                username = f"wandb_user_{int(time.time())}"
                password = generate_secure_password()
                email = f"{username}@{MAIL_TM_DOMAIN}"
                
                self.logger.info(f"生成账户信息: {email}")
                
                # 创建临时邮箱账户
                account = self.mail_client.create_account(username, password, MAIL_TM_DOMAIN)
                if not account:
                    self.logger.error("创建临时邮箱账户失败")
                    time.sleep(10)  # 等待10秒
                    continue
                
                # 启动浏览器
                if not self.browser_service.start_browser(headless=headless):
                    self.logger.error("启动浏览器失败")
                    time.sleep(10)  # 等待10秒
                    continue
                
                # 导航到注册页面并填写表单
                if not self.browser_service.navigate_to_signup():
                    self.logger.error("导航到注册页面失败")
                    self.browser_service.close_browser()
                    time.sleep(10)  # 等待10秒
                    continue
                
                if not self.browser_service.fill_registration_form(email, password):
                    self.logger.error("填写注册表单失败")
                    self.browser_service.close_browser()
                    time.sleep(10)  # 等待10秒
                    continue
                
                # 等待注册完成
                # 使用改进的检查方式
                if hasattr(self.browser_service, 'page') and self.browser_service.page:
                    self.browser_service.page.wait_for_load_state('networkidle')
                
                # 获取验证链接
                self.logger.info("等待验证邮件...")
                verification_link = self.mail_client.get_verification_link(email, password)
                
                if not verification_link:
                    self.logger.error("获取验证链接失败")
                    self.browser_service.close_browser()
                    time.sleep(10)  # 等待10秒
                    continue
                
                # 打开验证链接
                if not self.browser_service.open_verification_link_in_new_tab(verification_link):
                    self.logger.error("打开验证链接失败")
                    self.browser_service.close_browser()
                    time.sleep(10)  # 等待10秒
                    continue
                
                # 完成注册后的步骤
                if self.complete_registration_process(email, password, verification_link):
                    # 提取API密钥
                    api_key = self.extract_api_key()
                    
                    # 保存账户信息和API密钥
                    self.save_account_info(email, password, api_key)
                    
                    self.logger.info(f"注册成功: {email}")
                    # 确保浏览器正确关闭
                    try:
                        self.browser_service.close_browser()
                    except Exception as close_error:
                        self.logger.warning(f"关闭浏览器时发生错误: {str(close_error)}")
                    return True
                else:
                    self.logger.error("完成注册流程失败")
                    # 确保浏览器正确关闭
                    try:
                        self.browser_service.close_browser()
                    except Exception as close_error:
                        self.logger.warning(f"关闭浏览器时发生错误: {str(close_error)}")
                    return False
                
            except Exception as e:
                self.logger.error(f"注册过程中发生错误: {str(e)}")
                try:
                    self.browser_service.close_browser()
                except Exception as close_error:
                    self.logger.warning(f"关闭浏览器时发生错误: {str(close_error)}")
                time.sleep(10)  # 增加延迟
                continue
        
        self.logger.error("所有注册尝试均失败")
        return False
    
    def complete_registration_process(self, email, password, verification_url):
        """完成注册后的所有步骤 - 协调方法
        
        Args:
            email (str): 临时邮箱地址，用于定位显示邮箱按钮
            password (str): 账户密码
            verification_url (str): 验证链接
        """
        try:
            # 使用改进的完整注册流程方法
            # success = self.browser_service.complete_registration_process(email, password, verification_url)
            # if not success:
            #     self.logger.error("浏览器服务中的完整注册流程执行失败")
            #     return False
            
            # 填写用户详情
            self._fill_user_details()
            
            # 处理组织设置
            self._handle_organization_setup()
            
            # 处理产品选择
            self._handle_product_selection()
            
            return True
        except Exception as e:
            self.logger.error(f"完成注册流程时发生错误: {str(e)}")
            return False
    
    def _fill_user_details(self):
        """填写用户详情信息"""
        # 检查页面是否可用
        if not hasattr(self.browser_service, 'page') or not self.browser_service.page:
            self.logger.error("浏览器页面未初始化，无法填写用户详情")
            return
            
        try:
            # 等待页面加载
            self.browser_service.page.wait_for_load_state('networkidle')
            
            # 填写Full name和Company or Institution
            full_name_input = self.browser_service.page.locator('input[aria-label="Full name"]')
            if full_name_input.count() > 0:
                full_name_input.fill(FULL_NAME)
                self.logger.info(f"已填写Full name: {FULL_NAME}")
            
            company_input = self.browser_service.page.locator('input[aria-label="Company or Institution"]')
            if company_input.count() > 0:
                company_input.fill(COMPANY_NAME)
                self.logger.info(f"已填写Company or Institution: {COMPANY_NAME}")
            
            # 勾选复选框
            terms_checkbox = self.browser_service.page.locator('input[type="checkbox"]')
            if terms_checkbox.count() > 0:
                terms_checkbox.first.click()
                self.logger.info("已勾选Terms of Service and Privacy Policy")
            
            # 点击Continue按钮
            continue_button = self.browser_service.page.locator('button:has-text("Continue")').first
            if continue_button.count() > 0:
                continue_button.click()
                self.logger.info("已点击Continue按钮")
            
            # 等待页面跳转
            self.browser_service.page.wait_for_load_state('networkidle')
        except Exception as e:
            self.logger.error(f"填写用户详情时发生错误: {str(e)}")
            # 不抛出异常，继续执行
    
    def _handle_organization_setup(self):
        """处理组织设置"""
        # 检查页面是否可用
        if not hasattr(self.browser_service, 'page') or not self.browser_service.page:
            self.logger.error("浏览器页面未初始化，无法处理组织设置")
            return
            
        try:
            # 等待页面加载
            self.browser_service.page.wait_for_load_state('networkidle')
            
            # 在Create your organization页面点击Continue按钮
            create_org_continue_button = self.browser_service.page.locator('button:has-text("Continue")').first
            if create_org_continue_button.count() > 0:
                create_org_continue_button.click()
                self.logger.info("已在Create your organization页面点击Continue按钮")
            
            # 等待页面跳转
            self.browser_service.page.wait_for_load_state('networkidle')
        except Exception as e:
            self.logger.error(f"处理组织设置时发生错误: {str(e)}")
            # 不抛出异常，继续执行
    
    def _handle_product_selection(self):
        """处理产品选择"""
        # 检查页面是否可用
        if not hasattr(self.browser_service, 'page') or not self.browser_service.page:
            self.logger.error("浏览器页面未初始化，无法处理产品选择")
            return
            
        try:
            # 等待页面加载
            self.browser_service.page.wait_for_load_state('networkidle')
            
            # 在What do you want to try first?页面点击Weave选项
            weave_option = self.browser_service.page.locator('button:has-text("Weave")')
            if weave_option.count() > 0:
                weave_option.click()
                self.logger.info("已点击Weave选项")
                
                # 点击Continue按钮
                weave_continue_button = self.browser_service.page.locator('button:has-text("Continue")').first
                if weave_continue_button.count() > 0:
                    weave_continue_button.click()
                    self.logger.info("已在Weave页面点击Continue按钮")
                
                # 等待页面跳转
                self.browser_service.page.wait_for_load_state('networkidle')
        except Exception as e:
            self.logger.error(f"处理产品选择时发生错误: {str(e)}")
            # 不抛出异常，继续执行
    
    def extract_api_key(self):
        """提取API密钥"""
        # 检查页面是否可用
        if not hasattr(self.browser_service, 'page') or not self.browser_service.page:
            self.logger.error("浏览器页面未初始化，无法提取API密钥")
            return None
            
        try:
            # 导航到API密钥页面
            self.browser_service.page.goto("https://wandb.ai/authorize", timeout=DEFAULT_RETRY_ATTEMPTS * 1000)
            self.browser_service.page.wait_for_load_state('networkidle')
            
            # 等待页面内容加载，使用动态等待替代time.sleep
            # 等待包含API密钥的元素出现（如code或pre标签）
            self.browser_service.page.wait_for_selector('code, pre, body', timeout=10000)
            
            # 提取API密钥
            # 方法1: 查找包含API密钥的代码块
            code_elements = self.browser_service.page.locator('code, pre')
            for i in range(code_elements.count()):
                element_text = code_elements.nth(i).text_content()
                # 匹配wandb API密钥格式（通常为40位以上的字母数字字符）
                api_key_match = re.search(r'[a-zA-Z0-9_-]{40,}', element_text)
                if api_key_match:
                    api_key = api_key_match.group(0)
                    self.logger.info(f"在代码块中找到API密钥: {api_key[:10]}...")
                    return api_key
            
            # 方法2: 查找页面上的文本内容
            page_content = self.browser_service.page.text_content('body')
            if page_content:
                api_key_match = re.search(r'[a-zA-Z0-9_-]{40,}', page_content)
                if api_key_match:
                    api_key = api_key_match.group(0)
                    self.logger.info(f"在页面文本中找到API密钥: {api_key[:10]}...")
                    return api_key
            
            self.logger.warning("未找到API密钥")
            return None
        except Exception as e:
            self.logger.error(f"提取API密钥时发生错误: {str(e)}")
            return None
    
    def save_account_info(self, email, password, api_key=None, auth_filename='auth.txt', key_filename='key.txt'):
        """保存账户信息到文件"""
        try:
            # 保存账户信息到auth.txt
            with open(auth_filename, 'a', encoding='utf-8') as f:
                if api_key:
                    f.write(f"{email}:{password}:{api_key}\n")
                else:
                    f.write(f"{email}:{password}\n")
            self.logger.info(f"账户信息已保存到 {auth_filename}")
            
            # 如果有API密钥，也保存到key.txt
            if api_key:
                with open(key_filename, 'a', encoding='utf-8') as f:
                    f.write(f"{api_key}\n")
                self.logger.info(f"API密钥已保存到 {key_filename}")
        except Exception as e:
            self.logger.error(f"保存账户信息时发生错误: {str(e)}")
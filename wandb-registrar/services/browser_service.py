import asyncio
import logging
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from config.settings import DEFAULT_TIMEOUT, PROXY_URL, parse_proxy_url, VISUAL_DEBUG_ENABLED, HEADLESS_MODE


class BrowserAutomation:
    """浏览器自动化控制 - 统一同步实现"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._event_loop = None
        self.headless_mode = None
        self.screenshot_dir = None
        self.screenshot_counter = 0
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，确保资源正确释放"""
        self.close_browser()
    
    def start_browser(self, headless=True):
        """启动浏览器"""
        self.headless_mode = headless
        if VISUAL_DEBUG_ENABLED and self.headless_mode:
            run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_dir = os.path.join("screenshots", f"run_{run_timestamp}")
            os.makedirs(self.screenshot_dir, exist_ok=True)
            self.screenshot_counter = 0
            self.logger.info(f"可视化调试已启用。截图将保存到: {self.screenshot_dir}")

        try:
            # 确保之前的所有资源都已正确清理
            self.close_browser()
            
            self.playwright = sync_playwright().start()
            
            # 配置浏览器启动参数
            launch_args = ['--no-sandbox', '--disable-dev-shm-usage']
            
            # 配置代理
            if PROXY_URL:
                proxy_config = parse_proxy_url(PROXY_URL)
                if proxy_config:
                    launch_args.extend([
                        f"--proxy-server={proxy_config['scheme']}://{proxy_config['hostname']}:{proxy_config['port']}"
                    ])
            
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=launch_args
            )
            
            # 创建带代理认证的上下文（如果需要）
            if PROXY_URL and proxy_config and proxy_config['username']:
                self.context = self.browser.new_context(
                    proxy={
                        "server": f"{proxy_config['scheme']}://{proxy_config['hostname']}:{proxy_config['port']}",
                        "username": proxy_config['username'],
                        "password": proxy_config['password']
                    }
                )
            else:
                self.context = self.browser.new_context()
            
            self.page = self.context.new_page()
            self.logger.info("浏览器启动成功")
            return True
        except Exception as e:
            self.logger.error(f"启动浏览器时发生错误: {str(e)}")
            # 确保在启动失败时清理资源
            self.close_browser()
            return False
    
    def navigate_to_signup(self, url="https://wandb.ai/site/"):
        """导航到注册页面"""
        if not self._check_page():
            return False
            
        try:
            self.page.goto(url, timeout=DEFAULT_TIMEOUT * 1000)
            self.logger.info(f"已导航到 {url}")
            
            # 等待新页面出现并切换
            with self.context.expect_page() as new_page_info:
                # 点击SIGN UP按钮
                signup_button = self.page.locator('a:has-text("Sign up"), a:has-text("SIGN UP")').first
                signup_button.click()
                self.logger.info("已点击 SIGN UP 按钮")
            
            self.page = new_page_info.value
            self.logger.info("已切换到新的注册页面")
            
            # 等待注册表单的邮件输入框出现
            self.page.wait_for_selector('input[type="email"]', timeout=DEFAULT_TIMEOUT * 1000)
            self.logger.info("注册表单已加载")
            return True
        except Exception as e:
            self.logger.error(f"导航到注册页面时发生错误: {str(e)}")
            return False
    
    def fill_registration_form(self, email, password):
        """填写注册表单"""
        if not self._check_page():
            return False
            
        try:
            # 填写邮箱
            email_input = self.page.locator('input[type="email"]')
            email_input.fill(email)
            self.logger.info(f"已填写邮箱: {email}")
            
            # 填写密码
            password_input = self.page.locator('input[type="password"]').first
            password_input.fill(password)
            self.logger.info("已填写密码")
            
            # 点击注册按钮
            signup_button = self.page.locator('button:has-text("Sign up")').first
            signup_button.click()
            self.logger.info("已提交注册表单")
            
            return True
        except Exception as e:
            self.logger.error(f"填写注册表单时发生错误: {str(e)}")
            return False
    
    def open_verification_link(self, verification_url):
        """打开验证链接"""
        if not self._check_page():
            return False
            
        try:
            self.page.goto(verification_url, timeout=DEFAULT_TIMEOUT * 1000)
            self.logger.info(f"已打开验证链接: {verification_url}")
            
            # 等待页面加载完成
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception as e:
            self.logger.error(f"打开验证链接时发生错误: {str(e)}")
            return False
    
    def click_show_email_button(self, email):
        """点击显示邮箱按钮
        
        Args:
            email (str): 临时邮箱地址，用于定位包含该邮箱文本的按钮
        """
        if not self._check_page():
            return False
            
        try:
            # 首先尝试主要定位器 - 查找具有特定类和文本的<a>标签
            main_selector = f'a.auth0-lock-social-button.auth0-lock-social-big-button:has-text("{email}")'
            self.logger.debug(f"尝试主要定位器: {main_selector}")
            
            # 等待按钮出现
            self.page.wait_for_selector(main_selector, timeout=DEFAULT_TIMEOUT * 1000)
            
            # 点击按钮
            self.page.click(main_selector)
            self.logger.info(f"成功点击显示邮箱按钮(主要定位器): {email}")
            
            # 等待页面加载完成
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception as main_error:
            self.logger.warning(f"使用主要定位器点击显示邮箱按钮失败: {main_error}")
            try:
                # 回退到基于类的选择器
                fallback_selector = f'a.auth0-lock-social-button.auth0-lock-social-big-button:has(div.auth0-lock-social-button-text:has-text("{email}"))'
                self.logger.debug(f"尝试备用定位器: {fallback_selector}")
                
                # 等待按钮出现
                self.page.wait_for_selector(fallback_selector, timeout=DEFAULT_TIMEOUT * 1000)
                
                # 点击按钮
                self.page.click(fallback_selector)
                self.logger.info(f"成功点击显示邮箱按钮(备用定位器): {email}")
                
                # 等待页面加载完成
                self.page.wait_for_load_state('networkidle')
                return True
            except Exception as fallback_error:
                self.logger.error(f"使用备用定位器点击显示邮箱按钮也失败: {fallback_error}")
                # 记录截图以便调试
                try:
                    screenshot_path = f"error_screenshot_{email.split('@')[0]}.png"
                    self.page.screenshot(path=screenshot_path)
                    self.logger.info(f"错误截图已保存至: {screenshot_path}")
                except Exception as screenshot_error:
                    self.logger.warning(f"保存错误截图时发生错误: {screenshot_error}")
                return False
    
    def handle_post_verification_navigation(self):
        """处理验证后页面导航"""
        if not self._check_page():
            return False
            
        try:
            # 等待页面加载
            self.page.wait_for_load_state('networkidle')
            
            # 可以在这里添加后续页面操作的逻辑
            self.logger.info("验证后页面处理完成")
            return True
        except Exception as e:
            self.logger.warning(f"处理验证后页面导航时出现问题: {e}")
            return False
    
    def complete_registration_process(self, email, password, verification_url):
        """执行完整注册流程"""
        try:
            # 1. 填写并提交注册表单
            if not self.fill_registration_form(email, password):
                return False
            
            # 2. 打开验证链接
            if not self.open_verification_link(verification_url):
                return False
            
            # 3. 点击显示邮箱按钮
            if not self.click_show_email_button(email):
                # 不抛出异常，记录错误并继续执行
                self.logger.warning("点击显示邮箱按钮失败，但继续执行后续步骤")
            
            # 4. 处理验证后的页面导航
            if not self.handle_post_verification_navigation():
                return False
            
            self.logger.info("完整注册流程执行成功")
            return True
        except Exception as e:
            self.logger.error(f"注册流程执行失败: {e}")
            return False
    
    def close_browser(self):
        """关闭浏览器实例"""
        try:
            # 先检查浏览器是否存在且已连接
            if self.browser and self.browser.is_connected():
                try:
                    self.browser.close()
                    self.logger.info("浏览器已关闭")
                except Exception as e:
                    self.logger.warning(f"关闭浏览器时发生错误: {e}")
            else:
                if self.browser:
                    self.logger.warning("浏览器已经断开连接或未初始化")
                else:
                    self.logger.debug("浏览器未初始化")
        except Exception as e:
            self.logger.error(f"关闭浏览器时出错: {e}")
        finally:
            # 清理资源
            self.browser = None
            self.context = None
            self.page = None
            
            # 关闭playwright实例
            try:
                if self.playwright:
                    self.playwright.stop()
                    self.logger.info("Playwright实例已停止")
            except Exception as e:
                self.logger.error(f"停止Playwright实例时出错: {e}")
            finally:
                self.playwright = None
    
    def open_verification_link_in_new_tab(self, verification_url):
        """在新标签页中打开验证链接"""
        if not self._check_context():
            return False
            
        try:
            # 保存当前页面引用，以便在需要时回退
            original_page = self.page
            
            # 创建新页面
            new_page = self.context.new_page()
            
            try:
                # 在新页面中打开验证链接
                new_page.goto(verification_url, timeout=DEFAULT_TIMEOUT * 1000)
                self.logger.info(f"已在新标签页中打开验证链接: {verification_url}")
                
                # 等待页面加载完成
                new_page.wait_for_load_state('networkidle')
                
                # 将新页面设置为当前页面，以便后续操作可以正常进行
                self.page = new_page
                
                # 尝试关闭原始页面以释放资源
                try:
                    if original_page and not original_page.is_closed():
                        original_page.close()
                except Exception as close_error:
                    self.logger.warning(f"关闭原始页面时发生错误: {str(close_error)}")
                
                return True
            except Exception as goto_error:
                # 如果导航失败，尝试关闭新页面
                try:
                    if new_page and not new_page.is_closed():
                        new_page.close()
                except Exception as close_error:
                    self.logger.warning(f"关闭新页面时发生错误: {str(close_error)}")
                
                self.logger.error(f"在新标签页中打开验证链接时发生错误: {str(goto_error)}")
                return False
                
        except Exception as e:
            self.logger.error(f"创建新页面时发生错误: {str(e)}")
            return False
    
    def _check_page(self):
        """检查页面是否可用"""
        if not self.page:
            self.logger.error("页面未初始化")
            return False
        return True
    
    def _check_context(self):
        """检查上下文是否可用"""
        if not self.context:
            self.logger.error("浏览器上下文未初始化")
            return False
        return True

    def take_screenshot_if_needed(self, step_name: str):
        """如果启用了可视化调试并且在无头模式下，则截取屏幕截图"""
        if VISUAL_DEBUG_ENABLED and self.headless_mode and self.page and self.screenshot_dir:
            self.screenshot_counter += 1
            screenshot_path = os.path.join(
                self.screenshot_dir, f"{self.screenshot_counter:02d}_{step_name}.png"
            )
            try:
                self.page.screenshot(path=screenshot_path)
                self.logger.info(f"截图已保存: {screenshot_path}")
            except Exception as e:
                self.logger.error(f"保存截图失败: {screenshot_path}, 错误: {e}")

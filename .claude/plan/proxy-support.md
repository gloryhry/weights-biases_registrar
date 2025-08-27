# 代理支持实施计划

## 目标定义

为Wandb.ai自动注册工具添加全面的代理支持，使所有网络请求（包括Mail.tm API调用和Playwright浏览器请求）都能通过配置的代理服务器发出。支持HTTP、HTTPS和SOCKS5协议，以及带身份验证的代理URL。

## 功能分解

### 需要修改的关键组件

1. **配置管理** (`config/settings.py`)
   - 添加代理URL环境变量读取
   - 添加代理配置解析函数

2. **Mail服务** (`services/mail_service.py`)
   - 修改`requests.Session`以支持代理配置
   - 更新所有HTTP请求以使用代理

3. **浏览器服务** (`services/browser_service.py`)
   - 修改Playwright浏览器启动配置以支持代理
   - 添加代理认证处理

4. **环境配置** (`.env.example`)
   - 添加代理配置说明和示例

### 新增依赖

可能需要添加以下依赖到`requirements.txt`:
- `httpx` (如果需要替换requests以获得更好的代理支持)
- `socksio` (如果需要更好的SOCKS支持)

## 实施步骤

### 第1步：更新配置管理

**文件**: `config/settings.py`

1. 添加代理URL环境变量读取：
   ```python
   # 代理配置
   PROXY_URL = os.getenv('PROXY_URL', None)
   ```

2. 添加代理配置解析函数：
   ```python
   def parse_proxy_url(proxy_url):
       """解析代理URL并返回代理配置字典"""
       if not proxy_url:
           return None
       
       import urllib.parse
       parsed = urllib.parse.urlparse(proxy_url)
       
       proxy_config = {
           'scheme': parsed.scheme,
           'hostname': parsed.hostname,
           'port': parsed.port,
           'username': parsed.username,
           'password': parsed.password
       }
       
       return proxy_config
   ```

### 第2步：修改Mail服务以支持代理

**文件**: `services/mail_service.py`

1. 修改`__init__`方法以支持代理：
   ```python
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
   ```

### 第3步：修改浏览器服务以支持代理

**文件**: `services/browser_service.py`

1. 修改`start_browser`方法以支持代理：
   ```python
   def start_browser(self, headless=True):
       """启动浏览器"""
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
   ```

### 第4步：更新环境配置示例

**文件**: `.env.example`

1. 添加代理配置说明：
   ```env
   # Proxy settings (optional)
   # Supported protocols: http, https, socks5
   # Example: PROXY_URL=http://user:pass@host:port
   # PROXY_URL=
   ```

### 第5步：更新依赖（如需要）

**文件**: `requirements.txt`

如果需要更好的代理支持，可以考虑添加：
```
httpx==0.25.0
socksio==1.0.0
```

## 验收标准

### 功能验证

1. **环境变量配置**：
   - [ ] 可以通过`.env`文件配置`PROXY_URL`环境变量
   - [ ] 支持HTTP、HTTPS和SOCKS5协议
   - [ ] 支持带身份验证的代理URL格式

2. **Mail服务代理**：
   - [ ] Mail.tm API请求通过配置的代理发出
   - [ ] 代理认证信息正确传递
   - [ ] 无代理配置时正常工作

3. **浏览器代理**：
   - [ ] Playwright浏览器启动时使用代理配置
   - [ ] 浏览器请求通过代理发出
   - [ ] 代理认证在浏览器中正常工作

### 测试场景

1. **无代理配置**：
   - 不设置`PROXY_URL`环境变量
   - 确认所有功能正常工作

2. **HTTP代理**：
   - 配置HTTP代理URL
   - 验证所有网络请求通过代理

3. **带认证的HTTPS代理**：
   - 配置带用户名密码的HTTPS代理
   - 验证代理认证正常工作

4. **SOCKS5代理**：
   - 配置SOCKS5代理URL
   - 验证SOCKS代理正常工作

### 验证方法

1. **日志验证**：
   - 检查日志中是否显示代理配置信息
   - 确认代理URL正确解析

2. **网络监控**：
   - 使用网络监控工具确认请求通过代理
   - 验证目标服务器收到的请求来源

3. **功能测试**：
   - 执行完整的注册流程
   - 确认在代理环境下能成功创建账户

## 风险与缓解

### 潜在问题

1. **代理认证失败**：
   - 某些代理服务器可能不支持Chromium的认证方式
   - 缓解：提供备用认证方法或文档说明

2. **SOCKS支持限制**：
   - Playwright对SOCKS代理的支持可能有限
   - 缓解：测试并提供明确的使用说明

3. **性能影响**：
   - 代理可能增加请求延迟
   - 缓解：调整超时设置以适应代理延迟

### 向后兼容性

- 未配置代理时，应用行为应与之前完全一致
- 现有环境变量和配置保持不变
- 不影响现有的无代理使用场景
# Wandb.ai自动注册工具执行计划

## 项目目标
实现一个自动化工具，用于在Wandb.ai网站上自动注册账户，包括：
1. 使用临时邮箱服务(mail.tm)创建邮箱账户
2. 生成符合要求的随机密码
3. 自动完成Wandb.ai网站的注册流程
4. 自动处理邮箱验证流程
5. 保存注册成功的账号信息到auth.txt文件

## 技术方案
采用Playwright作为浏览器自动化工具，结合mail.tm API实现完整的注册流程。

## 项目结构
```
wandb-registrar/
├── .env
├── .gitignore
├── auth.txt
├── main.py
├── requirements.txt
├── config/
│   └── settings.py
├── services/
│   ├── mail_service.py
│   ├── browser_service.py
│   └── registration_service.py
├── utils/
│   ├── password_generator.py
│   └── logger.py
└── logs/
    └── app.log
```

## 模块功能说明

### config/settings.py
- 管理环境变量配置
- 配置mail.tm API地址和默认参数

### utils/logger.py
- 提供统一的日志记录功能
- 支持文件和控制台双输出

### utils/password_generator.py
- 生成安全密码（至少10位，包含大小写字母和特殊字符）

### services/mail_service.py
- MailTMApiClient类：管理与mail.tm API的交互
- create_temp_email()：创建临时邮箱账户
- get_verification_email()：轮询获取验证邮件并解析验证链接

### services/browser_service.py
- BrowserAutomation类：控制Playwright浏览器自动化
- navigate_to_signup()：导航到注册页面
- fill_registration_form()：填写注册表单
- open_verification_link()：打开验证链接

### services/registration_service.py
- RegistrationOrchestrator类：注册流程协调器
- execute_registration()：执行完整的注册流程
- save_account_info()：保存账户信息到文件

### main.py
- 程序主入口
- 整合所有服务模块
- 控制注册流程执行

## 实施步骤
1. 创建项目目录结构
2. 创建配置文件(.env, .gitignore, requirements.txt)
3. 实现工具模块(logger, password_generator)
4. 实现邮件服务模块(mail_service.py)
5. 实现浏览器自动化模块(browser_service.py)
6. 实现注册流程协调器(registration_service.py)
7. 实现主程序(main.py)
8. 安装依赖并初始化Playwright
9. 测试完整流程
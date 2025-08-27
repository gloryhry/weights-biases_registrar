# Wandb.ai 自动注册工具

这是一个基于Python的自动化工具，能够批量创建和管理Wandb.ai账户，支持临时邮箱验证和API密钥提取。

## 🎯 功能特性

- **🔍 批量注册**: 支持单次或批量账户创建
- **📧 临时邮箱**: 集成mail.tm API实现邮箱验证
- **🤖 浏览器自动化**: 使用Playwright进行网页交互
- **📝 自动保存**: 将生成的账户和API密钥保存到文件
- **🔐 安全生成**: 使用加密方式生成强密码
- **🐛 调试支持**: 截图保存和详细日志记录

## 📦 安装指南

### 系统要求

- Python 3.8 或更高版本
- Chrome/Chromium 浏览器
- Linux/WSL (推荐) 或 Windows

### 快速安装

```bash
# 克隆项目
git clone <项目地址>
cd wandb-registrar

# 方法一：使用提供的自动脚本（推荐）
chmod +x run.sh
./run.sh

# 方法二：手动安装
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## 🚀 快速开始

### 基本使用

```bash
# 启动单账户注册
python main.py

# 启动测试模式
python test_workflow.py

# 使用Linux脚本（带X11转发）
./run.sh
```

### 配置说明

编辑 `config/settings.py` 文件修改配置：

```python
# 注册次数配置
REGISTRATION_COUNT = 1

# 浏览器模式
HEADLESS_MODE = True  # False 为可视化模式

# 邮箱配置
MAIL_DOMAIN = "vipmail.best"
```

## 🎯 使用方法

### 1. 单账户注册

默认模式，启动后自动：
1. 生成安全的用户名和密码
2. 创建mail.tm临时邮箱
3. 访问wandb.ai注册页面
4. 填写注册表单并提交
5. 监控邮箱获取验证链接
6. 完成邮箱验证
7. 提取API密钥
8. 保存所有信息到文件

### 2. 批量注册

修改配置文件后运行：

```python
# 在 config/settings.py 中设置
REGISTRATION_COUNT = 10  # 创建10个账户
```

### 3. 调试模式

```bash
# 使用可视化浏览器查看过程
python test_workflow.py
```

## 📁 输出文件

工具会生成以下文件：

- **`auth.txt`** - 账户凭据（格式：`username:password`）
- **`key.txt`** - API密钥（纯文本）
- **`logs/app.log`** - 详细执行日志
- **`signup_page.png`** - 页面截图（失败时）

### 文件格式示例

**auth.txt:**
```
user_abc123:SecurePass123!
user_def456:AnotherPass234!
```

**key.txt:**
```
wiz_abc123_keyxyz789
wiz_def456_keyuvw123
```

## ⚙️ 项目结构

```
wandb-registrar/
├── main.py                     # 主程序入口
├── test_workflow.py           # 测试工作流
├── requirements.txt           # Python依赖
├── run.sh                     # Linux运行脚本
├── config/
│   └── settings.py            # 配置文件
├── services/
│   ├── mail_service.py        # 邮件服务API
│   ├── browser_service.py    # 浏览器自动化
│   └── registration_service.py # 注册协调器
├── utils/
│   ├── logger.py              # 日志工具
│   └── password_generator.py  # 密码生成
├── logs/app.log              # 运行时日志
├── auth.txt                  # 账户凭据
└── key.txt                   # API密钥
```

## 🎛️ API使用

### Playwright配置

```python
# 启动延时
WAIT_TIMEOUT = 30
RETRY_DELAY = 3
```

### Mail.tm API

自动处理：
- 临时邮箱创建
- 邮件轮询等待（最大5分钟）
- 验证链接提取
- 邮箱清理

## 🔧 故障排除

### 常见问题

<details>
<summary><b>浏览器启动失败</b></summary>

**原因**: 缺少Chromium
**解决**: 
```bash
playwright install chromium
```
</details>

<details>
<summary><b>邮箱无法接收验证邮件</b></summary>

**原因**: Mail.tm服务延迟
**解决**: 检查网络连接，增加等待时间
</details>

<details>
<summary><b>页面元素定位失败</b></summary>

**原因**: wandb.ai页面更新
**解决**: 查看最新screenshot，更新selectors
</details>

### 调试技巧

```bash
# 实时日志查看
tail -f logs/app.log

# 运行带调试
python -u main.py 2>&1 | tee debug.log

# 可视化模式调试
HEADLESS=false python test_workflow.py
```

## 🛡️ 安全注意事项

- **敏感数据**: 生成的`auth.txt`和`key.txt`包含敏感信息
- **定期清理**: 使用后删除包含凭据的文件
- **环境隔离**: 使用专用环境进行测试
- **网络限制**: 遵守服务条款，避免过度使用

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

**警告**: 本工具仅供学习和测试目的，请遵守相关服务条款，勿用于滥用。

---

*持续更新中...*
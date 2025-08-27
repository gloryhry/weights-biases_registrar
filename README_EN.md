# Wandb.ai Automated Registration Tool

A Python-based automation tool for bulk account creation and management on Wandb.ai, with temporary email verification and API key extraction.

## 🎯 Features

- **🔍 Batch Registration**: Single or multiple account creation
- **📧 Temporary Email**: Integrated mail.tm API for verification
- **🤖 Browser Automation**: Playwright-powered web interactions
- **📝 Auto-Save**: Generated credentials and API keys saved to files
- **🔐 Secure Generation**: Cryptographically strong password generation
- **🐛 Debugging Support**: Screenshot capture and detailed logging

## 📦 Installation Guide

### System Requirements

- Python 3.8 or higher
- Chrome/Chromium browser
- Linux/WSL (recommended) or Windows

### Quick Installation

```bash
# Clone project
git clone <project-url>
cd wandb-registrar

# Method 1: Use provided automation script (recommended)
chmod +x run.sh
./run.sh

# Method 2: Manual installation
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## 🚀 Quick Start

### Basic Usage

```bash
# Single account registration
python main.py

# Launch test mode
python test_workflow.py

# Use Linux script (with X11 forwarding)
./run.sh
```

### Configuration

Edit `config/settings.py`:

```python
# Registration count config
REGISTRATION_COUNT = 1

# Browser mode
HEADLESS_MODE = True  # False for visual mode

# Email configuration
MAIL_DOMAIN = "vipmail.best"
```

## 🎯 Usage

### 1. Single Account Registration

Default mode automatically:
1. Generates secure username and password
2. Creates mail.tm temporary email
3. Visits wandb.ai registration page
4. Completes registration form
5. Monitors email for verification link
6. Completes email verification
7. Extracts API keys
8. Saves all information to files

### 2. Batch Registration

After modifying config:

```python
# In config/settings.py
REGISTRATION_COUNT = 10  # Create 10 accounts
```

### 3. Debug Mode

```bash
# Use visual browser to observe process
python test_workflow.py
```

## 📁 Output Files

Tool generates:
- **`auth.txt`** - Account credentials (`username:password`)
- **`key.txt`** - API keys (plain text)
- **`logs/app.log`** - Detailed execution logs
- **`signup_page.png`** - Page screenshots (on failure)

### File Format Examples

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

## ⚙️ Project Structure

```
wandb-registrar/
├── main.py                     # Main program entry
├── test_workflow.py           # Test workflow
├── requirements.txt           # Python dependencies
├── run.sh                     # Linux run script
├── config/
│   └── settings.py            # Configuration file
├── services/
│   ├── mail_service.py        # Email service API
│   ├── browser_service.py    # Browser automation
│   └── registration_service.py # Registration orchestrator
├── utils/
│   ├── logger.py              # Logging utilities
│   └── password_generator.py  # Password generation
├── logs/app.log              # Runtime logs
├── auth.txt                  # Account credentials
└── key.txt                   # API keys
```

## 🎛️ API Configuration

### Playwright Settings

```python
# Launch timeouts
WAIT_TIMEOUT = 30
RETRY_DELAY = 3
```

### Mail.tm API

Automatically handles:
- Temporary email creation
- Email polling (max 5 mins)
- Verification link extraction
- Email cleanup

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>Browser Launch Failure</b></summary>

**Cause**: Missing Chromium
**Solution**: 
```bash
playwright install chromium
```
</details>

<details>
<summary><b>Email Not Received</b></summary>

**Cause**: Mail.tm service delay
**Solution**: Check network connection, increase wait time
</details>

<details>
<summary><b>Element Locator Failure</b></summary>

**Cause**: wandb.ai page updates
**Solution**: Check latest screenshot, update selectors
</details>

### Debug Tools

```bash
# Real-time log monitoring
tail -f logs/app.log

# Debug with output
python -u main.py 2>&1 | tee debug.log

# Visual debugging
HEADLESS=false python test_workflow.py
```

## 🛡️ Security Notes

- **Sensitive Data**: Generated `auth.txt` and `key.txt` contain credentials
- **Cleanup**: Delete credential files after use
- **Environment**: Use isolated environment for testing
- **Network**: Respect ToS, avoid excessive usage

## 🤝 Contributing

1. Fork the project
2. Create feature branch
3. Submit changes
4. Create Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Warning**: This tool is for educational/testing purposes only. Please respect service terms and avoid abuse.

---

*Continuously updated...*
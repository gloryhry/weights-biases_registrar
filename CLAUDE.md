# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based automated registration tool for Wandb.ai that uses Playwright for browser automation and Mail.tm for temporary email verification. The tool automatically creates accounts on Wandb.ai by:
1. Generating temporary email addresses
2. Automating the signup process through browser automation
3. Receiving and parsing verification emails
4. Completing account verification

## Common Commands

### Environment Setup with UV
```bash
# Create virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Running the Application
```bash
# Direct run
python main.py

# Or use the provided run script (recommended)
./run.sh
```

### Development
```bash
# Run individual test
python test_workflow.py

# Manual code formatting
python -m black wandb-registrar/
python -m isort wandb-registrar/
```

## Code Architecture

### UV Environment Setup
The project now supports UV virtual environment setup for faster dependency management:
1. UV virtual environment is created with `uv venv`
2. Dependencies are installed with `uv pip install -r requirements.txt`
3. A convenient run script (`run.sh`) automates environment activation and program execution
4. Environment variables are managed through `.env` file


### High-Level Structure
```
wandb-registrar/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── run.sh                  # Shell script for automated setup and run
├── config/
│   └── settings.py         # Configuration settings and environment variables
├── services/
│   ├── mail_service.py     # Mail.tm API integration for temporary email handling
│   ├── browser_service.py  # Playwright browser automation for web interactions
│   └── registration_service.py # Registration workflow orchestration and coordination
├── utils/
│   ├── password_generator.py # Secure password generation utilities
│   └── logger.py           # Centralized logging configuration
├── logs/
│   └── app.log             # Application logs and debugging output
├── auth.txt                # Generated account credentials storage
├── key.txt                 # Wandb AI API keys storage
└── test_workflow.py        # Test script for verification workflows
```

### Key Components

1. **RegistrationOrchestrator** (`services/registration_service.py`): The main workflow coordinator managing the complete registration pipeline including account creation, verification, and API key extraction
2. **MailTMApiClient** (`services/mail_service.py`): RESTful API client for Mail.tm temporary email service with automated email polling and link extraction
3. **BrowserAutomation** (`services/browser_service.py`): Playwright-based browser management with custom page interactions, form filling, and screenshot handling
4. **PasswordGenerator** (`utils/password_generator.py`): Cryptographically secure password and username generation utilities
5. **TestWorkflow** (`test_workflow.py`): Integration testing suite for verifying service connectivity and registration workflows

### Data Flow
1. `main.py` initializes the `RegistrationOrchestrator`
2. Orchestrator generates credentials and creates a temporary email via `MailTMApiClient`
3. `BrowserAutomation` handles the web signup process
4. `MailTMApiClient` polls for verification emails and extracts verification links
5. `BrowserAutomation` opens the verification link to complete registration
6. After verification, the tool fills additional forms and navigates through setup pages
7. API key is extracted from wandb.ai/authorize page
8. Credentials and API key are saved to `auth.txt` and `key.txt`

## Technical Specifications

### Environment Requirements
- **Python**: 3.8+ (tested with 3.11)
- **Browser**: Chromium-based (Playwright-managed)
- **OS**: Linux/WSL (primary), Windows (with WSL2), macOS (untested)

### Dependencies
```
playwright==1.40.0     # Browser automation
requests==2.31.0       # HTTP client for API interactions
python-dotenv==1.0.0   # Environment variable management
```

### Critical Files
- **auth.txt**: Stores `username:password` pairs for created accounts
- **key.txt**: Stores Wandb AI API keys in plain text format
- **logs/app.log**: Real-time application logs with timestamps
- **wandb-registrar/signup_page.png**: Screenshots for debugging failed workflows

### Security Considerations
- Credentials are stored in plain text files locally
- No external logging or data transmission
- Temporary email service minimizes email exposure
- Use disposable email addresses only for registration

## Development Notes

- **WinRM/SSH**: Execute `run.sh` using WSL or Git Bash on Windows
- **Logs**: Real-time monitoring with `tail -f logs/app.log`
- **Cleanup**: Generated `auth.txt` and `key.txt` contain sensitive data - delete after use
- **Privacy**: Configured for minimal external dependencies (only Mail.tm API)
- **API Limits**: Mail.tm has rate limits - implement delays between requests if processing multiple accounts
- **Browser**: Chromium instance runs in headless mode with screenshot capture for debugging
- **Timeouts**: Default timeouts of 30 seconds for most operations, 5 minutes for email waiting
- **Error Recovery**: Automatic retry mechanisms with exponential backoff

### External Documentation
- **Mail.tm API**: https://docs.mail.tm/ - Essential for understanding temporary email workflows
- **Playwright**: https://playwright.dev/python/docs/api/class-page - Browser automation reference
- **Wandb.ai**: https://wandb.ai/authorize - API key location and account management
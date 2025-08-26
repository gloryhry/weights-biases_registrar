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
# No specific linting or testing framework configured yet
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
├── config/
│   └── settings.py         # Configuration settings
├── services/
│   ├── mail_service.py     # Mail.tm API integration
│   ├── browser_service.py  # Playwright browser automation
│   └── registration_service.py # Registration workflow orchestration
├── utils/
│   ├── password_generator.py # Secure password generation
│   └── logger.py           # Logging configuration
└── logs/
    └── app.log             # Application logs
```

### Key Components

1. **RegistrationOrchestrator** (`services/registration_service.py`): The main controller that coordinates the entire registration flow, including post-verification steps
2. **MailTMApiClient** (`services/mail_service.py`): Handles all Mail.tm API interactions for temporary email creation and verification
3. **BrowserAutomation** (`services/browser_service.py`): Manages Playwright-based browser automation for web interactions
4. **Password Generation** (`utils/password_generator.py`): Creates secure passwords for new accounts

### Data Flow
1. `main.py` initializes the `RegistrationOrchestrator`
2. Orchestrator generates credentials and creates a temporary email via `MailTMApiClient`
3. `BrowserAutomation` handles the web signup process
4. `MailTMApiClient` polls for verification emails and extracts verification links
5. `BrowserAutomation` opens the verification link to complete registration
6. After verification, the tool fills additional forms and navigates through setup pages
7. API key is extracted from wandb.ai/authorize page
8. Credentials and API key are saved to `auth.txt` and `key.txt`

## Development Notes

- All services use a centralized logging system from `utils/logger.py`
- Configuration is managed through environment variables in `config/settings.py`
- The project follows a service-oriented architecture with clear separation of concerns
- Error handling and retries are implemented throughout the registration flow
- Mail.tm API documentation: https://docs.mail.tm/ - Consult this documentation before making any changes to mail service functionality
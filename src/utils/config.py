"""
Configuration settings for the Brew and Bite Café Management System.
"""

import os
from datetime import timedelta

# Application settings
APP_NAME = "Brew and Bite Café"
APP_VERSION = "1.0.0"

# Database settings
DATABASE = {
    'dir': 'data',
    'name': 'brew_and_bite.db',
    'backup_dir': 'data/backups'
}
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE['dir'], DATABASE['name'])}"

# Logging configuration
LOG_CONFIG = {
    'dir': 'logs',
    'filename': 'application.log',
    'level': 'DEBUG',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Security settings
PASSWORD_RESET_TIMEOUT_DAYS = 1
SESSION_TIMEOUT_MINUTES = 30
MIN_PASSWORD_LENGTH = 8

# Email settings (placeholder for future implementation)
EMAIL_CONFIG = {
    'smtp_server': '',
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': '',
    'sender_name': APP_NAME
}

# File paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, DATABASE['dir'])
LOG_DIR = os.path.join(ROOT_DIR, LOG_CONFIG['dir'])

# Create required directories
for directory in [DATA_DIR, LOG_DIR, os.path.join(DATA_DIR, 'backups')]:
    os.makedirs(directory, exist_ok=True)
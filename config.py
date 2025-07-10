import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Africa's Talking Settings
    AT_SANDBOX = os.getenv("AT_SANDBOX", "True").lower() == "true"
    AT_SANDBOX_NUMBER = "+254711082480"
    AT_USERNAME = os.getenv("AT_USERNAME")
    AT_API_KEY = os.getenv("AT_API_KEY")
    
    # System Settings
    MAX_SESSION_AGE = 3600  # 1 hour in seconds

    @classmethod
    def check_config(cls):
        """Validate configuration"""
        if not cls.AT_SANDBOX and (not cls.AT_USERNAME or not cls.AT_API_KEY):
            raise ValueError("Live mode requires AT_USERNAME and AT_API_KEY")

# Validate on import
Config.check_config()
"""Configuration management for Resilience Coach Agent"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Agent Settings
    AGENT_NAME = 'resilience_coach'
    AGENT_VERSION = '1.0.0'
    
    # Flask Settings
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Model Settings
    MODEL_NAME = 'gemini-pro'
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        return True

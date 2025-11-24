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
    
    # API Rate Limits (adjusted for free tier)
    MAX_REQUESTS_PER_MINUTE = 15  # Match Gemini free tier limit
    
    # Model Settings
    MODEL_NAME = 'models/gemini-2.0-flash-lite'  # Lighter model with better quota limits
    EMBEDDING_MODEL = 'models/embedding-001'  # For ChromaDB embeddings
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
    
    # Rate Limiting Settings
    API_RETRY_ATTEMPTS = 3
    API_RETRY_DELAY = 2  # seconds
    REQUEST_TIMEOUT = 30  # seconds
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        return True

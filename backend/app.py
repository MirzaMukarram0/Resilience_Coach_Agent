"""
Flask Application Entry Point
Resilience Coach Agent API
"""
from flask import Flask
from flask_cors import CORS
from backend.agent.config import Config
from backend.routes.api import api_bp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application"""
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    logger.info(f"Resilience Coach Agent v{Config.AGENT_VERSION} initialized")
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting server on port {Config.PORT}")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )

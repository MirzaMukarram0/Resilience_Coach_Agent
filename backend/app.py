"""
Flask Application Entry Point
Resilience Coach Agent API
Serves both API endpoints and static frontend files
"""
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from backend.agent.config import Config
from backend.routes.api import api_bp
import logging
import os

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
    # Set static folder to frontend directory
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Register API blueprints
    app.register_blueprint(api_bp)
    
    # Serve frontend files
    @app.route('/')
    def serve_frontend():
        """Serve the main HTML file"""
        return send_file(os.path.join(app.static_folder, 'index.html'))
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files (CSS, JS, etc.)"""
        try:
            return send_from_directory(app.static_folder, path)
        except:
            # If file not found, serve index.html (for SPA routing)
            return send_file(os.path.join(app.static_folder, 'index.html'))
    
    logger.info(f"Resilience Coach Agent v{Config.AGENT_VERSION} initialized")
    logger.info(f"Serving frontend from: {app.static_folder}")
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting server on port {Config.PORT}")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )

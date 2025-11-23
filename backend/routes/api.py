"""API Routes for Resilience Coach Agent"""
from flask import Blueprint, request, jsonify
from backend.agent.workflow import ResilienceWorkflow
from backend.utils import InputValidator, ResponseValidator
from backend.agent.config import Config
import logging
import time

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

# Initialize workflow
workflow = ResilienceWorkflow()

# Rate limiting (simple in-memory store)
request_timestamps = {}


def check_rate_limit(user_id: str) -> bool:
    """Simple rate limiting check (adjusted for Gemini API limits)"""
    current_time = time.time()
    if user_id not in request_timestamps:
        request_timestamps[user_id] = []
    
    # Remove timestamps older than 1 minute
    request_timestamps[user_id] = [
        ts for ts in request_timestamps[user_id] 
        if current_time - ts < 60
    ]
    
    # Check if exceeded limit (15 req/min for gemini-2.0-flash-exp)
    if len(request_timestamps[user_id]) >= 12:  # Conservative: 12 instead of 15
        return False
    
    # Add current timestamp
    request_timestamps[user_id].append(current_time)
    return True


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for supervisor integration"""
    return jsonify({
        'status': 'ok',
        'agent': 'resilience_coach',
        'version': Config.AGENT_VERSION,
        'message': 'Resilience Coach Agent is running'
    }), 200


@api_bp.route('/resilience', methods=['POST'])
def resilience_endpoint():
    """Main agent endpoint for processing user input"""
    try:
        # Validate content type
        if not request.is_json:
            logger.warning("Invalid content type received")
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate request structure
        if not isinstance(data, dict):
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': 'Request body must be a JSON object'
            }), 400
        
        # Validate agent field
        if 'agent' not in data:
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': 'Missing required field: agent'
            }), 400
        
        if data['agent'] != 'resilience_coach':
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': f"Invalid agent name. Expected: 'resilience_coach', got: '{data['agent']}'"
            }), 400
        
        # Validate input_text field
        if 'input_text' not in data:
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': 'Missing required field: input_text'
            }), 400
        
        # Validate and sanitize input
        is_valid, sanitized_input, error_msg = InputValidator.validate_input(data['input_text'])
        if not is_valid:
            logger.warning(f"Invalid input: {error_msg}")
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': error_msg
            }), 400
        
        # Validate and sanitize metadata
        metadata = data.get('metadata', {})
        is_valid_meta, sanitized_metadata, meta_error = InputValidator.validate_metadata(metadata)
        if not is_valid_meta:
            logger.warning(f"Invalid metadata: {meta_error}")
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': meta_error
            }), 400
        
        # Rate limiting
        user_id = sanitized_metadata.get('user_id', 'anonymous')
        if not check_rate_limit(user_id):
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': 'Rate limit exceeded. Please wait a moment before trying again.'
            }), 429
        
        logger.info(f"Processing request for user: {user_id}")
        
        # Process through workflow
        result = workflow.process(sanitized_input, sanitized_metadata)
        
        # Validate response
        is_valid_response, validated_result, response_error = ResponseValidator.validate_response(result)
        if not is_valid_response:
            logger.error(f"Invalid response generated: {response_error}")
            return jsonify({
                'status': 'error',
                'agent': 'resilience_coach',
                'message': 'Failed to generate valid response. Please try again.'
            }), 500
        
        logger.info("Request processed successfully")
        return jsonify(validated_result), 200
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'agent': 'resilience_coach',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500


@api_bp.route('/api', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'agent': 'resilience_coach',
        'version': Config.AGENT_VERSION,
        'status': 'running',
        'endpoints': {
            'api_info': {
                'path': '/api',
                'method': 'GET',
                'description': 'API information'
            },
            'health': {
                'path': '/health',
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            'resilience': {
                'path': '/resilience',
                'method': 'POST',
                'description': 'Main agent interaction endpoint',
                'required_fields': ['agent', 'input_text'],
                'optional_fields': ['metadata']
            }
        },
        'documentation': 'https://github.com/MirzaMukarram0/Resilience_Coach_Agent'
    }), 200


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'agent': 'resilience_coach',
        'message': 'Endpoint not found. Use / for API information.'
    }), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'status': 'error',
        'agent': 'resilience_coach',
        'message': 'Method not allowed for this endpoint.'
    }), 405


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'status': 'error',
        'agent': 'resilience_coach',
        'message': 'Internal server error. Please try again later.'
    }), 500

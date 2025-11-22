"""API Routes for Resilience Coach Agent"""
from flask import Blueprint, request, jsonify
from backend.agent.workflow import ResilienceWorkflow
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

# Initialize workflow
workflow = ResilienceWorkflow()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for supervisor integration"""
    return jsonify({
        'status': 'ok',
        'agent': 'resilience_coach',
        'message': 'Resilience Coach Agent is running'
    }), 200


@api_bp.route('/resilience', methods=['POST'])
def resilience_endpoint():
    """Main agent endpoint for processing user input"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'agent' not in data or data['agent'] != 'resilience_coach':
            return jsonify({
                'status': 'error',
                'message': 'Invalid agent name. Expected: resilience_coach'
            }), 400
        
        if 'input_text' not in data or not data['input_text'].strip():
            return jsonify({
                'status': 'error',
                'message': 'input_text is required and cannot be empty'
            }), 400
        
        # Extract input
        input_text = data['input_text']
        metadata = data.get('metadata', {})
        
        logger.info(f"Processing request for user: {metadata.get('user_id', 'anonymous')}")
        
        # Process through workflow
        result = workflow.process(input_text, metadata)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'agent': 'resilience_coach',
            'message': f'Internal server error: {str(e)}'
        }), 500


@api_bp.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'agent': 'resilience_coach',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'main': '/resilience'
        },
        'documentation': 'https://github.com/MirzaMukarram0/Resilience_Coach_Agent'
    }), 200

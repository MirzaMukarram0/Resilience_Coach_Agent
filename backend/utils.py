"""
Input validation and sanitization utilities
"""
import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and sanitizes user inputs"""
    
    # Configuration
    MIN_INPUT_LENGTH = 1
    MAX_INPUT_LENGTH = 2000
    MIN_MEANINGFUL_LENGTH = 3
    
    # Patterns for detection
    SPAM_PATTERNS = [
        r'(.)\1{10,}',  # Repeated characters (10+)
        r'^[^a-zA-Z0-9\s]{20,}$',  # Too many special characters
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
    ]
    
    # Blocked patterns (security)
    BLOCKED_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS attempts
        r'javascript:',
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',
        r'exec\s*\(',
    ]
    
    @classmethod
    def validate_input(cls, input_text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate and sanitize user input
        
        Args:
            input_text: Raw user input
            
        Returns:
            Tuple of (is_valid, sanitized_text, error_message)
        """
        # Check if input exists
        if input_text is None:
            return False, None, "Input text is required"
        
        # Convert to string and strip
        input_text = str(input_text).strip()
        
        # Check length constraints
        if len(input_text) < cls.MIN_INPUT_LENGTH:
            return False, None, "Input cannot be empty"
        
        if len(input_text) > cls.MAX_INPUT_LENGTH:
            return False, None, f"Input too long. Maximum {cls.MAX_INPUT_LENGTH} characters allowed"
        
        # Check for meaningful content
        if len(input_text) < cls.MIN_MEANINGFUL_LENGTH:
            return False, None, "Input too short. Please share more about how you're feeling"
        
        # Security checks - block malicious patterns
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                logger.warning(f"Blocked malicious pattern detected: {pattern}")
                return False, None, "Invalid input detected. Please avoid special characters or code"
        
        # Detect spam/gibberish
        if cls._is_spam(input_text):
            return False, None, "Input appears invalid. Please share genuine thoughts or feelings"
        
        # Sanitize input
        sanitized = cls._sanitize(input_text)
        
        logger.info(f"Input validated successfully (length: {len(sanitized)})")
        return True, sanitized, None
    
    @classmethod
    def _is_spam(cls, text: str) -> bool:
        """Detect spam or gibberish patterns"""
        for pattern in cls.SPAM_PATTERNS:
            if re.search(pattern, text):
                return True
        
        # Check for too few alphabetic characters
        alpha_count = sum(c.isalpha() for c in text)
        if len(text) > 10 and alpha_count / len(text) < 0.3:
            return True
        
        return False
    
    @classmethod
    def _sanitize(cls, text: str) -> str:
        """Sanitize input text"""
        # Remove potential HTML/script tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Trim to max length
        if len(text) > cls.MAX_INPUT_LENGTH:
            text = text[:cls.MAX_INPUT_LENGTH]
        
        return text.strip()
    
    @classmethod
    def validate_metadata(cls, metadata: dict) -> Tuple[bool, dict, Optional[str]]:
        """
        Validate metadata fields
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Tuple of (is_valid, sanitized_metadata, error_message)
        """
        if not isinstance(metadata, dict):
            return False, {}, "Metadata must be a dictionary"
        
        sanitized = {}
        
        # Validate user_id if present
        if 'user_id' in metadata:
            user_id = str(metadata['user_id']).strip()
            if len(user_id) > 100:
                return False, {}, "user_id too long"
            sanitized['user_id'] = user_id
        
        # Validate language if present
        if 'language' in metadata:
            lang = str(metadata['language']).strip().lower()
            if len(lang) > 10:
                return False, {}, "Invalid language code"
            # Only support English for now
            if lang not in ['en', 'english', '']:
                sanitized['language'] = 'en'
                logger.info(f"Unsupported language '{lang}', defaulting to 'en'")
            else:
                sanitized['language'] = 'en'
        else:
            sanitized['language'] = 'en'
        
        return True, sanitized, None


class ResponseValidator:
    """Validates agent responses to prevent hallucination"""
    
    REQUIRED_RESPONSE_FIELDS = ['agent', 'status', 'analysis', 'recommendation', 'message']
    REQUIRED_ANALYSIS_FIELDS = ['sentiment', 'stress_level', 'emotions']
    REQUIRED_RECOMMENDATION_FIELDS = ['type', 'steps']
    
    VALID_SENTIMENTS = ['positive', 'neutral', 'negative', 'deeply_negative', 'error_quota_exceeded', 'error_api_failed']
    VALID_STRESS_LEVELS = ['low', 'medium', 'high', 'crisis', 'api_unavailable']
    
    @classmethod
    def validate_response(cls, response: dict) -> Tuple[bool, dict, Optional[str]]:
        """
        Validate agent response structure and content
        
        Args:
            response: Response dictionary from workflow
            
        Returns:
            Tuple of (is_valid, validated_response, error_message)
        """
        try:
            # Check required fields
            for field in cls.REQUIRED_RESPONSE_FIELDS:
                if field not in response:
                    logger.error(f"Missing required field: {field}")
                    return False, {}, f"Invalid response: missing {field}"
            
            # Validate analysis
            analysis = response['analysis']
            if not isinstance(analysis, dict):
                return False, {}, "Invalid analysis format"
            
            for field in cls.REQUIRED_ANALYSIS_FIELDS:
                if field not in analysis:
                    return False, {}, f"Invalid analysis: missing {field}"
            
            # Validate sentiment
            if analysis['sentiment'] not in cls.VALID_SENTIMENTS:
                logger.warning(f"Invalid sentiment: {analysis['sentiment']}, defaulting to neutral")
                analysis['sentiment'] = 'neutral'
            
            # Validate stress level
            if analysis['stress_level'] not in cls.VALID_STRESS_LEVELS:
                logger.warning(f"Invalid stress level: {analysis['stress_level']}, defaulting to medium")
                analysis['stress_level'] = 'medium'
            
            # Validate emotions (must be list)
            if not isinstance(analysis['emotions'], list) or len(analysis['emotions']) == 0:
                logger.warning("Invalid emotions format, using default")
                analysis['emotions'] = ['uncertain']
            
            # Validate recommendation
            recommendation = response['recommendation']
            if not isinstance(recommendation, dict):
                return False, {}, "Invalid recommendation format"
            
            for field in cls.REQUIRED_RECOMMENDATION_FIELDS:
                if field not in recommendation:
                    return False, {}, f"Invalid recommendation: missing {field}"
            
            # Validate steps (must be list with content)
            if not isinstance(recommendation['steps'], list) or len(recommendation['steps']) == 0:
                return False, {}, "Invalid recommendation steps"
            
            # Validate message (must be non-empty string)
            if not isinstance(response['message'], str) or len(response['message'].strip()) == 0:
                logger.warning("Empty message, using default")
                response['message'] = "I'm here to support you."
            
            # Truncate message if too long
            if len(response['message']) > 500:
                response['message'] = response['message'][:497] + "..."
            
            logger.info("Response validation successful")
            return True, response, None
            
        except Exception as e:
            logger.error(f"Response validation error: {e}", exc_info=True)
            return False, {}, f"Response validation failed: {str(e)}"

"""
Gemini API Client
Handles all interactions with Google's Gemini API for emotional analysis
"""
import google.generativeai as genai
from backend.agent.config import Config
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client with API key"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.MODEL_NAME)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def analyze_emotion(self, user_input: str) -> dict:
        """
        Analyze user's emotional state and stress level
        
        Args:
            user_input: User's text input
            
        Returns:
            dict: Analysis containing sentiment, stress_level, and emotions
        """
        try:
            prompt = self._build_analysis_prompt(user_input)
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': Config.TEMPERATURE,
                    'max_output_tokens': Config.MAX_TOKENS,
                }
            )
            
            analysis = self._parse_analysis_response(response.text)
            logger.info(f"Analysis completed - Sentiment: {analysis['sentiment']}, Stress: {analysis['stress_level']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            # Return default analysis on error
            return {
                'sentiment': 'neutral',
                'stress_level': 'medium',
                'emotions': ['uncertain']
            }
    
    def generate_supportive_message(self, user_input: str, analysis: dict) -> str:
        """
        Generate empathetic and supportive message
        
        Args:
            user_input: User's text input
            analysis: Emotional analysis results
            
        Returns:
            str: Supportive message
        """
        try:
            prompt = self._build_support_prompt(user_input, analysis)
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.8,  # Higher temperature for more varied responses
                    'max_output_tokens': 150,
                }
            )
            
            message = response.text.strip()
            logger.info("Supportive message generated")
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating support message: {e}")
            return "I'm here to support you. Take things one step at a time."
    
    def _build_analysis_prompt(self, user_input: str) -> str:
        """Build prompt for emotional analysis"""
        return f"""You are an empathetic mental wellness AI assistant. Analyze the following user input for emotional state and stress level.

User Input: "{user_input}"

Provide your analysis in EXACTLY this format (one line each, no extra text):
SENTIMENT: [positive/neutral/negative]
STRESS_LEVEL: [low/medium/high]
EMOTIONS: [list 2-4 specific emotions separated by commas, e.g., anxiety, overwhelm, sadness]

Be precise and concise. Only output the three lines above, nothing else."""

    def _build_support_prompt(self, user_input: str, analysis: dict) -> str:
        """Build prompt for supportive message"""
        return f"""You are a compassionate mental wellness coach. The user shared: "{user_input}"

Analysis shows:
- Sentiment: {analysis['sentiment']}
- Stress Level: {analysis['stress_level']}
- Emotions: {', '.join(analysis['emotions'])}

Write ONE SHORT supportive message (2-3 sentences max) that:
1. Validates their feelings
2. Offers gentle encouragement
3. Is warm and empathetic

Keep it conversational and natural. Do not give medical advice."""

    def _parse_analysis_response(self, response_text: str) -> dict:
        """
        Parse Gemini's response into structured analysis
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            dict: Structured analysis
        """
        try:
            lines = response_text.strip().split('\n')
            
            sentiment = 'neutral'
            stress_level = 'medium'
            emotions = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('SENTIMENT:'):
                    sentiment = line.split(':', 1)[1].strip().lower()
                elif line.startswith('STRESS_LEVEL:'):
                    stress_level = line.split(':', 1)[1].strip().lower()
                elif line.startswith('EMOTIONS:'):
                    emotions_str = line.split(':', 1)[1].strip()
                    emotions = [e.strip().lower() for e in emotions_str.split(',')]
            
            # Validate and set defaults if needed
            if sentiment not in ['positive', 'neutral', 'negative']:
                sentiment = 'neutral'
            if stress_level not in ['low', 'medium', 'high']:
                stress_level = 'medium'
            if not emotions:
                emotions = ['mixed']
            
            return {
                'sentiment': sentiment,
                'stress_level': stress_level,
                'emotions': emotions[:4]  # Limit to 4 emotions
            }
            
        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return {
                'sentiment': 'neutral',
                'stress_level': 'medium',
                'emotions': ['uncertain']
            }

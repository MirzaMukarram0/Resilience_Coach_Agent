"""
Gemini API Client
Handles all interactions with Google's Gemini API for emotional analysis
"""
import google.generativeai as genai
from backend.agent.config import Config
import logging
import time
from typing import Optional

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
        Analyze user's emotional state and stress level with retry logic
        
        Args:
            user_input: User's text input
            
        Returns:
            dict: Analysis containing sentiment, stress_level, and emotions
        """
        prompt = self._build_analysis_prompt(user_input)
        
        for attempt in range(Config.API_RETRY_ATTEMPTS):
            try:
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
                error_str = str(e)
                
                # Check for rate limit error (429)
                if '429' in error_str or 'quota' in error_str.lower():
                    if attempt < Config.API_RETRY_ATTEMPTS - 1:
                        wait_time = Config.API_RETRY_DELAY * (attempt + 1)
                        logger.warning(f"Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{Config.API_RETRY_ATTEMPTS})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {Config.API_RETRY_ATTEMPTS} attempts")
                else:
                    logger.error(f"Error analyzing emotion: {e}")
                
                # Return rule-based analysis on final error
                if attempt == Config.API_RETRY_ATTEMPTS - 1:
                    logger.warning("Using rule-based fallback analysis")
                    return self._rule_based_analysis(user_input)
    
    def _rule_based_analysis(self, text: str) -> dict:
        """
        Simple rule-based emotional analysis fallback
        when Gemini API is unavailable
        """
        text_lower = text.lower()
        
        # Negative emotion keywords
        negative_keywords = {
            'sad': 'sadness', 'depressed': 'depression', 'lonely': 'loneliness',
            'anxious': 'anxiety', 'worried': 'worry', 'scared': 'fear',
            'stressed': 'stress', 'overwhelmed': 'overwhelm', 'panic': 'panic',
            'angry': 'anger', 'frustrated': 'frustration', 'hopeless': 'hopelessness',
            'suicidal': 'crisis', 'suicide': 'crisis', 'harm': 'crisis',
            'hurt': 'pain', 'cry': 'sadness', 'afraid': 'fear'
        }
        
        # Positive emotion keywords
        positive_keywords = {
            'happy': 'happiness', 'joy': 'joy', 'excited': 'excitement',
            'grateful': 'gratitude', 'love': 'love', 'content': 'contentment',
            'proud': 'pride', 'calm': 'calmness', 'peaceful': 'peace',
            'good': 'positivity', 'great': 'positivity', 'wonderful': 'joy'
        }
        
        # High stress indicators
        high_stress_keywords = ['overwhelmed', 'panic', 'can\'t cope', 'too much',
                                'breaking down', 'suicidal', 'suicide', 'crisis']
        
        # Medium stress indicators
        medium_stress_keywords = ['stressed', 'worried', 'anxious', 'nervous',
                                  'pressure', 'tense', 'difficult']
        
        # Detect emotions
        emotions = []
        sentiment_score = 0
        
        for keyword, emotion in negative_keywords.items():
            if keyword in text_lower:
                emotions.append(emotion)
                sentiment_score -= 1
        
        for keyword, emotion in positive_keywords.items():
            if keyword in text_lower:
                emotions.append(emotion)
                sentiment_score += 1
        
        # Determine sentiment
        if sentiment_score > 0:
            sentiment = 'positive'
        elif sentiment_score < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Determine stress level
        stress_level = 'low'
        for keyword in high_stress_keywords:
            if keyword in text_lower:
                stress_level = 'high'
                break
        
        if stress_level == 'low':
            for keyword in medium_stress_keywords:
                if keyword in text_lower:
                    stress_level = 'medium'
                    break
        
        # Default emotions if none detected
        if not emotions:
            if sentiment == 'negative':
                emotions = ['concerned']
            elif sentiment == 'positive':
                emotions = ['content']
            else:
                emotions = ['neutral']
        
        return {
            'sentiment': sentiment,
            'stress_level': stress_level,
            'emotions': list(set(emotions))[:3]  # Max 3 emotions
        }
    
    def generate_supportive_message(self, user_input: str, analysis: dict) -> str:
        """
        Generate empathetic and supportive message with retry logic
        
        Args:
            user_input: User's text input
            analysis: Emotional analysis results
            
        Returns:
            str: Supportive message
        """
        prompt = self._build_support_prompt(user_input, analysis)
        
        for attempt in range(Config.API_RETRY_ATTEMPTS):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.8,  # Higher temperature for more varied responses
                        'max_output_tokens': 150,
                    }
                )
                
                # Handle response parts properly
                try:
                    message = response.text.strip()
                except:
                    # If response.text doesn't work, try parts
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            message = ''.join(part.text for part in candidate.content.parts).strip()
                        else:
                            message = "I'm here to support you. Take things one step at a time."
                    else:
                        message = "I'm here to support you. Take things one step at a time."
                
                logger.info("Supportive message generated")
                return message
                
            except Exception as e:
                error_str = str(e)
                
                # Check for rate limit error
                if '429' in error_str or 'quota' in error_str.lower():
                    if attempt < Config.API_RETRY_ATTEMPTS - 1:
                        wait_time = Config.API_RETRY_DELAY * (attempt + 1)
                        logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                
                logger.error(f"Error generating support message: {e}")
                if attempt == Config.API_RETRY_ATTEMPTS - 1:
                    logger.warning("Using rule-based fallback message")
                    return self._rule_based_message(user_input, analysis)
    
    def _rule_based_message(self, user_input: str, analysis: dict) -> str:
        """
        Generate supportive message using rules when API unavailable
        """
        sentiment = analysis.get('sentiment', 'neutral')
        stress_level = analysis.get('stress_level', 'medium')
        emotions = analysis.get('emotions', [])
        
        text_lower = user_input.lower()
        
        # Crisis detection
        crisis_keywords = ['suicidal', 'suicide', 'kill myself', 'end it', 'harm myself']
        if any(keyword in text_lower for keyword in crisis_keywords):
            return ("I'm deeply concerned about what you're sharing. Please reach out to a crisis helpline immediately: "
                   "National Suicide Prevention Lifeline: 988 or 1-800-273-8255. You don't have to face this alone - "
                   "professional help is available 24/7.")
        
        # High stress
        if stress_level == 'high':
            messages = [
                "I can sense you're going through a really difficult time right now. It's completely understandable to feel overwhelmed.",
                "What you're experiencing sounds incredibly challenging. Remember, it's okay to ask for help and take things one moment at a time.",
                "I hear how much you're struggling right now. Your feelings are valid, and there are ways to work through this together."
            ]
            import random
            return random.choice(messages)
        
        # Negative sentiment
        if sentiment == 'negative':
            if 'sadness' in emotions or 'depression' in emotions or 'loneliness' in emotions:
                return "I'm here with you. These feelings of sadness are difficult, but they won't last forever. Let's explore some gentle techniques that might help."
            elif 'anxiety' in emotions or 'worry' in emotions:
                return "Anxiety can feel overwhelming, but you're taking a positive step by reaching out. Let's work on some calming strategies together."
            elif 'anger' in emotions or 'frustration' in emotions:
                return "It's okay to feel frustrated or angry. These emotions are valid. Let's find healthy ways to process what you're experiencing."
            else:
                return "I hear that you're going through a tough time. You're not alone in this, and there are strategies that can help."
        
        # Positive sentiment
        if sentiment == 'positive':
            return "It's wonderful to hear you're feeling positive! Let's build on this momentum with some practices to maintain your well-being."
        
        # Neutral/default
        return "I'm here to support you. Let's explore some techniques that can help you build resilience and manage stress."
    
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

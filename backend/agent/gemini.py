"""
Pure Gemini AI Client - No Hardcoded Rules
Uses Gemini API for ALL analysis, recommendations, and responses
"""
import google.generativeai as genai
from backend.agent.config import Config
import logging
import json
import re

logger = logging.getLogger(__name__)


class GeminiClient:
    """Pure AI-driven analysis using only Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Use stable model with better quota
        self.model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            generation_config={
                'temperature': Config.TEMPERATURE,
                'max_output_tokens': Config.MAX_TOKENS,
            }
        )
        
        logger.info(f"Pure Gemini client initialized: {Config.MODEL_NAME}")

    def analyze_emotion_with_context(
        self,
        input_text: str,
        memory_context: list = None,
        emotional_patterns: dict = None
    ) -> dict:
        """
        Pure Gemini emotional analysis - NO hardcoded rules
        """
        try:
            # Build context information
            context_info = ""
            if memory_context:
                context_info += f"\n\nPAST CONTEXT: Found {len(memory_context)} similar past conversations."
            
            if emotional_patterns and emotional_patterns.get('recurring_emotions'):
                recurring = emotional_patterns.get('recurring_emotions', [])
                context_info += f"\nUSER PATTERNS: Often experiences {', '.join(recurring[:3])}."
                
                if emotional_patterns.get('crisis_frequency', 0) > 0:
                    context_info += f" Has had {emotional_patterns['crisis_frequency']} crisis episodes."

            prompt = f"""You are an expert emotional intelligence AI. Analyze this message with deep psychological insight.

USER MESSAGE: "{input_text}"{context_info}

Analyze considering:
- Explicit emotions stated
- Hidden emotional cues (tone, contradictions, subtext)
- Stress indicators (overwhelm, pressure, exhaustion)
- Physical symptoms mentioned
- Behavioral patterns
- Crisis risk factors (hopelessness, suicidal ideation, self-harm)
- Emotional masking ("I'm fine" while showing distress)

Respond in EXACTLY this JSON format:
{{
  "sentiment": "positive/neutral/negative/deeply_negative",
  "stress_level": "low/medium/high/crisis",
  "emotions": ["specific_emotion1", "specific_emotion2", "specific_emotion3"],
  "confidence": 0.85,
  "reasoning": "Brief explanation of your analysis"
}}

Be accurate. Detect hidden emotions behind words like "I'm okay" or "just tired"."""

            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
                
                # Validate structure
                analysis = self._validate_analysis(analysis)
                logger.info(f"Gemini analysis: {analysis['sentiment']}/{analysis['stress_level']}")
                return analysis
            else:
                raise ValueError("Could not parse JSON response")
                
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            error_msg = str(e)
            
            # If quota exceeded, return clear error message
            if '429' in error_msg or 'quota' in error_msg.lower():
                return {
                    'sentiment': 'error_quota_exceeded',
                    'stress_level': 'api_unavailable', 
                    'emotions': ['api_quota_exceeded'],
                    'confidence': 0.0,
                    'reasoning': f'❌ Gemini API quota exceeded. Please try again later or upgrade API plan. Error: {error_msg}'
                }
            else:
                return {
                    'sentiment': 'error_api_failed',
                    'stress_level': 'api_unavailable',
                    'emotions': ['api_error'],
                    'confidence': 0.0,
                    'reasoning': f'❌ AI analysis unavailable: {error_msg}'
                }

    def assess_crisis_level(
        self,
        input_text: str,
        analysis: dict,
        emotional_patterns: dict = None
    ) -> float:
        """Pure Gemini crisis assessment"""
        try:
            patterns_info = ""
            if emotional_patterns and emotional_patterns.get('crisis_frequency', 0) > 0:
                patterns_info = f"\nHISTORY: {emotional_patterns['crisis_frequency']} past crisis episodes."

            prompt = f"""Rate the crisis risk level for this mental health message.

MESSAGE: "{input_text}"
ANALYSIS: {analysis.get('sentiment')} sentiment, {analysis.get('stress_level')} stress
EMOTIONS: {', '.join(analysis.get('emotions', []))}{patterns_info}

Rate 0.0-1.0:
• 0.0-0.2: Normal emotional expression
• 0.3-0.4: Mild distress, supportive conversation
• 0.5-0.6: Moderate concern, additional support helpful
• 0.7-0.8: High risk, hopelessness, suicidal thoughts
• 0.9-1.0: Immediate crisis, active plans, severe self-harm

Look for:
- Direct self-harm/suicide statements
- Severe hopelessness ("no point", "tired of existing")
- Escalation from past patterns
- Extreme despair language

Respond with ONLY a decimal number 0.0-1.0"""

            response = self.model.generate_content(prompt)
            score_text = response.text.strip()
            
            # Extract decimal number
            score_match = re.search(r'(\d*\.?\d+)', score_text)
            if score_match:
                score = float(score_match.group())
                return max(0.0, min(1.0, score))
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Crisis assessment failed: {e}")
            return 0.5

    def generate_reasoning(
        self,
        input_text: str,
        analysis: dict,
        memory_context: list = None,
        emotional_patterns: dict = None
    ) -> str:
        """Generate reasoning explanation using Gemini"""
        try:
            context_summary = ""
            if memory_context:
                context_summary = f"Considering {len(memory_context)} past conversations. "
            if emotional_patterns and emotional_patterns.get('recurring_emotions'):
                patterns = ', '.join(emotional_patterns.get('recurring_emotions', [])[:2])
                context_summary += f"User often experiences {patterns}. "

            prompt = f"""Explain in 1-2 sentences why this emotional analysis was reached:

USER: "{input_text}"
ANALYSIS: {analysis.get('sentiment')} sentiment, {analysis.get('stress_level')} stress
EMOTIONS: {', '.join(analysis.get('emotions', []))}
CONTEXT: {context_summary}

Provide brief, clear reasoning for this analysis."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Reasoning generation failed: {e}")
            return analysis.get('reasoning', 'Analysis based on emotional language patterns.')

    def generate_recommendation(
        self,
        input_text: str,
        analysis: dict,
        memory_context: list = None,
        emotional_patterns: dict = None
    ) -> dict:
        """
        Pure Gemini recommendation generation - NO hardcoded strategies
        """
        try:
            context_info = ""
            if memory_context:
                context_info += f"\nCONTEXT: User has {len(memory_context)} past conversations."
            if emotional_patterns and emotional_patterns.get('recurring_emotions'):
                recurring = ', '.join(emotional_patterns.get('recurring_emotions', [])[:2])
                context_info += f" Often experiences: {recurring}."

            prompt = f"""You are a mental health support AI recommending evidence-based coping strategies.

USER MESSAGE: "{input_text}"
EMOTIONAL STATE: {analysis.get('sentiment')} sentiment, {analysis.get('stress_level')} stress
EMOTIONS: {', '.join(analysis.get('emotions', []))}{context_info}

Choose the BEST strategy from these evidence-based options:
1. breathing_exercise - Anxiety, panic, acute stress
2. grounding_technique - Overwhelm, racing thoughts, dissociation
3. progressive_relaxation - Physical tension, burnout, exhaustion
4. mindful_meditation - General stress, emotional regulation
5. positive_affirmations - Low self-worth, negative self-talk
6. physical_activity - Anger, restlessness, energy release
7. journaling - Complex emotions, confusion, processing
8. social_connection - Loneliness, isolation, need support

Respond in EXACTLY this JSON format:
{{
  "type": "exact_strategy_name_from_list",
  "name": "Human readable name",
  "steps": [
    "Step 1: Specific actionable instruction",
    "Step 2: Another clear step",
    "Step 3: Continue with 5-7 steps total",
    "Step 4: Make each step very specific",
    "Step 5: End with reflection or grounding"
  ],
  "reasoning": "Why this strategy fits their emotional state"
}}

Choose based on their specific emotional needs, not generic advice."""

            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                recommendation = json.loads(json_str)
                
                # Validate required fields
                required = ['type', 'name', 'steps']
                if all(key in recommendation for key in required):
                    logger.info(f"Gemini recommended: {recommendation['type']}")
                    return recommendation
                else:
                    raise ValueError("Missing required recommendation fields")
            else:
                raise ValueError("Could not parse recommendation JSON")
                
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            error_msg = str(e)
            
            # If quota exceeded, return clear error message
            if '429' in error_msg or 'quota' in error_msg.lower():
                return {
                    'type': 'api_quota_exceeded',
                    'name': 'API Quota Exceeded',
                    'steps': ['❌ AI recommendations unavailable - API quota exceeded', 'Please try again later or upgrade your API plan'],
                    'reasoning': f'Gemini API quota exceeded: {error_msg}'
                }
            else:
                return {
                    'type': 'api_error',
                    'name': 'AI Service Error',
                    'steps': ['❌ AI recommendations temporarily unavailable', 'Please try again in a few moments'],
                    'reasoning': f'AI recommendation failed: {error_msg}'
                }

    def generate_supportive_message_with_context(
        self,
        user_input: str,
        analysis: dict,
        memory_context: list = None,
        emotional_patterns: dict = None,
        reasoning_trace: str = ""
    ) -> str:
        """Pure Gemini supportive message generation"""
        try:
            context_info = ""
            if memory_context:
                context_info += f"\nCONTINUITY: This user has reached out {len(memory_context)} times before."
            if emotional_patterns and emotional_patterns.get('recurring_emotions'):
                recurring = ', '.join(emotional_patterns.get('recurring_emotions', [])[:2])
                context_info += f" They often experience {recurring}."

            prompt = f"""You are a compassionate mental health support AI. Generate an empathetic response.

USER SHARED: "{user_input}"
EMOTIONAL STATE: {analysis.get('sentiment')} sentiment, {analysis.get('stress_level')} stress
EMOTIONS: {', '.join(analysis.get('emotions', []))}
REASONING: {reasoning_trace}{context_info}

Generate ONE warm, supportive response (2-3 sentences) that:
✓ Validates their specific emotional experience
✓ Shows genuine empathy without toxic positivity
✓ Acknowledges their courage in reaching out
✓ Makes them feel understood and supported
✗ Never minimize with "at least", "it could be worse"
✗ No medical advice or diagnosis
✗ No clichés like "everything happens for a reason"

Be authentically caring and understanding."""

            response = self.model.generate_content(prompt)
            message = response.text.strip().strip('"').strip("'")
            
            logger.info("Supportive message generated by pure Gemini")
            return message
            
        except Exception as e:
            logger.error(f"Message generation failed: {e}")
            error_msg = str(e)
            
            # If quota exceeded, return clear error message  
            if '429' in error_msg or 'quota' in error_msg.lower():
                return "❌ AI Support Unavailable: Gemini API quota exceeded. Please try again later or upgrade your API plan."
            else:
                return f"❌ AI support temporarily unavailable due to: {error_msg}. Please try again in a few moments."

    def generate_crisis_response(
        self,
        user_input: str,
        analysis: dict,
        crisis_score: float
    ) -> str:
        """Pure Gemini crisis response"""
        try:
            prompt = f"""Generate a compassionate crisis response for someone in emotional distress.

USER MESSAGE: "{user_input}"
CRISIS SEVERITY: {crisis_score:.1f}/1.0
EMOTIONS: {', '.join(analysis.get('emotions', []))}

Create a caring but urgent response (2-3 sentences) that:
✓ Acknowledges their pain without minimizing
✓ Shows deep concern and care
✓ Encourages immediate professional help
✓ Conveys appropriate urgency while being warm
✗ No judgment or dismissing
✗ No false promises or clichés

Be genuinely caring while emphasizing help is available."""

            response = self.model.generate_content(prompt)
            message = response.text.strip().strip('"').strip("'")
            
            # Always add crisis resources
            crisis_resources = "\n\n🆘 **Immediate Help Available:**\n" \
                             "• Call 988 (Suicide & Crisis Lifeline)\n" \
                             "• Text HELLO to 741741 (Crisis Text Line)\n" \
                             "• Call 1-800-273-8255 (24/7 Support)\n" \
                             "• If in immediate danger, call 911"
            
            return message + crisis_resources
            
        except Exception as e:
            logger.error(f"Crisis response failed: {e}")
            return ("I'm deeply concerned about what you're sharing. Please reach out for immediate help:\n\n"
                   "🆘 Call 988 (Suicide & Crisis Lifeline)\n"
                   "📱 Text 'HELLO' to 741741\n" 
                   "☎️ Call 1-800-273-8255 (24/7)\n"
                   "🚨 If in danger, call 911\n\n"
                   "You don't have to face this alone.")

    def _validate_analysis(self, analysis: dict) -> dict:
        """Validate analysis response"""
        defaults = {
            'sentiment': 'neutral',
            'stress_level': 'medium',
            'emotions': ['uncertain'],
            'confidence': 0.5,
            'reasoning': 'Analysis completed'
        }
        
        # Fill missing fields
        for key, default in defaults.items():
            if key not in analysis:
                analysis[key] = default
        
        # Validate sentiment
        valid_sentiments = ['positive', 'neutral', 'negative', 'deeply_negative']
        if analysis['sentiment'] not in valid_sentiments:
            analysis['sentiment'] = 'neutral'
            
        # Validate stress
        valid_stress = ['low', 'medium', 'high', 'crisis']
        if analysis['stress_level'] not in valid_stress:
            analysis['stress_level'] = 'medium'
            
        # Validate confidence
        try:
            analysis['confidence'] = float(analysis['confidence'])
            if analysis['confidence'] < 0 or analysis['confidence'] > 1:
                analysis['confidence'] = 0.5
        except:
            analysis['confidence'] = 0.5
            
        # Validate emotions
        if not isinstance(analysis['emotions'], list) or len(analysis['emotions']) == 0:
            analysis['emotions'] = ['uncertain']
            
        return analysis


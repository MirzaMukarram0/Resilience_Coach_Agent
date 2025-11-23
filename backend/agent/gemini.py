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
        Enhanced rule-based emotional analysis with deep pattern recognition
        Analyzes context, metaphors, and implicit emotional cues
        """
        text_lower = text.lower()
        
        # CRISIS DETECTION - Explicit and implicit
        explicit_crisis = ['suicidal', 'suicide', 'kill myself', 'end it all', 
                          'harm myself', 'want to die', 'better off dead', 'end my life']
        
        implicit_crisis = [
            "don't see the point", "no point", "pointless", "why bother",
            "fading", "disappearing", "not exist", "tired of existing",
            "give up on life", "can't go on", "rather not be here"
        ]
        
        # LONELINESS & ISOLATION patterns (nuanced)
        loneliness_patterns = [
            "no one", "invisible", "no one sees me", "no one cares", "all alone",
            "nobody understands", "surrounded but", "people but feel", "pretend i'm fine",
            "smile so", "mask", "hiding", "fake", "no one would notice"
        ]
        
        # HOPELESSNESS patterns
        hopelessness_patterns = [
            "no hope", "hopeless", "nothing will change", "never get better",
            "always be like this", "stuck forever", "no future", "no way out",
            "tried everything", "nothing works", "pointless to try"
        ]
        
        # EMOTIONAL EXHAUSTION / BURNOUT patterns
        burnout_patterns = [
            "tired but can't rest", "exhausted beyond", "sleep doesn't help",
            "drained", "empty", "running on empty", "burnt out", "numb",
            "nothing excites", "lost interest", "don't care anymore",
            "going through motions", "feel nothing"
        ]
        
        # OVERWHELM patterns
        overwhelm_patterns = [
            "too much", "can't handle", "falling behind", "drowning",
            "suffocating", "crushing", "can't keep up", "everything at once",
            "losing control", "spiraling", "can't breathe"
        ]
        
        # ANXIETY patterns
        anxiety_patterns = [
            "panic", "racing", "can't calm", "on edge", "terrified",
            "scared", "fear", "anxious", "worried sick", "catastrophizing",
            "what if", "worst case", "paranoid"
        ]
        
        # DEPRESSION markers
        depression_patterns = [
            "depressed", "sad all the time", "cry", "heavy", "dark",
            "worthless", "failure", "hate myself", "nothing matters",
            "grey", "fog", "hollow"
        ]
        
        # POSITIVE MOTIVATION markers
        positive_patterns = [
            "motivated", "accomplished", "proud", "progress", "better",
            "cleaned", "organized", "productive", "energy", "lighter",
            "refreshed", "hopeful", "excited", "grateful", "happy"
        ]
        
        # MASKING / PRETENDING markers
        masking_patterns = [
            "pretend", "act like", "smile so", "hide", "don't want to bother",
            "burden", "fake it", "put on a face"
        ]
        
        # Initialize
        emotions = []
        sentiment_score = 0
        crisis_level = 0
        
        # CRISIS ANALYSIS
        for phrase in explicit_crisis:
            if phrase in text_lower:
                emotions.append('crisis')
                crisis_level = 3
                sentiment_score -= 5
                break
        
        if crisis_level == 0:
            for phrase in implicit_crisis:
                if phrase in text_lower:
                    emotions.append('hopelessness')
                    crisis_level = 2
                    sentiment_score -= 3
                    break
        
        # LONELINESS DETECTION
        loneliness_score = sum(1 for p in loneliness_patterns if p in text_lower)
        if loneliness_score >= 2:
            emotions.append('loneliness')
            sentiment_score -= 2
        elif loneliness_score == 1:
            emotions.append('isolation')
            sentiment_score -= 1
        
        # MASKING DETECTION
        masking_score = sum(1 for p in masking_patterns if p in text_lower)
        if masking_score > 0:
            emotions.append('emotional-masking')
            sentiment_score -= 1
        
        # HOPELESSNESS
        if any(p in text_lower for p in hopelessness_patterns):
            if 'hopelessness' not in emotions:
                emotions.append('hopelessness')
            sentiment_score -= 2
        
        # BURNOUT / EXHAUSTION
        burnout_score = sum(1 for p in burnout_patterns if p in text_lower)
        if burnout_score >= 2:
            emotions.append('burnout')
            sentiment_score -= 2
        elif burnout_score == 1:
            emotions.append('exhaustion')
            sentiment_score -= 1
        
        # OVERWHELM
        if any(p in text_lower for p in overwhelm_patterns):
            emotions.append('overwhelm')
            sentiment_score -= 2
        
        # ANXIETY
        anxiety_score = sum(1 for p in anxiety_patterns if p in text_lower)
        if anxiety_score >= 2:
            emotions.append('anxiety')
            sentiment_score -= 1
        elif anxiety_score == 1:
            emotions.append('worry')
            sentiment_score -= 0.5
        
        # DEPRESSION
        if any(p in text_lower for p in depression_patterns):
            emotions.append('sadness')
            sentiment_score -= 1
        
        # POSITIVE EMOTIONS
        positive_score = sum(1 for p in positive_patterns if p in text_lower)
        if positive_score >= 2:
            emotions.extend(['motivation', 'pride'])
            sentiment_score += 3
        elif positive_score == 1:
            emotions.append('positivity')
            sentiment_score += 1
        
        # DETERMINE SENTIMENT
        if sentiment_score >= 2:
            sentiment = 'positive'
        elif sentiment_score <= -2:
            sentiment = 'negative'
        else:
            # Context check - if negative emotions but weak signal
            if any(e in emotions for e in ['loneliness', 'isolation', 'hopelessness', 
                                           'burnout', 'overwhelm', 'crisis']):
                sentiment = 'negative'
            elif any(e in emotions for e in ['motivation', 'pride', 'positivity']):
                sentiment = 'positive'
            else:
                sentiment = 'neutral'
        
        # DETERMINE STRESS LEVEL
        if crisis_level >= 2:
            stress_level = 'high'
        elif any(e in emotions for e in ['crisis', 'hopelessness', 'overwhelm', 'burnout']):
            stress_level = 'high'
        elif any(e in emotions for e in ['anxiety', 'loneliness', 'exhaustion', 'emotional-masking']):
            stress_level = 'medium'
        elif sentiment == 'negative':
            stress_level = 'medium'
        else:
            stress_level = 'low'
        
        # CLEAN UP EMOTIONS - remove generic ones if specific exist
        if not emotions:
            if sentiment == 'negative':
                emotions = ['concern', 'unease']
            elif sentiment == 'positive':
                emotions = ['contentment']
            else:
                emotions = ['neutral']
        
        # Remove duplicates and limit to 4
        emotions = list(dict.fromkeys(emotions))[:4]
        
        return {
            'sentiment': sentiment,
            'stress_level': stress_level,
            'emotions': emotions
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
        Generate contextual supportive message based on deep emotional analysis
        """
        sentiment = analysis.get('sentiment', 'neutral')
        stress_level = analysis.get('stress_level', 'medium')
        emotions = analysis.get('emotions', [])
        
        text_lower = user_input.lower()
        
        # CRISIS RESPONSE
        crisis_keywords = ['suicidal', 'suicide', 'kill myself', 'end it', 'harm myself',
                          'want to die', 'better off dead', 'end my life']
        implicit_crisis = ["don't see the point", "no point", "pointless", 
                          "tired of existing", "fading"]
        
        if any(k in text_lower for k in crisis_keywords):
            return ("I'm deeply concerned about what you're sharing. Please reach out to a crisis helpline immediately: "
                   "National Suicide Prevention Lifeline: 988 or 1-800-273-8255. You don't have to face this alone - "
                   "professional help is available 24/7.")
        
        if any(k in text_lower for k in implicit_crisis):
            return ("What you're describing sounds like you're carrying a very heavy emotional weight. "
                   "These feelings of hopelessness are serious, and I want you to know help is available. "
                   "Please consider reaching out to 988 or 1-800-273-8255 to talk with someone who can provide support right now.")
        
        # LONELINESS / ISOLATION / MASKING
        if any(e in emotions for e in ['loneliness', 'isolation', 'emotional-masking']):
            loneliness_responses = [
                "Feeling invisible even when surrounded by people is incredibly painful. That emotional loneliness you're describing is real and valid, not something you're imagining.",
                "It takes courage to admit you're pretending to be fine. Your feelings matter, and reaching out like this shows strength, not burden.",
                "The kind of isolation you're feeling - where you're physically present but emotionally disconnected - is one of the hardest experiences to endure. You deserve to be seen and heard."
            ]
            import random
            return random.choice(loneliness_responses)
        
        # HOPELESSNESS (non-crisis)
        if 'hopelessness' in emotions:
            return ("When everything feels pointless, it's hard to see a way forward. That heaviness you're feeling is real. "
                   "Small steps matter right now - even reaching out like this. Let's focus on grounding techniques that might help.")
        
        # BURNOUT / EXHAUSTION
        if any(e in emotions for e in ['burnout', 'exhaustion']):
            burnout_responses = [
                "That deep exhaustion that sleep can't fix is a sign of emotional burnout, not weakness. Your mind and body are signaling they need different kinds of rest.",
                "When you're tired in a way that rest doesn't help, it's often emotional depletion. This isn't about pushing through - it's about gentle recovery and pacing.",
                "The exhaustion you're describing goes beyond physical tiredness. It sounds like you're emotionally drained, which needs compassionate self-care and realistic expectations."
            ]
            import random
            return random.choice(burnout_responses)
        
        # OVERWHELM
        if 'overwhelm' in emotions:
            overwhelm_responses = [
                "Feeling like you're falling behind in everything can create a paralyzing sense of overwhelm. Let's break things down into one small manageable step.",
                "When everything feels like too much at once, it's okay to slow down and focus on just the next breath, the next hour. You don't have to fix everything today.",
                "That drowning sensation you're experiencing is overwhelm flooding your system. Grounding techniques can help bring you back to the present moment."
            ]
            import random
            return random.choice(overwhelm_responses)
        
        # ANXIETY
        if any(e in emotions for e in ['anxiety', 'worry', 'panic']):
            return ("Anxiety can feel like your mind is racing ahead to every worst-case scenario. Let's work on grounding you back in this moment, where you're safe right now.")
        
        # DEPRESSION / SADNESS
        if any(e in emotions for e in ['sadness', 'depression']):
            return ("The sadness you're carrying is real and heavy. You don't have to 'snap out of it' or think positive - sometimes we need to acknowledge the pain before we can move through it gently.")
        
        # POSITIVE MOTIVATION
        if any(e in emotions for e in ['motivation', 'pride', 'positivity']):
            positive_responses = [
                "That sense of accomplishment and lighter energy you're feeling is wonderful! Let's build on this momentum with practices that maintain and grow this positive space.",
                "It's great to hear you're feeling motivated and productive! This energy is valuable - let's talk about strategies to sustain it without burning out.",
                "The pride and progress you're experiencing shows your resilience is working. Let's reinforce these positive patterns so they become more consistent."
            ]
            import random
            return random.choice(positive_responses)
        
        # HIGH STRESS (general)
        if stress_level == 'high':
            return ("You're carrying a significant emotional load right now. It's completely valid to feel overwhelmed. Let's focus on immediate grounding and safety-first strategies.")
        
        # MEDIUM STRESS
        if stress_level == 'medium':
            return ("I can sense you're dealing with some challenging emotions. You're not alone in this - let's explore some techniques that can help you navigate what you're feeling.")
        
        # NEUTRAL / DEFAULT
        return "I'm here to support you. Let's work together to understand what you're experiencing and find strategies that fit your needs right now."
    
    def _build_analysis_prompt(self, user_input: str) -> str:
        """Build prompt for emotional analysis with enhanced specifications"""
        return f"""You are an emotionally intelligent mental wellness AI assistant with deep understanding of human psychology.

Your task: Analyze the user's message for emotional state, stress level, and underlying emotional patterns.

User Input: "{user_input}"

Analyze deeply, looking for:
- Explicit emotions stated directly
- Implicit emotions (tone, context, contradictions)
- Physical symptoms mentioned (chest pressure, nausea, fatigue)
- Behavioral patterns (avoidance, isolation, sleep issues)
- Hidden cues (loneliness masked as independence, anxiety masked as humor)
- Contradictions ("I'm fine" but describes crisis)
- Risk indicators (hopelessness, self-harm thoughts, extreme statements)

Provide your analysis in EXACTLY this format (one line each):
SENTIMENT: [positive/neutral/negative]
STRESS_LEVEL: [low/medium/high]
EMOTIONS: [2-4 specific emotions separated by commas - be precise: use anxiety not worry, overwhelm not stress, heartbreak not sadness when appropriate]

Be accurate and multi-dimensional. Consider emotional layers, not just keywords."""

    def _build_support_prompt(self, user_input: str, analysis: dict) -> str:
        """Build prompt for supportive message with enhanced specifications"""
        return f"""You are a compassionate mental wellness coach trained in evidence-based therapeutic communication.

User shared: "{user_input}"

Emotional Analysis:
- Sentiment: {analysis['sentiment']}
- Stress Level: {analysis['stress_level']}
- Emotions: {', '.join(analysis['emotions'])}

Generate ONE supportive response (2-3 sentences) that is:
✓ Warm, conversational, and human-like
✓ Direct but gentle
✓ Validating without toxic positivity (avoid "just think positive")
✓ Grounding and safety-oriented
✓ Uses simple psychological strategies: validation, normalization, gentle guidance

✗ Never diagnose or label as mental illness
✗ Never make medical claims
✗ Never replace professional therapy
✗ Never dismiss or minimize feelings

If high risk detected (self-harm, suicidal thoughts, extreme hopelessness):
- Respond with compassion
- Acknowledge the severity
- Urgently direct to crisis resources (988, 1-800-273-8255)

Write naturally as if speaking to a friend who needs support."""

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

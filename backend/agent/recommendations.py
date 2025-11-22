"""
Recommendation Engine
Provides personalized coping strategies based on emotional analysis
"""
import logging
import random

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Engine for generating personalized wellness recommendations"""
    
    def __init__(self):
        """Initialize recommendation database"""
        self.strategies = {
            'breathing_exercise': {
                'name': 'Breathing Exercise',
                'steps': [
                    'Find a comfortable seated position',
                    'Close your eyes or soften your gaze',
                    'Inhale slowly through your nose for 4 counts',
                    'Hold your breath gently for 2 counts',
                    'Exhale slowly through your mouth for 6 counts',
                    'Repeat this cycle 5-10 times',
                    'Notice how your body feels calmer'
                ]
            },
            'grounding_technique': {
                'name': 'Grounding Technique (5-4-3-2-1)',
                'steps': [
                    'Acknowledge 5 things you can see around you',
                    'Acknowledge 4 things you can touch',
                    'Acknowledge 3 things you can hear',
                    'Acknowledge 2 things you can smell',
                    'Acknowledge 1 thing you can taste',
                    'Take a deep breath and return to the present moment'
                ]
            },
            'progressive_relaxation': {
                'name': 'Progressive Muscle Relaxation',
                'steps': [
                    'Start with your toes - tense them for 5 seconds, then release',
                    'Move to your calves - tense and release',
                    'Continue with thighs, abdomen, and chest',
                    'Tense and release your hands and arms',
                    'Finally, tense and release your neck and face',
                    'Notice the difference between tension and relaxation',
                    'Breathe deeply and enjoy the calm'
                ]
            },
            'mindful_meditation': {
                'name': 'Mindful Meditation',
                'steps': [
                    'Sit or lie down in a comfortable position',
                    'Close your eyes and focus on your breath',
                    'Notice the sensation of air entering and leaving',
                    'When thoughts arise, acknowledge them without judgment',
                    'Gently return your focus to your breath',
                    'Continue for 5-10 minutes',
                    'Open your eyes slowly when ready'
                ]
            },
            'positive_affirmations': {
                'name': 'Positive Affirmations',
                'steps': [
                    'Stand or sit in front of a mirror',
                    'Take three deep breaths',
                    'Say aloud: "I am capable and strong"',
                    'Say aloud: "I can handle difficult emotions"',
                    'Say aloud: "This feeling is temporary"',
                    'Say aloud: "I am worthy of peace and happiness"',
                    'Repeat these as often as needed'
                ]
            },
            'physical_activity': {
                'name': 'Gentle Physical Activity',
                'steps': [
                    'Stand up and stretch your arms overhead',
                    'Roll your shoulders backward 5 times',
                    'Take a short 5-minute walk, even if just around your room',
                    'Do 10 gentle jumping jacks or march in place',
                    'Stretch your neck gently side to side',
                    'Shake out your hands and arms',
                    'Notice the energy shift in your body'
                ]
            },
            'journaling': {
                'name': 'Reflective Journaling',
                'steps': [
                    'Get a notebook or open a digital document',
                    'Write down what you\'re feeling right now',
                    'Don\'t judge your thoughts - just let them flow',
                    'Write about what might be causing these feelings',
                    'Write one thing you\'re grateful for today',
                    'Write one small action you can take to feel better',
                    'Close by writing a kind message to yourself'
                ]
            },
            'social_connection': {
                'name': 'Social Connection',
                'steps': [
                    'Think of someone who makes you feel safe',
                    'Reach out with a text, call, or video chat',
                    'Share how you\'re feeling (if comfortable)',
                    'Ask them about their day',
                    'Remember: asking for support is a sign of strength',
                    'Even brief connections can help',
                    'Thank them for being there'
                ]
            }
        }
    
    def get_recommendation(self, sentiment: str, stress_level: str, emotions: list) -> dict:
        """
        Select appropriate coping strategy based on analysis
        
        Args:
            sentiment: User's sentiment (positive/neutral/negative)
            stress_level: Stress level (low/medium/high)
            emotions: List of detected emotions
            
        Returns:
            dict: Recommendation with type and steps
        """
        try:
            strategy_key = self._select_strategy(sentiment, stress_level, emotions)
            strategy = self.strategies[strategy_key]
            
            logger.info(f"Recommended strategy: {strategy_key}")
            
            return {
                'type': strategy_key,
                'name': strategy['name'],
                'steps': strategy['steps']
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            # Return default strategy
            return {
                'type': 'breathing_exercise',
                'name': 'Breathing Exercise',
                'steps': self.strategies['breathing_exercise']['steps']
            }
    
    def _select_strategy(self, sentiment: str, stress_level: str, emotions: list) -> str:
        """
        Select most appropriate strategy based on user's state
        
        Args:
            sentiment: User's sentiment
            stress_level: Stress level
            emotions: List of emotions
            
        Returns:
            str: Strategy key
        """
        emotions_str = ' '.join(emotions).lower()
        
        # High stress or anxiety -> Breathing or grounding
        if stress_level == 'high' or any(word in emotions_str for word in ['anxiety', 'panic', 'overwhelm', 'stressed']):
            return random.choice(['breathing_exercise', 'grounding_technique'])
        
        # Sadness or depression indicators -> Affirmations or social connection
        if any(word in emotions_str for word in ['sad', 'depressed', 'lonely', 'hopeless', 'down']):
            return random.choice(['positive_affirmations', 'social_connection'])
        
        # Anger or frustration -> Physical activity or progressive relaxation
        if any(word in emotions_str for word in ['angry', 'frustrated', 'irritated', 'annoyed']):
            return random.choice(['physical_activity', 'progressive_relaxation'])
        
        # Rumination or worry -> Journaling or meditation
        if any(word in emotions_str for word in ['worried', 'thinking', 'ruminating', 'confused']):
            return random.choice(['journaling', 'mindful_meditation'])
        
        # Medium stress -> Meditation or relaxation
        if stress_level == 'medium':
            return random.choice(['mindful_meditation', 'progressive_relaxation'])
        
        # Low stress or positive sentiment -> Maintain wellness
        if stress_level == 'low' or sentiment == 'positive':
            return random.choice(['mindful_meditation', 'positive_affirmations', 'journaling'])
        
        # Default fallback
        return 'breathing_exercise'
    
    def get_all_strategies(self) -> dict:
        """Return all available strategies"""
        return self.strategies

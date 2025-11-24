"""
Recommendation Engine - Now powered by pure Gemini AI
"""
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Simplified recommendation engine - Gemini handles strategy selection"""
    
    def __init__(self):
        """Initialize with basic strategy reference (for fallback only)"""
        # Keep minimal reference for emergencies only
        self.fallback_strategy = {
            'type': 'breathing_exercise',
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
        }
    
    def get_personalized_recommendation(
        self,
        sentiment: str,
        stress_level: str,
        emotions: list,
        emotional_patterns: dict,
        memory_context: list
    ) -> dict:
        """
        This method is now deprecated - Gemini handles all recommendation logic
        in gemini.py generate_recommendation()
        
        This only serves as a fallback if Gemini fails completely
        """
        logger.warning("Using fallback recommendation - Gemini should handle this")
        
        return {
            'type': 'breathing_exercise',
            'name': 'Simple Breathing Exercise', 
            'steps': [
                'Sit comfortably and close your eyes',
                'Focus on your natural breathing',
                'Breathe in slowly through your nose',
                'Breathe out slowly through your mouth',
                'Continue for 2-3 minutes',
                'Notice how you feel afterward'
            ]
        }
    
    def get_recommendation(self, sentiment: str, stress_level: str, emotions: list) -> dict:
        """Deprecated - keeping for backward compatibility"""
        logger.warning("Using deprecated recommendation method")
        return self.fallback_strategy
    
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
        Select most appropriate strategy based on deep emotional analysis
        
        Args:
            sentiment: User's sentiment
            stress_level: Stress level
            emotions: List of emotions
            
        Returns:
            str: Strategy key
        """
        emotions_str = ' '.join(emotions).lower()
        
        # CRISIS / HOPELESSNESS -> Grounding (bring to present)
        if any(word in emotions_str for word in ['crisis', 'hopelessness', 'suicidal']):
            return 'grounding_technique'
        
        # LONELINESS / ISOLATION -> Social connection
        if any(word in emotions_str for word in ['loneliness', 'isolation', 'invisible', 'alone', 'masking']):
            return 'social_connection'
        
        # BURNOUT / EXHAUSTION -> Progressive relaxation (physical rest)
        if any(word in emotions_str for word in ['burnout', 'exhaustion', 'drained', 'empty', 'numb']):
            return 'progressive_relaxation'
        
        # OVERWHELM -> Grounding (reduce stimulation)
        if any(word in emotions_str for word in ['overwhelm', 'drowning', 'suffocating', 'too much']):
            return 'grounding_technique'
        
        # ANXIETY / PANIC -> Breathing (calm nervous system)
        if any(word in emotions_str for word in ['anxiety', 'panic', 'racing', 'scared', 'terrified']):
            return 'breathing_exercise'
        
        # DEPRESSION / SADNESS (not loneliness) -> Affirmations or gentle activity
        if any(word in emotions_str for word in ['depression', 'sadness', 'hopeless', 'worthless', 'dark']):
            # Vary to prevent repetition
            return random.choice(['positive_affirmations', 'physical_activity'])
        
        # ANGER / FRUSTRATION -> Physical activity (release)
        if any(word in emotions_str for word in ['anger', 'frustrated', 'irritated', 'annoyed', 'rage']):
            return 'physical_activity'
        
        # WORRY / RUMINATION -> Journaling (externalize thoughts)
        if any(word in emotions_str for word in ['worry', 'ruminating', 'confused', 'uncertain', 'thinking']):
            return 'journaling'
        
        # POSITIVE MOTIVATION -> Journaling (reinforce gains) or affirmations
        if any(word in emotions_str for word in ['motivation', 'pride', 'progress', 'accomplished', 'productive']):
            return random.choice(['journaling', 'positive_affirmations'])
        
        # HIGH STRESS (general) -> Breathing or grounding
        if stress_level == 'high':
            return random.choice(['breathing_exercise', 'grounding_technique'])
        
        # MEDIUM STRESS -> Meditation or relaxation
        if stress_level == 'medium':
            return random.choice(['mindful_meditation', 'progressive_relaxation'])
        
        # LOW STRESS / POSITIVE -> Maintain wellness
        if stress_level == 'low' or sentiment == 'positive':
            return random.choice(['mindful_meditation', 'journaling', 'positive_affirmations'])
        
        # Default fallback
        return 'breathing_exercise'
    
    def get_all_strategies(self) -> dict:
        """Return all available strategies"""
        return self.strategies
    
    def get_personalized_recommendation(
        self,
        sentiment: str,
        stress_level: str,
        emotions: list,
        emotional_patterns: dict,
        memory_context: list
    ) -> dict:
        """
        Get personalized recommendation considering user history and patterns
        
        Args:
            sentiment: Current sentiment
            stress_level: Current stress level
            emotions: Current emotions
            emotional_patterns: User's historical patterns
            memory_context: Past interactions
            
        Returns:
            dict: Personalized recommendation with type and steps
        """
        try:
            # Check what strategies were used recently
            recent_strategies = []
            for ctx in memory_context[:3]:
                meta = ctx.get('metadata', {})
                if 'strategy_type' in meta:
                    recent_strategies.append(meta['strategy_type'])
            
            # Get primary strategy selection
            primary_strategy = self._select_strategy(sentiment, stress_level, emotions)
            
            # Check for pattern-based adjustments
            recurring = emotional_patterns.get('recurring_emotions', [])
            
            # If user repeatedly experiences loneliness, prioritize connection
            if 'loneliness' in recurring or 'isolation' in recurring:
                if stress_level in ['medium', 'high'] and primary_strategy not in ['social_connection', 'grounding_technique']:
                    primary_strategy = 'social_connection'
            
            # If user frequently anxious and breathwork was recent, try grounding instead
            if 'anxiety' in recurring and 'breathing_exercise' in recent_strategies[:2]:
                if primary_strategy == 'breathing_exercise':
                    primary_strategy = 'grounding_technique'
            
            # If repeated burnout, alternate between rest strategies
            if 'burnout' in recurring or 'exhaustion' in recurring:
                if primary_strategy == 'progressive_relaxation' and 'progressive_relaxation' in recent_strategies[:1]:
                    primary_strategy = 'mindful_meditation'
            
            # If overwhelm is recurring and recent, ensure grounding or journaling
            if 'overwhelm' in recurring:
                if stress_level == 'high' and primary_strategy not in ['grounding_technique', 'journaling']:
                    primary_strategy = 'grounding_technique'
            
            # Avoid suggesting same strategy consecutively unless it's crisis-appropriate
            if recent_strategies and primary_strategy == recent_strategies[0]:
                if stress_level != 'crisis' and stress_level != 'high':
                    # Find an alternative in same category
                    alternatives = self._get_strategy_alternatives(primary_strategy)
                    primary_strategy = alternatives[0] if alternatives else primary_strategy
            
            strategy = self.strategies[primary_strategy]
            
            logger.info(f"Personalized strategy: {primary_strategy} (considering {len(recent_strategies)} past uses)")
            
            return {
                'type': primary_strategy,
                'name': strategy['name'],
                'steps': strategy['steps']
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendation: {e}")
            # Fallback to standard recommendation
            return self.get_recommendation(sentiment, stress_level, emotions)
    
    def _get_strategy_alternatives(self, current_strategy: str) -> list:
        """
        Get alternative strategies in same category
        
        Args:
            current_strategy: Current strategy key
            
        Returns:
            list: Alternative strategy keys
        """
        # Group strategies by purpose
        calming_strategies = ['breathing_exercise', 'grounding_technique', 'progressive_relaxation', 'mindful_meditation']
        emotional_strategies = ['positive_affirmations', 'journaling', 'social_connection']
        energizing_strategies = ['physical_activity', 'positive_affirmations', 'social_connection']
        
        # Find alternatives in same group
        if current_strategy in calming_strategies:
            return [s for s in calming_strategies if s != current_strategy]
        elif current_strategy in emotional_strategies:
            return [s for s in emotional_strategies if s != current_strategy]
        elif current_strategy in energizing_strategies:
            return [s for s in energizing_strategies if s != current_strategy]
        
        return ['breathing_exercise']  # Safe default

"""
LangGraph Workflow with Reasoning Capabilities
Orchestrates intelligent emotional analysis with memory and branching logic
"""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from backend.agent.gemini import GeminiClient
from backend.agent.recommendations import RecommendationEngine
from backend.agent.memory import MemoryStore
from backend.agent.config import Config
import logging

logger = logging.getLogger(__name__)


# Define the enhanced state structure
class AgentState(TypedDict):
    """Enhanced state with memory and reasoning context"""
    input_text: str
    metadata: dict
    user_id: str
    analysis: dict
    memory_context: list
    emotional_patterns: dict
    crisis_score: float
    reasoning_trace: str
    recommendation: dict
    message: str
    status: str
    agent: str
    confidence_score: float


class ResilienceWorkflow:
    """LangGraph workflow with reasoning and memory integration"""
    
    def __init__(self):
        """Initialize workflow components with memory"""
        self.gemini_client = GeminiClient()
        self.recommendation_engine = RecommendationEngine()
        self.memory_store = MemoryStore()
        self.graph = self._build_graph()
        logger.info("Resilience workflow initialized with reasoning capabilities")
    
    def _build_graph(self) -> StateGraph:
        """Build the enhanced LangGraph workflow with reasoning branches"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("memory_retrieval", self._memory_retrieval_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("crisis_detection", self._crisis_detection_node)
        workflow.add_node("reasoning", self._reasoning_node)
        workflow.add_node("recommend", self._recommend_node)
        workflow.add_node("support", self._support_node)
        workflow.add_node("crisis_response", self._crisis_response_node)
        workflow.add_node("memory_storage", self._memory_storage_node)
        workflow.add_node("format", self._format_node)
        
        # Define entry and edges with conditional routing
        workflow.set_entry_point("memory_retrieval")
        workflow.add_edge("memory_retrieval", "analyze")
        workflow.add_edge("analyze", "crisis_detection")
        
        # Conditional routing based on crisis detection
        workflow.add_conditional_edges(
            "crisis_detection",
            self._route_crisis,
            {
                "crisis": "crisis_response",
                "normal": "reasoning"
            }
        )
        
        # Normal flow
        workflow.add_edge("reasoning", "recommend")
        workflow.add_edge("recommend", "support")
        workflow.add_edge("support", "memory_storage")
        workflow.add_edge("memory_storage", "format")
        
        # Crisis flow
        workflow.add_edge("crisis_response", "memory_storage")
        
        # End
        workflow.add_edge("format", END)
        
        return workflow.compile()
    
    def process(self, input_text: str, metadata: dict = None) -> dict:
        """
        Process user input through the enhanced reasoning workflow
        
        Args:
            input_text: User's message
            metadata: Optional metadata (user_id, language, etc.)
            
        Returns:
            dict: Complete response with analysis, reasoning, recommendation, and message
        """
        try:
            # Extract user_id from metadata or generate anonymous one
            user_id = (metadata or {}).get('user_id', 'anonymous')
            
            # Initialize enhanced state
            initial_state = {
                'input_text': input_text,
                'metadata': metadata or {},
                'user_id': user_id,
                'analysis': {},
                'memory_context': [],
                'emotional_patterns': {},
                'crisis_score': 0.0,
                'reasoning_trace': '',
                'recommendation': {},
                'message': '',
                'status': 'processing',
                'agent': Config.AGENT_NAME,
                'confidence_score': 0.0
            }
            
            logger.info(f"Processing input with reasoning for user {user_id}: {input_text[:50]}...")
            
            # Run through enhanced workflow
            result = self.graph.invoke(initial_state)
            
            # Format final response
            response = {
                'agent': result['agent'],
                'status': result['status'],
                'analysis': result['analysis'],
                'recommendation': result['recommendation'],
                'message': result['message'],
                'crisis_score': result.get('crisis_score', 0.0),
                'confidence': result.get('confidence_score', 0.0),
                'reasoning': result.get('reasoning_trace', '')
            }
            
            logger.info("Workflow completed successfully with reasoning")
            return response
            
        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            return self._error_response(str(e))
    
    def _memory_retrieval_node(self, state: AgentState) -> AgentState:
        """
        Node: Retrieve relevant context from memory
        """
        try:
            logger.info("Retrieving memory context...")
            
            # Get relevant past interactions
            memory_context = self.memory_store.retrieve_relevant_context(
                user_id=state['user_id'],
                current_message=state['input_text'],
                n_results=3
            )
            
            # Get emotional patterns
            emotional_patterns = self.memory_store.get_emotional_patterns(
                user_id=state['user_id'],
                limit=10
            )
            
            state['memory_context'] = memory_context
            state['emotional_patterns'] = emotional_patterns
            
            logger.info(f"Retrieved {len(memory_context)} past contexts and patterns")
            
        except Exception as e:
            logger.error(f"Memory retrieval error: {e}")
            state['memory_context'] = []
            state['emotional_patterns'] = {}
        
        return state
    
    def _analyze_node(self, state: AgentState) -> AgentState:
        """
        Node: Analyze emotional state with memory context (using Gemini)
        """
        try:
            logger.info("Analyzing emotional state with Gemini...")
            
            # Use Gemini for deep emotional analysis with context
            analysis = self.gemini_client.analyze_emotion_with_context(
                input_text=state['input_text'],
                memory_context=state['memory_context'],
                emotional_patterns=state['emotional_patterns']
            )
            
            state['analysis'] = analysis
            state['confidence_score'] = analysis.get('confidence', 0.0)
            
            logger.info(f"Analysis complete: {analysis}")
            
        except Exception as e:
            logger.error(f"Analysis node error: {e}")
            # Return error state instead of fake analysis
            error_msg = str(e)
            if '429' in error_msg or 'quota' in error_msg.lower():
                state['analysis'] = {
                    'sentiment': 'error_quota_exceeded',
                    'stress_level': 'api_unavailable',
                    'emotions': ['api_quota_exceeded'],
                    'confidence': 0.0,
                    'reasoning': f'❌ Analysis failed: API quota exceeded - {error_msg}'
                }
            else:
                state['analysis'] = {
                    'sentiment': 'error_api_failed',
                    'stress_level': 'api_unavailable',
                    'emotions': ['api_error'],
                    'confidence': 0.0,
                    'reasoning': f'❌ Analysis failed: {error_msg}'
                }
            state['confidence_score'] = 0.0
        
        return state
    
    def _crisis_detection_node(self, state: AgentState) -> AgentState:
        """
        Node: Detect crisis level using Gemini reasoning
        """
        try:
            logger.info("Detecting crisis level...")
            
            # Use Gemini to assess crisis severity
            crisis_score = self.gemini_client.assess_crisis_level(
                input_text=state['input_text'],
                analysis=state['analysis'],
                emotional_patterns=state['emotional_patterns']
            )
            
            state['crisis_score'] = crisis_score
            
            if crisis_score > 0.7:
                logger.warning(f"HIGH CRISIS DETECTED: Score {crisis_score}")
            else:
                logger.info(f"Crisis score: {crisis_score}")
            
        except Exception as e:
            logger.error(f"Crisis detection error: {e}")
            # Conservative approach - mark as potential crisis if error
            state['crisis_score'] = 0.5
        
        return state
    
    def _route_crisis(self, state: AgentState) -> Literal["crisis", "normal"]:
        """
        Conditional routing based on crisis score
        """
        if state['crisis_score'] > 0.7:
            logger.info("Routing to CRISIS response")
            return "crisis"
        else:
            logger.info("Routing to NORMAL flow")
            return "normal"
    
    def _reasoning_node(self, state: AgentState) -> AgentState:
        """
        Node: Perform reasoning to integrate analysis, memory, and context
        """
        try:
            logger.info("Performing reasoning integration...")
            
            # Generate reasoning trace
            reasoning = self.gemini_client.generate_reasoning(
                input_text=state['input_text'],
                analysis=state['analysis'],
                memory_context=state['memory_context'],
                emotional_patterns=state['emotional_patterns']
            )
            
            state['reasoning_trace'] = reasoning
            logger.info("Reasoning complete")
            
        except Exception as e:
            logger.error(f"Reasoning node error: {e}")
            state['reasoning_trace'] = "Unable to generate reasoning trace"
        
        return state
    
    def _recommend_node(self, state: AgentState) -> AgentState:
        """
        Node: Generate recommendation using pure Gemini intelligence
        """
        try:
            logger.info("Generating Gemini-powered recommendation...")
            
            # Use Gemini to generate recommendation directly
            recommendation = self.gemini_client.generate_recommendation(
                input_text=state['input_text'],
                analysis=state['analysis'],
                memory_context=state['memory_context'],
                emotional_patterns=state['emotional_patterns']
            )
            
            state['recommendation'] = recommendation
            logger.info(f"Gemini recommended: {recommendation['type']}")
            
        except Exception as e:
            logger.error(f"Gemini recommendation error: {e}")
            # Minimal fallback
            state['recommendation'] = {
                'type': 'breathing_exercise',
                'name': 'Simple Breathing',
                'steps': ['Breathe slowly and deeply', 'Focus on your breath', 'Continue for a few minutes'],
                'reasoning': 'Default calming technique'
            }
        
        return state
    
    def _support_node(self, state: AgentState) -> AgentState:
        """
        Node: Generate supportive message with full context
        """
        try:
            logger.info("Generating context-aware supportive message...")
            
            message = self.gemini_client.generate_supportive_message_with_context(
                user_input=state['input_text'],
                analysis=state['analysis'],
                memory_context=state['memory_context'],
                emotional_patterns=state['emotional_patterns'],
                reasoning_trace=state['reasoning_trace']
            )
            
            state['message'] = message
            logger.info("Supportive message generated")
            
        except Exception as e:
            logger.error(f"Support node error: {e}")
            state['message'] = "I'm here to support you. Let's work through this together, one step at a time."
        
        return state
    
    def _crisis_response_node(self, state: AgentState) -> AgentState:
        """
        Node: Handle crisis situation with immediate support
        """
        try:
            logger.warning("Generating CRISIS response...")
            
            # Generate crisis-specific supportive message
            crisis_message = self.gemini_client.generate_crisis_response(
                user_input=state['input_text'],
                analysis=state['analysis'],
                crisis_score=state['crisis_score']
            )
            
            state['message'] = crisis_message
            
            # Override recommendation with crisis resources
            state['recommendation'] = {
                'type': 'crisis_support',
                'name': 'Immediate Crisis Support',
                'steps': [
                    'Call 988 (National Suicide Prevention Lifeline)',
                    'Text "HELLO" to 741741 (Crisis Text Line)',
                    'Call 1-800-273-8255 (24/7 Support)',
                    'If in immediate danger, call 911',
                    'Reach out to a trusted friend or family member',
                    'Go to the nearest emergency room'
                ]
            }
            
            logger.warning("Crisis response generated")
            
        except Exception as e:
            logger.error(f"Crisis response error: {e}")
            # Ensure crisis resources are provided even if error
            state['message'] = ("I'm very concerned about what you're sharing. Please reach out for immediate help:\n\n"
                               "🆘 Call 988 (Suicide & Crisis Lifeline)\n"
                               "📱 Text 'HELLO' to 741741 (Crisis Text Line)\n"
                               "☎️ Call 1-800-273-8255 (24/7 Support)\n\n"
                               "You don't have to face this alone. Professional help is available right now.")
            
            state['recommendation'] = {
                'type': 'crisis_support',
                'name': 'Crisis Resources',
                'steps': ['Call 988 immediately', 'Text 741741', 'Call 911 if in immediate danger']
            }
        
        return state
    
    def _memory_storage_node(self, state: AgentState) -> AgentState:
        """
        Node: Store interaction in memory for future context
        """
        try:
            logger.info("Storing interaction in memory...")
            
            self.memory_store.store_interaction(
                user_id=state['user_id'],
                user_message=state['input_text'],
                analysis=state['analysis'],
                recommendation=state['recommendation'],
                crisis_score=state['crisis_score']
            )
            
            logger.info("Interaction stored successfully")
            
        except Exception as e:
            logger.error(f"Memory storage error: {e}")
            # Non-critical - continue anyway
        
        return state
    
    def _format_node(self, state: AgentState) -> AgentState:
        """
        Node: Format final response
        """
        try:
            # Clean up recommendation format for response
            if 'name' in state['recommendation']:
                del state['recommendation']['name']
            
            state['status'] = 'success'
            logger.info("Response formatted successfully")
            
        except Exception as e:
            logger.error(f"Format node error: {e}")
            state['status'] = 'success'  # Still mark as success with partial data
        
        return state
    
    def _error_response(self, error_message: str) -> dict:
        """
        Generate error response
        """
        return {
            'agent': Config.AGENT_NAME,
            'status': 'error',
            'message': f'An error occurred: {error_message}',
            'analysis': {},
            'recommendation': {},
            'crisis_score': 0.0,
            'confidence': 0.0,
            'reasoning': ''
        }

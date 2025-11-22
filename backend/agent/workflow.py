"""
LangGraph Workflow
Orchestrates the agent's processing pipeline
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from backend.agent.gemini import GeminiClient
from backend.agent.recommendations import RecommendationEngine
from backend.agent.config import Config
import logging

logger = logging.getLogger(__name__)


# Define the state structure
class AgentState(TypedDict):
    """State passed through the workflow"""
    input_text: str
    metadata: dict
    analysis: dict
    recommendation: dict
    message: str
    status: str
    agent: str


class ResilienceWorkflow:
    """LangGraph workflow for processing user requests"""
    
    def __init__(self):
        """Initialize workflow components"""
        self.gemini_client = GeminiClient()
        self.recommendation_engine = RecommendationEngine()
        self.graph = self._build_graph()
        logger.info("Resilience workflow initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("recommend", self._recommend_node)
        workflow.add_node("support", self._support_node)
        workflow.add_node("format", self._format_node)
        
        # Define edges (flow)
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "recommend")
        workflow.add_edge("recommend", "support")
        workflow.add_edge("support", "format")
        workflow.add_edge("format", END)
        
        return workflow.compile()
    
    def process(self, input_text: str, metadata: dict = None) -> dict:
        """
        Process user input through the workflow
        
        Args:
            input_text: User's message
            metadata: Optional metadata (user_id, language, etc.)
            
        Returns:
            dict: Complete response with analysis, recommendation, and message
        """
        try:
            # Initialize state
            initial_state = {
                'input_text': input_text,
                'metadata': metadata or {},
                'analysis': {},
                'recommendation': {},
                'message': '',
                'status': 'processing',
                'agent': Config.AGENT_NAME
            }
            
            logger.info(f"Processing input: {input_text[:50]}...")
            
            # Run through workflow
            result = self.graph.invoke(initial_state)
            
            # Format final response
            response = {
                'agent': result['agent'],
                'status': result['status'],
                'analysis': result['analysis'],
                'recommendation': result['recommendation'],
                'message': result['message']
            }
            
            logger.info("Workflow completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            return self._error_response(str(e))
    
    def _analyze_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Analyze emotional state
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with analysis
        """
        try:
            logger.info("Analyzing emotional state...")
            analysis = self.gemini_client.analyze_emotion(state['input_text'])
            state['analysis'] = analysis
            logger.info(f"Analysis complete: {analysis}")
        except Exception as e:
            logger.error(f"Analysis node error: {e}")
            state['analysis'] = {
                'sentiment': 'neutral',
                'stress_level': 'medium',
                'emotions': ['uncertain']
            }
        
        return state
    
    def _recommend_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Generate recommendation
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with recommendation
        """
        try:
            logger.info("Generating recommendation...")
            analysis = state['analysis']
            recommendation = self.recommendation_engine.get_recommendation(
                sentiment=analysis['sentiment'],
                stress_level=analysis['stress_level'],
                emotions=analysis['emotions']
            )
            state['recommendation'] = recommendation
            logger.info(f"Recommendation: {recommendation['type']}")
        except Exception as e:
            logger.error(f"Recommendation node error: {e}")
            state['recommendation'] = {
                'type': 'breathing_exercise',
                'name': 'Breathing Exercise',
                'steps': ['Take slow, deep breaths']
            }
        
        return state
    
    def _support_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Generate supportive message
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with supportive message
        """
        try:
            logger.info("Generating supportive message...")
            message = self.gemini_client.generate_supportive_message(
                user_input=state['input_text'],
                analysis=state['analysis']
            )
            state['message'] = message
            logger.info("Supportive message generated")
        except Exception as e:
            logger.error(f"Support node error: {e}")
            state['message'] = "I'm here to support you. Take things one step at a time."
        
        return state
    
    def _format_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Format final response
        
        Args:
            state: Current workflow state
            
        Returns:
            Final formatted state
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
        
        Args:
            error_message: Error description
            
        Returns:
            Error response dict
        """
        return {
            'agent': Config.AGENT_NAME,
            'status': 'error',
            'message': f'An error occurred: {error_message}',
            'analysis': {},
            'recommendation': {}
        }

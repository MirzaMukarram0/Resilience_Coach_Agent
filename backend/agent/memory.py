"""
Memory Layer using ChromaDB
Provides long-term context and continuity for emotional analysis
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import google.generativeai as genai
from datetime import datetime
from backend.agent.config import Config
import logging
import json
import os

logger = logging.getLogger(__name__)


class MemoryStore:
    """ChromaDB-based memory store for conversation history and emotional patterns"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB with persistent storage
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_db')
            os.makedirs(db_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Use Gemini embeddings for semantic search
            self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=Config.GEMINI_API_KEY,
                model_name="models/embedding-001"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="resilience_memory",
                embedding_function=self.embedding_function,
                metadata={"description": "Emotional history and conversation context"}
            )
            
            logger.info("Memory store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing memory store: {e}")
            # Fallback to in-memory store
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
            self.collection = self.client.get_or_create_collection(
                name="resilience_memory",
                metadata={"description": "Emotional history (in-memory)"}
            )
            logger.warning("Using in-memory storage (no persistence)")
    
    def store_interaction(
        self,
        user_id: str,
        user_message: str,
        analysis: dict,
        recommendation: dict,
        crisis_score: float = 0.0
    ) -> str:
        """
        Store user interaction with emotional analysis
        
        Args:
            user_id: Unique user identifier
            user_message: User's input text
            analysis: Emotional analysis results
            recommendation: Recommended coping strategy
            crisis_score: Crisis severity (0-1)
            
        Returns:
            str: Stored document ID
        """
        try:
            timestamp = datetime.now().isoformat()
            doc_id = f"{user_id}_{timestamp}"
            
            # Create metadata for filtering
            metadata = {
                "user_id": user_id,
                "timestamp": timestamp,
                "sentiment": analysis.get('sentiment', 'neutral'),
                "stress_level": analysis.get('stress_level', 'medium'),
                "crisis_score": crisis_score,
                "emotions": json.dumps(analysis.get('emotions', [])),
                "strategy_type": recommendation.get('type', 'unknown')
            }
            
            # Create document text for semantic search
            document = f"""
            User Message: {user_message}
            Emotional State: {analysis.get('sentiment', 'neutral')}
            Stress Level: {analysis.get('stress_level', 'medium')}
            Emotions: {', '.join(analysis.get('emotions', []))}
            Crisis Severity: {crisis_score}
            Recommended Strategy: {recommendation.get('type', 'unknown')}
            Timestamp: {timestamp}
            """
            
            # Store in ChromaDB
            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            logger.info(f"Stored interaction for user {user_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            return ""
    
    def retrieve_relevant_context(
        self,
        user_id: str,
        current_message: str,
        n_results: int = 3
    ) -> list:
        """
        Retrieve relevant past interactions for context
        
        Args:
            user_id: User identifier
            current_message: Current user message
            n_results: Number of results to retrieve
            
        Returns:
            list: Relevant past interactions
        """
        try:
            # Query with user_id filter
            results = self.collection.query(
                query_texts=[current_message],
                n_results=n_results,
                where={"user_id": user_id}
            )
            
            if not results['ids'] or not results['ids'][0]:
                logger.info(f"No previous context found for user {user_id}")
                return []
            
            # Format results
            context = []
            for i in range(len(results['ids'][0])):
                context_item = {
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                context.append(context_item)
            
            logger.info(f"Retrieved {len(context)} relevant contexts for user {user_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def get_emotional_patterns(self, user_id: str, limit: int = 10) -> dict:
        """
        Analyze emotional patterns from user history
        
        Args:
            user_id: User identifier
            limit: Number of recent interactions to analyze
            
        Returns:
            dict: Pattern analysis (recurring emotions, stress trends, crisis frequency)
        """
        try:
            # Get recent interactions
            results = self.collection.get(
                where={"user_id": user_id},
                limit=limit
            )
            
            if not results['ids']:
                return {
                    'recurring_emotions': [],
                    'avg_stress': 'medium',
                    'crisis_frequency': 0,
                    'total_interactions': 0
                }
            
            # Analyze patterns
            emotions_count = {}
            stress_levels = []
            crisis_count = 0
            
            for metadata in results['metadatas']:
                # Count emotions
                emotions = json.loads(metadata.get('emotions', '[]'))
                for emotion in emotions:
                    emotions_count[emotion] = emotions_count.get(emotion, 0) + 1
                
                # Track stress levels
                stress_levels.append(metadata.get('stress_level', 'medium'))
                
                # Count crisis situations
                if float(metadata.get('crisis_score', 0)) > 0.7:
                    crisis_count += 1
            
            # Find recurring emotions (top 3)
            recurring_emotions = sorted(
                emotions_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            # Calculate average stress
            stress_map = {'low': 1, 'medium': 2, 'high': 3, 'crisis': 4}
            avg_stress_num = sum(stress_map.get(s, 2) for s in stress_levels) / len(stress_levels)
            avg_stress = 'low' if avg_stress_num < 1.5 else 'medium' if avg_stress_num < 2.5 else 'high'
            
            return {
                'recurring_emotions': [e[0] for e in recurring_emotions],
                'avg_stress': avg_stress,
                'crisis_frequency': crisis_count,
                'total_interactions': len(results['ids'])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return {
                'recurring_emotions': [],
                'avg_stress': 'medium',
                'crisis_frequency': 0,
                'total_interactions': 0
            }
    
    def clear_user_history(self, user_id: str) -> bool:
        """
        Clear all history for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: Success status
        """
        try:
            # Get all IDs for this user
            results = self.collection.get(where={"user_id": user_id})
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Cleared history for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False

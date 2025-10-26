import time
import uuid
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages conversation sessions for context-aware query routing."""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.session_timeout = 3600  # 1 hour
        self.max_session_history = 10  # Keep last 10 queries per session
    
    def create_session(self) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        
        session_data = {
            'id': session_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'query_history': [],
            'categories': [],
            'context': {}
        }
        
        self.cache_manager.set_session(session_id, session_data, ttl=self.session_timeout)
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        try:
            return self.cache_manager.get_session(session_id)
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, query: str, categories: List[str], 
                      response_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update session with new query and routing information."""
        try:
            session_data = self.get_session(session_id)
            if not session_data:
                logger.warning(f"Session {session_id} not found, creating new one")
                session_data = {
                    'id': session_id,
                    'created_at': time.time(),
                    'last_activity': time.time(),
                    'query_history': [],
                    'categories': [],
                    'context': {}
                }
            
            # Update session data
            session_data['last_activity'] = time.time()
            session_data['categories'] = categories
            
            # Add to query history
            query_entry = {
                'query': query,
                'categories': categories,
                'timestamp': time.time(),
                'response_data': response_data
            }
            
            session_data['query_history'].append(query_entry)
            
            # Keep only recent queries
            if len(session_data['query_history']) > self.max_session_history:
                session_data['query_history'] = session_data['query_history'][-self.max_session_history:]
            
            # Update context based on recent queries
            session_data['context'] = self._extract_context(session_data['query_history'])
            
            # Save updated session
            self.cache_manager.set_session(session_id, session_data, ttl=self.session_timeout)
            
            logger.info(f"Updated session {session_id} with query: {query[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    def _extract_context(self, query_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract context from query history."""
        if not query_history:
            return {}
        
        # Get most recent categories
        recent_categories = []
        for entry in query_history[-3:]:  # Last 3 queries
            recent_categories.extend(entry.get('categories', []))
        
        # Count category frequency
        category_counts = {}
        for category in recent_categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Get most common categories
        common_categories = sorted(
            category_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        return {
            'recent_categories': [cat for cat, count in common_categories],
            'category_frequency': category_counts,
            'total_queries': len(query_history),
            'session_duration': time.time() - query_history[0]['timestamp'] if query_history else 0
        }
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get context for a session."""
        session_data = self.get_session(session_id)
        if session_data:
            return session_data.get('context', {})
        return None
    
    def is_session_active(self, session_id: str) -> bool:
        """Check if session is still active."""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        last_activity = session_data.get('last_activity', 0)
        return (time.time() - last_activity) < self.session_timeout
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session timeout."""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                session_data['last_activity'] = time.time()
                self.cache_manager.set_session(session_id, session_data, ttl=self.session_timeout)
                return True
            return False
        except Exception as e:
            logger.error(f"Error extending session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            self.cache_manager.delete_session(session_id)
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a session."""
        session_data = self.get_session(session_id)
        if not session_data:
            return None
        
        query_history = session_data.get('query_history', [])
        
        return {
            'session_id': session_id,
            'created_at': session_data.get('created_at'),
            'last_activity': session_data.get('last_activity'),
            'total_queries': len(query_history),
            'current_categories': session_data.get('categories', []),
            'session_age_seconds': time.time() - session_data.get('created_at', time.time()),
            'is_active': self.is_session_active(session_id)
        }
    
    def health_check(self) -> bool:
        """Check if session manager is healthy."""
        try:
            # Test session creation and retrieval
            test_session_id = self.create_session()
            session_data = self.get_session(test_session_id)
            
            if session_data and session_data.get('id') == test_session_id:
                self.delete_session(test_session_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Session manager health check failed: {e}")
            return False

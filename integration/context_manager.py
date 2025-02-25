"""
Context Manager: Manages shared context and state across MCP server modules.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import asyncio
import json
import hashlib

@dataclass
class ContextState:
    """Represents a snapshot of the current processing context"""
    session_id: str
    timestamp: float
    input_data: Dict[str, Any]
    module_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContextManager:
    """
    Manages and tracks context across different modules of the MCP server.
    """
    def __init__(self, max_history: int = 100):
        """
        Initialize the context manager
        
        Args:
            max_history: Maximum number of context states to retain
        """
        self._context_history: Dict[str, ContextState] = {}
        self._max_history = max_history
        self._lock = asyncio.Lock()

    def _generate_session_id(self, input_data: Dict[str, Any]) -> str:
        """
        Generate a unique session ID based on input data
        
        Args:
            input_data: Input data to generate session ID from
        
        Returns:
            Unique session ID
        """
        # Create a hash from input data to ensure uniqueness
        input_hash = hashlib.md5(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()
        
        return f"session_{input_hash}"

    async def create_context(
        self, 
        input_data: Dict[str, Any], 
        initial_metadata: Optional[Dict[str, Any]] = None
    ) -> ContextState:
        """
        Create a new context state
        
        Args:
            input_data: Initial input data
            initial_metadata: Optional initial metadata
        
        Returns:
            Created context state
        """
        async with self._lock:
            session_id = self._generate_session_id(input_data)
            
            context_state = ContextState(
                session_id=session_id,
                timestamp=asyncio.get_event_loop().time(),
                input_data=input_data,
                metadata=initial_metadata or {}
            )
            
            # Store context state
            self._context_history[session_id] = context_state
            
            # Manage history size
            if len(self._context_history) > self._max_history:
                oldest_key = min(
                    self._context_history, 
                    key=lambda k: self._context_history[k].timestamp
                )
                del self._context_history[oldest_key]
            
            return context_state

    async def update_context(
        self, 
        session_id: str, 
        module_name: str, 
        module_state: Dict[str, Any]
    ) -> ContextState:
        """
        Update context state for a specific module
        
        Args:
            session_id: Session identifier
            module_name: Name of the module updating context
            module_state: State data from the module
        
        Returns:
            Updated context state
        """
        async with self._lock:
            context_state = self._context_history.get(session_id)
            
            if not context_state:
                raise ValueError(f"No context found for session {session_id}")
            
            # Update module states
            context_state.module_states[module_name] = module_state
            context_state.timestamp = asyncio.get_event_loop().time()
            
            return context_state

    async def get_context(self, session_id: str) -> Optional[ContextState]:
        """
        Retrieve a specific context state
        
        Args:
            session_id: Session identifier to retrieve
        
        Returns:
            Context state or None if not found
        """
        async with self._lock:
            return self._context_history.get(session_id)

    async def analyze_context_evolution(self, session_id: str) -> Dict[str, Any]:
        """
        Analyze how context evolved through different modules
        
        Args:
            session_id: Session identifier to analyze
        
        Returns:
            Context evolution analysis
        """
        context_state = await self.get_context(session_id)
        
        if not context_state:
            return {}
        
        analysis = {
            'session_id': session_id,
            'initial_input': context_state.input_data,
            'module_progression': [],
            'total_modules_processed': len(context_state.module_states)
        }
        
        # Track progression of module states
        for module_name, module_state in context_state.module_states.items():
            analysis['module_progression'].append({
                'module': module_name,
                'state_changes': list(module_state.keys())
            })
        
        return analysis

# Singleton instance
context_manager = ContextManager()

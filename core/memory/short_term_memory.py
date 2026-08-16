"""
Short-term Memory - Session-based memory with TTL
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class ShortTermMemory:
    """
    Short-term memory with time-to-live (TTL) and size limits.
    """
    
    def __init__(self, max_items: int = 1000, ttl_hours: int = 24):
        """
        Initialize short-term memory.
        
        Args:
            max_items: Maximum number of items to store
            ttl_hours: Time-to-live in hours
        """
        self.max_items = max_items
        self.ttl_hours = ttl_hours
        self._memory: Dict[str, Dict] = {}
        
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Store a value in short-term memory.
        
        Args:
            key: Unique identifier
            value: Data to store
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        # Enforce size limit
        if len(self._memory) >= self.max_items:
            self._evict_oldest()
            
        self._memory[key] = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now(),
            "access_count": 0
        }
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from short-term memory.
        
        Args:
            key: Unique identifier
            
        Returns:
            Stored value or None if not found/expired
        """
        if key not in self._memory:
            return None
            
        memory = self._memory[key]
        
        # Check if expired
        if self._is_expired(memory):
            del self._memory[key]
            return None
            
        # Update access
        memory["access_count"] += 1
        memory["last_access"] = datetime.now()
        
        return memory["value"]
    
    def remove(self, key: str) -> bool:
        """
        Remove a specific key from memory.
        
        Args:
            key: Key to remove
            
        Returns:
            Success status
        """
        if key in self._memory:
            del self._memory[key]
            return True
        return False
    
    def get_old_memories(self, age_hours: int) -> List[Dict]:
        """
        Get memories older than specified age.
        
        Args:
            age_hours: Age threshold in hours
            
        Returns:
            List of old memory entries
        """
        threshold = datetime.now() - timedelta(hours=age_hours)
        old_memories = []
        
        for key, memory in self._memory.items():
            if memory["timestamp"] < threshold:
                old_memories.append({
                    "key": key,
                    "value": memory["value"],
                    "metadata": memory.get("metadata", {})
                })
                
        return old_memories
    
    def cleanup(self) -> int:
        """
        Remove expired memories.
        
        Returns:
            Number of memories removed
        """
        expired_keys = []
        
        for key, memory in self._memory.items():
            if self._is_expired(memory):
                expired_keys.append(key)
                
        for key in expired_keys:
            del self._memory[key]
            
        return len(expired_keys)
    
    def _is_expired(self, memory: Dict) -> bool:
        """Check if a memory entry is expired."""
        age = datetime.now() - memory["timestamp"]
        return age.total_seconds() > (self.ttl_hours * 3600)
    
    def _evict_oldest(self) -> None:
        """Evict the oldest memory entry."""
        if not self._memory:
            return
            
        oldest_key = min(
            self._memory.keys(),
            key=lambda k: self._memory[k]["timestamp"]
        )
        del self._memory[oldest_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_access = sum(m["access_count"] for m in self._memory.values())
        
        return {
            "total_items": len(self._memory),
            "max_items": self.max_items,
            "ttl_hours": self.ttl_hours,
            "total_accesses": total_access,
            "average_access": total_access / len(self._memory) if self._memory else 0
        }
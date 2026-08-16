"""
Memory System - Main orchestration of memory components
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .short_term_memory import ShortTermMemory
from .long_term_memory import LongTermMemory
from .vector_store import VectorStore


class MemorySystem:
    """
    Main memory system that coordinates short-term, long-term, and vector memory.
    """
    
    def __init__(self, storage_path: str = "./memory_data"):
        """
        Initialize the memory system.
        
        Args:
            storage_path: Path to store memory data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize memory components
        self.short_term = ShortTermMemory(max_items=1000, ttl_hours=24)
        self.long_term = LongTermMemory(
            db_path=str(self.storage_path / "long_term.db")
        )
        self.vector_store = VectorStore(
            db_path=str(self.storage_path / "vectors.db")
        )
        
    def store(self, key: str, value: Any, memory_type: str = "short_term", 
              metadata: Optional[Dict] = None) -> bool:
        """
        Store information in memory.
        
        Args:
            key: Unique identifier for the memory
            value: Data to store
            memory_type: "short_term", "long_term", or "both"
            metadata: Additional metadata for the memory
            
        Returns:
            Success status
        """
        try:
            if memory_type in ["short_term", "both"]:
                self.short_term.store(key, value, metadata)
                
            if memory_type in ["long_term", "both"]:
                self.long_term.store(key, value, metadata)
                
            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def retrieve(self, key: str, memory_type: str = "short_term") -> Optional[Any]:
        """
        Retrieve information from memory.
        
        Args:
            key: Unique identifier for the memory
            memory_type: "short_term", "long_term", or "both"
            
        Returns:
            Retrieved data or None if not found
        """
        if memory_type == "short_term":
            return self.short_term.retrieve(key)
        elif memory_type == "long_term":
            return self.long_term.retrieve(key)
        elif memory_type == "both":
            # Try short-term first, then long-term
            result = self.short_term.retrieve(key)
            if result is not None:
                return result
            return self.long_term.retrieve(key)
        return None
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search memory using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching memories with similarity scores
        """
        return self.vector_store.search(query, limit)
    
    def consolidate(self, age_hours: int = 12) -> int:
        """
        Consolidate old short-term memories into long-term storage.
        
        Args:
            age_hours: Age threshold for consolidation
            
        Returns:
            Number of memories consolidated
        """
        old_memories = self.short_term.get_old_memories(age_hours)
        count = 0
        
        for memory in old_memories:
            key = memory["key"]
            value = memory["value"]
            metadata = memory.get("metadata", {})
            
            # Store in long-term memory
            self.long_term.store(key, value, metadata)
            
            # Add to vector store for semantic search
            if isinstance(value, str):
                self.vector_store.add_document(key, value, metadata)
            
            # Remove from short-term
            self.short_term.remove(key)
            count += 1
            
        return count
    
    def cleanup(self) -> Dict[str, int]:
        """
        Clean up expired memories and optimize storage.
        
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            "short_term_cleaned": self.short_term.cleanup(),
            "long_term_cleaned": self.long_term.cleanup(),
            "vector_store_cleaned": self.vector_store.cleanup()
        }
        return stats
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        return {
            "short_term": self.short_term.get_stats(),
            "long_term": self.long_term.get_stats(),
            "vector_store": self.vector_store.get_stats()
        }
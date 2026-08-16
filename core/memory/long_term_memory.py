"""
Long-term Memory - Persistent storage with SQLite
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class LongTermMemory:
    """
    Long-term memory using SQLite for persistent storage.
    """
    
    def __init__(self, db_path: str = "./long_term_memory.db"):
        """
        Initialize long-term memory.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self) -> None:
        """Initialize the database schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON memories(created_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_access_count 
                ON memories(access_count)
            """)
            
            conn.commit()
    
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Store a value in long-term memory.
        
        Args:
            key: Unique identifier
            value: Data to store (will be JSON serialized)
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        try:
            value_json = json.dumps(value, default=str)
            metadata_json = json.dumps(metadata or {}, default=str)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO memories 
                    (key, value, metadata, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (key, value_json, metadata_json))
                conn.commit()
                
            return True
        except Exception as e:
            print(f"Error storing in long-term memory: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from long-term memory.
        
        Args:
            key: Unique identifier
            
        Returns:
            Stored value or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value, access_count FROM memories 
                    WHERE key = ?
                """, (key,))
                
                result = cursor.fetchone()
                if result:
                    # Update access count
                    cursor.execute("""
                        UPDATE memories 
                        SET access_count = access_count + 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE key = ?
                    """, (key,))
                    conn.commit()
                    
                    return json.loads(result[0])
                    
        except Exception as e:
            print(f"Error retrieving from long-term memory: {e}")
            
        return None
    
    def search_metadata(self, metadata_query: Dict) -> List[Dict]:
        """
        Search memories by metadata.
        
        Args:
            metadata_query: Dictionary of metadata key-value pairs to match
            
        Returns:
            List of matching memories
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value, metadata FROM memories")
                
                results = []
                for row in cursor.fetchall():
                    key, value, metadata = row
                    metadata_dict = json.loads(metadata)
                    
                    # Check if all query keys match
                    if all(
                        metadata_dict.get(k) == v 
                        for k, v in metadata_query.items()
                    ):
                        results.append({
                            "key": key,
                            "value": json.loads(value),
                            "metadata": metadata_dict
                        })
                        
                return results
                
        except Exception as e:
            print(f"Error searching metadata: {e}")
            return []
    
    def cleanup(self, age_days: int = 365) -> int:
        """
        Remove old memories.
        
        Args:
            age_days: Remove memories older than this
            
        Returns:
            Number of memories removed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM memories 
                    WHERE created_at < datetime('now', '-' || ? || ' days')
                """, (age_days,))
                
                deleted = cursor.rowcount
                conn.commit()
                
                return deleted
                
        except Exception as e:
            print(f"Error cleaning up long-term memory: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM memories")
                total = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(access_count) FROM memories")
                total_access = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT AVG(access_count) FROM memories
                """)
                avg_access = cursor.fetchone()[0] or 0
                
                return {
                    "total_memories": total,
                    "total_accesses": total_access,
                    "average_access": avg_access,
                    "db_path": self.db_path
                }
                
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"error": str(e)}
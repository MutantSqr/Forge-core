"""
Vector Store - Semantic search using vector embeddings
"""

import sqlite3
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class VectorStore:
    """
    Simple vector store for semantic search using SQLite.
    For production, consider using specialized vector databases like 
    pgvector, Milvus, or Pinecone.
    """
    
    def __init__(self, db_path: str = "./vectors.db"):
        """
        Initialize vector store.
        
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
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    key TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    vector_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_key 
                ON documents(key)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vector_hash 
                ON documents(vector_hash)
            """)
            
            # Full-text search for basic semantic matching
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts 
                USING fts5(content, key, content_rowid=documents.rowid)
            """)
            
            conn.commit()
    
    def _generate_vector_hash(self, text: str) -> str:
        """Generate a hash for text to simulate vector embedding."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def add_document(self, key: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a document to the vector store.
        
        Args:
            key: Unique identifier
            content: Document content
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        try:
            doc_id = hashlib.sha256(f"{key}_{content}".encode()).hexdigest()
            vector_hash = self._generate_vector_hash(content)
            metadata_json = json.dumps(metadata or {}, default=str)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO documents 
                    (id, key, content, metadata, vector_hash)
                    VALUES (?, ?, ?, ?, ?)
                """, (doc_id, key, content, metadata_json, vector_hash))
                
                # Update full-text search
                cursor.execute("""
                    INSERT OR REPLACE INTO documents_fts (rowid, content, key)
                    VALUES (last_insert_rowid(), ?, ?)
                """, (content, key))
                
                conn.commit()
                
            return True
        except Exception as e:
            print(f"Error adding document to vector store: {e}")
            return False
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search documents using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching documents with similarity scores
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Use full-text search for basic semantic matching
                cursor.execute("""
                    SELECT d.key, d.content, d.metadata, 
                          _bm25.documents_fts as score
                    FROM documents d
                    JOIN documents_fts fts ON d.rowid = fts.rowid
                    WHERE documents_fts MATCH ?
                    ORDER BY score
                    LIMIT ?
                """, (query, limit))
                
                results = []
                for row in cursor.fetchall():
                    key, content, metadata, score = row
                    results.append({
                        "key": key,
                        "content": content,
                        "metadata": json.loads(metadata),
                        "similarity_score": abs(score) if score else 0.0
                    })
                    
                return results
                
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    def keyword_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Simple keyword search fallback.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT key, content, metadata
                    FROM documents
                    WHERE content LIKE ? OR key LIKE ?
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
                
                results = []
                for row in cursor.fetchall():
                    key, content, metadata = row
                    results.append({
                        "key": key,
                        "content": content,
                        "metadata": json.loads(metadata),
                        "similarity_score": 0.5  # Default score for keyword match
                    })
                    
                return results
                
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []
    
    def get_document(self, key: str) -> Optional[Dict]:
        """
        Retrieve a document by key.
        
        Args:
            key: Document key
            
        Returns:
            Document or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT content, metadata FROM documents 
                    WHERE key = ?
                """, (key,))
                
                result = cursor.fetchone()
                if result:
                    content, metadata = result
                    return {
                        "key": key,
                        "content": content,
                        "metadata": json.loads(metadata)
                    }
                    
        except Exception as e:
            print(f"Error retrieving document: {e}")
            
        return None
    
    def delete_document(self, key: str) -> bool:
        """
        Delete a document by key.
        
        Args:
            key: Document key
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents WHERE key = ?", (key,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def cleanup(self, age_days: int = 365) -> int:
        """
        Remove old documents.
        
        Args:
            age_days: Remove documents older than this
            
        Returns:
            Number of documents removed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM documents 
                    WHERE created_at < datetime('now', '-' || ? || ' days')
                """, (age_days,))
                
                deleted = cursor.rowcount
                conn.commit()
                
                return deleted
                
        except Exception as e:
            print(f"Error cleaning up vector store: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM documents")
                total = cursor.fetchone()[0]
                
                return {
                    "total_documents": total,
                    "db_path": self.db_path
                }
                
        except Exception as e:
            print(f"Error getting vector store stats: {e}")
            return {"error": str(e)}
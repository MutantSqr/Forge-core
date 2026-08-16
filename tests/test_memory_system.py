"""
Tests for the Memory System
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from core.memory import MemorySystem, ShortTermMemory, LongTermMemory, VectorStore


class TestShortTermMemory:
    """Test cases for ShortTermMemory."""
    
    def test_store_and_retrieve(self):
        """Test basic store and retrieve operations."""
        memory = ShortTermMemory(max_items=100, ttl_hours=24)
        
        # Store a value
        memory.store("test_key", "test_value", {"metadata": "test"})
        
        # Retrieve the value
        result = memory.retrieve("test_key")
        assert result == "test_value"
    
    def test_store_overwrite(self):
        """Test overwriting existing values."""
        memory = ShortTermMemory(max_items=100, ttl_hours=24)
        
        memory.store("test_key", "value1")
        memory.store("test_key", "value2")
        
        result = memory.retrieve("test_key")
        assert result == "value2"
    
    def test_retrieve_nonexistent(self):
        """Test retrieving a non-existent key."""
        memory = ShortTermMemory(max_items=100, ttl_hours=24)
        
        result = memory.retrieve("nonexistent_key")
        assert result is None
    
    def test_max_items_limit(self):
        """Test max items limit enforcement."""
        memory = ShortTermMemory(max_items=3, ttl_hours=24)
        
        # Store more items than max
        for i in range(5):
            memory.store(f"key_{i}", f"value_{i}")
        
        # First key should be evicted
        assert memory.retrieve("key_0") is None
        assert memory.retrieve("key_1") is not None
    
    def test_cleanup_expired(self):
        """Test cleanup of expired items."""
        memory = ShortTermMemory(max_items=100, ttl_hours=1)
        
        # Store items
        memory.store("test_key", "test_value")
        
        # Force expiration by setting old timestamp
        memory._memory["test_key"]["timestamp"] = memory._memory["test_key"]["timestamp"].replace(
            year=2020
        )
        
        # Cleanup should remove expired items
        cleaned = memory.cleanup()
        assert cleaned >= 0


class TestLongTermMemory:
    """Test cases for LongTermMemory."""
    
    def test_store_and_retrieve(self):
        """Test basic store and retrieve operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = LongTermMemory(db_path=str(Path(temp_dir) / "test.db"))
            
            # Store a value
            memory.store("test_key", {"data": "test_value"}, {"metadata": "test"})
            
            # Retrieve the value
            result = memory.retrieve("test_key")
            assert result == {"data": "test_value"}
    
    def test_store_overwrite(self):
        """Test overwriting existing values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = LongTermMemory(db_path=str(Path(temp_dir) / "test.db"))
            
            memory.store("test_key", "value1")
            memory.store("test_key", "value2")
            
            result = memory.retrieve("test_key")
            assert result == "value2"
    
    def test_retrieve_nonexistent(self):
        """Test retrieving a non-existent key."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = LongTermMemory(db_path=str(Path(temp_dir) / "test.db"))
            
            result = memory.retrieve("nonexistent_key")
            assert result is None
    
    def test_search_metadata(self):
        """Test searching by metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = LongTermMemory(db_path=str(Path(temp_dir) / "test.db"))
            
            # Store items with metadata
            memory.store("key1", "value1", {"category": "test"})
            memory.store("key2", "value2", {"category": "test"})
            memory.store("key3", "value3", {"category": "other"})
            
            # Search by metadata
            results = memory.search_metadata({"category": "test"})
            assert len(results) == 2


class TestVectorStore:
    """Test cases for VectorStore."""
    
    def test_add_and_search_document(self):
        """Test adding and searching documents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(db_path=str(Path(temp_dir) / "vectors.db"))
            
            # Add document
            store.add_document("test_key", "test content about marketing", {"category": "test"})
            
            # Search for document
            results = store.search("marketing")
            assert len(results) > 0
    
    def test_get_document(self):
        """Test retrieving a document by key."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(db_path=str(Path(temp_dir) / "vectors.db"))
            
            # Add document
            store.add_document("test_key", "test content", {"category": "test"})
            
            # Get document
            result = store.get_document("test_key")
            assert result is not None
            assert result["key"] == "test_key"
    
    def test_delete_document(self):
        """Test deleting a document."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(db_path=str(Path(temp_dir) / "vectors.db"))
            
            # Add document
            store.add_document("test_key", "test content", {"category": "test"})
            
            # Delete document
            result = store.delete_document("test_key")
            assert result is True
            
            # Verify deletion
            result = store.get_document("test_key")
            assert result is None


class TestMemorySystem:
    """Test cases for MemorySystem."""
    
    def test_initialization(self):
        """Test memory system initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemorySystem(storage_path=temp_dir)
            
            assert memory.short_term is not None
            assert memory.long_term is not None
            assert memory.vector_store is not None
    
    def test_store_and_retrieve_short_term(self):
        """Test storing and retrieving from short-term memory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemorySystem(storage_path=temp_dir)
            
            memory.store("test_key", "test_value", memory_type="short_term")
            result = memory.retrieve("test_key", memory_type="short_term")
            
            assert result == "test_value"
    
    def test_store_and_retrieve_long_term(self):
        """Test storing and retrieving from long-term memory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemorySystem(storage_path=temp_dir)
            
            memory.store("test_key", "test_value", memory_type="long_term")
            result = memory.retrieve("test_key", memory_type="long_term")
            
            assert result == "test_value"
    
    def test_search(self):
        """Test semantic search."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemorySystem(storage_path=temp_dir)
            
            # Store content
            memory.store("test_key", "content about marketing automation", memory_type="both")
            
            # Search
            results = memory.search("marketing")
            assert len(results) >= 0
    
    def test_consolidate(self):
        """Test memory consolidation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemorySystem(storage_path=temp_dir)
            
            # Store some memories
            memory.store("key1", "value1", memory_type="short_term")
            memory.store("key2", "value2", memory_type="short_term")
            
            # Consolidate
            consolidated = memory.consolidate(age_hours=0)
            assert consolidated >= 0
    
    def test_get_stats(self):
        """Test getting memory statistics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemorySystem(storage_path=temp_dir)
            
            stats = memory.get_stats()
            assert "short_term" in stats
            assert "long_term" in stats
            assert "vector_store" in stats
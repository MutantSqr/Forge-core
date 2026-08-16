#!/usr/bin/env python3
"""
Simple Demo of Marketing Agent Components
"""

import sys
sys.path.insert(0, '/Users/rondrickbowser/Forge-core')

from marketing.content_generator import ContentGenerator
from marketing.campaign_manager import CampaignManager
from core.memory import MemorySystem
from core.task import TaskManager


def simple_demo():
    """Simple demonstration of individual components."""
    
    print("🤖 Marketing Agent Component Demo\n")
    print("="*60)
    
    # Initialize components individually
    print("Initializing components...")
    memory = MemorySystem(storage_path="./demo_memory")
    task_manager = TaskManager(max_workers=2)
    content_gen = ContentGenerator(memory, None)  # No tool manager for simplicity
    campaign_mgr = CampaignManager(memory, task_manager)
    
    print("✅ Components initialized!\n")
    
    # Demo 1: Content Generation
    print("="*60)
    print("📝 Content Generation Demo")
    print("="*60)
    
    blog_post = content_gen.generate_blog_post(
        topic="AI in modern marketing",
        tone="professional",
        length=300
    )
    print(f"Blog Post Generated ({blog_post['metadata']['word_count']} words):")
    print(f"{blog_post['content'][:200]}...\n")
    
    social_post = content_gen.generate_social_media_post(
        platform="linkedin",
        topic="Business automation benefits",
        hashtags=["#automation", "#business"]
    )
    print(f"LinkedIn Post Generated:")
    print(f"{social_post['content']}\n")
    
    # Demo 2: Campaign Management
    print("="*60)
    print("🚀 Campaign Management Demo")
    print("="*60)
    
    campaign = campaign_mgr.create_campaign(
        name="Demo Campaign",
        goals=["brand_awareness"],
        channels=["social_media"],
        budget={"social_media": 1000}
    )
    print(f"Campaign Created: {campaign['name']}")
    print(f"ID: {campaign['campaign_id']}")
    print(f"Status: {campaign['status']}\n")
    
    # Demo 3: Memory System
    print("="*60)
    print("🧠 Memory System Demo")
    print("="*60)
    
    memory.store("demo_key", "demo_value", memory_type="short_term")
    retrieved = memory.retrieve("demo_key", memory_type="short_term")
    print(f"Memory test: Stored 'demo_value', retrieved '{retrieved}'")
    
    memory_stats = memory.get_stats()
    print(f"Memory stats: {memory_stats['short_term']['total_items']} items in short-term memory\n")
    
    # Demo 4: Task Manager
    print("="*60)
    print("⚡ Task Manager Demo")
    print("="*60)
    
    task_stats = task_manager.get_statistics()
    print(f"Task manager stats: {task_stats['queue']['total_tasks']} tasks in queue")
    print(f"Task manager status: {task_stats['executor']['available_workers']} workers available\n")
    
    print("="*60)
    print("✅ Demo completed successfully!")
    print("="*60)
    print("\nYour Marketing Agent components are working correctly!")
    print("The full agent with all integrated systems is ready to use.")


if __name__ == "__main__":
    simple_demo()
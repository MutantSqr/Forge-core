#!/usr/bin/env python3
"""
Demo of Marketing Agent - Shows agent capabilities without interactive input
"""

import sys
sys.path.insert(0, '/Users/rondrickbowser/Forge-core')

from marketing import MarketingAgent


def demo_marketing_agent():
    """Demonstrate the marketing agent's capabilities."""
    
    print("🤖 Initializing Marketing Agent...")
    agent = MarketingAgent(
        config={
            "memory_path": "./marketing_memory",
            "module_path": "./marketing_modules",
            "max_workers": 4
        },
        enable_security=True,
        enable_auditing=True
    )
    print("✅ Marketing Agent is online and ready!\n")
    
    # Demo 1: Content Generation
    print("="*60)
    print("📝 DEMO 1: Content Generation")
    print("="*60)
    
    blog_post = agent.content_generator.generate_blog_post(
        topic="AI in modern marketing",
        tone="professional",
        length=500
    )
    print(f"Blog Post Generated:\n{blog_post['content'][:300]}...\n")
    print(f"Word count: {blog_post['metadata']['word_count']}\n")
    
    # Demo 2: Social Media Post
    social_post = agent.content_generator.generate_social_media_post(
        platform="linkedin",
        topic="Business automation benefits",
        hashtags=["#automation", "#business", "#efficiency"]
    )
    print(f"LinkedIn Post Generated:\n{social_post['content']}\n")
    
    # Demo 3: Campaign Creation
    print("="*60)
    print("🚀 DEMO 2: Campaign Management")
    print("="*60)
    
    campaign = agent.campaign_manager.create_campaign(
        name="Q4 Brand Awareness",
        goals=["increase_brand_recognition", "expand_reach"],
        channels=["social_media", "content_marketing", "email"],
        budget={"social_media": 5000, "content": 3000, "email": 2000}
    )
    print(f"Campaign Created: {campaign['name']}")
    print(f"Campaign ID: {campaign['campaign_id']}")
    print(f"Status: {campaign['status']}")
    print(f"Channels: {', '.join(campaign['channels'])}")
    print(f"Budget: ${sum(campaign['budget'].values()):,.2f}\n")
    
    # Demo 4: Marketing Strategy
    print("="*60)
    print("📊 DEMO 3: Marketing Strategy Planning")
    print("="*60)
    
    strategy = agent.plan_marketing_strategy(
        business_goals=["increase_brand_awareness", "generate_leads"],
        target_audience={"demographics": {"ages": [25, 35, 45], "locations": ["US", "UK"]}}
    )
    print(f"Strategy Goal: {strategy['goal']}")
    print(f"Reasoning Mode: {strategy['reasoning_mode']}")
    
    # Safely access plan data
    plan_data = strategy.get('plan', {})
    steps = plan_data.get('steps', [])
    print(f"Steps Planned: {len(steps)}")
    
    if steps:
        print("\nKey Steps:")
        for i, step in enumerate(steps[:3]):
            print(f"  {i+1}. {step.get('description', 'Unknown step')}")
    else:
        print("\nStrategy planning completed with detailed analysis")
    
    # Demo 5: Agent Status
    print("\n" + "="*60)
    print("🔧 DEMO 4: Agent Status")
    print("="*60)
    
    status = agent.get_agent_status()
    print(f"Memory System: {status['memory']['short_term']['total_items']} items in short-term memory")
    print(f"Reasoning Engine: {status['reasoning']['mode']} mode active")
    print(f"Task Manager: {status['tasks']['queue']['total_tasks']} tasks in queue")
    print(f"Tools Available: {status['tools']['registry']['total_tools']} tools registered")
    print(f"Active Modules: {status['modules']['active_modules']} modules running")
    print(f"Security: {'✅ Enabled' if status['security'].get('enabled', False) else '❌ Disabled'}")
    print(f"Auditing: {'✅ Enabled' if status['audit'].get('enabled', False) else '❌ Disabled'}")
    
    # Shutdown
    print("\n" + "="*60)
    print("👋 Demo completed! Shutting down agent...")
    print("="*60)
    agent.shutdown()
    print("✅ Agent shutdown complete")


if __name__ == "__main__":
    demo_marketing_agent()
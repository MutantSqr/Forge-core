#!/usr/bin/env python3
"""
Interactive Marketing Agent - CLI interface for conversational interaction
"""

import sys
import re
from typing import Dict, Any

# Add the current directory to path for imports
sys.path.insert(0, '/Users/rondrickbowser/Forge-core')

from marketing import MarketingAgent
from core.task import TaskPriority


class InteractiveMarketingAgent:
    """Interactive CLI interface for the Marketing Agent."""
    
    def __init__(self):
        """Initialize the interactive agent."""
        print("🤖 Initializing Marketing Agent...")
        self.agent = MarketingAgent(
            config={
                "memory_path": "./marketing_memory",
                "module_path": "./marketing_modules",
                "max_workers": 4
            },
            enable_security=True,
            enable_auditing=True
        )
        print("✅ Marketing Agent is online and ready!")
        print("\n" + "="*60)
        print("Welcome to your Marketing AI Assistant!")
        print("="*60)
        print("\nI can help you with:")
        print("• Marketing strategy planning")
        print("• Content generation (blogs, social media, emails)")
        print("• Campaign management and execution")
        print("• Audience analysis and segmentation")
        print("• Performance tracking and analytics")
        print("\nType 'help' for commands or just start talking!")
        print("-" * 60 + "\n")
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate response.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Agent's response
        """
        user_input = user_input.strip().lower()
        
        # Handle commands
        if user_input in ['help', 'commands', 'what can you do']:
            return self.get_help()
        elif user_input in ['status', 'how are you', 'agent status']:
            return self.get_status()
        elif user_input in ['quit', 'exit', 'bye']:
            return "goodbye"
        elif user_input in ['clear', 'reset']:
            return "clear"
        
        # Process marketing requests
        return self.process_marketing_request(user_input)
    
    def process_marketing_request(self, user_input: str) -> str:
        """Process marketing-related requests."""
        
        # Content generation requests
        if any(keyword in user_input for keyword in ['blog', 'article', 'post', 'write', 'create']):
            return self.handle_content_generation(user_input)
        
        # Campaign requests
        elif any(keyword in user_input for keyword in ['campaign', 'launch', 'create campaign']):
            return self.handle_campaign_request(user_input)
        
        # Strategy requests
        elif any(keyword in user_input for keyword in ['strategy', 'plan', 'marketing plan']):
            return self.handle_strategy_request(user_input)
        
        # Analytics requests
        elif any(keyword in user_input for keyword in ['analytics', 'performance', 'metrics', 'report']):
            return self.handle_analytics_request(user_input)
        
        # Audience requests
        elif any(keyword in user_input for keyword in ['audience', 'target', 'customers', 'segment']):
            return self.handle_audience_request(user_input)
        
        # General conversation
        else:
            return self.handle_general_conversation(user_input)
    
    def handle_content_generation(self, user_input: str) -> str:
        """Handle content generation requests."""
        # Extract topic from input
        topic = self.extract_topic(user_input)
        
        # Determine content type
        if 'social' in user_input or 'tweet' in user_input or 'linkedin' in user_input:
            platform = 'linkedin' if 'linkedin' in user_input else 'twitter'
            result = self.agent.content_generator.generate_social_media_post(
                platform=platform,
                topic=topic or "business automation",
                hashtags=["#marketing", "#business", "#AI"]
            )
            return f"📱 **Social Media Post Generated:**\n\n{result['content']}\n\n*Character count: {result['metadata']['character_count']}*"
        
        elif 'email' in user_input:
            result = self.agent.content_generator.generate_email_campaign(
                subject_type="benefit",
                recipient_data={"name": "Valued Customer", "company": "Your Company"},
                content=f"Special offer about {topic or 'our services'}"
            )
            return f"📧 **Email Campaign Generated:**\n\nSubject: {result['subject']}\n\n{result['content']}"
        
        else:  # Default to blog post
            result = self.agent.content_generator.generate_blog_post(
                topic=topic or "digital marketing trends",
                tone="professional",
                length=800
            )
            return f"📝 **Blog Post Generated:**\n\n{result['content']}\n\n*Word count: {result['metadata']['word_count']}*"
    
    def handle_campaign_request(self, user_input: str) -> str:
        """Handle campaign creation requests."""
        # Extract campaign name
        campaign_name = self.extract_campaign_name(user_input)
        
        result = self.agent.campaign_manager.create_campaign(
            name=campaign_name or "New Marketing Campaign",
            goals=["increase_brand_awareness", "generate_leads"],
            channels=["social_media", "email", "content"],
            budget={"social_media": 5000, "email": 2000, "content": 3000}
        )
        
        return f"🚀 **Campaign Created Successfully!**\n\n" \
               f"Campaign ID: {result['campaign_id']}\n" \
               f"Name: {result['name']}\n" \
               f"Status: {result['status']}\n" \
               f"Channels: {', '.join(result['channels'])}\n" \
               f"Budget: ${sum(result['budget'].values()):,.2f}\n\n" \
               f"Would you like me to launch this campaign? (yes/no)"
    
    def handle_strategy_request(self, user_input: str) -> str:
        """Handle marketing strategy requests."""
        # Extract goals from input
        goals = self.extract_goals(user_input)
        
        result = self.agent.plan_marketing_strategy(
            business_goals=goals or ["increase_brand_awareness", "generate_leads"],
            target_audience={"demographics": {"ages": [25, 35, 45], "locations": ["US", "UK"]}}
        )
        
        return f"📊 **Marketing Strategy Plan Generated:**\n\n" \
               f"Goal: {result['goal']}\n" \
               f"Reasoning Mode: {result['reasoning_mode']}\n" \
               f"Steps Planned: {len(result['plan']['steps'])}\n\n" \
               f"**Key Steps:**\n" + \
               "\n".join([f"{i+1}. {step['description']}" for i, step in enumerate(result['plan']['steps'][:5])]) + \
               f"\n\n**Recommendations:**\n" + \
               "\n".join([f"• {rec}" for rec in result['decisions'][:3]])
    
    def handle_analytics_request(self, user_input: str) -> str:
        """Handle analytics and performance requests."""
        insights = self.agent.get_marketing_insights(time_period="7d")
        
        return f"📈 **Marketing Performance Insights (Last 7 Days):**\n\n" \
               f"Content Performance: {insights['content_performance']}\n" \
               f"Campaign Performance: {insights['campaign_performance']}\n" \
               f"Audience Insights: {insights['audience_insights']}\n" \
               f"Overall Metrics: {insights['overall_metrics']}"
    
    def handle_audience_request(self, user_input: str) -> str:
        """Handle audience analysis requests."""
        # Sample audience data
        audience_data = {
            "demographics": {
                "ages": [25, 30, 35, 40, 45, 28, 32, 38],
                "genders": ["male", "female", "male", "female", "male", "female", "male", "female"],
                "locations": ["US", "UK", "US", "UK", "US", "UK", "US", "UK"]
            },
            "behavior": {
                "purchases": [{"value": 100}, {"value": 150}, {"value": 200}],
                "engagement": [{"type": "email"}, {"type": "social"}, {"type": "web"}]
            }
        }
        
        result = self.agent.audience_analyzer.analyze_audience(
            audience_data=audience_data,
            analysis_type="demographic"
        )
        
        return f"👥 **Audience Analysis Results:**\n\n" \
               f"Analysis Type: {result['analysis_type']}\n" \
               f"Age Distribution: {result['demographic_analysis']['age_distribution']}\n" \
               f"Gender Distribution: {result['demographic_analysis']['gender_distribution']}\n" \
               f"Key Insights: {len(result['insights'])} insights generated\n" \
               f"Recommendations: {len(result['recommendations'])} recommendations provided"
    
    def handle_general_conversation(self, user_input: str) -> str:
        """Handle general conversational input."""
        responses = [
            "I'd be happy to help with that! Could you tell me more about what specific marketing task you'd like me to assist with?",
            "That's interesting! To better assist you, are you looking for content creation, campaign management, or perhaps audience analysis?",
            "I can help with various marketing tasks. Would you like me to generate some content, analyze your audience, or create a marketing strategy?",
            "Great question! I specialize in marketing automation. What specific aspect would you like to explore - content, campaigns, analytics, or strategy?"
        ]
        
        import random
        return random.choice(responses)
    
    def extract_topic(self, text: str) -> str:
        """Extract topic from user input."""
        # Simple extraction - look for patterns like "about X", "on X", etc.
        patterns = [
            r'about\s+(.+?)(?:\s|$)',
            r'on\s+(.+?)(?:\s|$)',
            r'for\s+(.+?)(?:\s|$)',
            r'write\s+(.+?)(?:\s|$)',
            r'create\s+(.+?)(?:\s|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_campaign_name(self, text: str) -> str:
        """Extract campaign name from user input."""
        patterns = [
            r'campaign\s+(?:called\s+)?(.+?)(?:\s|$)',
            r'create\s+(?:a\s+)?campaign\s+(?:called\s+)?(.+?)(?:\s|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_goals(self, text: str) -> list:
        """Extract business goals from user input."""
        # Simple keyword matching for common goals
        goals = []
        
        if 'awareness' in text or 'brand' in text:
            goals.append("increase_brand_awareness")
        if 'lead' in text or 'generate' in text:
            goals.append("generate_leads")
        if 'sales' in text or 'revenue' in text:
            goals.append("increase_sales")
        if 'engagement' in text:
            goals.append("improve_engagement")
        
        return goals if goals else ["increase_brand_awareness", "generate_leads"]
    
    def get_help(self) -> str:
        """Get help information."""
        return """📚 **Available Commands:**

**Content Generation:**
• "Write a blog post about [topic]"
• "Create a social media post for [platform]"
• "Generate an email about [topic]"

**Campaign Management:**
• "Create a campaign called [name]"
• "Launch marketing campaign"
• "Set up campaign for [goal]"

**Strategy & Planning:**
• "Create a marketing strategy for [goals]"
• "Plan a campaign to [objective]"
• "Develop marketing approach"

**Analytics & Insights:**
• "Show me performance analytics"
• "Generate marketing report"
• "Analyze campaign performance"

**Audience Analysis:**
• "Analyze my target audience"
• "Segment audience by [criteria]"
• "Show audience insights"

**General:**
• "status" - Check agent status
• "help" - Show this help
• "quit" - Exit the conversation

**Tips:**
• Be specific about your goals and target audience
• Include platform names for social media content
• Mention time periods for analytics requests
"""
    
    def get_status(self) -> str:
        """Get agent status."""
        status = self.agent.get_agent_status()
        
        return f"🤖 **Agent Status:**\n\n" \
               f"Memory System: {status['memory']['short_term']['total_items']} items in short-term memory\n" \
               f"Reasoning Engine: {status['reasoning']['mode']} mode active\n" \
               f"Task Manager: {status['tasks']['queue']['total_tasks']} tasks in queue\n" \
               f"Tools Available: {status['tools']['registry']['total_tools']} tools registered\n" \
               f"Active Modules: {status['modules']['active_modules']} modules running\n" \
               f"Security: {'✅ Enabled' if status['security']['enabled'] else '❌ Disabled'}\n" \
               f"Auditing: {'✅ Enabled' if status['audit']['enabled'] else '❌ Disabled'}"
    
    def run(self):
        """Run the interactive agent."""
        print("Marketing Agent: How can I help you with your marketing today?\n")
        
        while True:
            try:
                user_input = input("You: ")
                
                if not user_input.strip():
                    continue
                
                response = self.process_input(user_input)
                
                if response == "goodbye":
                    print("\nMarketing Agent: Goodbye! It was great helping you with your marketing. 🚀")
                    self.agent.shutdown()
                    break
                
                elif response == "clear":
                    print("\n" + "="*60 + "\n")
                    continue
                
                print(f"\nMarketing Agent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nMarketing Agent: Goodbye! Shutting down gracefully... 👋")
                self.agent.shutdown()
                break
            except Exception as e:
                print(f"\nMarketing Agent: I encountered an error: {str(e)}\n")
                print("Let's try again. What else can I help you with?\n")


def main():
    """Main entry point."""
    agent = InteractiveMarketingAgent()
    agent.run()


if __name__ == "__main__":
    main()
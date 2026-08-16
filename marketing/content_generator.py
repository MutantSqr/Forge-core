"""
Content Generator - AI-powered content generation for marketing
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import random


class ContentGenerator:
    """
    AI-powered content generator for marketing materials.
    """
    
    def __init__(self, memory_system, tool_manager):
        """
        Initialize the content generator.
        
        Args:
            memory_system: Memory system instance
            tool_manager: Tool manager instance
        """
        self.memory = memory_system
        self.tool_manager = tool_manager
        self._content_templates = self._load_content_templates()
        self._performance_metrics = []
    
    def _load_content_templates(self) -> Dict[str, Dict]:
        """Load content generation templates."""
        return {
            "blog_post": {
                "structure": ["introduction", "key_points", "examples", "conclusion"],
                "tone_options": ["professional", "casual", "educational", "promotional"],
                "default_length": 1000
            },
            "social_media": {
                "platforms": ["twitter", "linkedin", "instagram", "facebook"],
                "engagement_hooks": ["question", "statistic", "story", "call_to_action"],
                "hashtag_suggestions": ["#marketing", "#business", "#growth", "#innovation"]
            },
            "email": {
                "subject_lines": ["question", "benefit", "urgency", "personalization"],
                "structure": ["subject", "greeting", "body", "call_to_action", "signature"],
                "personalization_fields": ["name", "company", "industry"]
            }
        }
    
    def generate_blog_post(self, topic: str, tone: str = "professional", 
                          length: int = 1000, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a blog post on a given topic.
        
        Args:
            topic: Blog post topic
            tone: Writing tone
            length: Target word count
            keywords: Keywords to include
            
        Returns:
            Generated blog post content
        """
        # Store generation request in memory
        self.memory.store(
            key=f"blog_generation_{datetime.now().isoformat()}",
            value={
                "topic": topic,
                "tone": tone,
                "length": length,
                "keywords": keywords
            },
            memory_type="short_term"
        )
        
        # Generate content (simplified - in real implementation, use AI model)
        content = self._generate_blog_content(topic, tone, length, keywords)
        
        # Track performance
        self._track_generation("blog_post", len(content.split()), len(content))
        
        return {
            "content": content,
            "metadata": {
                "topic": topic,
                "tone": tone,
                "word_count": len(content.split()),
                "character_count": len(content),
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def _generate_blog_content(self, topic: str, tone: str, length: int, 
                              keywords: Optional[List[str]]) -> str:
        """Generate blog post content (simplified implementation)."""
        # In a real implementation, this would use an AI model like GPT
        template = self._content_templates["blog_post"]
        
        content_parts = []
        
        # Introduction
        intro = f"In today's fast-paced business landscape, {topic} has become increasingly important. "
        if tone == "professional":
            intro += "This comprehensive guide explores the key aspects and implications."
        elif tone == "casual":
            intro += "Let's dive into what makes this topic so fascinating and relevant."
        else:
            intro += "Understanding this subject can provide valuable insights for your business."
        
        content_parts.append(intro)
        
        # Key points
        key_points = [
            f"First, consider the fundamental aspects of {topic}.",
            f"Second, examine how {topic} impacts your business operations.",
            f"Third, explore the best practices for implementing {topic} strategies.",
            f"Finally, measure the success of your {topic} initiatives."
        ]
        
        content_parts.extend(key_points)
        
        # Add keywords if provided
        if keywords:
            keyword_section = f"\nKey topics to consider include: {', '.join(keywords)}."
            content_parts.append(keyword_section)
        
        # Conclusion
        conclusion = f"\nIn conclusion, {topic} represents a significant opportunity for business growth. "
        conclusion += "By following the strategies outlined above, you can effectively leverage this approach."
        
        content_parts.append(conclusion)
        
        full_content = " ".join(content_parts)
        
        # Adjust length (simplified)
        target_words = length
        current_words = len(full_content.split())
        
        if current_words < target_words:
            # Add more content to reach target length
            additional_content = self._generate_expansion_content(topic, target_words - current_words)
            full_content += " " + additional_content
        
        return full_content
    
    def _generate_expansion_content(self, topic: str, additional_words: int) -> str:
        """Generate additional content to reach target length."""
        expansion_phrases = [
            f"Furthermore, when considering {topic}, it's essential to think about long-term implications.",
            f"Additionally, many industry experts emphasize the importance of {topic} in modern business.",
            f"Research shows that organizations focusing on {topic} tend to outperform their competitors.",
            f"It's worth noting that {topic} continues to evolve with new technologies and methodologies.",
            f"Finally, staying updated with {topic} trends can give your business a competitive edge."
        ]
        
        additional_content = ""
        words_added = 0
        
        while words_added < additional_words:
            phrase = random.choice(expansion_phrases)
            additional_content += " " + phrase
            words_added += len(phrase.split())
        
        return additional_content
    
    def generate_social_media_post(self, platform: str, topic: str, 
                                  hashtags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a social media post.
        
        Args:
            platform: Social media platform
            topic: Post topic
            hashtags: Hashtags to include
            
        Returns:
            Generated social media post
        """
        # Store generation request
        self.memory.store(
            key=f"social_generation_{datetime.now().isoformat()}",
            value={
                "platform": platform,
                "topic": topic,
                "hashtags": hashtags
            },
            memory_type="short_term"
        )
        
        # Generate content
        content = self._generate_social_content(platform, topic, hashtags)
        
        # Track performance
        self._track_generation("social_media", len(content.split()), len(content))
        
        return {
            "content": content,
            "metadata": {
                "platform": platform,
                "topic": topic,
                "character_count": len(content),
                "hashtag_count": len(hashtags) if hashtags else 0,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def _generate_social_content(self, platform: str, topic: str, 
                               hashtags: Optional[List[str]]) -> str:
        """Generate social media content."""
        platform_configs = {
            "twitter": {"max_length": 280, "style": "concise"},
            "linkedin": {"max_length": 3000, "style": "professional"},
            "instagram": {"max_length": 2200, "style": "visual"},
            "facebook": {"max_length": 63206, "style": "engaging"}
        }
        
        config = platform_configs.get(platform, platform_configs["twitter"])
        
        # Generate hook
        hooks = [
            f"🚀 Exciting news about {topic}!",
            f"Have you considered the impact of {topic}?",
            f"Here's what you need to know about {topic}:",
            f"Transform your approach to {topic} with these insights:"
        ]
        
        content = random.choice(hooks) + "\n\n"
        
        # Add value
        content += f"{topic} is revolutionizing how businesses operate. "
        content += "Don't miss out on these key insights and strategies.\n\n"
        
        # Add call to action
        content += "💡 What's your experience with this? Share in the comments!\n\n"
        
        # Add hashtags
        if hashtags:
            tag_string = " ".join([f"#{tag}" if not tag.startswith("#") else tag for tag in hashtags])
        else:
            tag_string = " ".join(self._content_templates["social_media"]["hashtag_suggestions"])
        
        content += tag_string
        
        # Trim to platform limit
        if len(content) > config["max_length"]:
            content = content[:config["max_length"]-3] + "..."
        
        return content
    
    def generate_email_campaign(self, subject_type: str, recipient_data: Dict[str, Any],
                             content: str) -> Dict[str, Any]:
        """
        Generate an email campaign.
        
        Args:
            subject_type: Type of subject line
            recipient_data: Recipient information
            content: Email body content
            
        Returns:
            Generated email campaign
        """
        # Generate subject line
        subject = self._generate_subject_line(subject_type, recipient_data)
        
        # Personalize content
        personalized_content = self._personalize_content(content, recipient_data)
        
        return {
            "subject": subject,
            "content": personalized_content,
            "recipient": recipient_data.get("email", ""),
            "metadata": {
                "subject_type": subject_type,
                "personalization_fields": list(recipient_data.keys()),
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def _generate_subject_line(self, subject_type: str, recipient_data: Dict[str, Any]) -> str:
        """Generate email subject line."""
        templates = {
            "question": f"Have you considered {recipient_data.get('company', 'your business')}?",
            "benefit": f"Unlock new opportunities for {recipient_data.get('name', 'your business')}",
            "urgency": f"Last chance: Limited time offer for {recipient_data.get('name', 'you')}",
            "personalization": f"Personalized insights for {recipient_data.get('name', 'you')}"
        }
        
        return templates.get(subject_type, "Important information for your business")
    
    def _personalize_content(self, content: str, recipient_data: Dict[str, Any]) -> str:
        """Personalize email content."""
        personalized = content
        
        for field, value in recipient_data.items():
            placeholder = f"{{{field}}}"
            if placeholder in personalized:
                personalized = personalized.replace(placeholder, str(value))
        
        return personalized
    
    def _track_generation(self, content_type: str, word_count: int, char_count: int) -> None:
        """Track content generation performance."""
        metric = {
            "content_type": content_type,
            "word_count": word_count,
            "char_count": char_count,
            "timestamp": datetime.now().isoformat()
        }
        
        self._performance_metrics.append(metric)
        
        # Keep metrics manageable
        if len(self._performance_metrics) > 1000:
            self._performance_metrics = self._performance_metrics[-500]
    
    def get_performance_metrics(self, time_period: str = "7d") -> Dict[str, Any]:
        """
        Get content generation performance metrics.
        
        Args:
            time_period: Time period for metrics
            
        Returns:
            Performance metrics
        """
        # Filter metrics by time period (simplified)
        recent_metrics = self._performance_metrics[-100:]  # Last 100 generations
        
        if not recent_metrics:
            return {"message": "No performance data available"}
        
        # Calculate statistics
        total_generations = len(recent_metrics)
        avg_word_count = sum(m["word_count"] for m in recent_metrics) / total_generations
        avg_char_count = sum(m["char_count"] for m in recent_metrics) / total_generations
        
        # Count by content type
        content_type_counts = {}
        for metric in recent_metrics:
            content_type = metric["content_type"]
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        return {
            "time_period": time_period,
            "total_generations": total_generations,
            "average_word_count": avg_word_count,
            "average_character_count": avg_char_count,
            "content_type_breakdown": content_type_counts
        }
    
    def generate_content(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic content generation method.
        
        Args:
            parameters: Generation parameters
            
        Returns:
            Generated content
        """
        content_type = parameters.get("content_type", "blog_post")
        
        if content_type == "blog_post":
            return self.generate_blog_post(
                topic=parameters.get("topic", ""),
                tone=parameters.get("tone", "professional"),
                length=parameters.get("length", 1000),
                keywords=parameters.get("keywords")
            )
        elif content_type == "social_media":
            return self.generate_social_media_post(
                platform=parameters.get("platform", "twitter"),
                topic=parameters.get("topic", ""),
                hashtags=parameters.get("hashtags")
            )
        elif content_type == "email":
            return self.generate_email_campaign(
                subject_type=parameters.get("subject_type", "benefit"),
                recipient_data=parameters.get("recipient_data", {}),
                content=parameters.get("content", "")
            )
        else:
            return {"error": f"Unknown content type: {content_type}"}
"""
Caption Service for StoicAlgo
Builds Instagram captions with genuine insight, not generic motivation.
"""

import random
from typing import Dict, List
from scripts.logger import get_logger
from scripts.utils import load_settings, truncate_text

logger = get_logger("CaptionService")


class CaptionService:
    """Service for building compelling Instagram captions."""
    
    def __init__(self):
        self.settings = load_settings()
        self.max_length = self.settings['instagram'].get('max_caption_length', 2200)
        self.hashtag_count = self.settings['instagram'].get('hashtag_count', 20)
    
    def build_caption(self, content: Dict) -> str:
        """Build a caption that extends the insight, not repeats it."""
        
        quote = content.get('quote', '')
        author = content.get('author', '')
        interpretation = content.get('interpretation', '')
        technical_insight = content.get('technical_insight', '')
        applications = content.get('practical_applications', [])
        
        sections = []
        
        # Opening hook - the quote
        quote_section = f'"{quote}"\n— {author}'
        sections.append(quote_section)
        
        # The insight layer - extend, don't explain
        if interpretation:
            sections.append(interpretation)
        
        # The leverage - specific and technical
        if technical_insight:
            sections.append(f"⚡ {technical_insight}")
        
        # The playbook - grey-hat tactics
        if applications:
            app_text = "The play:\n"
            for app in applications[:3]:
                app_text += f"→ {app}\n"
            sections.append(app_text.strip())
        
        # Closing hook
        closers = [
            "Save this. You'll need it.",
            "Screenshot this before it clicks.",
            "The game rewards those who see it.",
            "Most won't act on this. That's the advantage.",
            "Information asymmetry is the only real edge.",
            "Now you know. What you do with it is on you.",
            "While they scroll, you strategize.",
            "This is the part they don't teach.",
        ]
        sections.append(random.choice(closers))
        
        caption_body = "\n\n".join(sections)
        
        # Hashtags - strategic, not spammy
        hashtags = self._generate_hashtags(content)
        hashtag_text = " ".join(hashtags)
        
        full_caption = f"{caption_body}\n\n.\n.\n.\n{hashtag_text}"
        
        if len(full_caption) > self.max_length:
            available_space = self.max_length - len(hashtag_text) - 20
            caption_body = truncate_text(caption_body, available_space)
            full_caption = f"{caption_body}\n\n.\n.\n.\n{hashtag_text}"
        
        logger.info(f"Built caption: {len(full_caption)} characters")
        return full_caption
    
    def _generate_hashtags(self, content: Dict) -> List[str]:
        """Generate strategic hashtags."""
        
        # Power/Strategy hashtags
        power_tags = [
            "#48lawsofpower",
            "#powerplays", 
            "#strategy",
            "#leverage",
            "#darkpsychology",
            "#manipulation",
            "#influence",
            "#powerdynamics",
            "#machiavelli",
            "#theprince"
        ]
        
        # Tech/Wealth hashtags  
        tech_tags = [
            "#aitools",
            "#automation",
            "#passiveincome",
            "#systemsthinking",
            "#buildinpublic",
            "#techstartup",
            "#sidehustle",
            "#wealthbuilding",
            "#entrepreneurmindset",
            "#financialfreedom"
        ]
        
        # Philosophy hashtags
        philosophy_tags = [
            "#stoicism",
            "#stoic",
            "#philosophy",
            "#wisdom",
            "#ancientwisdom",
            "#mentalmodels",
            "#criticalthinking",
            "#selfmastery"
        ]
        
        # Growth/Viral hashtags
        growth_tags = [
            "#reels",
            "#explorepage",
            "#mindset",
            "#growthmindset",
            "#successmindset",
            "#highvalue",
            "#selfimprovement",
            "#leveling"
        ]
        
        # Author hashtag
        author = content.get('author', '').lower().replace(' ', '').replace('(', '').replace(')', '')
        author_tag = f"#{author}" if author else ""
        
        # Combine strategically
        selected = []
        selected.extend(random.sample(power_tags, 4))
        selected.extend(random.sample(tech_tags, 4))
        selected.extend(random.sample(philosophy_tags, 3))
        selected.extend(random.sample(growth_tags, 4))
        if author_tag:
            selected.append(author_tag)
        
        # Dedupe and limit
        selected = list(dict.fromkeys(selected))[:self.hashtag_count]
        
        return selected


def build_caption(content: Dict) -> str:
    """Convenience function to build caption."""
    service = CaptionService()
    return service.build_caption(content)


if __name__ == "__main__":
    test_content = {
        "quote": "Your network isn't your net worth—it's your surveillance system.",
        "author": "Robert Greene",
        "interpretation": "Every connection is an information node. The question isn't who you know—it's what you know about who you know, and what they know about you.",
        "technical_insight": "CRM + AI sentiment analysis on communications = knowing who's loyal before they prove it. Most still use spreadsheets.",
        "practical_applications": [
            "Map your network's incentive structures. Who benefits from your failure?",
            "Automate relationship maintenance with scheduled, personalized touchpoints",
            "Build information asymmetry: know more about them than they know about you"
        ],
        "mood": "calculated"
    }
    
    service = CaptionService()
    print("=== Full Caption ===")
    caption = service.build_caption(test_content)
    print(caption)
    print(f"\nLength: {len(caption)} characters")

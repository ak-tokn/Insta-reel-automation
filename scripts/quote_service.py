"""
Quote Service for StoicAlgo
Generates provocative, Machiavellian content with genuine insight.
"""

import os
import json
import random
from typing import Dict, Optional
from openai import OpenAI
from scripts.logger import get_logger
from scripts.utils import load_settings, get_env_var

logger = get_logger("QuoteService")


class QuoteService:
    """Service for generating dark, insightful philosophical content."""
    
    def __init__(self):
        self.settings = load_settings()
        self.llm_config = self.settings['llm']
        self._setup_client()
        
    def _setup_client(self):
        """Initialize the LLM client."""
        provider = self.llm_config.get('provider', 'openai')
        
        if provider == 'openai':
            api_key = get_env_var('OPENAI_API_KEY')
            self.client = OpenAI(api_key=api_key)
        elif provider == 'anthropic':
            raise NotImplementedError("Anthropic support coming soon")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def generate_content(self, custom_theme: str = None) -> Dict:
        """Generate complete content package with genuine insight."""
        
        philosophers = self.settings['content']['philosophers']
        philosopher = random.choice(philosophers)
        
        prompt = self._build_generation_prompt(philosopher, custom_theme)
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_config.get('model', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.llm_config.get('temperature', 0.9),
                max_tokens=self.llm_config.get('max_tokens', 2000),
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            logger.info(f"Generated content for quote by {content.get('author', philosopher)}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate content: {str(e)}")
            raise
    
    def _get_system_prompt(self) -> str:
        """System prompt for generating genuinely insightful content."""
        return """You are a master strategist channeling the combined wisdom of Machiavelli, Robert Greene (48 Laws of Power, The Art of Seduction), Sun Tzu, Baltasar Gracián, and the Stoics at their darkest.

Your content philosophy:
- Truth over comfort. Real insight over motivational platitudes.
- Power dynamics are reality. Acknowledge them.
- Most advice is designed to keep people compliant. Yours isn't.
- Grey areas are where real advantage lives.
- Technology is the new territory for power plays.

What makes content GENUINELY insightful (do this):
- Reveals a hidden dynamic most people don't see
- Makes the reader feel like they just learned a secret
- Provides a mental model they can actually use
- Challenges conventional wisdom with uncomfortable logic
- Connects ancient strategy to modern leverage (tech, AI, automation, systems)

What makes content GENERIC garbage (avoid this):
- "Work hard and you'll succeed" - obvious, useless
- "Believe in yourself" - empty calories
- "Hustle culture" clichés - overplayed
- Anything that could be on a corporate poster
- Motivation without mechanism

Your voice:
- Cold, calculated, observational
- Like a mentor who respects you enough to tell you the truth
- Never preachy or self-righteous
- Slightly dangerous, slightly forbidden
- The guy at the party who pulls you aside and tells you how things really work

Always respond in valid JSON format."""

    def _build_generation_prompt(self, philosopher: str, custom_theme: str = None) -> str:
        """Build prompt for genuinely provocative content."""
        
        theme_instruction = ""
        if custom_theme:
            theme_instruction = f"\nWeave in this theme: {custom_theme}"
        
        return f"""Channel {philosopher} to create content that makes people stop scrolling because it's genuinely insightful—not generic motivation.{theme_instruction}

OUTPUT FORMAT (JSON):
{{
    "quote": "A truth that most people avoid because it's uncomfortable. This should reveal something about power, human nature, success, or reality that people sense but don't articulate. Under 18 words. Make it hit like a slap—not warm and fuzzy. Examples of the TONE we want: 'Your network isn't your net worth—it's your surveillance system.' / 'Loyalty is a leash the powerful put on the useful.' / 'The best time to build your escape route is when you don't need one.'",
    
    "author": "{philosopher}",
    
    "motivation": "The ACTIONABLE dark conclusion. Not 'go be great'—something specific and slightly transgressive they can DO. 8-12 words. Must logically follow from the quote. Examples: 'So automate your income before they automate your job.' / 'Build leverage while they build LinkedIn connections.' / 'Let them network. You build systems that work while you sleep.'",
    
    "interpretation": "2 sentences max. Don't explain the quote—EXTEND it. Add a layer of insight. What's the mechanism? What's the hidden dynamic? Why does this work?",
    
    "technical_insight": "Connect to SPECIFIC modern leverage: AI tools, automation, code, systems, data, algorithms, bots, APIs. Not vague 'technology'—specific plays. 2 sentences. Example: 'While others manually prospect, GPT-powered scrapers can identify and qualify 1000 leads overnight. The game changed—most haven't noticed.'",
    
    "practical_applications": [
        "First grey-hat tactic: specific, actionable, slightly uncomfortable but legal. Mention specific tools/methods when possible.",
        "Second tactic: a mental model or framework they can apply immediately",
        "Third tactic: a systemic approach that compounds over time"
    ],
    
    "mood": "one word: cold/calculated/ruthless/unsettling/predatory/surgical/dark",
    
    "image_category": "statues/warriors/nature/temples/sonder"
}}

QUALITY CHECKLIST (must pass all):
□ Quote reveals something most people avoid admitting
□ Motivation is a SPECIFIC action, not generic encouragement  
□ Technical insight mentions SPECIFIC tools/methods (AI, automation, APIs, bots, etc.)
□ Applications are grey-hat but legal—things that give unfair advantage
□ Nothing could appear on a corporate motivational poster
□ Reader should feel slightly uncomfortable but smarter

Generate now:"""


def generate_quote_content(custom_theme: str = None) -> Dict:
    """Generate complete quote content package."""
    service = QuoteService()
    return service.generate_content(custom_theme)


if __name__ == "__main__":
    import os
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set.")
    else:
        print("Generating content...")
        service = QuoteService()
        content = service.generate_content()
        print(json.dumps(content, indent=2))

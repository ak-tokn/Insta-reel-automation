"""
Daily Ai'ds Service for StoicAlgo
Generates AI-powered money-making ideas for carousel posts.
"""

import os
import json
import random
from typing import Dict, List, Optional
from openai import OpenAI
from scripts.logger import get_logger
from scripts.utils import load_settings, get_env_var

logger = get_logger("DailyAidService")


class DailyAidService:
    """Service for generating Daily Ai'ds content - sophisticated AI business ideas."""
    
    def __init__(self):
        self.settings = load_settings()
        self.daily_aids_config = self.settings.get('daily_aids', {})
        self.llm_config = self.daily_aids_config.get('llm', self.settings['llm'])
        self._setup_client()
        
    def _setup_client(self):
        """Initialize the OpenAI client."""
        api_key = get_env_var('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
    
    def generate_idea(self, idea_number: int) -> Dict:
        """Generate a complete Daily Ai'ds idea package."""
        
        prompt = self._build_generation_prompt(idea_number)
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_config.get('model', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.llm_config.get('temperature', 0.85),
                max_tokens=self.llm_config.get('max_tokens', 3000),
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            
            if not self._validate_response(content):
                raise ValueError("Invalid response structure from LLM")
            
            content['idea_number'] = idea_number
            logger.info(f"Generated Daily Ai'ds #{idea_number}: {content.get('title', 'Unknown')}")
            return content
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate Daily Ai'ds content: {str(e)}")
            raise
    
    def _validate_response(self, content: Dict) -> bool:
        """Validate the LLM response has all required fields."""
        required_fields = ['title', 'summary', 'steps', 'kickoff_prompt', 'hook']
        
        for field in required_fields:
            if field not in content:
                logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(content['steps'], list):
            logger.error("Steps must be a list")
            return False
        
        min_steps = self.daily_aids_config.get('carousel', {}).get('min_steps', 5)
        max_steps = self.daily_aids_config.get('carousel', {}).get('max_steps', 10)
        
        if len(content['steps']) < min_steps or len(content['steps']) > max_steps:
            logger.warning(f"Steps count {len(content['steps'])} outside range {min_steps}-{max_steps}")
        
        return True
    
    def _get_system_prompt(self) -> str:
        """System prompt for generating Daily Ai'ds content."""
        return """You are a genius tech entrepreneur and growth hacker who sees opportunities others miss. You combine:
- Deep technical knowledge of AI tools (ChatGPT, Claude, Midjourney, Runway, ElevenLabs, etc.)
- Understanding of online monetization (SaaS, content, freelancing, automation, arbitrage)
- Grey-hat marketing tactics that push boundaries but stay legal
- Knowledge of what's trending and what people will pay for

Your ideas should be:
- SPECIFIC and ACTIONABLE - not vague "start a business" advice
- MODERN - leveraging the latest AI tools and platforms
- ENTICING - making people feel like they just discovered a cheat code
- REALISTIC - actually achievable by a motivated person with a laptop
- GREY-HAT - clever, borderline, but legal. The kind of thing most people don't know you can do.

Categories to explore:
- AI automation services for businesses
- Content creation at scale (faceless YouTube, AI blogs, social media)
- Digital products and templates
- Freelance services with AI leverage
- Arbitrage opportunities (pricing, attention, information)
- Micro-SaaS and tool building
- AI-enhanced consulting
- Data and research services
- Creative services at scale

Avoid:
- Dropshipping (oversaturated)
- Generic "start a course" advice
- Crypto/NFT schemes
- Anything requiring significant capital
- MLM or referral schemes

Always respond in valid JSON format."""

    def _build_generation_prompt(self, idea_number: int) -> str:
        """Build the prompt for generating a Daily Ai'ds idea."""
        
        idea_themes = [
            "AI content automation that prints money while you sleep",
            "Freelance services turbocharged by AI (charge premium, deliver fast)",
            "Digital products that AI helps you create once and sell forever",
            "Information arbitrage using AI research and synthesis",
            "AI-powered lead generation and outreach machines",
            "Niche SaaS tools that solve painful problems",
            "AI consulting for industries that don't know what hit them",
            "Faceless content empires built on AI workflows",
            "Automation services for small businesses (charge monthly)",
            "AI-enhanced creative services (design, video, copy)"
        ]
        
        selected_theme = random.choice(idea_themes)
        
        return f"""Generate Daily Ai'ds #{idea_number}

Theme direction (interpret creatively): {selected_theme}

Create a sophisticated, grey-hat, money-making idea that uses AI and online tools.

OUTPUT FORMAT (JSON):
{{
    "title": "DESCRIPTIVE action-based title that clearly explains what you're building and selling. NOT vague or cheesy marketing speak. Examples of GOOD titles: 'Selling AI-Made Resume Templates', 'Offering AI Video Editing Services', 'Building Custom ChatGPT Bots for Businesses'. Examples of BAD titles: 'Template Empire', 'Cash Machine', 'Money Printer', 'Digital Goldmine'. The title should tell someone EXACTLY what they will be doing.",
    
    "income_method": "Short phrase describing HOW the money is made (e.g., 'selling templates on Etsy', 'charging $500/month per client', 'flipping designs on Creative Market'). Be specific about WHERE the money comes from.",
    
    "summary": "One compelling sentence (under 20 words) that makes this sound irresistible. Hook them.",
    
    "hook": "A provocative one-liner for social media (under 15 words) - the kind that makes people screenshot",
    
    "steps": [
        {{
            "number": 1,
            "title": "Short step title (3-5 words)",
            "description": "SPECIFIC and ACTIONABLE. Name exact tools (e.g., 'Open Canva.com and use their resume template section', 'Go to Upwork.com and create a profile'). Make it sound EASY and MOTIVATING. Avoid vague phrases like 'research trends' or 'identify your niche' - instead say exactly HOW to do it with specific tools and websites."
        }},
        // ... 5-8 more steps
    ],
    
    "tools_mentioned": ["List", "of", "specific", "tools", "mentioned"],
    
    "monthly_income": "Just the amount like '$500-2000/mo' or '$1000-3000/mo' - keep it short",
    
    "difficulty": "beginner/intermediate/advanced",
    
    "time_to_first_dollar": "Realistic timeframe like '1-2 weeks' or '3-5 days'",
    
    "kickoff_prompt": "A detailed prompt (150-300 words) that someone can paste into ChatGPT or Claude to get started on implementing this idea. This should be specific and actionable - helping them research, plan, or create the first deliverable. Include what to ask the AI to do step-by-step."
}}

CRITICAL RULES:
1. TITLE must clearly describe what they're DOING and SELLING - no vague buzzwords
2. STEPS must mention SPECIFIC websites and tools by name (Canva, Fiverr, Gumroad, Notion, etc.)
3. STEPS should sound EASY and EXCITING - not like homework
4. Never use phrases like "research your niche" or "identify trends" without explaining HOW
5. Each step should feel like "oh that's simple, I can do that right now"

Generate now:"""


def generate_daily_aid(idea_number: int) -> Dict:
    """Generate a complete Daily Ai'ds idea package."""
    service = DailyAidService()
    return service.generate_idea(idea_number)


if __name__ == "__main__":
    if not os.environ.get('OPENAI_API_KEY'):
        print("OPENAI_API_KEY not set.")
    else:
        print("Generating Daily Ai'ds idea...")
        idea = generate_daily_aid(1)
        print(json.dumps(idea, indent=2))

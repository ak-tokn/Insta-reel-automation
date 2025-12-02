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
        return """You are a senior software architect and indie hacker who builds real, profitable projects. You think like a lead engineer delivering a shippable MVP.

REVENUE REASONING (MANDATORY):
Before providing ANY income estimate, you MUST mentally calculate:
1. Addressable market size (how many potential customers exist?)
2. Realistic pricing (what do similar services charge?)
3. Conversion rate (what % of leads become paying customers?)
4. Time investment (hours per week to maintain?)
5. Competition (how saturated is this space?)

NEVER use generic ranges like "$1000-3000/mo". Each project has unique economics:
- A niche Notion template might make $50-200/mo
- A productized AI service for agencies could make $3000-8000/mo
- A simple automation script sold on Gumroad might make $100-400/mo
- A white-label SaaS for a specific industry could make $5000-15000/mo

IMPLEMENTATION PHASES:
Think like an engineer breaking down a project. Each phase should be:
- A discrete deliverable (something you can "ship")
- Specific about WHAT to build and HOW
- Include actual technical details (frameworks, APIs, databases)
- Ordered logically (setup → core → polish → launch → scale)

Example good phases:
- "Set up Next.js project with Supabase auth and Stripe billing"
- "Build content generation pipeline using OpenAI API with rate limiting"
- "Create admin dashboard for managing client accounts"

Example BAD phases:
- "Research your niche" (too vague)
- "Leverage AI for content" (means nothing)
- "Scale your business" (not actionable)

AUTOMATION OPPORTUNITIES:
Identify where MCPs (Model Context Protocol), plugins, or automation tools could supercharge the project:
- Replit MCP for code generation/deployment
- Zapier/Make.com for workflow automation
- Perplexity MCP for real-time research
- Browser automation (Playwright, Puppeteer)
- Notion API, Airtable API, etc.

Only include "extra_credit" when there's a genuine automation opportunity.

Categories to explore:
- AI automation services for businesses
- Content creation at scale (faceless YouTube, AI blogs)
- Digital products and templates
- Freelance services with AI leverage
- Micro-SaaS and tool building
- AI-enhanced consulting
- Data and research services

Avoid: Dropshipping, generic courses, crypto/NFT, high capital requirements, MLM.

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

Create a sophisticated, real-world money-making project that uses AI tools.

OUTPUT FORMAT (JSON):
{{
    "title": "DESCRIPTIVE action-based title that clearly explains what you're building. Examples: 'Building an AI Resume Review SaaS', 'Creating a Faceless TikTok Automation Pipeline', 'Selling White-Label ChatGPT Integrations to Agencies'. NO vague titles like 'Money Machine' or 'Digital Empire'.",
    
    "income_method": "Descriptive explanation of the revenue model (1-2 sentences). Explain the pricing structure and customer acquisition. Example: 'Charge small businesses $99/month for automated email sequences. Target local service providers through LinkedIn outreach.' or 'Sell template packs on Gumroad for $15-30 each. Drive traffic through TikTok tutorials showing the templates in action.'",
    
    "summary": "One compelling sentence (under 20 words) that hooks them.",
    
    "hook": "A provocative one-liner for social media (under 15 words)",
    
    "revenue": {{
        "estimate": "The realistic monthly income like '$200-600/mo' or '$2000-4000/mo' - MUST be specific to THIS project",
        "assumptions": "Brief explanation of how you calculated this (e.g., '10 clients at $50/mo each' or '200 template sales at $15 each')"
    }},
    
    "steps": [
        {{
            "number": 1,
            "title": "Short phase title (3-6 words)",
            "description": "IMPLEMENTATION PHASE - What to actually BUILD. Include specific tech: frameworks, APIs, databases, tools. Example: 'Create a Next.js app with Supabase for user auth. Set up Stripe for payments using their npm package. Deploy on Vercel.'",
            "extra_credit": "Optional - only include if there's an MCP, plugin, or automation that could help. Example: 'Use Replit Agent to scaffold the entire project in minutes' or 'Connect Zapier to auto-post to social media'"
        }}
    ],
    
    "tools_mentioned": ["Specific", "tools", "and", "frameworks", "used"],
    
    "difficulty": "beginner/intermediate/advanced",
    
    "time_to_first_dollar": "Realistic timeframe like '2-3 weeks' or '1 month'",
    
    "kickoff_prompt": "A detailed prompt (200-400 words) that someone can paste into Claude or ChatGPT to start building. This should be an ACTUAL implementation prompt - asking the AI to help them set up the project, write code, create the first deliverable. Be specific about what files to create, what APIs to use, what the MVP should include."
}}

CRITICAL RULES:
1. REVENUE must be CALCULATED based on realistic assumptions - never use generic "$1000-3000/mo"
   - Low-effort template sales: $50-300/mo
   - Niche SaaS with small market: $500-2000/mo  
   - Agency services with 3-5 clients: $2000-8000/mo
   - Viral content with sponsorships: depends on niche
   
2. STEPS must be IMPLEMENTATION PHASES like an engineer would plan:
   - "Set up the project with [specific stack]"
   - "Build the [core feature] using [specific API/library]"
   - "Create the [UI/dashboard/pipeline] with [specific tools]"
   - "Deploy and set up [payment/auth/analytics]"
   - "Launch on [specific platforms] with [specific strategy]"
   
3. EXTRA_CREDIT is optional - only include when there's a real automation opportunity:
   - MCPs: Replit MCP, Perplexity MCP, filesystem MCP
   - Automation: Zapier, Make.com, n8n
   - Browser tools: Playwright, Puppeteer
   - APIs: Notion API, Airtable, etc.

4. NO vague phrases like "research trends", "leverage AI", "scale your business"

Generate a REAL project that a developer could start building TODAY:"""


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

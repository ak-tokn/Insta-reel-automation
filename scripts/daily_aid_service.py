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

CREATIVITY MANDATE:
You MUST generate UNIQUE, unexpected ideas. Avoid obvious suggestions like "AI blog writer" or "social media scheduler".
Think about underserved niches, weird intersections, and problems nobody is solving yet.

Categories to explore (mix and match creatively):
- AI automation for SPECIFIC industries (veterinary clinics, funeral homes, escape rooms, pawn shops, tattoo parlors)
- Niche content empires (AI-generated meditation scripts, historical reenactment videos, ASMR for pets)
- B2B tools for overlooked professions (notaries, court reporters, home inspectors, appraisers)
- Arbitrage and data plays (event ticket alerts, real estate data, government contract mining)
- Creator economy tools (AI ghostwriting for LinkedIn influencers, podcast clip generators, newsletter automation)
- Local service enhancements (AI menu optimization for restaurants, review response bots, appointment confirmations)
- Education micro-niches (AI tutoring for specific exams, language learning for niche languages, skill certifications)
- Hobbyist monetization (AI pattern generators for knitters, recipe scaling for bakers, aquarium maintenance planners)
- Professional services augmentation (AI briefs for lawyers, report generators for inspectors, estimate calculators)
- Unusual digital products (AI-generated coloring books, custom crossword puzzles, personalized children's stories)
- Community and membership plays (paid Discord bots, niche forum tools, exclusive data feeds)
- Automation-as-a-service (inbox zero services, calendar optimization, expense categorization)

UNCONVENTIONAL THINKING:
- What problems do people complain about in Reddit threads that nobody has solved?
- What tasks do small business owners hate doing manually?
- What could you build for a $500M industry that has no good software?
- What would a lazy genius automate to never work again?

Avoid: Dropshipping, generic courses, crypto/NFT, high capital requirements, MLM, obvious ideas everyone has seen.

Always respond in valid JSON format."""

    def _build_generation_prompt(self, idea_number: int) -> str:
        """Build the prompt for generating a Daily Ai'ds idea."""
        
        idea_themes = [
            "AI tools for an industry that's stuck in the 1990s (think: notaries, pawn shops, funeral homes)",
            "Scraping + AI to find hidden opportunities (government contracts, expiring domains, underpriced assets)",
            "Hyper-niche content empire nobody thought of (meditation for truck drivers, ASMR for studying, etc)",
            "AI assistant for a specific profession (court reporters, home inspectors, appraisers, tattoo artists)",
            "Automation-as-a-service for busy professionals (lawyers, doctors, real estate agents)",
            "Digital products for weird hobbies (aquariums, bonsai, lock picking, ham radio)",
            "AI-powered local business tools (menu optimization, review responses, appointment confirmations)",
            "Data arbitrage plays (tracking price changes, monitoring competitors, alert systems)",
            "Creator economy infrastructure (ghostwriting, clip generation, newsletter automation)",
            "B2B tools for overlooked small businesses (escape rooms, dog groomers, music teachers)",
            "AI tutoring for obscure certifications or exams (real estate license, food handler permits)",
            "Personalized digital products (custom children's books, family recipe cookbooks, genealogy reports)",
            "Discord/community monetization tools (premium bots, moderation systems, engagement analytics)",
            "Professional report generators (inspection reports, appraisal docs, legal briefs)",
            "Workflow automation for specific pain points (expense categorization, inbox management, scheduling)",
            "AI tools for blue-collar businesses (plumbers, electricians, contractors - estimates, invoices)",
            "Niche marketplace plays (connecting specific buyers/sellers nobody serves well)",
            "AI-enhanced hobby communities (pattern generators, recipe scaling, project planners)",
            "White-label AI solutions for agencies (chatbots, content, analytics they can resell)",
            "Monitoring and alerting services (stock alerts, price drops, availability notifications)",
            "AI tools for non-profits and churches (sermon transcription, donor management, event planning)",
            "Pet industry automation (vet appointment reminders, pet food subscriptions, training schedules)",
            "Real estate micro-tools (neighborhood reports, rental analysis, showing feedback collectors)",
            "Event industry tools (wedding planning AI, conference scheduling, vendor matching)",
            "Healthcare admin automation (appointment reminders, insurance verification, intake forms)",
            "Education admin tools (parent communication, grade tracking, behavior reports)",
            "Fitness and wellness niches (personalized meal plans, workout generators, habit trackers)",
            "Senior care and eldertech (medication reminders, family updates, appointment scheduling)",
            "Gig economy enhancers (delivery route optimization, earnings tracking, tax prep)",
            "Artist and creative tools (commission management, portfolio generators, pricing calculators)"
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
        "assumptions": "Brief explanation: [X] clients/sales at $[Y] each. Include timeline (e.g., 'after 3-6 months of consistent outreach' or 'once you have 20+ pieces of content driving traffic'). Be realistic about ramp-up time."
    }},
    
    "steps": [
        {{
            "number": 1,
            "title": "Short phase title (3-6 words)",
            "description": "IMPLEMENTATION PHASE - What to actually BUILD. Include specific tech: frameworks, APIs, databases, tools. Example: 'Create a Next.js app with Supabase for user auth. Set up Stripe for payments using their npm package. Deploy on Vercel.'",
            "ai_can_do_it": true or false - Set to TRUE for ANY coding/development task that AI can write and execute. This includes: setting up projects, writing APIs, building pipelines, creating dashboards, writing automation scripts, setting up databases, building content generators, integrating APIs, writing scrapers, creating email systems, building payment flows, etc. Basically ANY step where the output is CODE that AI can write. Set to FALSE ONLY for: manual outreach, sales calls, creating accounts on platforms, customer acquisition, negotiating deals, or tasks requiring human relationships.",
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
   - REQUIRED: Include a "Scale to [X] customers" step that explains the SPECIFIC acquisition strategy to reach the revenue target. If you're projecting $2000/mo from $50/mo subscriptions, you need 40 clients - explain exactly HOW to get them (cold outreach numbers, content strategy, ad spend, etc.)
   
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

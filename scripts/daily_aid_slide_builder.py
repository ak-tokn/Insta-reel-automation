"""
Daily Ai'ds Slide Builder for StoicAlgo
Renders carousel images for Daily Ai'ds Instagram posts.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scripts.logger import get_logger
from scripts.utils import load_settings

logger = get_logger("DailyAidSlideBuilder")


class DailyAidSlideBuilder:
    """Builds carousel slides for Daily Ai'ds posts."""
    
    def __init__(self):
        self.settings = load_settings()
        self.config = self.settings.get('daily_aids', {})
        self.carousel_config = self.config.get('carousel', {})
        self.branding = self.config.get('branding', {})
        
        self.width = self.carousel_config.get('width', 1080)
        self.height = self.carousel_config.get('height', 1350)
        self.bg_color = self.carousel_config.get('background_color', '#0A0A0A')
        self.accent_color = self.carousel_config.get('accent_color', '#00FF88')
        self.secondary_color = self.carousel_config.get('secondary_color', '#FF6B35')
        
        self.base_output_dir = Path('output/daily_aids')
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = None
        
        self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts for rendering with improved visual hierarchy."""
        display_font = 'assets/fonts/Panchang-Medium.ttf'
        accent_font = 'assets/fonts/Panchang-Regular.ttf'
        body_font = 'assets/fonts/Montserrat-Variable.ttf'
        
        try:
            self.font_title = ImageFont.truetype(display_font, 88)
            self.font_title_large = ImageFont.truetype(display_font, 100)
            self.font_subtitle = ImageFont.truetype(accent_font, 48)
            self.font_body = ImageFont.truetype(body_font, 38)
            self.font_body_large = ImageFont.truetype(body_font, 42)
            self.font_step_number = ImageFont.truetype(display_font, 180)
            self.font_step_title = ImageFont.truetype(display_font, 52)
            self.font_header = ImageFont.truetype(accent_font, 36)
            self.font_small = ImageFont.truetype(body_font, 30)
            self.font_cta = ImageFont.truetype(display_font, 64)
        except Exception as e:
            logger.warning(f"Failed to load custom fonts: {e}, using default")
            self.font_title = ImageFont.load_default()
            self.font_title_large = ImageFont.load_default()
            self.font_subtitle = ImageFont.load_default()
            self.font_body = ImageFont.load_default()
            self.font_body_large = ImageFont.load_default()
            self.font_step_number = ImageFont.load_default()
            self.font_step_title = ImageFont.load_default()
            self.font_header = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_cta = ImageFont.load_default()
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_base_image(self) -> Image.Image:
        """Create base image with background."""
        bg_rgb = self._hex_to_rgb(self.bg_color)
        return Image.new('RGB', (self.width, self.height), bg_rgb)
    
    def _add_gradient_overlay(self, img: Image.Image) -> Image.Image:
        """Add subtle gradient overlay for depth."""
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        for y in range(self.height):
            opacity = int(30 * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, opacity))
        
        img = img.convert('RGBA')
        return Image.alpha_composite(img, overlay).convert('RGB')
    
    def _add_accent_elements(self, draw: ImageDraw.Draw, variant: str = 'default'):
        """Add decorative accent elements."""
        accent_rgb = self._hex_to_rgb(self.accent_color)
        secondary_rgb = self._hex_to_rgb(self.secondary_color)
        
        if variant == 'title':
            draw.rectangle([(0, 0), (self.width, 8)], fill=accent_rgb)
            draw.rectangle([(0, self.height - 8), (self.width, self.height)], fill=accent_rgb)
            draw.line([(50, 200), (self.width - 50, 200)], fill=(*accent_rgb, 100), width=2)
        
        elif variant == 'step':
            draw.rectangle([(40, 100), (48, self.height - 100)], fill=(*accent_rgb, 80))
        
        elif variant == 'cta':
            draw.rectangle([(0, 0), (self.width, 8)], fill=secondary_rgb)
            draw.rectangle([(0, self.height - 8), (self.width, self.height)], fill=secondary_rgb)
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        dummy_img = Image.new('RGB', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_text_with_shadow(self, draw: ImageDraw.Draw, pos: Tuple[int, int], 
                                text: str, font: ImageFont.FreeTypeFont, 
                                fill: Tuple[int, int, int], shadow_offset: int = 3):
        """Draw text with shadow effect."""
        x, y = pos
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0))
        draw.text(pos, text, font=font, fill=fill)
    
    def build_title_slide(self, idea: Dict) -> Path:
        """Build the title slide (first carousel image)."""
        img = self._create_base_image()
        img = self._add_gradient_overlay(img)
        draw = ImageDraw.Draw(img)
        
        self._add_accent_elements(draw, 'title')
        
        header_text = self.branding.get('header_text', 'DAILY AI\'DS')
        idea_number = idea.get('idea_number', 1)
        
        accent_rgb = self._hex_to_rgb(self.accent_color)
        header_full = f"{header_text} #{idea_number}"
        bbox = draw.textbbox((0, 0), header_full, font=self.font_subtitle)
        header_width = bbox[2] - bbox[0]
        header_x = (self.width - header_width) // 2
        draw.text((header_x, 60), header_full, font=self.font_subtitle, fill=accent_rgb)
        
        title = idea.get('title', 'AI Money Idea')
        title_lines = self._wrap_text(title.upper(), self.font_title_large, self.width - 100)
        
        y_offset = 250
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_title_large)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            self._draw_text_with_shadow(draw, (x, y_offset), line, self.font_title_large, (255, 255, 255), shadow_offset=4)
            y_offset += 110
        
        summary = idea.get('summary', '')
        summary_lines = self._wrap_text(summary, self.font_body_large, self.width - 140)
        
        y_offset += 60
        for line in summary_lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_body_large)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            draw.text((x, y_offset), line, font=self.font_body_large, fill=(200, 200, 200))
            y_offset += 55
        
        earnings = idea.get('estimated_earnings', '')
        difficulty = idea.get('difficulty', '')
        time_to_money = idea.get('time_to_first_dollar', '')
        
        if earnings or difficulty or time_to_money:
            y_offset = self.height - 380
            
            secondary_rgb = self._hex_to_rgb(self.secondary_color)
            
            if earnings:
                bbox = draw.textbbox((0, 0), earnings, font=self.font_cta)
                x = (self.width - (bbox[2] - bbox[0])) // 2
                self._draw_text_with_shadow(draw, (x, y_offset), earnings, self.font_cta, secondary_rgb, shadow_offset=3)
                y_offset += 85
            
            if difficulty:
                diff_text = f"Difficulty: {difficulty.upper()}"
                bbox = draw.textbbox((0, 0), diff_text, font=self.font_body)
                x = (self.width - (bbox[2] - bbox[0])) // 2
                draw.text((x, y_offset), diff_text, font=self.font_body, fill=(150, 150, 150))
                y_offset += 50
            
            if time_to_money:
                time_text = f"First $ in: {time_to_money}"
                bbox = draw.textbbox((0, 0), time_text, font=self.font_body)
                x = (self.width - (bbox[2] - bbox[0])) // 2
                draw.text((x, y_offset), time_text, font=self.font_body, fill=(150, 150, 150))
        
        watermark = self.branding.get('watermark', '@techiavelli')
        bbox = draw.textbbox((0, 0), watermark, font=self.font_small)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 70), watermark, font=self.font_small, fill=(100, 100, 100))
        
        output_path = self.output_dir / f"slide_00_title.png"
        img.save(output_path, 'PNG', quality=95)
        logger.info(f"Created title slide: {output_path}")
        return output_path
    
    def build_step_slide(self, step: Dict, step_index: int, total_steps: int) -> Path:
        """Build a step slide."""
        img = self._create_base_image()
        img = self._add_gradient_overlay(img)
        draw = ImageDraw.Draw(img)
        
        self._add_accent_elements(draw, 'step')
        
        accent_rgb = self._hex_to_rgb(self.accent_color)
        step_num = str(step.get('number', step_index + 1))
        
        self._draw_text_with_shadow(draw, (70, 80), step_num, self.font_step_number, accent_rgb, shadow_offset=5)
        
        progress_text = f"STEP {step_num} OF {total_steps}"
        draw.text((70, 280), progress_text, font=self.font_header, fill=(120, 120, 120))
        
        step_title = step.get('title', f'Step {step_num}')
        title_lines = self._wrap_text(step_title.upper(), self.font_step_title, self.width - 140)
        
        y_offset = 380
        for line in title_lines:
            self._draw_text_with_shadow(draw, (70, y_offset), line, self.font_step_title, (255, 255, 255), shadow_offset=3)
            y_offset += 70
        
        y_offset += 30
        draw.line([(70, y_offset), (self.width - 70, y_offset)], fill=accent_rgb, width=3)
        y_offset += 50
        
        description = step.get('description', '')
        desc_lines = self._wrap_text(description, self.font_body_large, self.width - 140)
        
        for line in desc_lines:
            draw.text((70, y_offset), line, font=self.font_body_large, fill=(220, 220, 220))
            y_offset += 55
        
        watermark = self.branding.get('watermark', '@techiavelli')
        bbox = draw.textbbox((0, 0), watermark, font=self.font_small)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 70), watermark, font=self.font_small, fill=(100, 100, 100))
        
        output_path = self.output_dir / f"slide_{step_index + 1:02d}_step.png"
        img.save(output_path, 'PNG', quality=95)
        logger.info(f"Created step slide {step_index + 1}: {output_path}")
        return output_path
    
    def build_cta_slide(self, idea: Dict) -> Path:
        """Build the call-to-action slide (final carousel image)."""
        img = self._create_base_image()
        img = self._add_gradient_overlay(img)
        draw = ImageDraw.Draw(img)
        
        self._add_accent_elements(draw, 'cta')
        
        secondary_rgb = self._hex_to_rgb(self.secondary_color)
        accent_rgb = self._hex_to_rgb(self.accent_color)
        
        ready_text = "READY TO START?"
        bbox = draw.textbbox((0, 0), ready_text, font=self.font_title_large)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self._draw_text_with_shadow(draw, (x, 250), ready_text, self.font_title_large, (255, 255, 255), shadow_offset=4)
        
        cta_text = self.branding.get('cta_text', 'Copy the caption into Claude/ChatGPT to get started')
        cta_lines = self._wrap_text(cta_text, self.font_step_title, self.width - 100)
        
        y_offset = 450
        for line in cta_lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_step_title)
            x = (self.width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y_offset), line, font=self.font_step_title, fill=accent_rgb)
            y_offset += 70
        
        arrow_y = y_offset + 80
        arrow_text = "↓"
        bbox = draw.textbbox((0, 0), arrow_text, font=self.font_step_number)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self._draw_text_with_shadow(draw, (x, arrow_y), arrow_text, self.font_step_number, secondary_rgb, shadow_offset=4)
        
        caption_hint = "THE PROMPT IS IN THE CAPTION"
        bbox = draw.textbbox((0, 0), caption_hint, font=self.font_subtitle)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, arrow_y + 180), caption_hint, font=self.font_subtitle, fill=(200, 200, 200))
        
        tools = idea.get('tools_mentioned', [])
        if tools:
            tools_text = "Tools: " + ", ".join(tools[:5])
            tools_lines = self._wrap_text(tools_text, self.font_body, self.width - 160)
            y_tools = self.height - 180
            for line in tools_lines:
                bbox = draw.textbbox((0, 0), line, font=self.font_body)
                x = (self.width - (bbox[2] - bbox[0])) // 2
                draw.text((x, y_tools), line, font=self.font_body, fill=(120, 120, 120))
                y_tools += 45
        
        watermark = self.branding.get('watermark', '@techiavelli')
        bbox = draw.textbbox((0, 0), watermark, font=self.font_small)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 70), watermark, font=self.font_small, fill=(100, 100, 100))
        
        output_path = self.output_dir / "slide_99_cta.png"
        img.save(output_path, 'PNG', quality=95)
        logger.info(f"Created CTA slide: {output_path}")
        return output_path
    
    def build_all_slides(self, idea: Dict, is_preview: bool = False) -> List[Path]:
        """Build all carousel slides for an idea.
        
        Args:
            idea: The idea dictionary with title, steps, etc.
            is_preview: If True, saves to 'preview' folder instead of numbered post folder
            
        Returns:
            List of paths to generated slide images
        """
        slides = []
        
        idea_number = idea.get('idea_number', 1)
        
        if is_preview:
            self.output_dir = self.base_output_dir / 'preview'
        else:
            self.output_dir = self.base_output_dir / f'post_{idea_number}'
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for f in self.output_dir.glob('slide_*.png'):
            f.unlink()
        
        slides.append(self.build_title_slide(idea))
        
        steps = idea.get('steps', [])
        total_steps = len(steps)
        
        for i, step in enumerate(steps):
            slides.append(self.build_step_slide(step, i, total_steps))
        
        slides.append(self.build_cta_slide(idea))
        
        logger.info(f"Built {len(slides)} slides for Daily Ai'ds #{idea_number} in {self.output_dir}")
        return slides


def build_daily_aid_slides(idea: Dict) -> List[Path]:
    """Build all slides for a Daily Ai'ds idea."""
    builder = DailyAidSlideBuilder()
    return builder.build_all_slides(idea)


if __name__ == "__main__":
    test_idea = {
        "idea_number": 1,
        "title": "AI Ghostwriter Empire",
        "summary": "Build a faceless content agency using AI to write for executives.",
        "hook": "CEOs pay $500/post. AI writes it in 60 seconds.",
        "estimated_earnings": "$2,000-5,000/month",
        "difficulty": "intermediate",
        "time_to_first_dollar": "1-2 weeks",
        "steps": [
            {"number": 1, "title": "Find Your Niche", "description": "Target LinkedIn executives in tech, finance, or consulting. They need content but hate writing."},
            {"number": 2, "title": "Build Your AI Stack", "description": "Use Claude for strategy and GPT-4 for drafting. Create reusable prompts for each client's voice."},
            {"number": 3, "title": "Create Sample Portfolio", "description": "Write 5 sample posts across different executive personas. These are your sales tools."},
            {"number": 4, "title": "Cold Outreach System", "description": "Use Apollo.io to find decision-makers. Personalize with their recent posts using AI."},
            {"number": 5, "title": "Productize Your Service", "description": "Offer packages: 3 posts/week for $1,500/month. Scale with templates."},
        ],
        "tools_mentioned": ["Claude", "GPT-4", "Apollo.io", "LinkedIn"],
        "kickoff_prompt": "Help me build a LinkedIn ghostwriting service..."
    }
    
    slides = build_daily_aid_slides(test_idea)
    print(f"Created {len(slides)} slides:")
    for slide in slides:
        print(f"  - {slide}")

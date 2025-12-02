"""
Daily Ai'ds Slide Builder for StoicAlgo
Renders carousel images for Daily Ai'ds Instagram posts.
"""

import os
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
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
        """Load fonts for rendering with trendy visual hierarchy."""
        title_font = 'assets/fonts/Nippo-Bold.ttf'
        number_font = 'assets/fonts/Orbitron-Bold.ttf'
        body_font = 'assets/fonts/Chillax-Variable.ttf'
        display_font = 'assets/fonts/Comico-Regular.ttf'
        light_font = 'assets/fonts/Montserrat-Light.ttf'
        stardom_font = 'assets/fonts/Stardom-Regular.ttf'
        montserrat_font = 'assets/fonts/Montserrat-Light.ttf'
        
        try:
            self.font_title = ImageFont.truetype(title_font, 92)
            self.font_title_large = ImageFont.truetype(title_font, 105)
            self.font_subtitle = ImageFont.truetype(title_font, 50)
            self.font_body = ImageFont.truetype(body_font, 38)
            self.font_body_large = ImageFont.truetype(body_font, 44)
            self.font_step_number = ImageFont.truetype(number_font, 200)
            self.font_step_title = ImageFont.truetype(title_font, 56)
            self.font_header = ImageFont.truetype(title_font, 40)
            self.font_small = ImageFont.truetype(body_font, 32)
            self.font_cta = ImageFont.truetype(title_font, 68)
            self.font_display_large = ImageFont.truetype(display_font, 85)
            self.font_display_xl = ImageFont.truetype(display_font, 110)
            self.font_light = ImageFont.truetype(light_font, 34)
            self.font_light_small = ImageFont.truetype(light_font, 28)
            self.font_stardom_large = ImageFont.truetype(stardom_font, 105)
            self.font_stardom_medium = ImageFont.truetype(stardom_font, 36)
            self.font_montserrat_400 = ImageFont.truetype(montserrat_font, 44)
            self.font_montserrat_400_medium = ImageFont.truetype(montserrat_font, 38)
            self.font_montserrat_500 = ImageFont.truetype(montserrat_font, 50)
            self.font_step_header_light = ImageFont.truetype(light_font, 58)
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
            self.font_display_large = ImageFont.load_default()
            self.font_display_xl = ImageFont.load_default()
            self.font_light = ImageFont.load_default()
            self.font_light_small = ImageFont.load_default()
            self.font_stardom_large = ImageFont.load_default()
            self.font_stardom_medium = ImageFont.load_default()
            self.font_montserrat_400 = ImageFont.load_default()
            self.font_montserrat_400_medium = ImageFont.load_default()
            self.font_montserrat_500 = ImageFont.load_default()
            self.font_step_header_light = ImageFont.load_default()
    
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
    
    def _get_random_background_image(self) -> Optional[Path]:
        """Get a random background image from assets."""
        image_dirs = [
            Path('assets/images/nature'),
            Path('assets/images/sonder'),
            Path('assets/images/warriors'),
            Path('assets/images/temples'),
        ]
        
        all_images = []
        for dir_path in image_dirs:
            if dir_path.exists():
                images = list(dir_path.glob('*.png')) + list(dir_path.glob('*.jpg'))
                images = [img for img in images if 'used' not in str(img)]
                all_images.extend(images)
        
        if all_images:
            return random.choice(all_images)
        return None
    
    def _create_title_background(self) -> Image.Image:
        """Create a trendy title slide background with lightly dimmed image."""
        bg_img = self._get_random_background_image()
        
        if bg_img and bg_img.exists():
            try:
                img = Image.open(bg_img).convert('RGB')
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(0.45)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(0.85)
                img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
                overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 120))
                img = img.convert('RGBA')
                img = Image.alpha_composite(img, overlay).convert('RGB')
                
                return img
            except Exception as e:
                logger.warning(f"Failed to load background image: {e}")
        
        return self._create_base_image()
    
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
        """Build the title slide (first carousel image) - trendy and eye-catching."""
        img = self._create_title_background()
        draw = ImageDraw.Draw(img)
        
        accent_rgb = self._hex_to_rgb(self.accent_color)
        green_rgb = (0, 200, 100)
        idea_number = idea.get('idea_number', 1)
        
        draw.rectangle([(0, 0), (self.width, 6)], fill=accent_rgb)
        draw.rectangle([(0, self.height - 6), (self.width, self.height)], fill=accent_rgb)
        
        header_text = f"Daily Ai'Ds #{idea_number}"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_display_xl)
        header_width = bbox[2] - bbox[0]
        header_x = (self.width - header_width) // 2
        self._draw_text_with_shadow(draw, (header_x, 40), header_text, self.font_display_xl, accent_rgb, shadow_offset=5)
        
        title = idea.get('title', 'AI Money Idea')
        income_method = idea.get('income_method', 'automating tasks')
        
        focal_start_y = 340
        
        label_text = "Easy Prompting Idea:"
        bbox = draw.textbbox((0, 0), label_text, font=self.font_montserrat_400)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, focal_start_y), label_text, font=self.font_montserrat_400, fill=(160, 160, 160))
        
        title_lines = self._wrap_text(title.upper(), self.font_stardom_large, self.width - 100)
        y_offset = focal_start_y + 60
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_stardom_large)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            self._draw_text_with_shadow(draw, (x, y_offset), line, self.font_stardom_large, (255, 255, 255), shadow_offset=4)
            y_offset += 100
        
        y_offset += 60
        
        money_text = "make money by"
        bbox = draw.textbbox((0, 0), money_text, font=self.font_montserrat_400_medium)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_offset), money_text, font=self.font_montserrat_400_medium, fill=(150, 150, 150))
        y_offset += 50
        
        method_lines = self._wrap_text(income_method.lower(), self.font_montserrat_500, self.width - 100)
        for line in method_lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_montserrat_500)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            draw.text((x, y_offset), line, font=self.font_montserrat_500, fill=accent_rgb)
            y_offset += 50
        
        monthly_income = idea.get('monthly_income', idea.get('estimated_earnings', '$500-2000/mo'))
        if monthly_income:
            earnings_text = "set up in hours and make up to"
            
            y_earnings = self.height - 320
            bbox = draw.textbbox((0, 0), earnings_text, font=self.font_montserrat_400_medium)
            x = (self.width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y_earnings), earnings_text, font=self.font_montserrat_400_medium, fill=(170, 170, 170))
            
            bbox = draw.textbbox((0, 0), monthly_income, font=self.font_montserrat_500)
            x = (self.width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y_earnings + 42), monthly_income, font=self.font_montserrat_500, fill=green_rgb)
        
        tagline = "The hardest part is getting started.."
        tagline2 = "I just solved that - so give this a shot?"
        
        tagline_font = ImageFont.truetype('assets/fonts/Comico-Regular.ttf', 32)
        
        bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 190), tagline, font=tagline_font, fill=accent_rgb)
        
        bbox = draw.textbbox((0, 0), tagline2, font=tagline_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 150), tagline2, font=tagline_font, fill=accent_rgb)
        
        watermark = self.branding.get('watermark', '@techiavelli')
        bbox = draw.textbbox((0, 0), watermark, font=self.font_stardom_medium)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 70), watermark, font=self.font_stardom_medium, fill=(120, 120, 120))
        
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
        title_lines = self._wrap_text(step_title.upper(), self.font_step_header_light, self.width - 140)
        
        y_offset = 380
        for line in title_lines:
            draw.text((70, y_offset), line, font=self.font_step_header_light, fill=(255, 255, 255))
            y_offset += 75
        
        y_offset += 30
        draw.line([(70, y_offset), (self.width - 70, y_offset)], fill=accent_rgb, width=3)
        y_offset += 50
        
        description = step.get('description', '')
        desc_lines = self._wrap_text(description, self.font_body_large, self.width - 140)
        
        for line in desc_lines:
            draw.text((70, y_offset), line, font=self.font_body_large, fill=(220, 220, 220))
            y_offset += 55
        
        watermark = self.branding.get('watermark', '@techiavelli')
        bbox = draw.textbbox((0, 0), watermark, font=self.font_stardom_medium)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 70), watermark, font=self.font_stardom_medium, fill=(120, 120, 120))
        
        output_path = self.output_dir / f"slide_{step_index + 1:02d}_step.png"
        img.save(output_path, 'PNG', quality=95)
        logger.info(f"Created step slide {step_index + 1}: {output_path}")
        return output_path
    
    def build_cta_slide(self, idea: Dict) -> Path:
        """Build the call-to-action slide (final carousel image) - matches title slide styling."""
        img = self._create_title_background()
        draw = ImageDraw.Draw(img)
        
        accent_rgb = self._hex_to_rgb(self.accent_color)
        green_rgb = (0, 200, 100)
        
        draw.rectangle([(0, 0), (self.width, 6)], fill=accent_rgb)
        draw.rectangle([(0, self.height - 6), (self.width, self.height)], fill=accent_rgb)
        
        ready_text = "Ready to Start?"
        bbox = draw.textbbox((0, 0), ready_text, font=self.font_display_xl)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self._draw_text_with_shadow(draw, (x, 180), ready_text, self.font_display_xl, accent_rgb, shadow_offset=5)
        
        cta_label = "Just copy the caption below into"
        bbox = draw.textbbox((0, 0), cta_label, font=self.font_montserrat_400)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 380), cta_label, font=self.font_montserrat_400, fill=(160, 160, 160))
        
        cta_main = "CHATGPT OR CLAUDE"
        bbox = draw.textbbox((0, 0), cta_main, font=self.font_stardom_large)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self._draw_text_with_shadow(draw, (x, 440), cta_main, self.font_stardom_large, (255, 255, 255), shadow_offset=4)
        
        cta_label2 = "and let AI guide you through it"
        bbox = draw.textbbox((0, 0), cta_label2, font=self.font_montserrat_400)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 560), cta_label2, font=self.font_montserrat_400, fill=(160, 160, 160))
        
        arrow_text = "↓"
        arrow_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 120)
        bbox = draw.textbbox((0, 0), arrow_text, font=arrow_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 680), arrow_text, font=arrow_font, fill=green_rgb)
        
        caption_hint = "THE PROMPT IS IN THE CAPTION"
        bbox = draw.textbbox((0, 0), caption_hint, font=self.font_montserrat_400_medium)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 850), caption_hint, font=self.font_montserrat_400_medium, fill=(180, 180, 180))
        
        tools = idea.get('tools_mentioned', [])
        if tools:
            tools_text = "Tools: " + ", ".join(tools[:5])
            tools_lines = self._wrap_text(tools_text, self.font_montserrat_400_medium, self.width - 160)
            y_tools = self.height - 180
            for line in tools_lines:
                bbox = draw.textbbox((0, 0), line, font=self.font_montserrat_400_medium)
                x = (self.width - (bbox[2] - bbox[0])) // 2
                draw.text((x, y_tools), line, font=self.font_montserrat_400_medium, fill=(120, 120, 120))
                y_tools += 45
        
        watermark = self.branding.get('watermark', '@techiavelli')
        bbox = draw.textbbox((0, 0), watermark, font=self.font_stardom_medium)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 70), watermark, font=self.font_stardom_medium, fill=(120, 120, 120))
        
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

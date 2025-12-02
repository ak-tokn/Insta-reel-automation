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
    
    def _get_dynamic_font(self, text: str, font_path: str, max_width: int, max_size: int, min_size: int = 24) -> ImageFont.FreeTypeFont:
        """Get a font sized to fit text within max_width."""
        for size in range(max_size, min_size - 1, -2):
            font = ImageFont.truetype(font_path, size)
            dummy_img = Image.new('RGB', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0, 0), text, font=font)
            if bbox[2] - bbox[0] <= max_width:
                return font
        return ImageFont.truetype(font_path, min_size)
    
    def _get_text_height(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> int:
        """Calculate total height needed for wrapped text."""
        lines = self._wrap_text(text, font, max_width)
        dummy_img = Image.new('RGB', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        total_height = 0
        for line in lines:
            bbox = dummy_draw.textbbox((0, 0), line, font=font)
            total_height += bbox[3] - bbox[1] + 10
        return total_height

    def build_title_slide(self, idea: Dict) -> Path:
        """Build the title slide with the specified layout."""
        img = self._create_title_background()
        draw = ImageDraw.Draw(img)
        
        accent_rgb = self._hex_to_rgb(self.accent_color)
        green_rgb = (0, 220, 100)
        idea_number = idea.get('idea_number', 1)
        
        draw.rectangle([(0, 0), (self.width, 6)], fill=accent_rgb)
        draw.rectangle([(0, self.height - 6), (self.width, self.height)], fill=accent_rgb)
        
        padding = 40
        max_text_width = self.width - (padding * 2)
        
        header_text = f"Daily Ai'Ds #{idea_number}"
        header_font = ImageFont.truetype('assets/fonts/Comico-Regular.ttf', 95)
        bbox = draw.textbbox((0, 0), header_text, font=header_font)
        header_x = (self.width - (bbox[2] - bbox[0])) // 2
        header_height = bbox[3] - bbox[1]
        self._draw_text_with_shadow(draw, (header_x, 25), header_text, header_font, accent_rgb, shadow_offset=4)
        
        title = idea.get('title', 'AI Money Idea')
        income_method = idea.get('income_method', 'automating tasks')
        monthly_income = idea.get('monthly_income', idea.get('estimated_earnings', '$500-2000/mo'))
        
        label_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 40)
        title_font = self._get_dynamic_font(title.upper(), 'assets/fonts/Stardom-Regular.ttf', max_text_width, 120, 65)
        title_lines = self._wrap_text(title.upper(), title_font, max_text_width)
        earnings_label_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 36)
        amount_font = ImageFont.truetype('assets/fonts/Montserrat-Bold.ttf', 68)
        method_font = self._get_dynamic_font(income_method.lower(), 'assets/fonts/Montserrat-Bold.ttf', max_text_width, 44, 30)
        method_lines = self._wrap_text(income_method.lower(), method_font, max_text_width)
        
        label_bbox = draw.textbbox((0, 0), "Easy Prompting Idea:", font=label_font)
        label_h = label_bbox[3] - label_bbox[1]
        title_bbox = draw.textbbox((0, 0), "Ag", font=title_font)
        title_line_h = title_bbox[3] - title_bbox[1] + 18
        title_block_h = title_line_h * len(title_lines)
        earnings_label_bbox = draw.textbbox((0, 0), "set up in hours and make up to", font=earnings_label_font)
        earnings_label_h = earnings_label_bbox[3] - earnings_label_bbox[1]
        amount_bbox = draw.textbbox((0, 0), monthly_income, font=amount_font)
        amount_h = amount_bbox[3] - amount_bbox[1]
        method_bbox = draw.textbbox((0, 0), "Ag", font=method_font)
        method_line_h = method_bbox[3] - method_bbox[1] + 10
        method_block_h = method_line_h * len(method_lines)
        
        total_content_h = label_h + 20 + title_block_h + 40 + earnings_label_h + 15 + amount_h + 35 + method_block_h
        
        header_bottom = 25 + header_height + 40
        footer_top = self.height - 180
        available_space = footer_top - header_bottom
        content_start_y = header_bottom + (available_space - total_content_h) // 2
        
        label_text = "Easy Prompting Idea:"
        bbox = draw.textbbox((0, 0), label_text, font=label_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, content_start_y), label_text, font=label_font, fill=(160, 160, 160))
        
        title_y = content_start_y + label_h + 20
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            self._draw_text_with_shadow(draw, (x, title_y), line, title_font, (255, 255, 255), shadow_offset=5)
            title_y += title_line_h
        
        earnings_y = title_y + 40
        
        earnings_label = "set up in hours and make up to"
        bbox = draw.textbbox((0, 0), earnings_label, font=earnings_label_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, earnings_y), earnings_label, font=earnings_label_font, fill=(170, 170, 170))
        
        earnings_y += earnings_label_h + 15
        bbox = draw.textbbox((0, 0), monthly_income, font=amount_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self._draw_text_with_shadow(draw, (x, earnings_y), monthly_income, amount_font, green_rgb, shadow_offset=3)
        
        earnings_y += amount_h + 35
        
        for line in method_lines:
            bbox = draw.textbbox((0, 0), line, font=method_font)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            self._draw_text_with_shadow(draw, (x, earnings_y), line, method_font, accent_rgb, shadow_offset=2)
            earnings_y += method_line_h
        
        tagline_font = ImageFont.truetype('assets/fonts/Comico-Regular.ttf', 30)
        tagline = "The hardest part is getting started.."
        tagline2 = "I just solved that - so give this a shot?"
        
        bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 150), tagline, font=tagline_font, fill=accent_rgb)
        
        bbox = draw.textbbox((0, 0), tagline2, font=tagline_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 110), tagline2, font=tagline_font, fill=accent_rgb)
        
        watermark = self.branding.get('watermark', '@techiavelli')
        watermark_font = ImageFont.truetype('assets/fonts/Stardom-Regular.ttf', 32)
        bbox = draw.textbbox((0, 0), watermark, font=watermark_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 60), watermark, font=watermark_font, fill=(120, 120, 120))
        
        output_path = self.output_dir / f"slide_00_title.png"
        img.save(output_path, 'PNG', quality=95)
        logger.info(f"Created title slide: {output_path}")
        return output_path
    
    def build_step_slide(self, step: Dict, step_index: int, total_steps: int) -> Path:
        """Build a step slide with Stardom headers and Montserrat body."""
        img = self._create_base_image()
        img = self._add_gradient_overlay(img)
        draw = ImageDraw.Draw(img)
        
        self._add_accent_elements(draw, 'step')
        
        accent_rgb = self._hex_to_rgb(self.accent_color)
        step_num = str(step.get('number', step_index + 1))
        padding = 70
        max_text_width = self.width - (padding * 2)
        
        number_font = ImageFont.truetype('assets/fonts/Orbitron-Bold.ttf', 180)
        self._draw_text_with_shadow(draw, (padding, 60), step_num, number_font, accent_rgb, shadow_offset=5)
        
        progress_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 36)
        progress_text = f"STEP {step_num} OF {total_steps}"
        draw.text((padding, 250), progress_text, font=progress_font, fill=(120, 120, 120))
        
        step_title = step.get('title', f'Step {step_num}')
        title_font = self._get_dynamic_font(step_title.upper(), 'assets/fonts/Stardom-Regular.ttf', max_text_width, 70, 40)
        title_lines = self._wrap_text(step_title.upper(), title_font, max_text_width)
        
        bbox = draw.textbbox((0, 0), "Ag", font=title_font)
        line_height = bbox[3] - bbox[1] + 12
        
        y_offset = 340
        for line in title_lines:
            self._draw_text_with_shadow(draw, (padding, y_offset), line, title_font, (255, 255, 255), shadow_offset=3)
            y_offset += line_height
        
        y_offset += 30
        draw.line([(padding, y_offset), (self.width - padding, y_offset)], fill=accent_rgb, width=3)
        y_offset += 45
        
        description = step.get('description', '')
        body_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 38)
        desc_lines = self._wrap_text(description, body_font, max_text_width)
        
        for line in desc_lines:
            draw.text((padding, y_offset), line, font=body_font, fill=(210, 210, 210))
            y_offset += 52
        
        watermark = self.branding.get('watermark', '@techiavelli')
        watermark_font = ImageFont.truetype('assets/fonts/Stardom-Regular.ttf', 32)
        bbox = draw.textbbox((0, 0), watermark, font=watermark_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 60), watermark, font=watermark_font, fill=(120, 120, 120))
        
        output_path = self.output_dir / f"slide_{step_index + 1:02d}_step.png"
        img.save(output_path, 'PNG', quality=95)
        logger.info(f"Created step slide {step_index + 1}: {output_path}")
        return output_path
    
    def build_cta_slide(self, idea: Dict) -> Path:
        """Build the call-to-action slide with large, impactful content."""
        img = self._create_title_background()
        draw = ImageDraw.Draw(img)
        
        accent_rgb = self._hex_to_rgb(self.accent_color)
        green_rgb = (0, 200, 100)
        
        draw.rectangle([(0, 0), (self.width, 6)], fill=accent_rgb)
        draw.rectangle([(0, self.height - 6), (self.width, self.height)], fill=accent_rgb)
        
        padding = 50
        max_text_width = self.width - (padding * 2)
        
        header_font = ImageFont.truetype('assets/fonts/Comico-Regular.ttf', 95)
        ready_text = "Ready to Start?"
        bbox = draw.textbbox((0, 0), ready_text, font=header_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self._draw_text_with_shadow(draw, (x, 50), ready_text, header_font, accent_rgb, shadow_offset=4)
        
        label_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 40)
        cta_label = "Just copy the caption below into"
        bbox = draw.textbbox((0, 0), cta_label, font=label_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 220), cta_label, font=label_font, fill=(160, 160, 160))
        
        cta_main = "CHATGPT OR CLAUDE"
        main_font = self._get_dynamic_font(cta_main, 'assets/fonts/Stardom-Regular.ttf', max_text_width, 90, 50)
        bbox = draw.textbbox((0, 0), cta_main, font=main_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self._draw_text_with_shadow(draw, (x, 290), cta_main, main_font, (255, 255, 255), shadow_offset=4)
        
        cta_label2 = "and let AI guide you through it"
        bbox = draw.textbbox((0, 0), cta_label2, font=label_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 420), cta_label2, font=label_font, fill=(160, 160, 160))
        
        arrow_text = "↓"
        arrow_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 140)
        bbox = draw.textbbox((0, 0), arrow_text, font=arrow_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 520), arrow_text, font=arrow_font, fill=green_rgb)
        
        hint_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 42)
        caption_hint = "THE PROMPT IS IN THE CAPTION"
        bbox = draw.textbbox((0, 0), caption_hint, font=hint_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, 730), caption_hint, font=hint_font, fill=(180, 180, 180))
        
        tools = idea.get('tools_mentioned', [])
        if tools:
            tools_font = ImageFont.truetype('assets/fonts/Montserrat-Light.ttf', 32)
            tools_text = "Tools: " + ", ".join(tools[:5])
            tools_lines = self._wrap_text(tools_text, tools_font, max_text_width)
            y_tools = self.height - 160
            for line in tools_lines:
                bbox = draw.textbbox((0, 0), line, font=tools_font)
                x = (self.width - (bbox[2] - bbox[0])) // 2
                draw.text((x, y_tools), line, font=tools_font, fill=(120, 120, 120))
                y_tools += 42
        
        watermark = self.branding.get('watermark', '@techiavelli')
        watermark_font = ImageFont.truetype('assets/fonts/Stardom-Regular.ttf', 32)
        bbox = draw.textbbox((0, 0), watermark, font=watermark_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        draw.text((x, self.height - 60), watermark, font=watermark_font, fill=(120, 120, 120))
        
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

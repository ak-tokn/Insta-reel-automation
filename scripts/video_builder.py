"""
Video Builder for StoicAlgo
Generates vertical videos with Ken Burns effect and text overlays using FFmpeg.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from scripts.logger import get_logger
from scripts.utils import load_settings, ensure_dir, wrap_text, get_timestamp_filename

logger = get_logger("VideoBuilder")


class VideoBuilder:
    """Builds Instagram Reels videos with motion and text overlays."""
    
    def __init__(self):
        self.settings = load_settings()
        self.video_config = self.settings['video']
        
        # Video settings
        self.duration = self.video_config.get('duration_seconds', 10)
        self.fps = self.video_config.get('fps', 30)
        self.width = self.settings['image']['output_width']
        self.height = self.settings['image']['output_height']
        
        # Ken Burns settings
        self.zoom_factor = self.video_config.get('zoom_factor', 1.15)
        
        # Text settings
        self.text_color = self.video_config.get('text_color', '#FFFFFF')
        self.stroke_color = self.video_config.get('text_stroke_color', '#000000')
        self.stroke_width = self.video_config.get('text_stroke_width', 3)
        
        # Paths
        project_root = Path(__file__).parent.parent
        self.output_dir = project_root / self.settings['paths']['output']
        self.fonts_dir = project_root / self.settings['paths']['fonts']
        
        # Ensure output directories exist
        ensure_dir(self.output_dir / "videos")
        ensure_dir(self.output_dir / "thumbnails")
    
    def build_video(
        self,
        image_path: Path,
        content: Dict,
        audio_info: Dict = None,
        output_name: str = None
    ) -> Tuple[Path, Path]:
        """
        Build a complete video with Ken Burns effect, text overlay, and audio.
        
        Args:
            image_path: Path to the background image
            content: Content dict with quote, author, motivation
            audio_info: Audio selection info from AudioSelector
            output_name: Optional custom output filename
            
        Returns:
            Tuple of (video_path, thumbnail_path)
        """
        
        logger.info(f"Building video from {image_path.name}")
        
        # Extract content
        quote = content.get('quote', '')
        author = content.get('author', '')
        motivation = content.get('motivation', '')
        
        # Generate output filename
        if output_name is None:
            output_name = get_timestamp_filename("reel", "mp4")
        
        video_output = self.output_dir / "videos" / output_name
        thumbnail_output = self.output_dir / "thumbnails" / output_name.replace('.mp4', '.jpg')
        
        # Create text overlays (main and motivation separate for timing)
        overlay_path = self._create_text_overlay(quote, author, motivation)
        motivation_overlay_path = self._create_motivation_overlay(motivation)
        
        try:
            # Build video with Ken Burns effect
            temp_video = self._apply_ken_burns(image_path)
            
            # Add vignette effect
            video_with_vignette = self._add_vignette(temp_video)
            
            # Add subtle randomized digital glitch effect
            video_with_glitch = self._add_glitch_effect(video_with_vignette)
            
            # Add dramatic fade in/out to video
            video_with_fades = self._add_video_fades(video_with_glitch)
            
            # Add main text overlay (quote + author intro)
            video_with_text = self._add_overlay(video_with_fades, overlay_path)
            
            # Add motivation overlay with delayed fade-in (appears after 2 seconds)
            video_with_motivation = self._add_delayed_overlay(video_with_text, motivation_overlay_path, delay=2.0)
            
            # Add audio
            if audio_info and audio_info.get('path'):
                final_video = self._add_audio(
                    video_with_motivation,
                    audio_info['path'],
                    audio_info.get('volume', 0.3),
                    audio_info.get('fade_in', 1.0),
                    audio_info.get('fade_out', 2.0)
                )
            elif audio_info and audio_info.get('generate_silent'):
                final_video = self._add_silent_audio(video_with_motivation)
            else:
                final_video = video_with_motivation
            
            # Move to final output
            shutil.move(final_video, video_output)
            
            # Generate thumbnail from middle frame of final video
            self._generate_thumbnail(video_output, thumbnail_output)
            
            logger.info(f"Video built successfully: {video_output}")
            return video_output, thumbnail_output
            
        except Exception as e:
            logger.error(f"Video build failed: {str(e)}")
            raise
        
        finally:
            # Cleanup temp files
            for p in [overlay_path, motivation_overlay_path]:
                if p.exists():
                    os.remove(p)
    
    def _create_text_overlay(self, quote: str, author: str, motivation: str = "") -> Path:
        """Create a transparent PNG with text overlay and soft glow effect.
        
        Fonts:
        - Intro (author citation): Comico-Regular.ttf
        - Quote: Panchang-Regular.ttf
        """
        from PIL import ImageFilter
        
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        padding = 80
        max_text_width = self.width - (padding * 2)
        
        # Fixed font paths
        project_root = Path(__file__).parent.parent
        intro_font_path = project_root / "assets/fonts/Comico-Regular.ttf"
        quote_font_path = project_root / "assets/fonts/Panchang-Regular.ttf"
        
        # Get dynamic sizes for quote font
        intro_font, quote_font = self._get_dynamic_fonts(str(quote_font_path), quote, max_text_width)
        
        # Load intro font at appropriate size (smaller than quote)
        quote_size = quote_font.size if hasattr(quote_font, 'size') else 60
        intro_size = max(int(quote_size * 0.55), 28)
        
        try:
            intro_font = ImageFont.truetype(str(intro_font_path), intro_size)
        except:
            intro_font = ImageFont.truetype(str(quote_font_path), intro_size)
        
        # Wrap quote text
        wrapped_quote = self._wrap_text_to_width(quote, quote_font, max_text_width)
        
        # Calculate line height
        test_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bbox = test_draw.textbbox((0, 0), "Ayg", font=quote_font)
        line_height = int((bbox[3] - bbox[1]) * 1.25)
        
        # Positions - intro at 22%, more space before quote
        intro_y = int(self.height * 0.22)
        
        # Get intro height for spacing
        intro_text = f"— {author}"
        intro_bbox = test_draw.textbbox((0, 0), intro_text, font=intro_font)
        intro_height = intro_bbox[3] - intro_bbox[1]
        
        # Quote starts with more spacing after intro
        quote_y = intro_y + intro_height + 50
        
        # Create glow layer
        glow_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        
        def draw_centered_text(draw, text, y, font, fill):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = max(padding, (self.width - text_width) // 2)
            draw.text((text_x, y), text, font=font, fill=fill)
            return text_x
        
        # Draw intro
        intro_x = draw_centered_text(glow_draw, intro_text, intro_y, intro_font, (0, 0, 0, 255))
        
        # Draw quote with quotation marks
        quote_positions = []
        for i, line in enumerate(wrapped_quote):
            display_line = line
            if i == 0:
                display_line = f'"{line}'
            if i == len(wrapped_quote) - 1:
                display_line = f'{display_line}"'
            
            y_pos = quote_y + (i * line_height)
            text_x = draw_centered_text(glow_draw, display_line, y_pos, quote_font, (0, 0, 0, 255))
            quote_positions.append((display_line, text_x, y_pos))
        
        # Apply HEAVY blur for large glow
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=20))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=15))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=10))
        
        # Many passes for strong glow
        for _ in range(6):
            overlay = Image.alpha_composite(overlay, glow_layer)
            overlay = Image.alpha_composite(overlay, glow_layer)
        
        # Draw crisp white text on top
        text_draw = ImageDraw.Draw(overlay)
        text_draw.text((intro_x, intro_y), intro_text, font=intro_font, fill=(255, 255, 255, 255))
        
        for display_line, text_x, y_pos in quote_positions:
            text_draw.text((text_x, y_pos), display_line, font=quote_font, fill=(255, 255, 255, 255))
        
        # Add watermark at bottom
        watermark_text = "real applications in caption"
        watermark_size = 24
        try:
            watermark_font = ImageFont.truetype(str(quote_font_path), watermark_size)
        except:
            watermark_font = ImageFont.load_default()
        
        watermark_bbox = text_draw.textbbox((0, 0), watermark_text, font=watermark_font)
        watermark_width = watermark_bbox[2] - watermark_bbox[0]
        watermark_x = (self.width - watermark_width) // 2
        watermark_y = int(self.height * 0.95)
        text_draw.text((watermark_x, watermark_y), watermark_text, font=watermark_font, fill=(255, 255, 255, 180))
        
        # Save overlay
        overlay_path = Path(tempfile.gettempdir()) / "stoic_overlay.png"
        overlay.save(overlay_path, 'PNG')
        
        return overlay_path
    
    def _get_dynamic_fonts(self, font_path: str, quote: str, max_width: int):
        """Get dynamically sized fonts that fit within frame zones.
        
        Layout zones (of 1920px height):
        - Intro zone: 25-30% (starts ~480px)
        - Quote zone: 30-62% (~580px to ~1190px = 610px max)
        - Motivation zone: 68-85% (separate overlay)
        """
        
        padding = 80
        usable_width = self.width - (padding * 2)  # ~920px on 1080 wide
        quote_zone_height = int(self.height * 0.32)  # ~615px for quote
        
        try:
            # Iteratively find the largest font that fits
            for quote_size in range(72, 32, -4):  # Start big, reduce
                test_font = ImageFont.truetype(font_path, quote_size)
                
                # Wrap text at this size
                wrapped = self._wrap_text_to_width(quote, test_font, usable_width)
                
                # Measure line height
                test_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
                bbox = test_draw.textbbox((0, 0), "Ayg", font=test_font)
                line_height = int((bbox[3] - bbox[1]) * 1.25)
                
                total_height = len(wrapped) * line_height
                
                if total_height <= quote_zone_height:
                    # This size fits!
                    intro_size = max(int(quote_size * 0.65), 32)
                    
                    intro_font = ImageFont.truetype(font_path, intro_size)
                    quote_font = ImageFont.truetype(font_path, quote_size)
                    
                    logger.info(f"Font sizes - quote: {quote_size}px ({len(wrapped)} lines), intro: {intro_size}px")
                    return intro_font, quote_font
            
            # Fallback to minimum
            intro_font = ImageFont.truetype(font_path, 32)
            quote_font = ImageFont.truetype(font_path, 36)
            return intro_font, quote_font
            
        except Exception as e:
            logger.warning(f"Font loading failed ({e}), using defaults")
            return ImageFont.load_default(), ImageFont.load_default()
    
    def _wrap_text_to_width(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width pixels."""
        
        words = text.split()
        lines = []
        current_line = []
        
        test_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = test_draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _create_motivation_overlay(self, motivation: str) -> Path:
        """Create a separate overlay for the motivation text (for delayed fade-in).
        Uses Comico-Regular font with BLACK glow for readability."""
        from PIL import ImageFilter
        
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        if not motivation:
            overlay_path = Path(tempfile.gettempdir()) / "stoic_motivation.png"
            overlay.save(overlay_path, 'PNG')
            return overlay_path
        
        padding = 80
        max_text_width = self.width - (padding * 2)
        
        # Fixed font: Comico-Regular for motivation
        project_root = Path(__file__).parent.parent
        font_path = str(project_root / "assets/fonts/Comico-Regular.ttf")
        
        # Motivation zone: 68% to 88% of height
        motivation_zone_height = int(self.height * 0.18)
        motivation_y_start = int(self.height * 0.68)
        
        try:
            # Find largest font that fits
            for font_size in range(52, 28, -4):
                test_font = ImageFont.truetype(font_path, font_size)
                wrapped = self._wrap_text_to_width(motivation, test_font, max_text_width)
                
                test_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
                bbox = test_draw.textbbox((0, 0), "Ayg", font=test_font)
                line_height = int((bbox[3] - bbox[1]) * 1.3)
                
                total_height = len(wrapped) * line_height
                
                if total_height <= motivation_zone_height:
                    motivation_font = test_font
                    logger.info(f"Motivation font: {font_size}px ({len(wrapped)} lines)")
                    break
            else:
                motivation_font = ImageFont.truetype(font_path, 32)
                wrapped = self._wrap_text_to_width(motivation, motivation_font, max_text_width)
                font_size = 32
                
        except Exception as e:
            logger.warning(f"Font loading failed ({e})")
            motivation_font = ImageFont.load_default()
            wrapped = [motivation]
            font_size = 32
        
        # Recalculate line height
        test_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bbox = test_draw.textbbox((0, 0), "Ayg", font=motivation_font)
        line_height = int((bbox[3] - bbox[1]) * 1.3)
        
        # Center vertically in motivation zone
        total_text_height = len(wrapped) * line_height
        motivation_y = motivation_y_start + (motivation_zone_height - total_text_height) // 2
        
        # Create BLACK glow layer (changed from white)
        glow_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        
        motivation_positions = []
        for i, line in enumerate(wrapped):
            bbox = glow_draw.textbbox((0, 0), line, font=motivation_font)
            text_width = bbox[2] - bbox[0]
            text_x = max(padding, (self.width - text_width) // 2)
            y_pos = motivation_y + (i * line_height)
            # BLACK glow
            glow_draw.text((text_x, y_pos), line, font=motivation_font, fill=(0, 0, 0, 255))
            motivation_positions.append((line, text_x, y_pos))
        
        # Apply HEAVY blur for large glow
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=25))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=20))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=15))
        
        # Many passes for strong glow
        for _ in range(8):
            overlay = Image.alpha_composite(overlay, glow_layer)
        
        # Draw RED text
        text_draw = ImageDraw.Draw(overlay)
        red_color = (220, 40, 40, 255)
        for line, text_x, y_pos in motivation_positions:
            text_draw.text((text_x, y_pos), line, font=motivation_font, fill=red_color)
        
        overlay_path = Path(tempfile.gettempdir()) / "stoic_motivation.png"
        overlay.save(overlay_path, 'PNG')
        
        return overlay_path
    
    def _get_font_path(self) -> str:
        """Get path to font file - randomly cycles through available fonts, excluding archive."""
        import random
        
        # Find available fonts (excluding archive folder)
        available = []
        if self.fonts_dir.exists():
            for f in self.fonts_dir.iterdir():
                if f.suffix.lower() in ['.ttf', '.otf'] and f.is_file():
                    # Skip files in archive folder
                    if 'archive' not in str(f).lower():
                        available.append(f)
        
        if available:
            selected = random.choice(available)
            logger.info(f"Using font: {selected.name}")
            return str(selected)
        
        # Fallback to system fonts
        system_fonts = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        
        for font in system_fonts:
            if os.path.exists(font):
                return font
        
        return None  # Will use default
    
    def _apply_ken_burns(self, image_path: Path) -> Path:
        """Apply Ken Burns (zoom/pan) effect using FFmpeg."""
        
        output_path = Path(tempfile.gettempdir()) / "stoic_ken_burns.mp4"
        
        # Calculate zoom parameters
        total_frames = self.duration * self.fps
        
        # Zoom in effect
        # zoompan filter: z increases from 1 to zoom_factor over duration
        zoom_expr = f"'zoom+{(self.zoom_factor - 1) / total_frames}'"
        
        # Pan slightly (optional subtle movement)
        # Center the zoom
        pan_x = f"'iw/2-(iw/zoom/2)'"
        pan_y = f"'ih/2-(ih/zoom/2)'"
        
        # FFmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', str(image_path),
            '-vf', (
                f"scale=8000:-1,"  # Scale up for smooth zoom
                f"zoompan=z={zoom_expr}:"
                f"x={pan_x}:y={pan_y}:"
                f"d={total_frames}:"
                f"s={self.width}x{self.height}:"
                f"fps={self.fps}"
            ),
            '-t', str(self.duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            str(output_path)
        ]
        
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg Ken Burns failed: {result.stderr}")
            raise RuntimeError(f"Ken Burns effect failed: {result.stderr}")
        
        return output_path
    
    def _add_vignette(self, video_path: Path) -> Path:
        """Add a dark vignette (fade to black around edges) for dramatic effect."""
        
        output_path = Path(tempfile.gettempdir()) / "stoic_vignette.mp4"
        
        # FFmpeg vignette filter
        # angle: pi/2 gives a nice oval vignette
        # mode: forward darkens the edges
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', 'vignette=PI/4:mode=forward',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Vignette effect failed, continuing without: {result.stderr}")
            return video_path
        
        # Clean up input video
        os.remove(video_path)
        
        return output_path
    
    def _add_glitch_effect(self, video_path: Path) -> Path:
        """Add a quick, cinematic glitch effect at a random point in the video."""
        import random
        
        output_path = Path(tempfile.gettempdir()) / "stoic_glitch.mp4"
        
        # Random timing for the glitch (between 2-7 seconds into the video)
        glitch_start = random.uniform(2.0, 7.0)
        glitch_duration = random.uniform(0.15, 0.3)  # Very quick: 150-300ms
        glitch_end = glitch_start + glitch_duration
        
        # Choose a glitch style
        glitch_styles = [
            # RGB split/chromatic aberration
            ("rgb_split", f"chromashift=cbh=8:cbv=4:crh=-8:crv=-4"),
            # Horizontal displacement
            ("h_displacement", f"rgbashift=rh=12:bh=-12:rv=0:bv=0"),
            # Color inversion flash
            ("color_flash", f"negate"),
            # Heavy RGB separation
            ("rgb_heavy", f"chromashift=cbh=15:cbv=8:crh=-15:crv=-8"),
            # Vertical tear effect
            ("v_tear", f"rgbashift=rv=10:bv=-10:rh=0:bh=0"),
        ]
        
        glitch_name, glitch_filter = random.choice(glitch_styles)
        
        logger.info(f"Applying glitch effect: {glitch_name} at {glitch_start:.2f}s for {glitch_duration:.2f}s")
        
        # Apply glitch only during the specified time window
        filter_str = f"{glitch_filter}:enable='between(t,{glitch_start},{glitch_end})'"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', filter_str,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Glitch effect '{glitch_name}' failed: {result.stderr[:150]}")
            # Try simpler RGB shift as fallback
            fallback_filter = f"rgbashift=rh=10:bh=-10:enable='between(t,{glitch_start},{glitch_end})'"
            cmd_fallback = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-vf', fallback_filter,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'medium',
                '-crf', '23',
                str(output_path)
            ]
            result = subprocess.run(cmd_fallback, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Glitch fallback also failed, continuing without")
                return video_path
        
        os.remove(video_path)
        return output_path
    
    def _add_video_fades(self, video_path: Path) -> Path:
        """Add dramatic fade in from black and fade out to black."""
        
        output_path = Path(tempfile.gettempdir()) / "stoic_fades.mp4"
        
        # Fade in for first 1.5 seconds, fade out for last 2 seconds
        fade_in_duration = 1.5
        fade_out_start = self.duration - 2.0
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', f'fade=t=in:st=0:d={fade_in_duration},fade=t=out:st={fade_out_start}:d=2',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Video fades failed, continuing without: {result.stderr}")
            return video_path
        
        os.remove(video_path)
        return output_path
    
    def _add_delayed_overlay(self, video_path: Path, overlay_path: Path, delay: float = 2.0) -> Path:
        """Add an overlay that fades in after a delay."""
        
        output_path = Path(tempfile.gettempdir()) / "stoic_with_motivation.mp4"
        
        # Fade duration for the motivation text
        fade_duration = 1.0
        
        # Use enable expression to hide overlay until delay, then fade in
        # The overlay starts invisible, becomes visible and fades in at delay
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-loop', '1', '-t', str(self.duration), '-i', str(overlay_path),
            '-filter_complex', 
            f"[1:v]format=rgba,colorchannelmixer=aa=0:enable='lt(t,{delay})',"
            f"fade=t=in:st={delay}:d={fade_duration}:alpha=1[ov];"
            f"[0:v][ov]overlay=0:0:format=auto:enable='gte(t,0)'",
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            '-t', str(self.duration),
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Delayed overlay method 1 failed: {result.stderr[:200]}")
            
            # Alternative: Use timeline editing with enable
            cmd_alt = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-loop', '1', '-t', str(self.duration), '-i', str(overlay_path),
                '-filter_complex', 
                f"[1:v]format=rgba[ov];"
                f"[0:v][ov]overlay=0:0:format=auto:enable='gte(t,{delay})'",
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'medium',
                '-crf', '23',
                '-t', str(self.duration),
                str(output_path)
            ]
            result = subprocess.run(cmd_alt, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Delayed overlay method 2 also failed: {result.stderr[:200]}, skipping motivation")
                return video_path
        
        os.remove(video_path)
        return output_path
    
    def _add_overlay(self, video_path: Path, overlay_path: Path) -> Path:
        """Add text overlay to video with fade-in matching the video fade."""
        
        output_path = Path(tempfile.gettempdir()) / "stoic_with_text.mp4"
        
        # Fade in overlay to match video fade (1.5 seconds)
        fade_in_duration = 1.5
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-loop', '1', '-t', str(self.duration), '-i', str(overlay_path),
            '-filter_complex', 
            f'[1:v]format=rgba,fade=t=in:st=0:d={fade_in_duration}:alpha=1[ov];[0:v][ov]overlay=0:0:format=auto',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            '-t', str(self.duration),
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg overlay failed: {result.stderr}")
            raise RuntimeError(f"Overlay failed: {result.stderr}")
        
        # Clean up input video
        os.remove(video_path)
        
        return output_path
    
    def _add_audio(
        self,
        video_path: Path,
        audio_path: Path,
        volume: float,
        fade_in: float,
        fade_out: float
    ) -> Path:
        """Add audio to video with volume and fades."""
        
        output_path = Path(tempfile.gettempdir()) / "stoic_final.mp4"
        
        # Audio filter for volume and fades
        audio_filter = f"volume={volume}"
        
        if fade_in > 0:
            audio_filter += f",afade=t=in:st=0:d={fade_in}"
        
        if fade_out > 0:
            fade_start = self.duration - fade_out
            audio_filter += f",afade=t=out:st={fade_start}:d={fade_out}"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-af', audio_filter,
            '-t', str(self.duration),
            '-shortest',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg audio failed: {result.stderr}")
            raise RuntimeError(f"Audio addition failed: {result.stderr}")
        
        # Clean up
        os.remove(video_path)
        
        return output_path
    
    def _add_silent_audio(self, video_path: Path) -> Path:
        """Add silent audio track (for Instagram compatibility)."""
        
        output_path = Path(tempfile.gettempdir()) / "stoic_final.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-f', 'lavfi',
            '-i', f'anullsrc=r=44100:cl=stereo',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-t', str(self.duration),
            '-shortest',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # If silent audio fails, just return video without audio
            logger.warning(f"Silent audio failed, returning video without audio")
            return video_path
        
        os.remove(video_path)
        return output_path
    
    def _generate_thumbnail(
        self,
        video_path: Path,
        output_path: Path
    ):
        """Extract a frame from the middle of the video to use as thumbnail/cover."""
        
        # Get frame from middle of video (5 seconds into a 10 second video)
        middle_time = self.duration / 2
        
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(middle_time),
            '-i', str(video_path),
            '-vframes', '1',
            '-q:v', '2',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Thumbnail extraction failed: {result.stderr}")
            raise RuntimeError(f"Thumbnail extraction failed: {result.stderr}")
        
        logger.info(f"Thumbnail generated from video frame: {output_path}")
    
    def _create_vignette_overlay(self) -> Image:
        """Create a vignette overlay image for thumbnails."""
        import math
        
        vignette = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        center_x = self.width // 2
        center_y = self.height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(self.height):
            for x in range(self.width):
                # Calculate distance from center
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                # Normalize and apply curve
                norm_dist = dist / max_dist
                # Stronger vignette at edges
                alpha = int(min(255, norm_dist**1.5 * 200))
                vignette.putpixel((x, y), (0, 0, 0, alpha))
        
        return vignette


def build_video(
    image_path: Path,
    content: Dict,
    audio_info: Dict = None
) -> Tuple[Path, Path]:
    """Convenience function to build video."""
    builder = VideoBuilder()
    return builder.build_video(image_path, content, audio_info)


if __name__ == "__main__":
    # Test video builder (requires FFmpeg and sample image)
    print("Video Builder Test")
    print("==================")
    
    # Check for FFmpeg
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )
        print("✓ FFmpeg found")
    except FileNotFoundError:
        print("✗ FFmpeg not found - please install FFmpeg")
        exit(1)
    
    builder = VideoBuilder()
    print(f"Output directory: {builder.output_dir}")
    print(f"Video dimensions: {builder.width}x{builder.height}")
    print(f"Duration: {builder.duration}s @ {builder.fps}fps")
    
    print("\nTo test video generation, provide a sample image:")
    print("  from scripts.video_builder import build_video")
    print("  from pathlib import Path")
    print("  video, thumb = build_video(")
    print("      Path('sample.jpg'),")
    print("      'The obstacle is the way.',")
    print("      'Marcus Aurelius'")
    print("  )")

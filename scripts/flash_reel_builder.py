"""
Flash Reel Builder for StoicAlgo
Generates dramatic flash-style reels with synchronized voiceover and word reveals.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from scripts.logger import get_logger
from scripts.utils import load_settings, ensure_dir, get_timestamp_filename
from scripts.voiceover_service import VoiceoverService, VoiceoverResult, WordTiming

logger = get_logger("FlashReelBuilder")


@dataclass
class FlashSegment:
    """A segment of the flash reel with image and text."""
    image_path: Path
    start_ms: int
    end_ms: int
    words: str
    is_dramatic_pause: bool = False


class FlashReelBuilder:
    """Builds dramatic flash-style reels with voiceover and word reveals."""
    
    def __init__(self):
        self.settings = load_settings()
        self.flash_settings = self.settings.get('flash_reel', {})
        self.video_config = self.settings['video']
        
        self.width = self.settings['image']['output_width']
        self.height = self.settings['image']['output_height']
        self.fps = self.video_config.get('fps', 30)
        
        self.flash_duration_ms = self.flash_settings.get('image_flash_duration_ms', 300)
        self.words_per_flash = self.flash_settings.get('words_per_flash', 2)
        
        project_root = Path(__file__).parent.parent
        self.output_dir = project_root / self.settings['paths']['output']
        self.fonts_dir = project_root / self.settings['paths']['fonts']
        self.audio_dir = project_root / self.settings['paths']['audio']
        
        ensure_dir(self.output_dir / "videos")
        ensure_dir(self.output_dir / "thumbnails")
        
        self.voiceover_service = VoiceoverService()
    
    def build_flash_reel(
        self,
        images: List[Path],
        content: Dict,
        background_audio_path: Optional[Path] = None,
        output_name: str = None
    ) -> Tuple[Path, Path]:
        """
        Build a complete flash reel video.
        
        Args:
            images: List of image paths for flash sequence
            content: Content dict with quote, author, motivation
            background_audio_path: Optional path to dramatic background music
            output_name: Optional custom output filename
            
        Returns:
            Tuple of (video_path, thumbnail_path)
        """
        quote = content.get('quote', '')
        motivation = content.get('motivation', '')
        author = content.get('author', '')
        
        logger.info(f"Building flash reel with {len(images)} images")
        
        if output_name is None:
            output_name = get_timestamp_filename("flash_reel", "mp4")
        
        video_output = self.output_dir / "videos" / output_name
        thumbnail_output = self.output_dir / "thumbnails" / output_name.replace('.mp4', '.jpg')
        
        try:
            voiceover_result = self.voiceover_service.generate_voiceover(
                quote_text=quote,
                motivation_text=motivation,
                author=author
            )
            
            if not voiceover_result:
                raise RuntimeError("Voiceover generation failed")
            
            logger.info(f"Voiceover duration: {voiceover_result.total_duration_ms}ms")
            
            display_timings = [
                t for t in voiceover_result.word_timings
                if not t.is_ending_phrase and not t.is_intro
            ]
            
            grouped_timings = self.voiceover_service.group_words_for_display(
                display_timings,
                self.words_per_flash
            )
            
            segments = self._create_segments_independent(
                images,
                grouped_timings,
                voiceover_result.total_duration_ms
            )
            
            base_video = self._create_flash_video(segments, voiceover_result)
            
            video_with_text = self._add_word_reveals(
                base_video, 
                grouped_timings,
                author,
                voiceover_result.total_duration_ms
            )
            
            video_with_effects = self._add_visual_effects(video_with_text)
            
            final_video = self._mix_audio(
                video_with_effects,
                voiceover_result.audio_path,
                background_audio_path
            )
            
            shutil.move(final_video, video_output)
            
            self._generate_thumbnail(video_output, thumbnail_output)
            
            logger.info(f"Flash reel built successfully: {video_output}")
            return video_output, thumbnail_output
            
        except Exception as e:
            logger.error(f"Flash reel build failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_segments_independent(
        self,
        images: List[Path],
        word_timings: List[WordTiming],
        total_duration_ms: int
    ) -> List[FlashSegment]:
        """
        Create flash segments with images cycling independently of words.
        Images flash at fixed intervals while words overlay based on speech timing.
        """
        image_interval_ms = self.flash_duration_ms
        
        num_image_changes = max(1, total_duration_ms // image_interval_ms)
        
        segments = []
        current_ms = 0
        image_index = 0
        
        for i in range(num_image_changes):
            start_ms = current_ms
            end_ms = min(current_ms + image_interval_ms, total_duration_ms)
            
            words_in_segment = ""
            is_pause = False
            for timing in word_timings:
                if timing.is_dramatic_pause:
                    if timing.start_ms <= start_ms < timing.end_ms:
                        is_pause = True
                elif timing.start_ms <= start_ms < timing.end_ms or (timing.start_ms >= start_ms and timing.end_ms <= end_ms):
                    if words_in_segment:
                        words_in_segment += " "
                    words_in_segment += timing.text
            
            segments.append(FlashSegment(
                image_path=images[image_index % len(images)],
                start_ms=start_ms,
                end_ms=end_ms,
                words=words_in_segment,
                is_dramatic_pause=is_pause
            ))
            
            image_index += 1
            current_ms = end_ms
        
        if current_ms < total_duration_ms:
            segments.append(FlashSegment(
                image_path=images[image_index % len(images)],
                start_ms=current_ms,
                end_ms=total_duration_ms,
                words="",
                is_dramatic_pause=False
            ))
        
        return segments
    
    def _create_flash_video(
        self,
        segments: List[FlashSegment],
        voiceover_result: VoiceoverResult
    ) -> Path:
        """Create the base video with flashing images."""
        output_path = Path(tempfile.gettempdir()) / "flash_base.mp4"
        
        total_duration_sec = voiceover_result.total_duration_ms / 1000.0
        
        concat_file = Path(tempfile.gettempdir()) / "flash_concat.txt"
        segment_files = []
        
        for i, segment in enumerate(segments):
            duration_sec = (segment.end_ms - segment.start_ms) / 1000.0
            if duration_sec <= 0:
                continue
            
            segment_path = Path(tempfile.gettempdir()) / f"segment_{i:04d}.mp4"
            
            prepared_image = self._prepare_image(segment.image_path)
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', str(prepared_image),
                '-t', str(duration_sec),
                '-vf', f'scale={self.width}:{self.height}:force_original_aspect_ratio=increase,crop={self.width}:{self.height},setsar=1',
                '-r', str(self.fps),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'ultrafast',
                '-an',
                str(segment_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Segment {i} creation failed: {result.stderr}")
                continue
            
            segment_files.append(segment_path)
            
            if prepared_image != segment.image_path:
                prepared_image.unlink(missing_ok=True)
        
        with open(concat_file, 'w') as f:
            for seg_file in segment_files:
                f.write(f"file '{seg_file.absolute()}'\n")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', str(concat_file),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        for seg_file in segment_files:
            seg_file.unlink(missing_ok=True)
        concat_file.unlink(missing_ok=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Video concatenation failed: {result.stderr}")
        
        return output_path
    
    def _prepare_image(self, image_path: Path) -> Path:
        """Prepare an image for video (resize/crop to 1080x1920)."""
        output_path = Path(tempfile.gettempdir()) / f"prepared_{image_path.name}"
        
        img = Image.open(image_path)
        
        target_aspect = self.width / self.height
        img_aspect = img.width / img.height
        
        if img_aspect > target_aspect:
            new_height = self.height
            new_width = int(new_height * img_aspect)
        else:
            new_width = self.width
            new_height = int(new_width / img_aspect)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        left = (new_width - self.width) // 2
        top = (new_height - self.height) // 2
        img = img.crop((left, top, left + self.width, top + self.height))
        
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[3])
            img = background
        
        img.save(output_path, 'PNG')
        return output_path
    
    def _add_word_reveals(
        self,
        video_path: Path,
        word_timings: List[WordTiming],
        author: str,
        total_duration_ms: int
    ) -> Path:
        """Add synchronized word reveals to the video."""
        output_path = Path(tempfile.gettempdir()) / "flash_with_text.mp4"
        
        text_style = self.flash_settings.get('text_style', {})
        font_path = text_style.get('font', 'assets/fonts/Panchang-Regular.ttf')
        text_color = text_style.get('color', '#FFFFFF')
        glow_color = text_style.get('glow_color', '#FF4444')
        size_multiplier = text_style.get('size_multiplier', 1.3)
        
        drawtext_filters = []
        
        font_size = int(72 * size_multiplier)
        
        for timing in word_timings:
            if timing.is_dramatic_pause or not timing.text:
                continue
            
            start_sec = timing.start_ms / 1000.0
            end_sec = timing.end_ms / 1000.0
            
            escaped_text = self._escape_ffmpeg_text(timing.text.upper())
            
            word_filter = (
                f"drawtext=text='{escaped_text}':"
                f"fontfile='{font_path}':"
                f"fontsize={font_size}:"
                f"fontcolor=white:"
                f"borderw=4:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2:"
                f"enable='between(t,{start_sec},{end_sec})'"
            )
            drawtext_filters.append(word_filter)
        
        if not drawtext_filters:
            return video_path
        
        filter_chain = ','.join(drawtext_filters)
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', filter_chain,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'copy',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Word reveal overlay failed: {result.stderr}")
            return video_path
        
        return output_path
    
    def _escape_ffmpeg_text(self, text: str) -> str:
        """Escape special characters for FFmpeg drawtext filter."""
        text = text.replace("'", "'\\''")
        text = text.replace(":", "\\:")
        text = text.replace("\\", "\\\\")
        return text
    
    def _add_visual_effects(self, video_path: Path) -> Path:
        """Add visual effects like vignette and flash transitions."""
        output_path = Path(tempfile.gettempdir()) / "flash_with_effects.mp4"
        
        filter_chain = (
            "vignette=PI/4,"
            "eq=brightness=0.02:contrast=1.1:saturation=0.9"
        )
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', filter_chain,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'copy',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Visual effects failed: {result.stderr}")
            return video_path
        
        return output_path
    
    def _mix_audio(
        self,
        video_path: Path,
        voiceover_path: Path,
        background_audio_path: Optional[Path] = None
    ) -> Path:
        """Mix voiceover and background audio with the video."""
        output_path = Path(tempfile.gettempdir()) / "flash_final.mp4"
        
        if background_audio_path and background_audio_path.exists():
            bg_volume = self.flash_settings.get('background_audio', {}).get('volume', 0.25)
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-i', str(voiceover_path),
                '-i', str(background_audio_path),
                '-filter_complex', (
                    f"[1:a]volume=1.0[voice];"
                    f"[2:a]volume={bg_volume},afade=t=in:st=0:d=1,afade=t=out:st=8:d=2[bg];"
                    f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
                ),
                '-map', '0:v',
                '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                str(output_path)
            ]
        else:
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-i', str(voiceover_path),
                '-map', '0:v',
                '-map', '1:a',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                str(output_path)
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Audio mixing failed: {result.stderr}")
            raise RuntimeError(f"Audio mixing failed: {result.stderr}")
        
        return output_path
    
    def _generate_thumbnail(self, video_path: Path, output_path: Path) -> None:
        """Generate thumbnail from middle of video."""
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-ss', '2',
            '-vframes', '1',
            '-q:v', '2',
            str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True)
    
    def select_category_images(
        self,
        category: str,
        count: int = 15
    ) -> List[Path]:
        """Select images from a specific category for flash sequence."""
        project_root = Path(__file__).parent.parent
        images_dir = project_root / self.settings['paths']['images'] / category
        
        if not images_dir.exists():
            logger.warning(f"Category folder not found: {images_dir}")
            images_dir = project_root / self.settings['paths']['images']
        
        all_images = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
        
        all_images = [img for img in all_images if 'used' not in str(img)]
        
        if len(all_images) < count:
            all_images = all_images * (count // len(all_images) + 1)
        
        import random
        random.shuffle(all_images)
        
        return all_images[:count]


if __name__ == "__main__":
    builder = FlashReelBuilder()
    
    images = builder.select_category_images("warriors", count=10)
    
    content = {
        'quote': "The obstacle is the way",
        'author': "Marcus Aurelius",
        'motivation': "What blocks your path becomes your greatest teacher"
    }
    
    if images:
        print(f"Found {len(images)} images")
        video_path, thumb_path = builder.build_flash_reel(images, content)
        print(f"Video: {video_path}")
        print(f"Thumbnail: {thumb_path}")
    else:
        print("No images found")

"""
Voiceover Service for StoicAlgo Flash Reels
Generates dramatic voiceover using fal.ai Chatterbox HD TTS.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import fal_client

from scripts.logger import get_logger
from scripts.utils import load_settings, ensure_dir

logger = get_logger("VoiceoverService")

os.environ['FAL_KEY'] = os.environ.get('FAL_API_KEY', '')


@dataclass
class WordTiming:
    """Represents timing for a word or phrase in the voiceover."""
    text: str
    start_ms: int
    end_ms: int
    is_dramatic_pause: bool = False
    is_ending_phrase: bool = False
    is_intro: bool = False


@dataclass
class VoiceoverResult:
    """Result of voiceover generation."""
    audio_path: Path
    word_timings: List[WordTiming]
    total_duration_ms: int
    quote_end_ms: int
    motivation_start_ms: int


class VoiceoverService:
    """Generates dramatic voiceover for flash reels using fal.ai TTS."""
    
    def __init__(self):
        self.settings = load_settings()
        self.flash_settings = self.settings.get('flash_reel', {})
        self.voice_settings = self.flash_settings.get('voice', {})
        
        self.output_dir = Path(self.settings['paths']['output']) / 'voiceover'
        ensure_dir(self.output_dir)
    
    def generate_voiceover(
        self,
        quote_text: str,
        motivation_text: str,
        author: str = "",
        ending_phrase: str = None
    ) -> Optional[VoiceoverResult]:
        """
        Generate dramatic voiceover for flash reel.
        
        Args:
            quote_text: The main quote to read
            motivation_text: The motivational follow-up text
            author: The author name for intro
            ending_phrase: Optional ending phrase (defaults to config)
            
        Returns:
            VoiceoverResult with audio path and word timings
        """
        if ending_phrase is None:
            ending_phrase = self.flash_settings.get(
                'ending_phrase',
                'read the caption for real world applications'
            )
        
        logger.info("Generating voiceover for flash reel...")
        
        try:
            audio_segments = []
            word_timings = []
            current_time_ms = 0
            
            if author:
                intro_text = f"As {author} once said..."
                intro_audio, intro_timings, intro_duration = self._generate_segment(
                    intro_text,
                    is_sinister=False,
                    is_intro=True
                )
                if intro_audio:
                    audio_segments.append(intro_audio)
                    for timing in intro_timings:
                        timing.start_ms += current_time_ms
                        timing.end_ms += current_time_ms
                        timing.is_intro = True
                        word_timings.append(timing)
                    current_time_ms += intro_duration
                    
                    intro_pause_ms = 400
                    word_timings.append(WordTiming(
                        text="",
                        start_ms=current_time_ms,
                        end_ms=current_time_ms + intro_pause_ms,
                        is_dramatic_pause=True
                    ))
                    current_time_ms += intro_pause_ms
            
            quote_audio, quote_timings, quote_duration = self._generate_segment(
                quote_text,
                is_sinister=False
            )
            if quote_audio:
                audio_segments.append(quote_audio)
                for timing in quote_timings:
                    timing.start_ms += current_time_ms
                    timing.end_ms += current_time_ms
                    word_timings.append(timing)
                current_time_ms += quote_duration
            
            quote_end_ms = current_time_ms
            
            dramatic_pause_ms = self.flash_settings.get('dramatic_pause_ms', 800)
            word_timings.append(WordTiming(
                text="",
                start_ms=current_time_ms,
                end_ms=current_time_ms + dramatic_pause_ms,
                is_dramatic_pause=True
            ))
            current_time_ms += dramatic_pause_ms
            
            motivation_start_ms = current_time_ms
            
            motivation_audio, motivation_timings, motivation_duration = self._generate_segment(
                motivation_text,
                is_sinister=True
            )
            if motivation_audio:
                audio_segments.append(motivation_audio)
                for timing in motivation_timings:
                    timing.start_ms += current_time_ms
                    timing.end_ms += current_time_ms
                    word_timings.append(timing)
                current_time_ms += motivation_duration
            
            ending_pause_ms = 300
            word_timings.append(WordTiming(
                text="",
                start_ms=current_time_ms,
                end_ms=current_time_ms + ending_pause_ms,
                is_dramatic_pause=True
            ))
            current_time_ms += ending_pause_ms
            
            ending_audio, ending_timings, ending_duration = self._generate_segment(
                ending_phrase,
                is_sinister=True,
                speed_factor=1.3
            )
            if ending_audio:
                audio_segments.append(ending_audio)
                for timing in ending_timings:
                    timing.start_ms += current_time_ms
                    timing.end_ms += current_time_ms
                    timing.is_ending_phrase = True
                    word_timings.append(timing)
                current_time_ms += ending_duration
            
            combined_audio_path = self._combine_audio_segments(
                audio_segments,
                dramatic_pause_ms
            )
            
            if combined_audio_path:
                logger.info(f"Voiceover generated: {combined_audio_path}")
                return VoiceoverResult(
                    audio_path=combined_audio_path,
                    word_timings=word_timings,
                    total_duration_ms=current_time_ms,
                    quote_end_ms=quote_end_ms,
                    motivation_start_ms=motivation_start_ms
                )
            
        except Exception as e:
            logger.error(f"Voiceover generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _generate_segment(
        self,
        text: str,
        is_sinister: bool = False,
        speed_factor: float = 1.0,
        is_intro: bool = False
    ) -> Tuple[Optional[Path], List[WordTiming], int]:
        """
        Generate a single audio segment using deep masculine voice.
        Uses ChatterboxHD with pre-built "Cliff" voice for deep masculine sound.
        
        Returns:
            Tuple of (audio_path, word_timings, duration_ms)
        """
        try:
            if is_sinister:
                exaggeration = self.voice_settings.get('sinister_exaggeration', 0.7)
                cfg = self.voice_settings.get('sinister_cfg', 0.35)
            elif is_intro:
                exaggeration = self.voice_settings.get('intro_exaggeration', 0.4)
                cfg = self.voice_settings.get('intro_cfg', 0.45)
            else:
                exaggeration = self.voice_settings.get('exaggeration', 0.5)
                cfg = self.voice_settings.get('cfg', 0.4)
            
            voice_name = self.voice_settings.get('voice', 'Cliff')
            
            logger.info(f"Generating TTS: '{text[:50]}...' (voice={voice_name}, sinister={is_sinister}, intro={is_intro})")
            
            result = fal_client.subscribe(
                'resemble-ai/chatterboxhd/text-to-speech',
                arguments={
                    'text': text,
                    'voice': voice_name,
                    'exaggeration': exaggeration,
                    'cfg': cfg,
                    'temperature': 0.75,
                    'high_quality_audio': True
                }
            )
            
            audio_url = None
            if result:
                if 'audio' in result and isinstance(result['audio'], dict):
                    audio_url = result['audio'].get('url')
                elif 'audio_url' in result:
                    audio_url = result['audio_url']
            
            if audio_url:
                
                import time
                ext = '.wav' if audio_url.endswith('.wav') else '.mp3'
                segment_path_raw = self.output_dir / f"segment_{int(time.time() * 1000)}_raw{ext}"
                segment_path = self.output_dir / f"segment_{int(time.time() * 1000)}.mp3"
                
                response = requests.get(audio_url, timeout=60)
                if response.status_code == 200:
                    with open(segment_path_raw, 'wb') as f:
                        f.write(response.content)
                    
                    import subprocess
                    subprocess.run([
                        'ffmpeg', '-y', '-i', str(segment_path_raw),
                        '-c:a', 'libmp3lame', '-q:a', '2',
                        str(segment_path)
                    ], capture_output=True)
                    
                    segment_path_raw.unlink(missing_ok=True)
                    
                    duration_ms = self._get_audio_duration_ms(segment_path)
                    
                    word_timings = self._estimate_word_timings(text, duration_ms)
                    
                    return segment_path, word_timings, duration_ms
            
        except Exception as e:
            logger.error(f"Segment generation failed: {e}")
        
        return None, [], 0
    
    def _estimate_word_timings(self, text: str, duration_ms: int) -> List[WordTiming]:
        """
        Estimate word timings based on text length and audio duration.
        This is an approximation - could be improved with forced alignment.
        """
        words = text.split()
        if not words:
            return []
        
        total_chars = sum(len(w) for w in words)
        if total_chars == 0:
            return []
        
        timings = []
        current_ms = 0
        
        for word in words:
            word_proportion = len(word) / total_chars
            word_duration = int(duration_ms * word_proportion)
            
            timings.append(WordTiming(
                text=word,
                start_ms=current_ms,
                end_ms=current_ms + word_duration
            ))
            current_ms += word_duration
        
        return timings
    
    def _get_audio_duration_ms(self, audio_path: Path) -> int:
        """Get audio duration in milliseconds using ffprobe."""
        import subprocess
        
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
                capture_output=True, text=True
            )
            duration_sec = float(result.stdout.strip())
            return int(duration_sec * 1000)
        except Exception:
            return 3000
    
    def _combine_audio_segments(
        self,
        segments: List[Path],
        pause_ms: int
    ) -> Optional[Path]:
        """
        Combine audio segments with a pause between quote and motivation.
        """
        if not segments:
            return None
        
        import subprocess
        import time
        
        output_path = self.output_dir / f"voiceover_{int(time.time())}.mp3"
        
        try:
            if len(segments) == 1:
                import shutil
                shutil.copy(segments[0], output_path)
                return output_path
            
            silence_path = self.output_dir / "silence.mp3"
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi',
                '-i', f'anullsrc=r=44100:cl=stereo',
                '-t', str(pause_ms / 1000),
                '-q:a', '2',
                str(silence_path)
            ], capture_output=True)
            
            concat_list = self.output_dir / "concat_list.txt"
            with open(concat_list, 'w') as f:
                f.write(f"file '{segments[0].absolute()}'\n")
                if len(segments) > 1:
                    f.write(f"file '{silence_path.absolute()}'\n")
                for seg in segments[1:]:
                    f.write(f"file '{seg.absolute()}'\n")
            
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(concat_list),
                '-c', 'copy',
                str(output_path)
            ], capture_output=True)
            
            for seg in segments:
                seg.unlink(missing_ok=True)
            silence_path.unlink(missing_ok=True)
            concat_list.unlink(missing_ok=True)
            
            if output_path.exists():
                return output_path
                
        except Exception as e:
            logger.error(f"Audio combination failed: {e}")
        
        return None
    
    def group_words_for_display(
        self,
        word_timings: List[WordTiming],
        words_per_group: int = 2
    ) -> List[WordTiming]:
        """
        Group word timings for display (showing 1-2 words at a time).
        Preserves is_ending_phrase and is_intro flags.
        """
        grouped = []
        current_group = []
        
        for timing in word_timings:
            if timing.is_dramatic_pause:
                if current_group:
                    is_ending = any(t.is_ending_phrase for t in current_group)
                    is_intro = any(t.is_intro for t in current_group)
                    grouped.append(WordTiming(
                        text=' '.join(t.text for t in current_group),
                        start_ms=current_group[0].start_ms,
                        end_ms=current_group[-1].end_ms,
                        is_ending_phrase=is_ending,
                        is_intro=is_intro
                    ))
                    current_group = []
                grouped.append(timing)
                continue
            
            current_group.append(timing)
            
            if len(current_group) >= words_per_group:
                is_ending = any(t.is_ending_phrase for t in current_group)
                is_intro = any(t.is_intro for t in current_group)
                grouped.append(WordTiming(
                    text=' '.join(t.text for t in current_group),
                    start_ms=current_group[0].start_ms,
                    end_ms=current_group[-1].end_ms,
                    is_ending_phrase=is_ending,
                    is_intro=is_intro
                ))
                current_group = []
        
        if current_group:
            is_ending = any(t.is_ending_phrase for t in current_group)
            is_intro = any(t.is_intro for t in current_group)
            grouped.append(WordTiming(
                text=' '.join(t.text for t in current_group),
                start_ms=current_group[0].start_ms,
                end_ms=current_group[-1].end_ms,
                is_ending_phrase=is_ending,
                is_intro=is_intro
            ))
        
        return grouped


if __name__ == "__main__":
    service = VoiceoverService()
    
    result = service.generate_voiceover(
        quote_text="The obstacle is the way",
        motivation_text="What stands in your way becomes your path to power",
        ending_phrase="read the caption for real world applications"
    )
    
    if result:
        print(f"Audio: {result.audio_path}")
        print(f"Duration: {result.total_duration_ms}ms")
        print(f"Quote ends at: {result.quote_end_ms}ms")
        print(f"Motivation starts at: {result.motivation_start_ms}ms")
        print("\nWord timings:")
        for timing in result.word_timings[:10]:
            print(f"  {timing.start_ms}-{timing.end_ms}ms: '{timing.text}'")
    else:
        print("Voiceover generation failed")

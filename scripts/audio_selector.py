"""
Audio Selector for StoicAlgo
Handles hybrid audio selection with multiple modes.
"""

import random
from pathlib import Path
from typing import Dict, Optional, Tuple
from scripts.logger import get_logger
from scripts.utils import load_settings, load_json, get_file_list

logger = get_logger("AudioSelector")


class AudioSelector:
    """Selects and manages audio for video generation."""
    
    # Audio modes
    ORIGINAL_ONLY = "ORIGINAL_ONLY"
    IG_AUDIO_ONLY = "IG_AUDIO_ONLY"
    MIXED = "MIXED"
    MINIMAL = "MINIMAL_FOR_MANUAL_REPLACE"
    
    def __init__(self):
        self.settings = load_settings()
        self.audio_config = self.settings['audio']
        
        # Paths
        project_root = Path(__file__).parent.parent
        audio_base = project_root / self.settings['paths']['audio']
        
        self.original_tracks_path = audio_base / "original_tracks"
        self.ig_audio_ids_path = audio_base / "instagram_audio_ids.json"
        
        # Current mode
        self.mode = self.audio_config.get('mode', self.MIXED)
        
        # Audio settings
        self.volume = self.audio_config.get('original_volume', 0.3)
        self.fade_in = self.audio_config.get('fade_in_duration', 1.0)
        self.fade_out = self.audio_config.get('fade_out_duration', 2.0)
        
        # Supported formats
        self.supported_formats = ['.mp3', '.wav', '.m4a', '.aac']
    
    def select_audio(self, mood: str = None) -> Dict:
        """
        Select audio based on current mode.
        
        Args:
            mood: Optional mood to influence selection
            
        Returns:
            Dictionary with audio info:
            {
                'type': 'original' | 'instagram' | 'minimal',
                'path': Path to audio file (if original),
                'asset_id': Instagram audio ID (if IG audio),
                'volume': Suggested volume level,
                'fade_in': Fade in duration,
                'fade_out': Fade out duration
            }
        """
        
        if self.mode == self.ORIGINAL_ONLY:
            return self._select_original_audio(mood)
        
        elif self.mode == self.IG_AUDIO_ONLY:
            return self._select_instagram_audio(mood)
        
        elif self.mode == self.MIXED:
            # Randomly choose between original and IG
            if random.random() < 0.5:
                result = self._select_original_audio(mood)
                if result['path']:
                    return result
            return self._select_instagram_audio(mood)
        
        elif self.mode == self.MINIMAL:
            return self._get_minimal_audio()
        
        else:
            logger.warning(f"Unknown audio mode: {self.mode}, using minimal")
            return self._get_minimal_audio()
    
    def _select_original_audio(self, mood: str = None) -> Dict:
        """Select an original audio track."""
        
        if not self.original_tracks_path.exists():
            logger.warning("Original tracks folder not found")
            return self._get_minimal_audio()
        
        tracks = get_file_list(self.original_tracks_path, self.supported_formats)
        
        # Exclude files in archive folder
        tracks = [t for t in tracks if 'archive' not in str(t).lower()]
        
        if not tracks:
            logger.warning("No original audio tracks found")
            return self._get_minimal_audio()
        
        # Select random track (could be enhanced with mood matching)
        selected = random.choice(tracks)
        
        logger.info(f"Selected original audio: {selected.name}")
        
        return {
            'type': 'original',
            'path': selected,
            'asset_id': None,
            'volume': self.volume,
            'fade_in': self.fade_in,
            'fade_out': self.fade_out
        }
    
    def _select_instagram_audio(self, mood: str = None) -> Dict:
        """Select an Instagram royalty-free audio ID."""
        
        if not self.ig_audio_ids_path.exists():
            logger.warning("Instagram audio IDs file not found")
            return self._get_minimal_audio()
        
        try:
            audio_data = load_json(self.ig_audio_ids_path)
            tracks = audio_data.get('royalty_free_tracks', [])
            
            if not tracks:
                logger.warning("No Instagram audio IDs configured")
                return self._get_minimal_audio()
            
            # Filter by mood if specified
            if mood:
                mood_tracks = [t for t in tracks if t.get('mood', '').lower() == mood.lower()]
                if mood_tracks:
                    tracks = mood_tracks
            
            # Select random track
            selected = random.choice(tracks)
            
            logger.info(f"Selected Instagram audio: {selected.get('name', selected.get('id'))}")
            
            return {
                'type': 'instagram',
                'path': None,
                'asset_id': selected.get('id'),
                'name': selected.get('name'),
                'volume': 1.0,  # IG handles volume
                'fade_in': 0,
                'fade_out': 0
            }
            
        except Exception as e:
            logger.error(f"Error loading Instagram audio IDs: {e}")
            return self._get_minimal_audio()
    
    def _get_minimal_audio(self) -> Dict:
        """Get minimal/silent audio for manual replacement."""
        
        logger.info("Using minimal audio mode (for manual replacement)")
        
        return {
            'type': 'minimal',
            'path': None,
            'asset_id': None,
            'volume': 0.1,  # Very quiet
            'fade_in': 0,
            'fade_out': 0,
            'generate_silent': True
        }
    
    def set_mode(self, mode: str):
        """Change the audio selection mode."""
        valid_modes = [
            self.ORIGINAL_ONLY,
            self.IG_AUDIO_ONLY,
            self.MIXED,
            self.MINIMAL
        ]
        
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Valid modes: {valid_modes}")
        
        self.mode = mode
        logger.info(f"Audio mode set to: {mode}")
    
    def get_audio_stats(self) -> Dict:
        """Get statistics about available audio."""
        stats = {
            'current_mode': self.mode,
            'original_tracks': 0,
            'instagram_tracks': 0
        }
        
        # Count original tracks
        if self.original_tracks_path.exists():
            stats['original_tracks'] = len(
                get_file_list(self.original_tracks_path, self.supported_formats)
            )
        
        # Count IG audio IDs
        if self.ig_audio_ids_path.exists():
            try:
                audio_data = load_json(self.ig_audio_ids_path)
                stats['instagram_tracks'] = len(
                    audio_data.get('royalty_free_tracks', [])
                )
            except Exception:
                pass
        
        return stats


def select_audio(mood: str = None) -> Dict:
    """Convenience function to select audio."""
    selector = AudioSelector()
    return selector.select_audio(mood)


if __name__ == "__main__":
    # Test audio selector
    selector = AudioSelector()
    
    print("=== Audio Statistics ===")
    stats = selector.get_audio_stats()
    print(f"Current mode: {stats['current_mode']}")
    print(f"Original tracks: {stats['original_tracks']}")
    print(f"Instagram tracks: {stats['instagram_tracks']}")
    
    print("\n=== Testing Selection (each mode) ===")
    
    for mode in [AudioSelector.ORIGINAL_ONLY, AudioSelector.IG_AUDIO_ONLY, 
                 AudioSelector.MIXED, AudioSelector.MINIMAL]:
        selector.set_mode(mode)
        result = selector.select_audio(mood="dark")
        print(f"\nMode: {mode}")
        print(f"  Type: {result['type']}")
        if result['path']:
            print(f"  Path: {result['path']}")
        if result.get('asset_id'):
            print(f"  Asset ID: {result['asset_id']}")
        print(f"  Volume: {result['volume']}")

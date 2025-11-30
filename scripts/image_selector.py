"""
Image Selector for StoicAlgo
Handles hybrid image selection from curated bank and AI-generated images.
"""

import os
import random
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
from scripts.logger import get_logger
from scripts.utils import load_settings, get_file_list, weighted_random_choice, ensure_dir

logger = get_logger("ImageSelector")


class ImageSelector:
    """Selects and prepares images for video generation."""
    
    def __init__(self):
        self.settings = load_settings()
        self.image_config = self.settings['image']
        
        # Paths
        project_root = Path(__file__).parent.parent
        self.images_path = project_root / self.settings['paths']['images']
        
        # Weights
        self.curated_weight = self.image_config.get('curated_weight', 0.85)
        self.ai_weight = self.image_config.get('ai_injected_weight', 0.15)
        
        # Output dimensions
        self.output_width = self.image_config.get('output_width', 1080)
        self.output_height = self.image_config.get('output_height', 1920)
        
        # Supported formats
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.PNG', '.JPG', '.JPEG']
        
        # Folders to exclude from selection
        self.excluded_folders = ['used', 'archive']
    
    def _filter_excluded_folders(self, images: List[Path]) -> List[Path]:
        """Filter out images from excluded folders (used, archive)."""
        return [img for img in images if not any(
            excluded in img.parts for excluded in self.excluded_folders
        )]
    
    def select_image(self, mood: str = None, category: str = None) -> Tuple[Path, str]:
        """
        Select an image using hybrid strategy.
        
        Args:
            mood: Optional mood to influence selection
            category: Optional specific category to select from
            
        Returns:
            Tuple of (image_path, source_type)
        """
        
        # Decide between curated and AI-injected
        source_type = weighted_random_choice(
            ['curated', 'ai_injected'],
            [self.curated_weight, self.ai_weight]
        )
        
        if source_type == 'ai_injected':
            image_path = self._select_ai_image()
            if image_path:
                logger.info(f"Selected AI-generated image: {image_path.name}")
                return image_path, 'ai_injected'
            else:
                # Fallback to curated if no AI images available
                logger.warning("No AI images available, falling back to curated")
                source_type = 'curated'
        
        # Select from curated bank
        image_path = self._select_curated_image(mood, category)
        logger.info(f"Selected curated image: {image_path.name}")
        return image_path, 'curated'
    
    def _select_ai_image(self) -> Optional[Path]:
        """Select a random image from AI-injected folder (excluding used/archive)."""
        ai_folder = self.images_path / "ai_injected"
        
        if not ai_folder.exists():
            return None
        
        images = get_file_list(ai_folder, self.supported_formats)
        images = self._filter_excluded_folders(images)
        
        if not images:
            return None
        
        return random.choice(images)
    
    def _select_curated_image(self, mood: str = None, category: str = None) -> Path:
        """Select an image from the curated bank (excluding used/archive)."""
        
        categories = self.image_config.get('categories', [
            'statues', 'warriors', 'nature', 'temples', 'cosmic', 'geometry'
        ])
        
        # If specific category requested
        if category and category in categories:
            selected_category = category
        # Select category based on mood
        elif mood:
            selected_category = self._mood_to_category(mood, categories)
        else:
            selected_category = random.choice(categories)
        
        # Get images from selected category
        category_path = self.images_path / selected_category
        
        if not category_path.exists():
            # Fallback: try to find any available images
            logger.warning(f"Category {selected_category} not found, searching all categories")
            return self._select_from_any_category(categories)
        
        images = get_file_list(category_path, self.supported_formats)
        images = self._filter_excluded_folders(images)
        
        if not images:
            logger.warning(f"No images in {selected_category}, searching other categories")
            return self._select_from_any_category(categories)
        
        return random.choice(images)
    
    def _select_from_any_category(self, categories: List[str]) -> Path:
        """Fallback: select from any available category (excluding used/archive)."""
        all_images = []
        
        for cat in categories:
            cat_path = self.images_path / cat
            if cat_path.exists():
                images = get_file_list(cat_path, self.supported_formats)
                images = self._filter_excluded_folders(images)
                all_images.extend(images)
        
        if not all_images:
            raise FileNotFoundError(
                f"No images found in any category under {self.images_path}"
            )
        
        return random.choice(all_images)
    
    def _mood_to_category(self, mood: str, categories: List[str]) -> str:
        """Map mood to appropriate image category."""
        
        mood_mappings = {
            "contemplative": ["nature", "temples", "statues"],
            "powerful": ["warriors", "statues"],
            "serene": ["nature", "cosmic", "temples"],
            "determined": ["warriors", "statues"],
            "epic": ["cosmic", "warriors"],
            "wise": ["statues", "temples", "geometry"]
        }
        
        preferred = mood_mappings.get(mood.lower(), categories)
        # Filter to available categories
        available = [c for c in preferred if c in categories]
        
        if available:
            return random.choice(available)
        return random.choice(categories)
    
    def prepare_image(self, image_path: Path, output_path: Path = None) -> Path:
        """
        Prepare image for video: resize/crop to vertical format.
        
        Args:
            image_path: Path to source image
            output_path: Optional path for processed image
            
        Returns:
            Path to prepared image
        """
        
        if output_path is None:
            output_path = image_path.parent / f"prepared_{image_path.name}"
        
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Calculate crop/resize
            original_ratio = img.width / img.height
            target_ratio = self.output_width / self.output_height
            
            if original_ratio > target_ratio:
                # Image is too wide, crop sides
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            elif original_ratio < target_ratio:
                # Image is too tall, crop top/bottom
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))
            
            # Resize to target dimensions
            img = img.resize(
                (self.output_width, self.output_height),
                Image.Resampling.LANCZOS
            )
            
            # Save
            img.save(output_path, 'JPEG', quality=95)
            logger.info(f"Prepared image: {output_path}")
        
        return output_path
    
    def mark_as_used(self, image_path: Path) -> Optional[Path]:
        """
        Move an image to the 'used' folder within its category.
        
        Args:
            image_path: Path to the image that was used
            
        Returns:
            New path to the moved image, or None if move failed
        """
        try:
            # Determine the category folder (parent of the image)
            category_folder = image_path.parent
            
            # Create 'used' subfolder if it doesn't exist
            used_folder = category_folder / "used"
            ensure_dir(used_folder)
            
            # Move the image
            new_path = used_folder / image_path.name
            shutil.move(str(image_path), str(new_path))
            
            logger.info(f"Moved to used: {image_path.name} -> {used_folder}")
            return new_path
            
        except Exception as e:
            logger.error(f"Failed to move image to used folder: {e}")
            return None
    
    def get_image_stats(self) -> Dict:
        """Get statistics about available images."""
        stats = {
            'total': 0,
            'by_category': {},
            'ai_injected': 0
        }
        
        # Count by category
        categories = self.image_config.get('categories', [])
        for cat in categories:
            cat_path = self.images_path / cat
            if cat_path.exists():
                count = len(get_file_list(cat_path, self.supported_formats))
                stats['by_category'][cat] = count
                stats['total'] += count
        
        # Count AI-injected
        ai_path = self.images_path / "ai_injected"
        if ai_path.exists():
            ai_count = len(get_file_list(ai_path, self.supported_formats))
            stats['ai_injected'] = ai_count
            stats['total'] += ai_count
        
        return stats


def select_image(mood: str = None, category: str = None) -> Tuple[Path, str]:
    """Convenience function to select an image."""
    selector = ImageSelector()
    return selector.select_image(mood, category)


if __name__ == "__main__":
    # Test image selector
    selector = ImageSelector()
    
    print("=== Image Statistics ===")
    stats = selector.get_image_stats()
    print(f"Total images: {stats['total']}")
    print(f"AI-injected: {stats['ai_injected']}")
    print("By category:")
    for cat, count in stats['by_category'].items():
        print(f"  {cat}: {count}")
    
    if stats['total'] > 0:
        print("\n=== Testing Selection ===")
        for mood in ['contemplative', 'powerful', 'serene']:
            try:
                path, source = selector.select_image(mood=mood)
                print(f"Mood '{mood}': {path.name} ({source})")
            except FileNotFoundError as e:
                print(f"Mood '{mood}': {e}")
    else:
        print("\n⚠️  No images found. Add images to assets/images/ folders.")

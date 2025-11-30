"""
Batch AI Image Generator for StoicAlgo
Generates categorized AI images for the image bank.
"""

import os
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load env before imports that need it
load_dotenv(project_root / '.env')

from scripts.ai_image_injector import AIImageInjector
from scripts.logger import get_logger

logger = get_logger("BatchImageGenerator")


# Category essence definitions - these capture the FEELING, not specific scenes
# The generator will create varied prompts based on these essences
CATEGORY_ESSENCES = {
    "statues": {
        "core_theme": "ancient wisdom frozen in stone, the weight of philosophy made physical",
        "visual_elements": ["marble", "bronze", "weathered stone", "classical sculpture", "museum lighting", "pedestals", "fragments", "busts", "full figures"],
        "moods": ["contemplative", "stoic", "timeless", "dignified", "solemn", "powerful"],
        "settings": ["dark void", "museum shadows", "temple ruins", "archaeological site", "spotlight isolation"],
        "subjects": ["Greek philosophers", "Roman emperors", "ancient sages", "classical warriors at rest", "mythological figures", "anonymous ancients"],
    },
    
    "warriors": {
        "core_theme": "disciplined power, the calm before violence, strategic patience - ANCIENT/HISTORICAL warriors only",
        "visual_elements": ["ancient armor", "historical weapons", "silhouettes", "mist", "battle-worn traditional gear", "meditation poses", "ready stances", "period-accurate equipment"],
        "moods": ["menacing", "calm focus", "deadly stillness", "honor-bound", "ruthless", "patient"],
        "settings": ["misty ancient battlefields", "traditional dojo shadows", "Roman arena ruins", "bamboo forest clearings", "mountain passes", "temple grounds"],
        "subjects": ["feudal samurai", "Spartan hoplites", "wandering ronin", "Roman legionnaires", "medieval knights", "Viking warriors", "Mongol horsemen", "Greek warriors"],
        "era_restriction": "ONLY ancient, medieval, or feudal era warriors - NO modern military, NO guns, NO contemporary soldiers",
    },
    
    "nature": {
        "core_theme": "the indifferent sublime, nature's brutal beauty, solitude against vastness",
        "visual_elements": ["mountains", "storms", "ancient trees", "still water", "fog", "cliffs", "vast skies", "minimal landscapes"],
        "moods": ["overwhelming", "serene violence", "lonely", "eternal", "unforgiving", "transcendent"],
        "settings": ["mountain peaks", "dark forests", "storm-lit plains", "ocean cliffs", "zen gardens", "desert wastes"],
        "subjects": ["lone trees", "distant peaks", "approaching storms", "calm before chaos", "empty paths", "solitary stones"],
    },
    
    "temples": {
        "core_theme": "sacred spaces abandoned by gods, architecture outliving its creators",
        "visual_elements": ["columns", "archways", "light beams", "dust motes", "worn steps", "sacred geometry in architecture", "shadows"],
        "moods": ["reverent", "abandoned", "mystical", "heavy silence", "ancient power", "forgotten"],
        "settings": ["Greek ruins", "Roman interiors", "Japanese shrines", "Gothic halls", "Egyptian chambers", "monastery corridors"],
        "subjects": ["empty thrones", "altar spaces", "entrance ways", "inner sanctums", "crumbling grandeur", "light through destruction"],
    },
    
    "sonder": {
        "core_theme": "the realization that every stranger has a life as vivid as your own - existential isolation in crowds, anonymous significance",
        "visual_elements": ["silhouettes", "urban spaces", "windows", "crowds from distance", "lone figures", "doorways", "reflections", "transit spaces"],
        "moods": ["melancholic", "contemplative", "isolating", "profound loneliness", "quiet observation", "existential"],
        "settings": ["city overlooks", "empty corridors", "window frames", "station platforms", "rooftop edges", "liminal spaces", "threshold moments"],
        "subjects": ["anonymous figures", "backs turned", "distant observers", "people in transition", "solitary contemplation", "the space between"],
    },
}

# Digital/glitch elements - MORE VISIBLE and specific
DIGITAL_TWIST_ELEMENTS = [
    "visible green matrix-style falling code in background shadows",
    "digital glitch artifacts with RGB color separation visible at edges",
    "horizontal scan lines cutting across the image",
    "binary code 0s and 1s subtly embedded in dark areas",
    "holographic blue interference patterns visible in shadows",
    "circuit board trace patterns glowing faintly in background",
    "pixelated data corruption blocks in corners",
    "neon green terminal text fragments floating in darkness",
    "digital noise static visible in darker regions",
    "glowing wireframe grid fading into the background",
    "cyberpunk-style digital rain overlay",
    "corrupted pixel blocks scattered subtly throughout",
]

# Film/realistic texture elements
FILM_TEXTURE_ELEMENTS = [
    "heavy 35mm film grain texture visible throughout",
    "strong cinematic film grain",
    "visible analog photography grain",
    "gritty film stock texture",
    "vintage film grain with dust particles",
    "raw unprocessed film grain look",
]

# Base aesthetic elements
BASE_ELEMENTS = [
    "dark cinematic lighting",
    "moody atmospheric", 
    "8k ultra detailed",
    "dramatic shadows",
    "professional photography",
]

TECHNICAL_REQUIREMENTS = [
    "vertical composition 9:16",
    "no text",
    "no logos", 
    "no watermarks",
    "no visible human faces",
]

NEGATIVE_PROMPT = (
    "blurry, low quality, text, watermark, signature, logo, "
    "bright cheerful colors, cartoon, anime, oversaturated, "
    "clear human faces, deformed hands, fingers, "
    "amateur, poorly composed, cluttered, generic stock photo, "
    "clean digital look, plastic, artificial, CGI obvious, "
    "modern military, contemporary soldiers, guns, firearms, "
    "tactical gear, camouflage, modern weapons, assault rifles"
)


def generate_dynamic_prompt(category: str) -> str:
    """Generate a unique prompt based on category essence rather than fixed examples."""
    import random
    
    if category not in CATEGORY_ESSENCES:
        raise ValueError(f"Unknown category: {category}")
    
    essence = CATEGORY_ESSENCES[category]
    
    # Pick random elements from each aspect
    visual = random.sample(essence["visual_elements"], min(3, len(essence["visual_elements"])))
    mood = random.choice(essence["moods"])
    setting = random.choice(essence["settings"])
    subject = random.choice(essence["subjects"])
    
    # Check for era restriction (warriors category)
    era_note = essence.get("era_restriction", "")
    
    # Build the creative prompt
    prompt_parts = [
        f"{subject} in {setting}",
        f"mood: {mood}",
        f"featuring {', '.join(visual)}",
    ]
    
    # Add era restriction for warriors
    if era_note:
        prompt_parts.append(f"IMPORTANT: {era_note}")
    
    # Add digital twist - make it more prominent
    digital_twist = random.choice(DIGITAL_TWIST_ELEMENTS)
    
    # Add film grain
    film_texture = random.choice(FILM_TEXTURE_ELEMENTS)
    
    # Combine all elements
    base = ", ".join(BASE_ELEMENTS)
    technical = ", ".join(TECHNICAL_REQUIREMENTS)
    
    # Structure prompt to emphasize digital fusion
    full_prompt = (
        f"{', '.join(prompt_parts)}, "
        f"DIGITAL FUSION ELEMENT: {digital_twist}, "
        f"ancient meets digital aesthetic, "
        f"{film_texture}, {base}, {technical}"
    )
    
    return full_prompt


class BatchImageGenerator:
    """Generates batches of categorized AI images."""
    
    def __init__(self):
        self.injector = AIImageInjector()
        self.output_base = Path(__file__).parent.parent / "assets/images/ai_injected"
        
        # Stats tracking
        self.stats = {
            "total_generated": 0,
            "total_failed": 0,
            "by_category": {}
        }
    
    def generate_category_batch(self, category: str, count: int = 20, delay: float = 2.0) -> List[Path]:
        """
        Generate a batch of images for a specific category.
        
        Args:
            category: Category name (statues, warriors, etc.)
            count: Number of images to generate
            delay: Delay between API calls in seconds
            
        Returns:
            List of generated image paths
        """
        
        if category not in CATEGORY_ESSENCES:
            raise ValueError(f"Unknown category: {category}. Available: {list(CATEGORY_ESSENCES.keys())}")
        
        output_dir = self.output_base / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated = []
        
        logger.info(f"Starting batch generation for '{category}': {count} images")
        
        for i in range(count):
            try:
                # Generate a unique dynamic prompt each time
                full_prompt = generate_dynamic_prompt(category)
                
                logger.info(f"[{category}] Generating {i+1}/{count}...")
                logger.debug(f"Prompt: {full_prompt[:100]}...")
                
                # Generate image
                image_path = self._generate_to_category(full_prompt, category)
                
                if image_path:
                    generated.append(image_path)
                    self.stats["total_generated"] += 1
                    logger.info(f"[{category}] ✓ {i+1}/{count}: {image_path.name}")
                else:
                    self.stats["total_failed"] += 1
                    logger.warning(f"[{category}] ✗ {i+1}/{count}: Generation failed")
                
                # Delay to avoid rate limiting
                if i < count - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                self.stats["total_failed"] += 1
                logger.error(f"[{category}] Error on {i+1}/{count}: {str(e)}")
                time.sleep(delay)
        
        self.stats["by_category"][category] = len(generated)
        logger.info(f"[{category}] Batch complete: {len(generated)}/{count} images generated")
        
        return generated
    
    def generate_all_categories(self, count_per_category: int = 20, delay: float = 2.0) -> Dict[str, List[Path]]:
        """
        Generate images for all categories.
        
        Args:
            count_per_category: Number of images per category
            delay: Delay between API calls
            
        Returns:
            Dictionary of category -> list of paths
        """
        
        results = {}
        categories = list(CATEGORY_ESSENCES.keys())
        total = len(categories) * count_per_category
        
        logger.info(f"Starting full batch generation: {total} total images across {len(categories)} categories")
        print(f"\n{'='*60}")
        print(f"BATCH IMAGE GENERATION")
        print(f"{'='*60}")
        print(f"Categories: {', '.join(categories)}")
        print(f"Images per category: {count_per_category}")
        print(f"Total images: {total}")
        print(f"Estimated time: ~{total * (delay + 15) / 60:.1f} minutes")
        print(f"{'='*60}\n")
        
        start_time = datetime.now()
        
        for cat_idx, category in enumerate(categories):
            print(f"\n[{cat_idx+1}/{len(categories)}] Processing category: {category.upper()}")
            print("-" * 40)
            
            results[category] = self.generate_category_batch(category, count_per_category, delay)
            
            # Progress update
            elapsed = (datetime.now() - start_time).total_seconds()
            completed = sum(len(paths) for paths in results.values())
            
            print(f"\nProgress: {completed}/{total} images ({completed/total*100:.1f}%)")
            print(f"Elapsed: {elapsed/60:.1f} minutes")
        
        # Final summary
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total generated: {self.stats['total_generated']}")
        print(f"Total failed: {self.stats['total_failed']}")
        print(f"Total time: {total_time/60:.1f} minutes")
        print(f"\nBy category:")
        for cat, count in self.stats["by_category"].items():
            print(f"  {cat}: {count} images")
        print(f"{'='*60}\n")
        
        return results
    
    def _generate_to_category(self, prompt: str, category: str) -> Path:
        """Generate image and save to category folder."""
        
        try:
            # Use the injector's API call logic
            import requests
            import base64
            from scripts.utils import get_env_var, generate_id
            
            api_key = get_env_var('STABILITY_API_KEY')
            url = f"https://api.stability.ai/v1/generation/{self.injector.model}/text-to-image"
            
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            body = {
                "text_prompts": [
                    {"text": prompt, "weight": 1},
                    {"text": NEGATIVE_PROMPT, "weight": -1}
                ],
                "cfg_scale": self.injector.cfg_scale,
                "height": self.injector.height,
                "width": self.injector.width,
                "samples": 1,
                "steps": self.injector.steps,
                "style_preset": self.injector.style_preset
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=120)
            
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text[:200]}")
                return None
            
            data = response.json()
            
            for artifact in data.get("artifacts", []):
                if artifact.get("finishReason") == "SUCCESS":
                    image_data = base64.b64decode(artifact["base64"])
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{category}_{timestamp}_{generate_id()[:6]}.png"
                    output_path = self.output_base / category / filename
                    
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    
                    return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return None


def main():
    """Main entry point for batch generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch AI Image Generator')
    parser.add_argument('--category', type=str, help='Single category to generate')
    parser.add_argument('--count', type=int, default=10, help='Images per category')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between API calls')
    parser.add_argument('--all', action='store_true', help='Generate all categories')
    
    args = parser.parse_args()
    
    generator = BatchImageGenerator()
    
    if args.category:
        generator.generate_category_batch(args.category, args.count, args.delay)
    elif args.all:
        generator.generate_all_categories(args.count, args.delay)
    else:
        print("Usage:")
        print("  Generate single category: python batch_image_generator.py --category statues --count 10")
        print("  Generate all categories:  python batch_image_generator.py --all --count 10")
        print(f"\nAvailable categories: {', '.join(CATEGORY_ESSENCES.keys())}")


if __name__ == "__main__":
    main()

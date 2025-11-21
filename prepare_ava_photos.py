"""
AVA Photo Preparation Script
============================

This script:
1. Finds all photos in ava/pictures
2. Identifies the "best" photo (filename contains "best")
3. Analyzes all photos for quality and suitability
4. Prepares photos for avatar creation
5. Copies the best photo to assets/ava for immediate use

Usage:
    python prepare_ava_photos.py
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import json
from typing import List, Dict, Tuple

class AvaPhotoPreparator:
    """Prepare AVA's photos for avatar creation"""

    SOURCE_DIR = Path("ava/pictures")
    DEST_DIR = Path("assets/ava")
    ANALYSIS_FILE = Path("ava/photo_analysis.json")

    # Supported formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

    def __init__(self):
        """Initialize preparator"""
        self.photos = []
        self.best_photo = None
        self.analysis_results = {}

    def find_photos(self) -> List[Path]:
        """Find all photos in source directory"""
        if not self.SOURCE_DIR.exists():
            print(f"❌ Source directory not found: {self.SOURCE_DIR}")
            print(f"📁 Please add your photos to: {self.SOURCE_DIR.absolute()}")
            return []

        photos = []
        for file in self.SOURCE_DIR.iterdir():
            if file.suffix.lower() in self.SUPPORTED_FORMATS:
                photos.append(file)

        print(f"✅ Found {len(photos)} photos in {self.SOURCE_DIR}")
        return photos

    def find_best_photo(self, photos: List[Path]) -> Path:
        """Find the photo with 'best' in filename"""
        for photo in photos:
            if 'best' in photo.stem.lower():
                print(f"🏆 Found 'best' photo: {photo.name}")
                return photo

        # If no 'best' photo, return first one
        if photos:
            print(f"⚠️  No photo with 'best' in name, using first photo: {photos[0].name}")
            return photos[0]

        return None

    def analyze_photo(self, photo_path: Path) -> Dict:
        """Analyze a single photo for quality and suitability"""
        try:
            with Image.open(photo_path) as img:
                width, height = img.size
                format = img.format
                mode = img.mode

                # Calculate quality score
                score = 0

                # Resolution score (0-40 points)
                min_dim = min(width, height)
                if min_dim >= 1024:
                    score += 40
                elif min_dim >= 512:
                    score += 30
                elif min_dim >= 256:
                    score += 20
                else:
                    score += 10

                # Aspect ratio score (0-20 points)
                aspect_ratio = width / height if height > 0 else 0
                if 0.8 <= aspect_ratio <= 1.2:  # Close to square
                    score += 20
                elif 0.7 <= aspect_ratio <= 1.4:
                    score += 15
                else:
                    score += 10

                # Format score (0-20 points)
                if format in ['PNG']:
                    score += 20
                elif format in ['JPEG', 'JPG']:
                    score += 15
                else:
                    score += 10

                # Color mode score (0-20 points)
                if mode == 'RGB' or mode == 'RGBA':
                    score += 20
                else:
                    score += 10

                analysis = {
                    'filename': photo_path.name,
                    'width': width,
                    'height': height,
                    'format': format,
                    'mode': mode,
                    'aspect_ratio': round(aspect_ratio, 2),
                    'quality_score': score,
                    'min_dimension': min_dim,
                    'suitable_for_avatar': min_dim >= 256,
                    'recommended_for_training': min_dim >= 512
                }

                return analysis

        except Exception as e:
            print(f"❌ Error analyzing {photo_path.name}: {e}")
            return {
                'filename': photo_path.name,
                'error': str(e),
                'quality_score': 0,
                'suitable_for_avatar': False
            }

    def prepare_for_avatar(self, photo_path: Path, output_name: str = "neutral.png"):
        """Prepare photo for avatar use"""
        try:
            # Create dest dir if needed
            self.DEST_DIR.mkdir(parents=True, exist_ok=True)

            output_path = self.DEST_DIR / output_name

            with Image.open(photo_path) as img:
                # Convert to RGB if needed
                if img.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize to optimal size (keep aspect ratio)
                max_size = 512
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                # Save
                img.save(output_path, 'PNG', quality=95)

            print(f"✅ Prepared avatar: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error preparing {photo_path.name}: {e}")
            return None

    def create_expressions_from_best(self, best_photo: Path):
        """Create expression placeholders from best photo"""
        expressions = {
            'neutral': 'Default expression',
            'thinking': 'Processing/analyzing',
            'happy': 'Success/positive response',
            'surprised': 'Unexpected/alert',
            'error': 'Error state'
        }

        print("\n📸 Creating expression images...")

        for expression, description in expressions.items():
            output_name = f"{expression}.png"
            output_path = self.DEST_DIR / output_name

            if not output_path.exists():
                # Copy best photo as base for each expression
                self.prepare_for_avatar(best_photo, output_name)
                print(f"   ✅ Created {expression}.png ({description})")
            else:
                print(f"   ⏭️  {expression}.png already exists")

    def save_analysis(self):
        """Save analysis results to JSON"""
        analysis_file = self.ANALYSIS_FILE
        analysis_file.parent.mkdir(parents=True, exist_ok=True)

        with open(analysis_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"\n💾 Analysis saved to: {analysis_file}")

    def create_readme(self):
        """Create README for the photos"""
        readme_content = f"""# AVA Photos

## Photo Analysis Complete

**Best Photo:** {self.best_photo.name if self.best_photo else 'None found'}

**Total Photos:** {len(self.photos)}

## Quality Breakdown

"""
        suitable_count = sum(1 for p in self.analysis_results.values()
                            if p.get('suitable_for_avatar', False))
        training_count = sum(1 for p in self.analysis_results.values()
                            if p.get('recommended_for_training', False))

        readme_content += f"- ✅ Suitable for avatar: {suitable_count}\n"
        readme_content += f"- 🎯 Recommended for training: {training_count}\n\n"

        readme_content += "## Photos by Quality\n\n"

        # Sort by quality score
        sorted_photos = sorted(self.analysis_results.items(),
                              key=lambda x: x[1].get('quality_score', 0),
                              reverse=True)

        for filename, analysis in sorted_photos:
            score = analysis.get('quality_score', 0)
            width = analysis.get('width', 0)
            height = analysis.get('height', 0)
            suitable = "✅" if analysis.get('suitable_for_avatar', False) else "❌"

            readme_content += f"### {filename}\n"
            readme_content += f"- Quality Score: {score}/100\n"
            readme_content += f"- Resolution: {width}x{height}\n"
            readme_content += f"- Suitable: {suitable}\n\n"

        readme_content += "\n## Next Steps\n\n"
        readme_content += "1. **Quick Start:** The best photo has been prepared as `assets/ava/neutral.png`\n"
        readme_content += "2. **Add Expressions:** Create different expressions and save as:\n"
        readme_content += "   - `thinking.gif` - Animated thinking\n"
        readme_content += "   - `happy.png` - Smiling/success\n"
        readme_content += "   - `surprised.png` - Alert state\n"
        readme_content += "   - `error.png` - Error state\n"
        readme_content += "3. **Model Training:** Use all {training_count} training-suitable photos for D-ID or HeyGen\n"
        readme_content += "4. **See:** `AVA_VISUAL_AVATAR_IMPLEMENTATION_GUIDE.md` for full instructions\n"

        readme_path = self.SOURCE_DIR / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)

        print(f"📄 README created: {readme_path}")

    def run(self):
        """Run the full preparation process"""
        print("🚀 AVA Photo Preparation Starting...\n")

        # 1. Find photos
        self.photos = self.find_photos()
        if not self.photos:
            print("\n❌ No photos found!")
            print(f"📁 Please add photos to: {self.SOURCE_DIR.absolute()}")
            print("   Supported formats: .jpg, .jpeg, .png, .gif, .webp, .bmp")
            return

        # 2. Find best photo
        self.best_photo = self.find_best_photo(self.photos)

        # 3. Analyze all photos
        print(f"\n🔍 Analyzing {len(self.photos)} photos...\n")
        for photo in self.photos:
            analysis = self.analyze_photo(photo)
            self.analysis_results[photo.name] = analysis

            # Print summary
            score = analysis.get('quality_score', 0)
            suitable = "✅" if analysis.get('suitable_for_avatar', False) else "❌"
            print(f"   {suitable} {photo.name}: Score {score}/100")

        # 4. Prepare best photo for avatar
        if self.best_photo:
            print(f"\n🎨 Preparing best photo for avatar...")
            self.prepare_for_avatar(self.best_photo, "neutral.png")

            # 5. Create expression placeholders
            self.create_expressions_from_best(self.best_photo)

        # 6. Save analysis
        self.save_analysis()

        # 7. Create README
        self.create_readme()

        # Summary
        print("\n" + "="*60)
        print("✅ AVA PHOTO PREPARATION COMPLETE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   - Total photos: {len(self.photos)}")
        print(f"   - Best photo: {self.best_photo.name if self.best_photo else 'None'}")
        print(f"   - Avatar ready: assets/ava/neutral.png")
        print(f"   - Analysis saved: {self.ANALYSIS_FILE}")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Check: ava/pictures/README.md")
        print(f"   2. Review: ava/photo_analysis.json")
        print(f"   3. Run dashboard to see AVA with her new face!")
        print(f"   4. See: AVA_VISUAL_AVATAR_IMPLEMENTATION_GUIDE.md")
        print()


if __name__ == "__main__":
    preparator = AvaPhotoPreparator()
    preparator.run()

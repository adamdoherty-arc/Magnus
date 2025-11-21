"""
Test AVA Visual Avatar Integration
====================================

Quick verification that AVA's visual avatar system is properly configured.
"""

import os
from pathlib import Path

def test_avatar_integration():
    """Verify all components of AVA's visual avatar are in place"""

    print("\nTesting AVA Visual Avatar Integration\n")
    print("=" * 60)

    # Test 1: Check avatar files exist
    print("\n1. Checking avatar files...")
    asset_path = Path("assets/ava")
    required_files = [
        "neutral.png",
        "happy.png",
        "thinking.png",
        "surprised.png",
        "error.png",
        "speaking.png"
    ]

    if not asset_path.exists():
        print(f"   [ERROR] Avatar directory not found: {asset_path}")
        return False

    all_exist = True
    for file in required_files:
        file_path = asset_path / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   [OK] {file} ({size:,} bytes)")
        else:
            print(f"   [MISSING] {file}")
            all_exist = False

    if not all_exist:
        return False

    # Test 2: Check ava_visual.py exists
    print("\n2. Checking AVA visual module...")
    visual_module = Path("src/ava/ava_visual.py")
    if visual_module.exists():
        print(f"   [OK] Module found: {visual_module}")
    else:
        print(f"   [ERROR] Module not found: {visual_module}")
        return False

    # Test 3: Check omnipresent_ava_enhanced.py has the integration
    print("\n3. Checking Enhanced AVA integration...")
    enhanced_ava = Path("src/ava/omnipresent_ava_enhanced.py")
    if enhanced_ava.exists():
        content = enhanced_ava.read_text(encoding='utf-8')

        # Check for import
        if "from src.ava.ava_visual import AvaVisual" in content:
            print("   [OK] AvaVisual import found")
        else:
            print("   [ERROR] AvaVisual import missing")
            return False

        # Check for show_avatar call
        if "AvaVisual.show_avatar" in content:
            print("   [OK] show_avatar() call found")
        else:
            print("   [ERROR] show_avatar() call missing")
            return False

        # Check for expression mapping
        if "get_expression_for_state" in content:
            print("   [OK] Expression mapping found")
        else:
            print("   [ERROR] Expression mapping missing")
            return False
    else:
        print(f"   [ERROR] Enhanced AVA not found: {enhanced_ava}")
        return False

    # Test 4: Check source photo
    print("\n4. Checking source photo...")
    source_photo = Path("C:/Code/Heracles/docs/ava/pics/NancyFace.jpg")
    if source_photo.exists():
        size = source_photo.stat().st_size
        print(f"   [OK] Source photo found: {source_photo.name} ({size:,} bytes)")
    else:
        print(f"   [NOTE] Source photo not accessible (but avatars already created)")

    print("\n" + "=" * 60)
    print("\n[SUCCESS] AVA Visual Avatar Integration: COMPLETE\n")
    print("Next steps:")
    print("  1. Open dashboard at http://localhost:8501")
    print("  2. Look for AVA expander at the top of any page")
    print("  3. Click to expand and see AVA's face!")
    print("  4. Ask AVA questions to see expressions change")
    print("\n")

    return True

if __name__ == "__main__":
    success = test_avatar_integration()
    exit(0 if success else 1)

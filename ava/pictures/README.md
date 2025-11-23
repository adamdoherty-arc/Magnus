# AVA Photos - Ready for Upload! 📸

**This folder is ready for your photos!**

---

## 🎯 Quick Instructions

### 1. Add Your Photos Here
Drop all your AVA photos into this folder.

### 2. Name One Photo with "best"
Examples:
- `best.jpg`
- `ava_best.png`
- `face_best_photo.jpg`

This will be used as the primary avatar.

### 3. Run the Preparation Script
```bash
cd ../..
python prepare_ava_photos.py
```

---

## 📸 Photo Guidelines

### Minimum Requirements:
- **10+ photos** from different angles
- **512x512 pixels** or larger
- **Clear face**, good lighting
- **Supported formats:** JPG, PNG, GIF, WEBP, BMP

### For Best Results:
- **20+ photos**
- **1024x1024 pixels** or larger
- Multiple angles: front, 45°, profile (left & right)
- Different expressions: neutral, happy, thinking, surprised
- Various lighting conditions
- Clear, not blurry

---

## 🎨 What the Script Does

When you run `python prepare_ava_photos.py`:

1. ✅ Finds all photos in this folder
2. ✅ Identifies the "best" photo
3. ✅ Analyzes quality (resolution, format, aspect ratio)
4. ✅ Creates optimized avatar images
5. ✅ Generates detailed analysis report
6. ✅ Prepares expressions for dashboard

---

## 📊 What Gets Created

### In `../../assets/ava/`:
- `neutral.png` - Default AVA face
- `thinking.gif` - When processing
- `happy.png` - When successful
- `surprised.png` - When alert
- `error.png` - When error occurs

### In this folder:
- `README.md` (this file) - will be updated with your photo analysis
- `../photo_analysis.json` - Detailed technical analysis

---

## ✅ Ready to Go!

1. **Add photos** to this folder
2. **Name one** with "best" in filename
3. **Run:** `python prepare_ava_photos.py` (from project root)
4. **Refresh** dashboard to see AVA with her new face!

---

**Status:** Waiting for photos... 📸

Once you add photos and run the script, this README will be updated with your photo quality analysis!

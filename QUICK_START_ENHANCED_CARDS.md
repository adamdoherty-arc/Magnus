# QUICK START: Enhanced Game Cards

## 🚀 3 Steps to Get Started

### Step 1: Add API Key
Open your `.env` file and add:
```
DEEPSEEK_API_KEY=sk-eebe860586be4b85a9ff86b9fd1f0a66
```

### Step 2: Restart Streamlit
```bash
# Double-click: FORCE_REFRESH_STREAMLIT.bat
# OR run manually:
streamlit run dashboard.py
```

### Step 3: View Enhanced Cards
1. Click "Sports Game Cards" in sidebar
2. Select NFL or NCAA tab
3. See the new features!

## ✨ What's New

### 1. Team Records
- Now shows W-L record: `Buffalo Bills (8-2)`
- Displayed right next to team name

### 2. Dual AI Predictions
- **Left Column**: Local Model (Elo-based)
- **Right Column**: DeepSeek R1 (Advanced AI)
- Compare both predictions side-by-side

### 3. DeepSeek Insights
- One-sentence AI reasoning
- Example: "Eagles' rushing attack dominates vs Lions D"
- Appears below DeepSeek prediction

### 4. Cleaner Layout
- Organized sections
- Better spacing
- Easier to read

## 📊 What You'll See

```
🤖 AI Predictions
┌─────────────────┬──────────────────┐
│ 🏈 Local Model  │ 🤖 DeepSeek R1   │
│ Winner: Eagles  │ Winner: Eagles    │
│ Probability:65% │ Probability: 68%  │
│ Spread: 3.5     │ Spread: 4.0       │
│ 🟢 HIGH         │ 🟢 HIGH           │
│                 │ 💡 "Key insight"  │
└─────────────────┴──────────────────┘
```

## ❓ Troubleshooting

**Don't see DeepSeek predictions?**
1. Check `.env` file has the API key
2. Restart Streamlit completely
3. Wait 3-5 seconds for DeepSeek to load

**Only see "Loading DeepSeek..."?**
- This is normal! DeepSeek takes 2-5 seconds
- Local prediction shows immediately
- DeepSeek appears once ready

## 💰 Cost

**Per prediction**: ~$0.00007 (almost free!)
**100 predictions**: ~$0.007 (less than 1 cent)

## 📚 More Info

See `ENHANCED_GAME_CARDS_COMPLETE.md` for full details!


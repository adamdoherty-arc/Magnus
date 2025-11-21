# AVA Visual Avatar Implementation Guide

**Date:** 2025-11-11
**Status:** Research Complete - Ready for Implementation

---

## Research Summary

Based on research from Reddit and GitHub communities, here are the **best methods** to create a visual face for AVA using your uploaded photos.

---

## 🏆 Recommended Approaches (Ranked by Feasibility)

### Approach 1: D-ID API Integration (BEST for Production) ⭐⭐⭐⭐⭐

**Why This is Best:**
- ✅ Real-time talking avatar from a single photo
- ✅ Integrates directly with chatbots
- ✅ Low latency (real-time responses)
- ✅ Professional quality
- ✅ Easy to implement with Python SDK
- ✅ Works in Streamlit

**How It Works:**
1. Upload one high-quality photo of AVA's face
2. D-ID creates a talking avatar model
3. Text-to-speech triggers lip-sync animation
4. Avatar responds in real-time

**Cost:**
- Free tier: 20 credits (about 5 minutes of video)
- Paid: $5.90/month for 10 minutes
- Enterprise: Custom pricing

**Implementation Steps:**

```python
# 1. Install D-ID SDK
pip install did-sdk

# 2. Basic Integration
from did_sdk import DIDClient
import streamlit as st

client = DIDClient(api_key="YOUR_API_KEY")

# Create avatar from photo
avatar = client.create_avatar(
    image_url="path/to/ava_photo.jpg",
    audio_url="path/to/response.mp3"
)

# Display in Streamlit
st.video(avatar.video_url)
```

**GitHub Example:**
- D-ID has official Python SDK with examples
- Integration guide: https://docs.d-id.com/reference/python-sdk

**Best For:**
- Production-ready solution
- Real-time conversations
- Professional appearance

---

### Approach 2: Static Avatar with Expressions (Quick & Free) ⭐⭐⭐⭐

**Why This Works:**
- ✅ No API costs
- ✅ Works entirely offline
- ✅ Fast implementation
- ✅ Multiple expressions for different moods

**How It Works:**
1. Create/use multiple photos showing different expressions:
   - Neutral (default)
   - Thinking (when processing)
   - Happy (successful response)
   - Surprised (error/alert)
   - Speaking (animated GIF of talking)
2. Display appropriate expression based on AVA's state

**Implementation:**

```python
import streamlit as st
from enum import Enum

class AvaExpression(Enum):
    NEUTRAL = "assets/ava/neutral.png"
    THINKING = "assets/ava/thinking.png"
    HAPPY = "assets/ava/happy.png"
    SPEAKING = "assets/ava/speaking.gif"
    SURPRISED = "assets/ava/surprised.png"

def show_ava_avatar(expression: AvaExpression, size: int = 100):
    """Display AVA's avatar with specific expression"""
    st.image(expression.value, width=size)

# Usage in Enhanced AVA
with st.expander("🤖 AVA - Your Expert Trading Assistant"):
    col1, col2 = st.columns([1, 5])

    with col1:
        # Show thinking while processing
        if st.session_state.get('ava_processing', False):
            show_ava_avatar(AvaExpression.THINKING)
        else:
            show_ava_avatar(AvaExpression.NEUTRAL)

    with col2:
        # Chat interface
        st.chat_message(...)
```

**Best For:**
- Quick implementation
- No recurring costs
- Lightweight solution

---

### Approach 3: HeyGen Custom Avatar (Professional Alternative) ⭐⭐⭐⭐

**Why Consider This:**
- ✅ High-quality custom avatars
- ✅ Train on multiple photos (10-20 images)
- ✅ Professional results
- ✅ API available

**How It Works:**
1. Upload 10-20 photos of the face from different angles
2. HeyGen trains a custom avatar model (takes ~1 hour)
3. Use API to generate talking videos
4. Embed in Streamlit

**Cost:**
- Creator Plan: $29/month for 15 minutes
- Business Plan: $89/month for 90 minutes

**Photo Requirements:**
- 4-8 face close-ups with shoulders
- 10-12 full body shots (optional)
- Different angles: front, left, right, 45°
- Different expressions: neutral, smiling, serious

**Implementation:**

```python
# Using HeyGen API
import requests

def create_heygen_avatar(photos_list):
    """Train custom avatar from multiple photos"""
    response = requests.post(
        "https://api.heygen.com/v1/avatar.create",
        headers={"X-Api-Key": "YOUR_API_KEY"},
        json={"images": photos_list}
    )
    return response.json()['avatar_id']

def generate_talking_video(avatar_id, text):
    """Generate talking video from text"""
    response = requests.post(
        "https://api.heygen.com/v1/video.generate",
        headers={"X-Api-Key": "YOUR_API_KEY"},
        json={
            "avatar_id": avatar_id,
            "text": text,
            "voice_id": "female_professional"
        }
    )
    return response.json()['video_url']
```

**Best For:**
- Custom-trained avatar
- Multiple photo input
- High production quality

---

### Approach 4: Open Source Face Animation (FREE, Technical) ⭐⭐⭐

**Why Consider This:**
- ✅ Completely free
- ✅ Full control
- ✅ No API dependencies
- ❌ More complex setup

**GitHub Projects:**

**Option A: Face_Animation_Real_Time**
- Repository: https://github.com/sky24h/Face_Animation_Real_Time
- One-shot face animation using webcam
- Real-time capable (30+ fps)

**Option B: First-Order-Motion-Model (FOMM)**
- Repository: https://github.com/AliaksandrSiarohin/first-order-model
- Animate face from single image
- Driving video controls animation

**Implementation:**

```python
# Install dependencies
pip install torch torchvision
pip install opencv-python
pip install face-alignment

# Basic usage
from first_order_model import load_checkpoints, make_animation

# Load model
generator, kp_detector = load_checkpoints(config_path='config/vox-256.yaml',
                                          checkpoint_path='checkpoints/vox-cpk.pth.tar')

# Create animation from source image
source_image = load_image('ava_face.jpg')
driving_video = load_video('talking_animation.mp4')

animation = make_animation(source_image, driving_video, generator, kp_detector)
```

**Best For:**
- Technical users
- Full customization
- No ongoing costs

---

### Approach 5: Stable Diffusion Avatar Training (Advanced) ⭐⭐⭐

**Why Consider This:**
- ✅ Generate consistent avatar across different poses
- ✅ Create custom expressions
- ✅ Multiple photo training

**How It Works:**
1. Train Dreambooth + LoRA model on 20+ photos
2. Generate various expressions/poses
3. Use static images in chatbot

**Tools:**
- NightCafe Studio (Web-based, easy)
- Automatic1111 (Local, more control)
- Stable Diffusion WebUI

**Implementation:**

```python
# Using trained model to generate expressions
from diffusers import StableDiffusionPipeline
import torch

# Load your trained model
pipe = StableDiffusionPipeline.from_pretrained(
    "path/to/your/trained/model",
    torch_dtype=torch.float16
)

# Generate different expressions
expressions = [
    "photo of sks person, neutral expression, professional",
    "photo of sks person, happy smiling, friendly",
    "photo of sks person, thinking, curious expression",
    "photo of sks person, surprised, wide eyes"
]

for i, prompt in enumerate(expressions):
    image = pipe(prompt).images[0]
    image.save(f"ava_expression_{i}.png")
```

**Best For:**
- Creating custom expressions
- Consistent character across poses
- One-time generation

---

## 🎯 Recommended Implementation Plan

### Phase 1: Quick Win (This Week)

**Use Static Avatar with Expressions**

1. **Prepare Photos:**
   - Create folder: `assets/ava/`
   - Add 5 images:
     - `neutral.png` - Default state
     - `thinking.gif` - When processing (animated)
     - `happy.png` - After successful response
     - `surprised.png` - On errors
     - `speaking.gif` - While responding

2. **Implement in Enhanced AVA:**

```python
# Add to omnipresent_ava_enhanced.py

class AvaAvatar:
    """Visual avatar manager for AVA"""

    ASSET_PATH = Path("assets/ava")

    @staticmethod
    def show(expression: str = "neutral", size: int = 80):
        """Show AVA's avatar"""
        avatar_path = AvaAvatar.ASSET_PATH / f"{expression}.png"
        if avatar_path.exists():
            st.image(str(avatar_path), width=size)
        else:
            st.markdown("🤖")  # Fallback emoji

def show_enhanced_ava():
    """Enhanced AVA with visual avatar"""

    with st.expander("🤖 AVA - Your Expert Trading Assistant (Enhanced)"):
        # Header with avatar
        col1, col2 = st.columns([1, 6])

        with col1:
            # Show dynamic expression
            if st.session_state.get('ava_processing'):
                AvaAvatar.show("thinking")
            elif st.session_state.get('ava_error'):
                AvaAvatar.show("surprised")
            else:
                AvaAvatar.show("neutral")

        with col2:
            st.caption("Your expert trading assistant with a face!")

        # Chat interface...
```

**Timeline:** 1-2 hours
**Cost:** Free

---

### Phase 2: Professional Avatar (Next Week)

**Integrate D-ID API**

1. **Sign up for D-ID:**
   - Visit: https://www.d-id.com/
   - Get API key
   - Upload AVA's photo

2. **Implement Real-Time Avatar:**

```python
# Install
pip install requests pillow

# Create src/ava/visual_avatar.py

import requests
import streamlit as st
from pathlib import Path

class DIDAvatar:
    """D-ID talking avatar integration"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.d-id.com"

    def create_talking_avatar(self, text: str, image_path: str = None):
        """Generate talking avatar video from text"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Use default AVA image if none provided
        if image_path is None:
            image_path = "assets/ava/base_photo.jpg"

        # Upload image
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Create talking head
        payload = {
            "source_url": image_path,
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-JennyNeural"
                }
            }
        }

        response = requests.post(
            f"{self.base_url}/talks",
            headers=headers,
            json=payload
        )

        return response.json()

    def get_video_status(self, talk_id: str):
        """Check if video is ready"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(
            f"{self.base_url}/talks/{talk_id}",
            headers=headers
        )

        return response.json()

# Integration with Enhanced AVA
def show_enhanced_ava_with_video():
    """AVA with real-time video avatar"""

    # Initialize D-ID
    if 'did_avatar' not in st.session_state:
        api_key = os.getenv('DID_API_KEY')
        if api_key:
            st.session_state.did_avatar = DIDAvatar(api_key)

    with st.expander("🤖 AVA - Your Expert Trading Assistant (Video)"):
        col1, col2 = st.columns([2, 5])

        with col1:
            # Show video avatar if available
            if 'current_video_url' in st.session_state:
                st.video(st.session_state.current_video_url)
            else:
                # Fallback to static image
                st.image("assets/ava/neutral.png", width=150)

        with col2:
            # Chat interface
            user_input = st.text_input("Ask AVA:")

            if st.button("Send"):
                # Get AVA response
                response = ava.process_message(user_input)

                # Generate talking avatar video
                if hasattr(st.session_state, 'did_avatar'):
                    talk_data = st.session_state.did_avatar.create_talking_avatar(
                        response['response']
                    )
                    st.session_state.current_video_url = talk_data['result_url']
                    st.rerun()
```

**Timeline:** 2-3 hours
**Cost:** $5.90/month

---

### Phase 3: Custom Training (Later)

**Train HeyGen or Stable Diffusion Model**

1. Collect 20+ photos of AVA from different angles
2. Train custom model
3. Generate consistent expressions
4. Use in production

**Timeline:** 1 day + training time
**Cost:** $29/month (HeyGen) or Free (Stable Diffusion)

---

## 📋 Photo Requirements Checklist

For **best results** with any approach, prepare these photos:

### Essential (Minimum 10 photos):
- [ ] Front-facing, neutral expression
- [ ] Front-facing, smiling
- [ ] Profile (left side)
- [ ] Profile (right side)
- [ ] 45° angle (left)
- [ ] 45° angle (right)
- [ ] Different lighting conditions (3 photos)
- [ ] Close-up of face with shoulders
- [ ] Slightly tilted up
- [ ] Slightly tilted down

### Recommended (Additional 10+ photos):
- [ ] Various expressions: happy, surprised, thinking, concerned
- [ ] Different backgrounds
- [ ] Different head positions
- [ ] Speaking/mouth open
- [ ] Eyes closed (for blinking)

### Photo Quality Guidelines:
- **Resolution:** Minimum 512x512, recommended 1024x1024
- **Format:** JPG or PNG
- **Lighting:** Good, even lighting on face
- **Background:** Neutral or blurred
- **Face:** Should occupy 60-80% of frame
- **Quality:** Clear, not blurry

---

## 🛠 Implementation Code

### Complete Static Avatar Implementation

```python
# File: src/ava/ava_visual.py

from pathlib import Path
from enum import Enum
import streamlit as st
from typing import Optional

class AvaExpression(Enum):
    """AVA's facial expressions"""
    NEUTRAL = "neutral"
    THINKING = "thinking"
    HAPPY = "happy"
    SURPRISED = "surprised"
    SPEAKING = "speaking"
    ERROR = "error"

class AvaVisual:
    """Visual avatar system for AVA"""

    ASSET_PATH = Path("assets/ava")

    # Expression to file mapping
    EXPRESSIONS = {
        AvaExpression.NEUTRAL: "neutral.png",
        AvaExpression.THINKING: "thinking.gif",
        AvaExpression.HAPPY: "happy.png",
        AvaExpression.SURPRISED: "surprised.png",
        AvaExpression.SPEAKING: "speaking.gif",
        AvaExpression.ERROR: "error.png"
    }

    @classmethod
    def show_avatar(cls, expression: AvaExpression = AvaExpression.NEUTRAL,
                   size: int = 100, caption: Optional[str] = None):
        """Display AVA's avatar with specific expression"""

        avatar_file = cls.EXPRESSIONS.get(expression)
        avatar_path = cls.ASSET_PATH / avatar_file

        if avatar_path.exists():
            st.image(str(avatar_path), width=size, caption=caption)
        else:
            # Fallback to emoji
            emoji_map = {
                AvaExpression.NEUTRAL: "🤖",
                AvaExpression.THINKING: "🤔",
                AvaExpression.HAPPY: "😊",
                AvaExpression.SURPRISED: "😲",
                AvaExpression.SPEAKING: "🗣️",
                AvaExpression.ERROR: "😕"
            }
            st.markdown(f"<h1 style='font-size: {size}px;'>{emoji_map[expression]}</h1>",
                       unsafe_allow_html=True)

    @classmethod
    def get_expression_for_state(cls, ava_state: str, success: bool = True) -> AvaExpression:
        """Determine expression based on AVA's state"""

        if not success:
            return AvaExpression.ERROR

        state_map = {
            "idle": AvaExpression.NEUTRAL,
            "processing": AvaExpression.THINKING,
            "awaiting_watchlist_name": AvaExpression.NEUTRAL,
            "awaiting_ticker_symbol": AvaExpression.NEUTRAL,
            "awaiting_task_details": AvaExpression.THINKING,
            "awaiting_confirmation": AvaExpression.SURPRISED,
            "responding": AvaExpression.SPEAKING,
            "success": AvaExpression.HAPPY
        }

        return state_map.get(ava_state, AvaExpression.NEUTRAL)

# Integration with Enhanced AVA
def show_enhanced_ava_visual():
    """Enhanced AVA with visual avatar"""

    with st.expander("🤖 AVA - Your Expert Trading Assistant (Visual)"):
        # Header with avatar
        col1, col2 = st.columns([1, 5])

        with col1:
            # Determine current expression
            current_state = st.session_state.get('ava_state', 'idle')
            success = st.session_state.get('ava_last_success', True)
            expression = AvaVisual.get_expression_for_state(current_state.value, success)

            # Show avatar
            AvaVisual.show_avatar(expression, size=100)

        with col2:
            st.caption("Your expert trading assistant")

            # Show state-specific message
            if current_state != 'idle':
                st.info("💬 Waiting for your response...")

        # Chat messages
        for msg in st.session_state.ava_messages[-10:]:
            if msg['role'] == 'user':
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**AVA:** {msg['content']}")

        # Input
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("Ask AVA:", key="ava_input_visual")
        with col2:
            send_button = st.button("Send", type="primary")

        if send_button and user_input:
            # Mark as processing
            st.session_state.ava_state = 'processing'
            st.rerun()
```

---

## 📊 Comparison Matrix

| Approach | Cost | Quality | Speed | Complexity | Recommended For |
|----------|------|---------|-------|------------|-----------------|
| **D-ID API** | $5.90/mo | ⭐⭐⭐⭐⭐ | Real-time | Easy | Production |
| **Static Expressions** | Free | ⭐⭐⭐ | Instant | Very Easy | Quick Start |
| **HeyGen** | $29/mo | ⭐⭐⭐⭐⭐ | Near real-time | Medium | Custom Avatar |
| **Open Source FOMM** | Free | ⭐⭐⭐⭐ | Slow | Hard | Technical Users |
| **Stable Diffusion** | Free | ⭐⭐⭐⭐ | One-time | Medium | Custom Generation |

---

## 🚀 Next Steps

### Immediate Actions:

1. **Create assets folder:**
   ```bash
   mkdir -p assets/ava
   ```

2. **Add your uploaded photos to `assets/ava/`**

3. **Choose implementation approach:**
   - Quick: Static expressions (1-2 hours)
   - Professional: D-ID API (2-3 hours)
   - Custom: HeyGen training (1 day)

4. **Implement visual avatar in Enhanced AVA**

5. **Test and iterate**

---

## 📚 Resources

### Official Documentation:
- D-ID API: https://docs.d-id.com/
- HeyGen API: https://docs.heygen.com/
- Streamlit Components: https://docs.streamlit.io/

### GitHub Projects:
- Face Animation Real-Time: https://github.com/sky24h/Face_Animation_Real_Time
- First-Order-Motion-Model: https://github.com/AliaksandrSiarohin/first-order-model
- OpenSeeFace: https://github.com/emilianavt/OpenSeeFace

### Communities:
- Reddit r/StableDiffusion
- Reddit r/ArtificialIntelligence
- D-ID Discord: https://discord.gg/did

---

## ✅ Summary

**Best Path Forward:**

1. **Start with Static Expressions** (Today)
   - Free, fast, works immediately
   - Use uploaded photos for different moods

2. **Upgrade to D-ID** (When budget allows)
   - Professional talking avatar
   - Real-time responses
   - Best user experience

3. **Custom Training** (For unique look)
   - Train on multiple photos
   - Consistent appearance
   - Full control

**Recommended First Step:**
Implement static expressions with your uploaded photos - this gives immediate visual personality to AVA while you evaluate paid options.

---

**Status: Ready to Implement**

Choose your approach and let's bring AVA to life! 🤖✨

"""
SkinGuard ML - Streamlit App
Skin Disease Prediction using AI
"""

import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="SkinGuard ML",
    page_icon="🏥",
    layout="centered"
)

# Constants
IMG_SIZE = 224
MODEL_PATH = Path(__file__).parent / "models" / "keras_model.h5"
LABELS_PATH = Path(__file__).parent / "models" / "labels.txt"
MAPPING_PATH = Path(__file__).parent / "models" / "disease_mapping.json"


@st.cache_resource
def load_model():
    """Load the ML model (cached)"""
    try:
        import tf_keras
        model = tf_keras.models.load_model(str(MODEL_PATH), compile=False)
        return model
    except ImportError:
        import tensorflow as tf
        return tf.keras.models.load_model(str(MODEL_PATH), compile=False)


@st.cache_data
def load_labels():
    """Load disease labels"""
    if MAPPING_PATH.exists():
        with open(MAPPING_PATH, 'r') as f:
            return json.load(f)
    elif LABELS_PATH.exists():
        labels = {}
        with open(LABELS_PATH, 'r') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    labels[parts[0]] = parts[1]
        return labels
    return {}


def preprocess_image(image):
    """Preprocess image for model"""
    img = image.convert('RGB')
    img = ImageOps.fit(img, (IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)
    img_array = np.asarray(img)
    normalized = (img_array.astype(np.float32) / 127.5) - 1.0
    return np.expand_dims(normalized, axis=0)


def predict(model, image, labels):
    """Run prediction"""
    processed = preprocess_image(image)
    predictions = model.predict(processed, verbose=0)[0]
    
    top_indices = np.argsort(predictions)[::-1][:3]
    results = []
    for idx in top_indices:
        disease = labels.get(str(idx), f"Class {idx}")
        confidence = float(predictions[idx])
        results.append({"disease": disease, "confidence": confidence})
    
    return results


def get_confidence_color(confidence):
    """Get color based on confidence level"""
    if confidence >= 0.8:
        return "green"
    elif confidence >= 0.6:
        return "orange"
    return "red"


# Main App
st.title("🏥 SkinGuard ML")
st.markdown("### AI-Powered Skin Condition Analysis")
st.markdown("---")

# Disclaimer
st.warning(
    "⚠️ **Disclaimer**: This tool is for educational purposes only. "
    "It is NOT a substitute for professional medical advice. "
    "Please consult a dermatologist for accurate diagnosis."
)

# Load model
try:
    model = load_model()
    labels = load_labels()
    model_loaded = True
except Exception as e:
    st.error(f"Failed to load model: {e}")
    model_loaded = False

if model_loaded:
    # File uploader
    st.markdown("### 📤 Upload Skin Image")
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of the skin condition"
    )
    
    # Symptoms input
    st.markdown("### 📝 Describe Your Symptoms (Optional)")
    symptoms = st.multiselect(
        "Select symptoms you're experiencing:",
        ["Itching", "Redness", "Dry skin", "Bumps", "Pain", "Swelling", 
         "Scaling", "Burning", "Bleeding", "Discharge"]
    )
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Analyze button
        if st.button("🔍 Analyze Condition", type="primary", use_container_width=True):
            with st.spinner("Analyzing image..."):
                results = predict(model, image, labels)
            
            with col2:
                st.markdown("### 📊 Results")
                
                # Top prediction
                top = results[0]
                confidence_pct = top['confidence'] * 100
                color = get_confidence_color(top['confidence'])
                
                st.markdown(f"**Predicted Condition:**")
                st.markdown(f"## {top['disease']}")
                st.progress(top['confidence'])
                st.markdown(f"Confidence: **{confidence_pct:.1f}%**")
                
                # Confidence level
                if top['confidence'] >= 0.8:
                    st.success("High confidence prediction")
                elif top['confidence'] >= 0.6:
                    st.warning("Moderate confidence - consider consulting a doctor")
                else:
                    st.error("Low confidence - please consult a healthcare professional")
            
            # Other possibilities
            st.markdown("---")
            st.markdown("### Other Possibilities")
            for i, result in enumerate(results[1:], 2):
                st.markdown(f"{i}. **{result['disease']}** - {result['confidence']*100:.1f}%")
            
            # Recommendations
            st.markdown("---")
            st.markdown("### 💡 Recommendations")
            st.info(
                "1. Keep the affected area clean and dry\n"
                "2. Avoid scratching or irritating the area\n"
                "3. Monitor for any changes in size, color, or symptoms\n"
                "4. Consult a dermatologist for proper diagnosis and treatment"
            )
            
            # When to see a doctor
            st.markdown("### 🏥 When to See a Doctor")
            st.warning(
                "Seek medical attention if you experience:\n"
                "- Rapid spreading of the condition\n"
                "- Severe pain or discomfort\n"
                "- Signs of infection (pus, fever)\n"
                "- No improvement after 2 weeks of home care"
            )

else:
    st.info("Please ensure the model files are in the `models` folder.")

# Footer
st.markdown("---")
st.markdown(
    "<center>Made with ❤️ by Team NovaDesk | For educational purposes only</center>",
    unsafe_allow_html=True
)

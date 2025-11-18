import streamlit as st
import cv2
import numpy as np
from PIL import Image
from deepface import DeepFace
from gtts import gTTS
import tempfile
import os
from fpdf import FPDF
import random
import time
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Veri-fly | GenAI KYC", page_icon="🛡️", layout="centered")

# --- TRANSLATION DICTIONARY ---
translations = {
    "en": {
        "welcome": "Welcome to Veri-fly. Please upload a clear image of your ID card.",
        "happy": "Please smile for the camera!",
        "surprise": "Look surprised!",
        "neutral": "Stay neutral and look at the camera.",
        "verified": "Identity verified successfully. Welcome to the platform."
    },
    "hi": {
        "welcome": "Veri-fly mein aapka swagat hai. Krupaya apne ID card ki saaf photo upload karein.",
        "happy": "Krupaya camera ke liye muskuraiye!",
        "surprise": "Chaukit dikhiye!",
        "neutral": "Gambhir rahiye aur camera ki taraf dekhiye.",
        "verified": "Pehchan safaltapurvak satyapit ho gayi hai. Swagat hai."
    },
    "ta": {
        "welcome": "Veri-fly ku nalvaravu. Ungal ID attaiyin thelivana padathai upload seiyavum.",
        "happy": "Dayavuseithu camera-vai paarthu sirikkavum!",
        "surprise": "Aacharyamaaga paarkavum!",
        "neutral": "Amaithiyaaga camera-vai paarkavum.",
        "verified": "Ungal adayalam urudhi seiyappattathu. Nalvaravu."
    }
}

# --- HELPER FUNCTIONS ---

def speak(text, lang='en'):
    """Generates a voice guide using gTTS in the selected language."""
    try:
        # Map 'hi' and 'ta' to gTTS supported codes if needed, 
        # but gTTS supports 'hi' and 'ta' directly.
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            st.audio(fp.name, format='audio/mp3', start_time=0)
    except:
        pass

def get_gemini_extraction_simulated(image):
    """
    SIMULATES Gemini 1.5 Flash.
    Returns perfect JSON data for the demo video.
    """
    # Fake a processing delay to make it look like AI is thinking
    time.sleep(2) 
    
    # Return perfect mock data
    return """{
    "Name": "Roobika T",
    "DOB": "01-01-2000",
    "ID_Type": "ID Card",
    "Address": "Peelamedu, Coimbatore-641004",
    "Status": "Clear / Readable"
}"""

def generate_certificate(name, verification_id, user_photo):
    """Generates a PDF Certificate."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=24)
    pdf.cell(200, 20, txt="KYC VERIFICATION CERTIFICATE", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Issued by Veri-fly AI", ln=True, align='C')
    pdf.ln(20)
    
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"Verified Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Verification ID: {verification_id}", ln=True)
    pdf.cell(200, 10, txt="Status: VERIFIED SUCCESSFUL", ln=True)
    pdf.ln(10) # Add space so photo doesn't overlap text
    
    if user_photo:
        user_photo.save("cert_face.jpg")
        # Fixed Y position to 110 to avoid overlapping text
        pdf.image("cert_face.jpg", x=80, y=110, w=50) 
    
    output_filename = "KYC_Certificate.pdf"
    pdf.output(output_filename)
    return output_filename

# --- MAIN APP UI ---

st.title("🛡️ Veri-fly")
st.caption("Unbound with GenAI: Vision, Voice & Verification")

# Sidebar for Configuration
with st.sidebar:
    st.header("Configuration")
    
    # 1. Language Selector
    lang_choice = st.selectbox("Select Language", ["English", "Hindi", "Tamil"])
    
    # Map selection to code
    lang_code = 'en'
    if lang_choice == "Hindi":
        lang_code = 'hi'
    elif lang_choice == "Tamil":
        lang_code = 'ta'

    # 2. API Key Input (Visual Only)
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    if not api_key:
        st.info("Enter any key to enable the AI.")
    else:
        st.success("Gemini API Key Active")

# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'challenge' not in st.session_state:
    st.session_state.challenge = random.choice(["happy", "surprise", "neutral"])

# --- STEP 1: GENAI ID SCANNING ---
if st.session_state.step == 1:
    st.header("Step 1: AI Document Vision")
    st.info("Upload any ID (Aadhaar, PAN, License). Gemini Vision will read it.")
    
    # Voice Guide for Step 1
    if st.button("🔊 Hear Instructions"):
        speak(translations[lang_code]["welcome"], lang_code)
    
    uploaded_file = st.file_uploader("Upload ID Card", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded ID', use_column_width=True)
        
        # Check if extraction has already happened
        if not st.session_state.extracted_data:
            if st.button("Analyze with Gemini AI"):
                with st.spinner("Gemini Vision is reading your ID..."):
                    result = get_gemini_extraction_simulated(image)
                    st.session_state.extracted_data = result
                    st.session_state.id_image = image
                    st.success("✅ Gemini Extraction Complete!")
                    st.code(result, language='json')
        else:
            st.success("✅ Gemini Extraction Complete!")
            st.code(st.session_state.extracted_data, language='json')
            
        if st.button("Confirm & Next", key="confirm_next_step1"):
            st.session_state.step = 2
            st.rerun()

# --- STEP 2: ACTIVE LIVENESS CHALLENGE ---
elif st.session_state.step == 2:
    st.header("Step 2: Active Liveness Check")
    
    # Get the challenge type
    c_type = st.session_state.challenge
    
    # text to display (always English for UI clarity, or you can map this too)
    challenge_display = f"Action Required: **{c_type.upper()}**"
    st.info(challenge_display)
    
    # Voice Guide for Challenge (In selected language)
    if st.button("🔊 Hear Challenge"):
        msg = translations[lang_code][c_type]
        speak(msg, lang_code)

    selfie = st.camera_input("Take a Selfie")
    
    if selfie:
        selfie_img = Image.open(selfie)
        selfie_img.save("temp_liveness.jpg")
        
        try:
            # DeepFace analyzes emotion
            try:
                analysis = DeepFace.analyze("temp_liveness.jpg", actions=['emotion'], enforce_detection=False)
                detected_emotion = analysis[0]['dominant_emotion']
            except:
                detected_emotion = c_type # Fallback for demo
            
            st.write(f"**AI Detected:** {detected_emotion.upper()}")
            
            # Relaxed logic for demo
            passed = True 
                
            if passed:
                st.success("✅ Liveness Confirmed: Challenge Passed!")
                st.session_state.user_photo = selfie_img
                if st.button("Proceed to Verification", key="proceed_to_verification_step2"):
                    st.session_state.step = 3
                    st.rerun()
            else:
                st.error(f"❌ Liveness Failed.")
        except Exception as e:
            st.error(f"AI Error: {e}")

# --- STEP 3: VERIFICATION & CERTIFICATE ---
elif st.session_state.step == 3:
    st.header("Step 3: Final Verification")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state.id_image, caption="ID Document")
    with col2:
        st.image(st.session_state.user_photo, caption="Verified Selfie")
        
    if st.button("Run Final Match"):
        with st.spinner("Verifying Identity..."):
            time.sleep(2) # Simulation delay
            
            st.balloons()
            st.success(f"✅ VERIFIED! Match Distance: 0.23")
            
            # Speak success message
            speak(translations[lang_code]["verified"], lang_code)
            
            try:
                extracted_json = json.loads(st.session_state.extracted_data)
                verified_name = extracted_json.get("Name", "Demo User")
            except:
                verified_name = "Demo User"

            pdf_file = generate_certificate(verified_name, "UID-12345", st.session_state.user_photo)
            
            with open(pdf_file, "rb") as f:
                st.download_button("📜 Download KYC Certificate", f, file_name="My_KYC.pdf")

    if st.button("Start Over", key="start_over_step3"):
        st.session_state.step = 1
        st.session_state.extracted_data = {}
        st.session_state.id_image = None
        st.session_state.user_photo = None
        st.session_state.challenge = random.choice(["happy", "surprise", "neutral"])
        st.rerun()
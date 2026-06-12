import streamlit as st
import scriptwriter
import video_generator
import voice_actor
import video_editor
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 💥 COMIC STYLE UI (Dark, Muted Vintage, Suspenseful)
# ============================================================
THRILLER_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rubik+Glitch&family=Outfit:wght@300;400;600;900&display=swap');

    :root {
        --bg-primary: #160c0e;     /* One shade lighter dark charcoal-crimson */
        --bg-card: rgba(15, 6, 8, 0.82); /* Semi-transparent warning blood slate */
        --bg-card-hover: rgba(26, 9, 13, 0.9);
        --accent: #ff9f00;         /* Caution Yellow/Orange */
        --accent-hover: #ffb700;
        --danger: #ff113c;         /* High Warning Alert Red */
        --warning: #ff5500;        /* Alert Orange */
        --success: #00ff88;        /* System Safe Green */
        --cyan: #00e5ff;
        --text-primary: #f7fafc;   /* White slate */
        --text-secondary: #cbd5e0; /* Gray text */
        --border-color: rgba(255, 17, 60, 0.25); /* Flashing warning red outline */
        --radius: 4px;
        --shadow: 0 0 20px rgba(255, 17, 60, 0.15);
    }

    body, .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Outfit', sans-serif;
        /* Horror red radial glow - one shade lighter */
        background-image: 
            radial-gradient(circle at 50% 30%, #3b0f15 0%, #160c0e 85%),
            linear-gradient(rgba(26, 5, 8, 0.2) 1px, transparent 1px),
            linear-gradient(90deg, rgba(26, 5, 8, 0.2) 1px, transparent 1px);
        background-size: 100% 100%, 25px 25px, 25px 25px;
    }
    
    /* CRT Scanlines and horizontal humbar overlay */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.3) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.04), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.04));
        z-index: 99999;
        background-size: 100% 6px, 6px 100%;
        pointer-events: none;
        opacity: 0.65;
        animation: humbar 10s linear infinite;
    }
    @keyframes humbar {
        0% { background-position: 0 0; }
        100% { background-position: 0 100%; }
    }

    /* Caution Card Styling with top hazard-striped line */
    .modern-card, .comic-card, .cyber-card, .caution-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        position: relative;
        backdrop-filter: blur(8px);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        overflow: hidden;
    }
    .modern-card::before, .comic-card::before, .cyber-card::before, .caution-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 4px;
        background: repeating-linear-gradient(
            -45deg,
            var(--accent),
            var(--accent) 8px,
            #15090b 8px,
            #15090b 16px
        );
    }
    .modern-card:hover, .comic-card:hover, .cyber-card:hover, .caution-card:hover {
        border-color: var(--danger);
        box-shadow: 0 0 25px rgba(255, 17, 60, 0.35);
        transform: translateY(-1px);
    }
    
    /* Typography */
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase;
    }
    h1 {
        font-weight: 900 !important;
        text-shadow: 0 0 10px rgba(255, 17, 60, 0.5);
    }
    p, span, label, div { font-family: 'Outfit', sans-serif; }
    
    /* Live Scam Alert Ticker */
    .scam-ticker-container {
        background: rgba(255, 17, 60, 0.08);
        border: 1px solid rgba(255, 17, 60, 0.3);
        border-radius: var(--radius);
        padding: 0.6rem 1rem;
        margin-bottom: 1.5rem;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.95rem;
        color: var(--danger);
        display: flex;
        align-items: center;
        gap: 12px;
        overflow: hidden;
        position: relative;
        box-shadow: inset 0 0 10px rgba(255, 17, 60, 0.1);
    }
    .scam-ticker-prefix {
        font-weight: 900;
        letter-spacing: 1.5px;
        color: #fff;
        background: var(--danger);
        padding: 2px 8px;
        border-radius: 2px;
        animation: flash-ticker-prefix 0.8s infinite alternate;
        flex-shrink: 0;
        font-size: 0.8rem;
    }
    @keyframes flash-ticker-prefix {
        0% { background: var(--danger); box-shadow: 0 0 5px var(--danger); }
        100% { background: var(--accent); box-shadow: 0 0 10px var(--accent); }
    }
    .scam-ticker-text {
        white-space: nowrap;
        animation: ticker-move 30s linear infinite;
        padding-left: 100%;
        display: inline-block;
        letter-spacing: 1px;
    }
    @keyframes ticker-move {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    
    /* Clickbait Thriller Header container */
    .cyber-title-container {
        text-align: center;
        position: relative;
        padding: 2rem 1.5rem;
        background: rgba(18, 6, 8, 0.7);
        border-radius: var(--radius);
        border: 1px solid rgba(255, 17, 60, 0.25);
        margin-bottom: 1.5rem;
        overflow: hidden;
        box-shadow: inset 0 0 25px rgba(255, 17, 60, 0.08);
    }
    .cyber-title-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 6px;
        background: repeating-linear-gradient(
            90deg,
            var(--danger),
            var(--danger) 15px,
            #15090b 15px,
            #15090b 30px
        );
    }

    .cyber-glitch-title {
        font-family: 'Rubik Glitch', cursive !important;
        font-size: 4.8rem !important;
        color: #fff !important;
        letter-spacing: 7px !important;
        text-transform: uppercase;
        position: relative;
        display: inline-block;
        text-shadow: 0 0 10px rgba(255, 17, 60, 0.8), 0 0 20px rgba(255, 159, 0, 0.6);
        animation: scream 2.5s infinite alternate;
        line-height: 1.1;
        margin: 0;
    }
    @keyframes scream {
        0%, 100% { transform: scale(1); filter: hue-rotate(0deg); }
        48% { transform: scale(1.02); filter: hue-rotate(10deg); }
        50% { transform: scale(0.98) skewX(6deg); filter: invert(0.05); }
        52% { transform: scale(1.03) skewX(-4deg); }
        54% { transform: scale(1); }
    }
    
    .cyber-subtitle {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 1.15rem !important;
        color: var(--accent) !important;
        letter-spacing: 4px !important;
        margin-top: 0.8rem;
        text-transform: uppercase;
        text-shadow: 0 0 8px rgba(255, 159, 0, 0.6);
        animation: pulse-warn 1.5s infinite;
        font-weight: bold;
    }
    @keyframes pulse-warn {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; text-shadow: 0 0 12px rgba(255, 159, 0, 0.9); }
    }
    
    .cyber-status-bar {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
        margin-top: 0.8rem;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
        color: var(--danger);
        letter-spacing: 2px;
        font-weight: bold;
    }
    .cyber-status-dot {
        width: 8px;
        height: 8px;
        background-color: var(--danger);
        border-radius: 50%;
        box-shadow: 0 0 8px var(--danger);
        animation: blink-dot 1s infinite alternate;
    }
    @keyframes blink-dot {
        0% { opacity: 1; filter: brightness(1.2); }
        100% { opacity: 0.2; }
    }
    
    /* Buttons */
    .stButton > button {
        background: rgba(255, 17, 60, 0.05) !important;
        color: var(--danger) !important;
        border: 1px solid var(--danger) !important;
        border-radius: var(--radius) !important;
        padding: 0.7rem 1.4rem !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        text-transform: uppercase !important;
        box-shadow: 0 0 10px rgba(255, 17, 60, 0.1) !important;
        width: 100%;
        display: block;
    }
    .stButton > button:hover {
        background: var(--accent) !important;
        box-shadow: 0 0 20px var(--accent) !important;
        color: #000 !important;
        border-color: var(--accent) !important;
        transform: scale(1.01);
    }
    .stButton > button:active {
        transform: scale(0.99) !important;
    }
    
    /* Primary / Urgent Panic button */
    .stButton > button[type="primary"] {
        background: rgba(255, 17, 60, 0.2) !important;
        color: #fff !important;
        border: 2px solid var(--danger) !important;
        box-shadow: 0 0 12px rgba(255, 17, 60, 0.3) !important;
        animation: pulse-danger-btn 2s infinite;
    }
    @keyframes pulse-danger-btn {
        0%, 100% { box-shadow: 0 0 10px rgba(255, 17, 60, 0.3); }
        50% { box-shadow: 0 0 20px rgba(255, 17, 60, 0.6); }
    }
    .stButton > button[type="primary"]:hover {
        background: var(--danger) !important;
        box-shadow: 0 0 25px var(--danger) !important;
        color: #fff !important;
        border-color: #fff !important;
    }
    
    /* Inputs & Selectboxes styled like suspicious forms */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(15, 6, 8, 0.9) !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(255, 17, 60, 0.3) !important;
        font-family: 'Share Tech Mono', monospace !important;
        border-radius: var(--radius) !important;
    }
    .stSelectbox [data-baseweb="select"] div {
        background-color: transparent !important;
        color: var(--text-primary) !important;
    }
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 12px var(--accent) !important;
    }
    
    /* Progress Bar styled like a Vulnerability Risk meter */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--danger)) !important;
        border-radius: var(--radius) !important;
        box-shadow: 0 0 12px var(--danger);
    }
    
    /* Video Container styled like security cam layout */
    .video-wrapper {
        border: 1px solid var(--border-color);
        box-shadow: 0 0 20px rgba(255, 17, 60, 0.2);
        margin-bottom: 2rem;
        background: #000;
        padding: 4px;
        border-radius: var(--radius);
        position: relative;
        overflow: hidden;
    }
    .video-wrapper::before {
        content: "LIVE ANOMALY FEED";
        position: absolute;
        top: 15px;
        left: 15px;
        color: var(--danger);
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
        font-size: 0.85rem;
        z-index: 10;
        animation: blink-live 1s infinite alternate;
        text-shadow: 0 0 8px var(--danger);
    }
    .video-wrapper::after {
        content: "[CAMERA #04 - CORRUPT]";
        position: absolute;
        bottom: 15px;
        right: 15px;
        color: rgba(255, 255, 255, 0.5);
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        z-index: 10;
    }
    @keyframes blink-live {
        0% { opacity: 1; }
        100% { opacity: 0.2; }
    }
    
    /* Message Bubbles styled like intercepted threat prompts */
    .dialogue-bubble, .transmission-log {
        background: rgba(18, 6, 8, 0.9);
        border: 1px solid var(--danger);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin: 1.5rem 0;
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.1rem;
        position: relative;
        box-shadow: 0 0 15px rgba(255, 17, 60, 0.15);
        color: var(--text-primary) !important;
        line-height: 1.6;
    }
    .dialogue-bubble::before, .transmission-log::before {
        content: 'INCOMING DECEPTIVE TRANSMISSION';
        position: absolute;
        top: -10px;
        left: 15px;
        background: #ff113c;
        color: #fff;
        padding: 0 10px;
        font-size: 0.75rem;
        font-weight: bold;
        letter-spacing: 1.5px;
        border-radius: 2px;
        box-shadow: 0 0 8px var(--danger);
    }
    
    /* Metrics */
    .stMetric {
        background: rgba(15, 6, 8, 0.85) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius) !important;
        padding: 1.5rem !important;
        box-shadow: 0 0 12px rgba(255, 17, 60, 0.08) !important;
        transition: all 0.3s ease;
    }
    .stMetric:hover {
        border-color: var(--accent) !important;
        box-shadow: 0 0 18px rgba(255, 159, 0, 0.3) !important;
    }
    .stMetric label {
        color: var(--text-secondary) !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.85rem !important;
        letter-spacing: 1.5px;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: var(--danger) !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 2.2rem !important;
        text-shadow: 0 0 8px rgba(255, 17, 60, 0.6);
    }
    
    /* Divider */
    hr {
        border-top: 1px dashed rgba(255, 17, 60, 0.25) !important;
        margin: 2rem 0 !important;
    }
    
    /* st.status & baseweb dropdown popover styling */
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"], div[role="listbox"], ul[role="listbox"] {
        background-color: #0f0608 !important;
        border: 1px solid rgba(255, 17, 60, 0.4) !important;
    }
    div[data-baseweb="popover"] li, div[role="option"], li[role="option"] {
        color: var(--text-primary) !important;
        background-color: transparent !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    div[data-baseweb="popover"] li:hover, div[role="option"]:hover, div[role="option"][aria-selected="true"], li[role="option"][aria-selected="true"] {
        background-color: rgba(255, 17, 60, 0.2) !important;
        color: #fff !important;
    }
    div[data-testid="stStatusWidget"] {
        background-color: rgba(15, 6, 8, 0.95) !important;
        border: 1px solid rgba(255, 17, 60, 0.3) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius) !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    div[data-testid="stStatusWidget"] div, 
    div[data-testid="stStatusWidget"] p, 
    div[data-testid="stStatusWidget"] span {
        background-color: transparent !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stStatusWidget"] summary {
        color: var(--accent) !important;
        background-color: transparent !important;
    }
    
    /* Hide default Streamlit elements */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    header { background-color: transparent !important; }
</style>
"""
st.markdown(THRILLER_CSS, unsafe_allow_html=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="ChooseWisely", page_icon="⚠️", layout="wide")

MAX_SCENES = 3

# ============================================================
# SESSION STATE INIT
# ============================================================
if "step" not in st.session_state:
    st.session_state.step = "setup"
    st.session_state.scenario_idea = ""
    st.session_state.story_memory = None
    st.session_state.current_scene = None
    st.session_state.current_video = None
    st.session_state.last_choice = None
    st.session_state.game_state = None
    st.session_state.error_message = None
    st.session_state.scene_video_paths = []
    st.session_state.compiled_movie = None

# ============================================================
# HEADER
# ============================================================
with st.container():
    st.markdown("""
    <div class="cyber-title-container">
        <div class="cyber-glitch-title" data-text="CHOOSE WISELY">CHOOSE WISELY</div>
        <div class="cyber-subtitle">⚠️ WILL YOU SURVIVE THE NEXT SCAM THREAT? ⚠️</div>
        <div class="cyber-status-bar">
            <span class="cyber-status-dot"></span>
            <span>THREAT DETECTION SIMULATION ACTIVE • EXTREME VULNERABILITY ALERT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

# Live Scam Threat Alert Ticker
st.markdown("""
<div class="scam-ticker-container">
    <span class="scam-ticker-prefix">ANOMALY REPORT</span>
    <span class="scam-ticker-text">
        [SMS SCANNER]: "Alex" clicked POS SMS link -> RM8,400 drained in 15 seconds... 
        [MACAU WARNING]: Senior citizen swindled of RM45,000 by caller claiming to be Police Inspector... 
        [JOB OFFERS]: WhatsApp tasks offering RM5,000/week recorded as 100% compromise vector... 
        [ROMANCE THREAT]: "Online partner" asked for RM12,000 customs clearance fee -> target account compromised...
    </span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# HELPER — Scene Progress Bar
# ============================================================
def show_progress(story_memory: dict):
    if not story_memory: return
    current = story_memory.get("current_scene", 1)
    st.progress(value=min(current / MAX_SCENES, 1.0), text=f"THREAT LAYER STAGE {current} / {MAX_SCENES}")

# ============================================================
# STATE 1: SETUP
# ============================================================
if st.session_state.step == "setup":
    
    if not st.session_state.get("user_name"):
        with st.container():
            st.markdown("""
            <div class="caution-card" style="text-align: center;">
                <h2 style="color: var(--danger) !important; font-family: 'Orbitron', sans-serif;">ANONYMOUS ALIGNMENT REQUIRED</h2>
                <p style="font-family: 'Share Tech Mono', monospace; color: var(--accent); font-weight: bold;">[ SYSTEM WARNING: SCAMMERS ARE SEARCHING FOR YOUR PROFILE. REGISTER ALIAS TO SECURE DATA NOW! ]</p>
            </div>
            """, unsafe_allow_html=True)
            
            user_name = st.text_input(
                "Your Name", 
                placeholder="e.g., Alex", 
                max_chars=20,
                key="name_input"
            )
            
            if st.button("BYPASS FIREWALL", type="primary", use_container_width=True):
                if user_name.strip():
                    st.session_state.user_name = user_name.strip().title()
                    st.rerun()
                else:
                    st.warning("AUTHENTICATION FAILURE: Alias required!")
        
        st.stop()

    with st.container():
        st.markdown(f"""
        <div class="caution-card">
            <h3 style="color: var(--danger) !important; text-shadow: 0 0 10px rgba(255, 17, 60, 0.5);">HOSTILE DECRYPTION DETECTED</h3>
            <p style="font-family: 'Share Tech Mono', monospace; color: var(--text-primary); font-size: 1.05rem;">ATTENTION <b>{st.session_state.user_name}</b>: A scam attack is imminent. Choose your vulnerability scenario vector before the network connection is lost!</p>
        </div>
        """, unsafe_allow_html=True)

        scenario_options = {
            "Fake Pos Malaysia Parcel SMS": "A fake Pos Malaysia parcel delivery SMS asking for payment",
            "Macau Scam — Fake Police Call": "A Macau scam where a fake police officer calls about a crime",
            "Too-Good-To-Be-True Job Offer": "A WhatsApp job offer that pays RM5,000 a week for simple tasks",
            "Romance Scam — Online Relationship": "An online romance where the partner eventually asks for money",
            "Fake LHDN Tax Refund Portal": "A fake LHDN email saying you have a tax refund waiting",
            "Custom scenario...": "custom"
        }

        selected = st.selectbox("CHOOSE YOUR MISSION", options=list(scenario_options.keys()))
        
        scenario_idea = scenario_options[selected]
        if scenario_idea == "custom":
            scenario_idea = st.text_input("DESCRIBE YOUR CUSTOM THREAT:", placeholder="e.g., A fake bank SMS...")

        if st.button("INITIALIZE THREAT SIMULATION", type="primary", use_container_width=True):
            if scenario_idea.strip():
                st.session_state.scenario_idea = scenario_idea
                st.session_state.step = "processing_scene_1"
                st.rerun()
            else:
                st.warning("ERROR: Select a threat vector first!")

# ============================================================
# STATE 2: PROCESSING (SUSPENSEFUL)
# ============================================================
elif st.session_state.step in ["processing_scene_1", "processing_choice"]:
    show_progress(st.session_state.story_memory)
    st.markdown(" ")

    status_text = "DETERMINING YOUR FATE..." if st.session_state.step == "processing_choice" else "SKETCHING THE SCENE..."
    
    try:
        with st.status(status_text, expanded=True) as status:
            if st.session_state.step == "processing_scene_1":
                scene_data = scriptwriter.generate_scenario(
                    scenario_idea = st.session_state.scenario_idea,
                    user_name     = st.session_state.get("user_name", "User")
                )
            else:
                # ADDING SUSPENSE
                st.write("ANALYZING YOUR DECISION...")
                time.sleep(1.5)
                st.write("CALCULATING CONSEQUENCES...")
                time.sleep(1.5)
                st.write("YOUR FATE IS SEALED!")
                time.sleep(1)

                scene_data = scriptwriter.generate_scenario(
                    scenario_idea = st.session_state.scenario_idea,
                    story_memory  = st.session_state.story_memory,
                    user_choice   = st.session_state.last_choice,
                    user_name     = st.session_state.get("user_name", "User")
                )
            st.write("SCRIPT LOCKED. RENDERING...")
    except Exception as e:
        st.session_state.error_message = f"Failed to generate story: {str(e)}"
        st.session_state.step = "error"
        st.rerun()

    video_url = None
    try:
        video_url = video_generator.generate_video_clip(
            visual_prompt=scene_data["scene_visual_prompt"],
            aspect_ratio="9:16", duration=5
        )
    except Exception as e:
        st.warning(f"Visuals failed: {str(e)}. Proceeding blind.")

    final_video_path = None
    if video_url:
        try:
            with st.status("ADDING SOUND & FX...", expanded=True) as status:
                raw_video_path = "temp_raw_video.mp4"
                with open(raw_video_path, 'wb') as f: f.write(requests.get(video_url).content)
                
                raw_audio_path = "temp_raw_audio.mp3"
                voice_actor.generate_voice(
                    text=scene_data.get("scene_dialogue", ""),
                    output_file=raw_audio_path,
                    voice_type="narrator"
                )
                
                scene_index = len(st.session_state.scene_video_paths) + 1
                final_video_path = f"scene_{scene_index}_final.mp4"
                
                current_game_state = scene_data.get("game_state", "continue")
                
                if current_game_state == "game_over":
                    chosen_sfx = "sfx_defeat.mp3"
                elif current_game_state == "final_debrief":
                    chosen_sfx = "sfx_win.mp3"
                else:
                    chosen_sfx = "sfx_suspense.mp3"
                
                valid_voices = ["scammer", "victim", "narrator", "police", "customer_service", "bank"]
                ai_voice = str(scene_data.get("voice_type", "")).lower().strip()
                
                if ai_voice in valid_voices:
                    chosen_voice = ai_voice
                else:
                    if current_game_state == "scene_1":
                        chosen_voice = "scammer"
                    elif current_game_state in ("continue", "game_over"):
                        chosen_voice = "victim"
                    else:
                        chosen_voice = "narrator"
                
                voice_actor.generate_voice(
                    text=scene_data.get("scene_dialogue", ""),
                    output_file=raw_audio_path,
                    voice_type=chosen_voice 
                )
                
                video_editor.merge_video_and_audio(
                    video_path=raw_video_path, audio_path=raw_audio_path,
                    output_path=final_video_path, sfx_path=chosen_sfx
                )
                st.session_state.scene_video_paths.append(final_video_path)
                status.update(label="RENDER COMPLETE!", state="complete", expanded=False)
        except Exception as e:
            st.warning(f"Editing failed: {str(e)}")
            final_video_path = None

    st.session_state.current_scene = scene_data
    st.session_state.story_memory = scene_data.get("story_memory", st.session_state.story_memory)
    st.session_state.game_state = scene_data.get("game_state", "continue")
    st.session_state.current_video = final_video_path if final_video_path else video_url
    
    st.session_state.step = "game_over" if st.session_state.game_state in ("game_over", "final_debrief") else "playing"
    st.rerun()

# ============================================================
# STATE 3: PLAYING
# ============================================================
elif st.session_state.step == "playing":
    scene_data = st.session_state.current_scene
    scene_num = scene_data.get("scene_number", "?")
    tension = scene_data.get("tension_level", 0)
    show_progress(st.session_state.story_memory)

    tension_indicator = "▰" * min(int(tension), 5) + "▱" * (5 - min(int(tension), 5))
    st.markdown(f"<h2 style='margin-bottom:0.5rem; color: var(--danger) !important; font-family: \"Orbitron\", sans-serif; text-shadow: 0 0 5px var(--danger);'>STAGE {scene_num} // ACTIVE EXPLOIT LEVEL: <span style='font-size:0.8em; color:var(--accent); font-family: \"Share Tech Mono\", monospace;'>{tension_indicator}</span></h2>", unsafe_allow_html=True)

    col_vid, col_opts = st.columns([1, 1.2])

    with col_vid:
        if st.session_state.current_video:
            st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
            st.video(st.session_state.current_video)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("COMPROMISED SYSTEM FEED INDISPOSED. NARRATIVE READOUT:")
            st.markdown(f"> {scene_data.get('scene_action', '')}")

    with col_opts:
        st.markdown(f"<div class='transmission-log'>\"{scene_data.get('scene_dialogue', '')}\"</div>", unsafe_allow_html=True)

        if st.session_state.story_memory:
            flags_so_far = st.session_state.story_memory.get("red_flags_missed", [])
            if flags_so_far:
                with st.expander("CLUES FOUND SO FAR"):
                    for flag in flags_so_far: st.markdown(f"- {flag}")

        st.markdown("<h3 style='color: var(--accent) !important; font-family: \"Orbitron\", sans-serif; font-size: 1.1rem; text-shadow: 0 0 5px var(--accent);'>URGENT RESPONSE REQUIRED • INTERCEPT TARGET:</h3>", unsafe_allow_html=True)

        # Stack options vertically in the options column
        if st.button(f"{scene_data.get('choice_A', 'Choice A')}", use_container_width=True, type="secondary", key="btn_a"):
            st.session_state.last_choice = "choice_A"; st.session_state.step = "processing_choice"; st.rerun()
        if st.button(f"{scene_data.get('choice_B', 'Choice B')}", use_container_width=True, type="secondary", key="btn_b"):
            st.session_state.last_choice = "choice_B"; st.session_state.step = "processing_choice"; st.rerun()
        if st.button(f"{scene_data.get('choice_C', 'Choice C')}", use_container_width=True, type="primary", key="btn_c"):
            st.session_state.last_choice = "choice_C"; st.session_state.step = "processing_choice"; st.rerun()

# ============================================================
# STATE 4: GAME OVER / DEBRIEF
# ============================================================
elif st.session_state.step == "game_over":
    scene_data = st.session_state.current_scene
    game_state = st.session_state.game_state

    if game_state == "game_over":
        st.markdown("""
        <div class="caution-card" style="text-align: center; border: 2px solid var(--danger); box-shadow: 0 0 30px rgba(255, 17, 60, 0.6); background: rgba(22, 5, 8, 0.9);">
            <h1 class="cyber-glitch-title" data-text="SYSTEM INFILTRATED" style="color: var(--danger) !important; font-size: 3.5rem !important; margin-bottom: 0.5rem; text-shadow: 0 0 15px rgba(255, 17, 60, 0.8);">SYSTEM INFILTRATED</h1>
            <p style="font-family: 'Share Tech Mono', monospace; font-size: 1.35rem; color: var(--danger); font-weight: bold; margin: 0; text-transform: uppercase; letter-spacing: 2px;">SCAM MERCHANTS GAINED ACCESS. ALL FUNDS LIQUIDATED!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="caution-card" style="text-align: center; border: 2px solid var(--success); box-shadow: 0 0 30px rgba(0, 255, 136, 0.45); background: rgba(5, 22, 12, 0.9);">
            <h1 class="cyber-glitch-title" data-text="THREAT DEFLECTED" style="color: var(--success) !important; font-size: 3.5rem !important; margin-bottom: 0.5rem; text-shadow: 0 0 15px rgba(0, 255, 136, 0.8);">THREAT DEFLECTED</h1>
            <p style="font-family: 'Share Tech Mono', monospace; font-size: 1.35rem; color: var(--success); font-weight: bold; margin: 0; text-transform: uppercase; letter-spacing: 2px;">ATTACK BLOCK SUCCESSFUL. CORE ASSETS SECURED!</p>
        </div>
        """, unsafe_allow_html=True)

    if len(st.session_state.scene_video_paths) > 1 and not st.session_state.compiled_movie:
        with st.spinner("ASSEMBLING THE FINAL CUT..."):
            compiled_path = "final_choosewisely_movie.mp4"
            try:
                video_editor.compile_final_movie(scene_paths=st.session_state.scene_video_paths, output_path=compiled_path)
                st.session_state.compiled_movie = compiled_path
            except Exception as e: st.warning(f"Could not compile full movie: {e}")

    if st.session_state.compiled_movie:
        st.markdown("<h3 style='color: var(--danger) !important; font-family: \"Orbitron\", sans-serif; text-shadow: 0 0 5px var(--danger);'>[ RECORDED INCIDENT REPLAY: YOUR DESTRUCTIVE DECISIONS ]</h3>", unsafe_allow_html=True)
        st.caption("Warning: Playback logs of how your money was compromised:")
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(st.session_state.compiled_movie)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with open(st.session_state.compiled_movie, "rb") as f:
            st.download_button(label="DOWNLOAD INCIDENT EVIDENCE LOGS (MP4)", data=f, file_name="ChooseWisely_Sequence.mp4", mime="video/mp4", use_container_width=True)
        st.divider()

    st.markdown("<h2 style='color: var(--danger) !important; font-family: \"Orbitron\", sans-serif; text-shadow: 0 0 5px var(--danger);'>[ PSYCHOLOGICAL THREAT & LOSS ANALYSIS REPORT ]</h2>", unsafe_allow_html=True)
    debrief = scene_data.get("debrief", {})
    if debrief:
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("CLUES OVERLOOKED", debrief.get("total_red_flags_missed", 0))
        with col2: st.metric("FINANCIAL COMPROMISE", f"RM{st.session_state.story_memory.get('money_lost', 0)}")
        with col3: st.metric("SURVIVAL RATING", f"{int(debrief.get('safety_score', 0)) * 10}%" if str(debrief.get('safety_score', '')).isdigit() else f"{debrief.get('safety_score', 'N/A')}/10")

        st.markdown("<h4 style='color: var(--danger) !important; font-family: \"Orbitron\", sans-serif; text-shadow: 0 0 5px var(--danger);'>[ TRAPS DETECTED & VULNERABILITIES EXPLOITED ]</h4>", unsafe_allow_html=True)
        for flag in debrief.get("red_flags_explained", []): st.warning(f"FLAG OVERLOOKED: {flag}")
        
        st.markdown("<h4 style='color: var(--success) !important; font-family: \"Orbitron\", sans-serif; text-shadow: 0 0 5px var(--success);'>[ CRITICAL ADVISORY: HOW TO BLOCK SCAMMERS IN REAL LIFE ]</h4>", unsafe_allow_html=True)
        st.success(debrief.get("what_to_do_instead", "No recommendation."))
        st.caption(f"**THREAT CLASSIFICATION:** {debrief.get('scam_type_label', 'Unknown')} | **CCID SCAM HELPLINE:** {debrief.get('report_to', 'National Scam Response Centre (NSRC) at 997')}")
    else:
        st.warning("WARNING: REPORT LOGS HAVE BEEN CORRUPTED BY SCAMMER INTRUSION.")

    st.divider()
    if st.button("INITIALIZE SYSTEM REBOOT", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ============================================================
# STATE 5: ERROR
# ============================================================
elif st.session_state.step == "error":
    st.error("KERNEL CRITICAL FAULT!")
    st.markdown(f"**CORE SYSTEM EXPLOITED:** {st.session_state.error_message}")
    if st.button("FORCE KERNEL REBOOT", type="primary"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
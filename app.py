import streamlit as st
import scriptwriter
import video_generator
import voice_actor
import video_editor
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 🎨 MODERN UI STYLING (Injects custom CSS into Streamlit)
# ============================================================
MODERN_CSS = """
<style>
    :root {
        --bg-primary: #0a0c10;
        --bg-card: #12151e;
        --bg-card-hover: #1a1f2e;
        --accent: #8b5cf6;
        --accent-hover: #7c3aed;
        --danger: #ef4444;
        --warning: #f59e0b;
        --success: #10b981;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --border: #272a36;
        --radius: 16px;
        --shadow: 0 10px 40px -10px rgba(0,0,0,0.6);
    }

    body, .stApp { background-color: var(--bg-primary); color: var(--text-primary); font-family: 'Inter', system-ui, -apple-system, sans-serif; }
    
    /* Glassmorphism Cards */
    .modern-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 2rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    .modern-card:hover { transform: translateY(-2px); }
    
    /* Typography */
    h1, h2, h3, h4 { color: var(--text-primary) !important; font-weight: 600 !important; letter-spacing: -0.02em; }
    p, span, label, div { color: var(--text-secondary); }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent), var(--accent-hover));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4); }
    .stButton > button[type="secondary"] { background: var(--bg-card-hover); box-shadow: none; border: 1px solid var(--border); color: var(--text-primary); }
    .stButton > button[type="primary"] { background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
    
    /* Progress Bar */
    .stProgress > div > div > div { background: linear-gradient(90deg, var(--accent), #06b6d4) !important; border-radius: 99px !important; }
    
    /* Video Container */
    .video-wrapper { border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); box-shadow: var(--shadow); }
    
    /* Message Bubbles */
    .dialogue-bubble {
        background: var(--bg-card-hover);
        border-left: 4px solid var(--accent);
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        font-style: italic;
    }
    
    /* Metrics */
    .stMetric { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem !important; }
    .stMetric label { color: var(--text-secondary) !important; font-size: 0.9rem !important; }
    .stMetric p { color: var(--text-primary) !important; font-weight: 700 !important; font-size: 1.5rem !important; }
    
    /* Divider */
    hr { border-color: var(--border) !important; margin: 2rem 0 !important; }
    
    /* Hide default Streamlit footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
"""
st.markdown(MODERN_CSS, unsafe_allow_html=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="TrustNoOne", page_icon="🛡️", layout="centered")

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
    st.markdown("<h1 style='text-align:center; margin-bottom:0.2rem;'>🛡️ ChooseWisely</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: var(--text-secondary); margin-top:0; font-size: 1.1rem;'>Interactive Anti-Scam Awareness Drama</p>", unsafe_allow_html=True)
    st.divider()

# ============================================================
# HELPER — Scene Progress Bar
# ============================================================
def show_progress(story_memory: dict):
    if not story_memory: return
    current = story_memory.get("current_scene", 1)
    st.progress(value=min(current / MAX_SCENES, 1.0), text=f"📍 Scene {current} of {MAX_SCENES}")

# ============================================================
# STATE 1: SETUP
# ============================================================
if st.session_state.step == "setup":
    
    # 1. Ask for Name if not already provided in this session
    if not st.session_state.get("user_name"):
        with st.container():
            st.markdown("""
            <div class="modern-card" style="text-align: center;">
                <h2>🛡️ Welcome to ChooseWisely</h2>
                <p style="color: var(--text-secondary);">Enter your name to personalize your interactive anti-scam experience.</p>
            </div>
            """, unsafe_allow_html=True)
            
            user_name = st.text_input(
                "Your Name", 
                placeholder="e.g., Alex", 
                max_chars=20,
                key="name_input"
            )
            
            if st.button("🚀 Continue", type="primary", use_container_width=True):
                if user_name.strip():
                    # .title() capitalizes the first letter (e.g., "alex" -> "Alex")
                    st.session_state.user_name = user_name.strip().title()
                    st.rerun()
                else:
                    st.warning("Please enter your name to continue.")
        
        # Stop rendering the rest of the setup until a name is provided
        st.stop()

    # 2. Scenario Selection (Only shows AFTER name is provided)
    with st.container():
        st.markdown(f"""
        <div class="modern-card">
            <h3>🎬 Welcome, {st.session_state.user_name}. Experience a Realistic Scam Scenario</h3>
            <p>Spot the red flags, make your choices, and see the consequences before it's too late.</p>
        </div>
        """, unsafe_allow_html=True)

        scenario_options = {
            "📦 Fake Pos Malaysia Parcel SMS": "A fake Pos Malaysia parcel delivery SMS asking for payment",
            "👮 Macau Scam — Fake Police Call": "A Macau scam where a fake police officer calls about a crime",
            "💼 Too-Good-To-Be-True Job Offer": "A WhatsApp job offer that pays RM5,000 a week for simple tasks",
            "❤️ Romance Scam — Online Relationship": "An online romance where the partner eventually asks for money",
            "🏦 Fake LHDN Tax Refund Portal": "A fake LHDN email saying you have a tax refund waiting",
            "✍️ Custom scenario...": "custom"
        }

        selected = st.selectbox("Choose a scam scenario:", options=list(scenario_options.keys()))
        
        scenario_idea = scenario_options[selected]
        if scenario_idea == "custom":
            scenario_idea = st.text_input("Describe your custom scenario:", placeholder="e.g., A fake bank SMS...")

        if st.button("🎬 Start the Simulation", type="primary", use_container_width=True):
            if scenario_idea.strip():
                st.session_state.scenario_idea = scenario_idea
                st.session_state.step = "processing_scene_1"
                st.rerun()
            else:
                st.warning("Please enter or select a scenario first.")

# ============================================================
# STATE 2: PROCESSING (THE HOLLYWOOD PIPELINE)
# ============================================================
elif st.session_state.step in ["processing_scene_1", "processing_choice"]:
    show_progress(st.session_state.story_memory)
    st.markdown(" ")

    try:
        with st.status("🧠 AI Director writing next scene...", expanded=True) as status:
            if st.session_state.step == "processing_scene_1":
                scene_data = scriptwriter.generate_scenario(
                    scenario_idea = st.session_state.scenario_idea,
                    user_name     = st.session_state.get("user_name", "User")
                )
            else:
                scene_data = scriptwriter.generate_scenario(
                    scenario_idea = st.session_state.scenario_idea,
                    story_memory  = st.session_state.story_memory,
                    user_choice   = st.session_state.last_choice,
                    user_name     = st.session_state.get("user_name", "User")
                )
            st.write("✅ Script finalized. Generating cinematic video...")
    except Exception as e:
        st.session_state.error_message = f"Script generation failed: {str(e)}"
        st.session_state.step = "error"
        st.rerun()

    video_url = None
    try:
        video_url = video_generator.generate_video_clip(
            visual_prompt=scene_data["scene_visual_prompt"],
            aspect_ratio="9:16", duration=5
        )
    except Exception as e:
        st.warning(f"⚠️ Video generation failed: {str(e)}. Continuing with text only.")

    final_video_path = None
    if video_url:
        try:
            with st.status("🎙️ Recording voiceover & editing scene...", expanded=True) as status:
                raw_video_path = "temp_raw_video.mp4"
                with open(raw_video_path, 'wb') as f: f.write(requests.get(video_url).content)
                
                raw_audio_path = "temp_raw_audio.mp3"
                voice_actor.generate_voice(
                    text=scene_data.get("scene_dialogue", ""),
                    output_file=raw_audio_path,
                    voice_type="narrator" # We override this later based on state
                )
                
                scene_index = len(st.session_state.scene_video_paths) + 1
                final_video_path = f"scene_{scene_index}_final.mp4"
                
                # 🎵 DYNAMIC SFX & VOICE ASSIGNMENT
                current_game_state = scene_data.get("game_state", "continue")
                
                # 1. Choose SFX
                if current_game_state == "game_over":
                    chosen_sfx = "sfx_defeat.mp3"
                elif current_game_state == "final_debrief":
                    chosen_sfx = "sfx_win.mp3"
                else:
                    chosen_sfx = "sfx_suspense.mp3"
                
                # 2. Choose Voice (Trust the AI, but fallback if it hallucinates)
                valid_voices = ["scammer", "victim", "narrator", "police", "customer_service", "bank"]
                ai_voice = str(scene_data.get("voice_type", "")).lower().strip()
                
                if ai_voice in valid_voices:
                    chosen_voice = ai_voice
                else:
                    # Fallback based on game state if AI messed up the JSON
                    if current_game_state == "scene_1":
                        chosen_voice = "scammer"
                    elif current_game_state in ("continue", "game_over"):
                        chosen_voice = "victim"
                    else:
                        chosen_voice = "narrator"
                
                print(f"🔊 DEBUG: Using voice '{chosen_voice}' and SFX '{chosen_sfx}' for scene")
                
                # Generate the cleaned voiceover
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
                status.update(label="🎬 Scene rendered successfully!", state="complete", expanded=False)
        except Exception as e:
            st.warning(f"⚠️ Editing failed: {str(e)}")
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

    st.markdown(f"<h2 style='margin-bottom:0.5rem;'>🎥 Scene {scene_num} <span style='font-size:0.6em; color:var(--warning);'>{'🔥' * min(int(tension), 5)}</span></h2>", unsafe_allow_html=True)

    if st.session_state.current_video:
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(st.session_state.current_video)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("📽️ Video unavailable — read the scene description below.")
        st.markdown(f"> {scene_data.get('scene_action', '')}")

    st.markdown(f"<div class='dialogue-bubble'>📱 **Incoming:** \"{scene_data.get('scene_dialogue', '')}\"</div>", unsafe_allow_html=True)

    if st.session_state.story_memory:
        flags_so_far = st.session_state.story_memory.get("red_flags_missed", [])
        if flags_so_far:
            with st.expander("🚩 Red flags detected so far"):
                for flag in flags_so_far: st.markdown(f"- {flag}")

    st.divider()
    st.markdown("### 🤔 What do you do?")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"⚠️ {scene_data.get('choice_A', 'Choice A')}", use_container_width=True, type="secondary", key="btn_a"):
            st.session_state.last_choice = "choice_A"; st.session_state.step = "processing_choice"; st.rerun()
    with col2:
        if st.button(f"⚡ {scene_data.get('choice_B', 'Choice B')}", use_container_width=True, type="secondary", key="btn_b"):
            st.session_state.last_choice = "choice_B"; st.session_state.step = "processing_choice"; st.rerun()
    with col3:
        if st.button(f"✅ {scene_data.get('choice_C', 'Choice C')}", use_container_width=True, type="primary", key="btn_c"):
            st.session_state.last_choice = "choice_C"; st.session_state.step = "processing_choice"; st.rerun()

# ============================================================
# STATE 4: GAME OVER / DEBRIEF
# ============================================================
elif st.session_state.step == "game_over":
    scene_data = st.session_state.current_scene
    game_state = st.session_state.game_state

    if game_state == "game_over": st.error("## 🛑 You got scammed.")
    else: st.success("## ✅ Simulation Complete!")

    if len(st.session_state.scene_video_paths) > 1 and not st.session_state.compiled_movie:
        with st.spinner("🎞️ Director is compiling your personalized movie..."):
            compiled_path = "final_choosewisely_movie.mp4"
            try:
                video_editor.compile_final_movie(scene_paths=st.session_state.scene_video_paths, output_path=compiled_path)
                st.session_state.compiled_movie = compiled_path
            except Exception as e: st.warning(f"Could not compile full movie: {e}")

    if st.session_state.compiled_movie:
        st.markdown("### 🎬 Your Personalized Scam Drama")
        st.caption("Here is the complete story based on your choices. Download it to share with friends & family.")
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(st.session_state.compiled_movie)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with open(st.session_state.compiled_movie, "rb") as f:
            st.download_button(label="⬇️ Download My Movie", data=f, file_name="ChooseWisely_MyStory.mp4", mime="video/mp4", use_container_width=True)
        st.divider()

    st.markdown("## 🧠 Personal Security Debrief")
    debrief = scene_data.get("debrief", {})
    if debrief:
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Red Flags Missed", debrief.get("total_red_flags_missed", 0))
        with col2: st.metric("Money Lost", f"RM{st.session_state.story_memory.get('money_lost', 0)}")
        with col3: st.metric("Safety Score", f"{debrief.get('safety_score', 'N/A')}/10")

        st.markdown("#### 🚩 What You Should Have Noticed")
        for flag in debrief.get("red_flags_explained", []): st.warning(f"- {flag}")
        st.markdown("#### ✅ Correct Action")
        st.success(debrief.get("what_to_do_instead", "No recommendation."))
        st.caption(f"**Scam Type:** {debrief.get('scam_type_label', 'Unknown')} | **Report To:** {debrief.get('report_to', 'CCID/B')}")
    else:
        st.warning("Debrief data unavailable.")

    st.divider()
    if st.button("🔄 Play Again", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ============================================================
# STATE 5: ERROR
# ============================================================
elif st.session_state.step == "error":
    st.error("## ❌ Something went wrong")
    st.markdown(f"**Error:** {st.session_state.error_message}")
    if st.button("🔄 Try Again", type="primary"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
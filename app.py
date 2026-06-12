import streamlit as st
import scriptwriter
import video_generator
import voice_actor
import video_editor
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
#  MODERN STYLE UI 
# ============================================================
MODERN_CSS = """
<style>
    :root {
        --bg-primary: #ffffff;
        --bg-card: #f9f9f9;
        --bg-card-hover: #f1f1f1;
        --accent: #212121;
        --accent-hover: #424242;
        --danger: #ef4444;
        --warning: #f59e0b;
        --success: #10b981;
        --text-primary: #171717;
        --text-secondary: #525252;
        --border: #e5e5e5;
        --radius: 8px;
        --shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f0f0f;
            --bg-card: #171717;
            --bg-card-hover: #212121;
            --accent: #ededed;
            --accent-hover: #ffffff;
            --text-primary: #ededed;
            --text-secondary: #a3a3a3;
            --border: #2a2a2a;
            --shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
    }

    body, .stApp { background-color: var(--bg-primary); color: var(--text-primary); font-family: 'Inter', system-ui, -apple-system, sans-serif; }
    
    /* Minimalist Cards */
    .modern-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
        transition: border-color 0.2s ease;
    }
    .modern-card:hover { border-color: #555; }
    
    /* Typography */
    h1, h2, h3, h4 { color: var(--text-primary) !important; font-weight: 500 !important; letter-spacing: -0.01em; }
    p, span, label, div { color: var(--text-secondary); }
    
    /* Buttons */
    .stButton > button {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: none;
    }
    .stButton > button:hover { background: var(--bg-card-hover); border-color: #888; }
    .stButton > button[type="primary"] { background: var(--text-primary); color: var(--bg-primary); border: none; }
    .stButton > button[type="primary"]:hover { opacity: 0.9; }
    
    /* Progress Bar */
    .stProgress > div > div > div { background: var(--text-primary) !important; border-radius: 4px !important; }
    
    /* Video Container */
    .video-wrapper { border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); margin-bottom: 1rem; }
    
    /* Message Bubbles (Chat style) */
    .dialogue-bubble {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
        color: var(--text-primary);
    }
    
    /* Metrics */
    .stMetric { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem !important; }
    .stMetric label { color: var(--text-secondary) !important; font-size: 0.85rem !important; }
    .stMetric p { color: var(--text-primary) !important; font-weight: 600 !important; font-size: 1.4rem !important; }
    
    /* Divider */
    hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
    
    /* Hide default Streamlit footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
"""
st.markdown(MODERN_CSS, unsafe_allow_html=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="ChooseWisely", page_icon="✨", layout="centered")

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
    st.markdown("<h1 style='text-align:center; margin-bottom:0.2rem;'>ChooseWisely</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: var(--text-secondary); margin-top:0; font-size: 1rem;'>Interactive Anti-Scam Awareness Drama</p>", unsafe_allow_html=True)
    st.divider()

# ============================================================
# HELPER — Scene Progress Bar
# ============================================================
def show_progress(story_memory: dict):
    if not story_memory: return
    current = story_memory.get("current_scene", 1)
    st.progress(value=min(current / MAX_SCENES, 1.0), text=f"Scene {current} of {MAX_SCENES}")

# ============================================================
# STATE 1: SETUP
# ============================================================
if st.session_state.step == "setup":
    
    # 1. Ask for Name if not already provided in this session
    if not st.session_state.get("user_name"):
        with st.container():
            st.markdown("""
            <div class="modern-card" style="text-align: center;">
                <h2>Welcome</h2>
                <p style="color: var(--text-secondary);">Enter your name to personalize your interactive experience.</p>
            </div>
            """, unsafe_allow_html=True)
            
            user_name = st.text_input(
                "Your Name", 
                placeholder="e.g., Alex", 
                max_chars=20,
                key="name_input"
            )
            
            if st.button("Continue", type="primary", use_container_width=True):
                if user_name.strip():
                    st.session_state.user_name = user_name.strip().title()
                    st.rerun()
                else:
                    st.warning("Please enter your name to continue.")
        
        st.stop()

    # 2. Scenario Selection
    with st.container():
        st.markdown(f"""
        <div class="modern-card">
            <h3>Welcome, {st.session_state.user_name}</h3>
            <p>Select a scenario to begin the simulation.</p>
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

        selected = st.selectbox("Scenario Selection", options=list(scenario_options.keys()))
        
        scenario_idea = scenario_options[selected]
        if scenario_idea == "custom":
            scenario_idea = st.text_input("Describe your custom scenario:", placeholder="e.g., A fake bank SMS...")

        if st.button("Start Simulation", type="primary", use_container_width=True):
            if scenario_idea.strip():
                st.session_state.scenario_idea = scenario_idea
                st.session_state.step = "processing_scene_1"
                st.rerun()
            else:
                st.warning("Please enter or select a scenario first.")

# ============================================================
# STATE 2: PROCESSING
# ============================================================
elif st.session_state.step in ["processing_scene_1", "processing_choice"]:
    show_progress(st.session_state.story_memory)
    st.markdown(" ")

    try:
        with st.status("Writing next scene...", expanded=True) as status:
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
            st.write("Script finalized. Generating sequence...")
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
        st.warning(f"Video generation failed: {str(e)}. Continuing with text only.")

    final_video_path = None
    if video_url:
        try:
            with st.status("Processing audio and assembling scene...", expanded=True) as status:
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
                status.update(label="Scene rendered successfully", state="complete", expanded=False)
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

    tension_indicator = "▪ " * min(int(tension), 5)
    st.markdown(f"<h2 style='margin-bottom:0.5rem;'>Scene {scene_num} <span style='font-size:0.5em; color:var(--text-secondary);'>{tension_indicator}</span></h2>", unsafe_allow_html=True)

    if st.session_state.current_video:
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(st.session_state.current_video)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Video unavailable. Read the scene description below.")
        st.markdown(f"> {scene_data.get('scene_action', '')}")

    st.markdown(f"<div class='dialogue-bubble'>Incoming message:<br/><br/>{scene_data.get('scene_dialogue', '')}</div>", unsafe_allow_html=True)

    if st.session_state.story_memory:
        flags_so_far = st.session_state.story_memory.get("red_flags_missed", [])
        if flags_so_far:
            with st.expander("Detected indicators"):
                for flag in flags_so_far: st.markdown(f"- {flag}")

    st.divider()
    st.markdown("### Action Required")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"{scene_data.get('choice_A', 'Choice A')}", use_container_width=True, type="secondary", key="btn_a"):
            st.session_state.last_choice = "choice_A"; st.session_state.step = "processing_choice"; st.rerun()
    with col2:
        if st.button(f"{scene_data.get('choice_B', 'Choice B')}", use_container_width=True, type="secondary", key="btn_b"):
            st.session_state.last_choice = "choice_B"; st.session_state.step = "processing_choice"; st.rerun()
    with col3:
        if st.button(f"{scene_data.get('choice_C', 'Choice C')}", use_container_width=True, type="primary", key="btn_c"):
            st.session_state.last_choice = "choice_C"; st.session_state.step = "processing_choice"; st.rerun()

# ============================================================
# STATE 4: GAME OVER / DEBRIEF
# ============================================================
elif st.session_state.step == "game_over":
    scene_data = st.session_state.current_scene
    game_state = st.session_state.game_state

    if game_state == "game_over": st.error("Simulation Terminated: Unsafe action detected.")
    else: st.success("Simulation Complete")

    if len(st.session_state.scene_video_paths) > 1 and not st.session_state.compiled_movie:
        with st.spinner("Compiling scenario sequence..."):
            compiled_path = "final_choosewisely_movie.mp4"
            try:
                video_editor.compile_final_movie(scene_paths=st.session_state.scene_video_paths, output_path=compiled_path)
                st.session_state.compiled_movie = compiled_path
            except Exception as e: st.warning(f"Could not compile full movie: {e}")

    if st.session_state.compiled_movie:
        st.markdown("### Scenario Playback")
        st.caption("Complete sequence based on your interactions.")
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(st.session_state.compiled_movie)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with open(st.session_state.compiled_movie, "rb") as f:
            st.download_button(label="Download Sequence", data=f, file_name="ChooseWisely_Sequence.mp4", mime="video/mp4", use_container_width=True)
        st.divider()

    st.markdown("## Debriefing")
    debrief = scene_data.get("debrief", {})
    if debrief:
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Indicators Missed", debrief.get("total_red_flags_missed", 0))
        with col2: st.metric("Simulated Loss", f"RM{st.session_state.story_memory.get('money_lost', 0)}")
        with col3: st.metric("Safety Score", f"{debrief.get('safety_score', 'N/A')}/10")

        st.markdown("#### Key Indicators")
        for flag in debrief.get("red_flags_explained", []): st.warning(f"- {flag}")
        st.markdown("#### Recommended Protocol")
        st.success(debrief.get("what_to_do_instead", "No recommendation."))
        st.caption(f"**Classification:** {debrief.get('scam_type_label', 'Unknown')} | **Report To:** {debrief.get('report_to', 'CCID/B')}")
    else:
        st.warning("Debrief data unavailable.")

    st.divider()
    if st.button("Restart Simulation", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ============================================================
# STATE 5: ERROR
# ============================================================
elif st.session_state.step == "error":
    st.error("System Error")
    st.markdown(f"**Details:** {st.session_state.error_message}")
    if st.button("Retry", type="primary"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
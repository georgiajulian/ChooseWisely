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
COMIC_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Nunito:wght@400;700;900&display=swap');

    :root {
        --bg-primary: #262422;   /* Dark muted slate/brown */
        --bg-card: #383431;      /* Slightly lighter card */
        --bg-card-hover: #4a4542;
        --accent: #D9B44A;       /* Muted Vintage Yellow */
        --accent-hover: #E0A96D;
        --danger: #C15447;       /* Muted Vintage Red */
        --warning: #CD853F;      /* Muted Orange */
        --success: #6B8E23;      /* Muted Green */
        --cyan: #488A99;         /* Muted Teal */
        --text-primary: #EBE5D9; /* Old paper / cream */
        --text-secondary: #B0A8A0; /* Light muted brown */
        --border-color: #1A1817; /* Very dark brown/black */
        --radius: 0px; 
        --shadow: 4px 4px 0px var(--accent);
    }

    body, .stApp { 
        background-color: var(--bg-primary); 
        color: var(--text-primary); 
        font-family: 'Nunito', sans-serif; 
        background-image: radial-gradient(circle, #383431 2px, transparent 2px);
        background-size: 24px 24px;
    }
    
    /* Comic Cards */
    .modern-card, .comic-card {
        background: var(--bg-card);
        border: 4px solid var(--border-color);
        padding: 1.5rem;
        box-shadow: 6px 6px 0px var(--accent);
        margin-bottom: 1.5rem;
        transition: transform 0.1s ease, box-shadow 0.1s ease;
    }
    .modern-card:hover, .comic-card:hover { 
        transform: translate(-2px, -2px);
        box-shadow: 8px 8px 0px var(--cyan);
    }
    
    /* Typography */
    h1, h2, h3, h4 { 
        font-family: 'Bangers', cursive !important; 
        color: var(--text-primary) !important; 
        letter-spacing: 2px !important; 
        text-transform: uppercase;
        text-shadow: 2px 2px 0px var(--border-color), -1px -1px 0px var(--border-color), 1px -1px 0px var(--border-color), -1px 1px 0px var(--border-color), 1px 1px 0px var(--border-color);
    }
    p, span, label, div { font-weight: 700; color: var(--text-primary); }
    
    /* Custom Title Style */
    .comic-title {
        font-family: 'Bangers', cursive !important;
        font-size: 5rem !important;
        color: var(--accent) !important;
        text-align: center;
        letter-spacing: 4px !important;
        text-shadow: 3px 3px 0px var(--border-color), 7px 7px 0px var(--danger) !important;
        transform: rotate(-3deg);
        line-height: 1;
        margin: 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--cyan);
        color: var(--border-color) !important;
        border: 4px solid var(--border-color);
        border-radius: 0px;
        padding: 0.5rem 1rem;
        font-family: 'Bangers', cursive;
        font-size: 1.4rem;
        letter-spacing: 1.5px;
        transition: all 0.1s ease;
        box-shadow: 5px 5px 0px var(--accent);
        text-transform: uppercase;
    }
    .stButton > button:active {
        transform: translate(5px, 5px);
        box-shadow: 0px 0px 0px var(--accent);
    }
    .stButton > button:hover { 
        background: var(--accent); 
        color: var(--border-color) !important;
    }
    .stButton > button[type="primary"] { 
        background: var(--danger); 
        color: var(--text-primary) !important; 
        border: 4px solid var(--border-color);
        box-shadow: 5px 5px 0px var(--cyan);
    }
    .stButton > button[type="primary"]:hover { 
        background: var(--cyan); 
        color: var(--border-color) !important; 
        box-shadow: 5px 5px 0px var(--danger);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div { background: var(--accent) !important; border-radius: 0px !important; border-right: 4px solid var(--border-color); }
    
    /* Video Container */
    .video-wrapper { 
        border: 4px solid var(--border-color); 
        box-shadow: 8px 8px 0px var(--danger); 
        margin-bottom: 2rem; 
        background: var(--border-color);
    }
    
    /* Message Bubbles (Comic style) */
    .dialogue-bubble {
        background: var(--text-primary);
        color: var(--border-color) !important;
        border: 4px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        font-family: 'Nunito', sans-serif;
        font-weight: 900;
        font-size: 1.1rem;
        position: relative;
        box-shadow: 5px 5px 0px var(--cyan);
        text-transform: uppercase;
    }
    .dialogue-bubble::after {
        content: '';
        position: absolute;
        bottom: -18px;
        left: 30px;
        border-width: 18px 18px 0;
        border-style: solid;
        border-color: var(--text-primary) transparent transparent transparent;
        display: block;
        width: 0;
        z-index: 1;
    }
    .dialogue-bubble::before {
        content: '';
        position: absolute;
        bottom: -25px;
        left: 26px;
        border-width: 25px 25px 0;
        border-style: solid;
        border-color: var(--border-color) transparent transparent transparent;
        display: block;
        width: 0;
        z-index: 0;
    }
    
    /* Metrics */
    .stMetric { background: var(--bg-card); border: 4px solid var(--border-color); padding: 1rem !important; box-shadow: 5px 5px 0px var(--warning); }
    .stMetric label { color: var(--text-secondary) !important; font-family: 'Bangers', cursive; font-size: 1.3rem !important; letter-spacing: 1px;}
    .stMetric p { color: var(--accent) !important; font-family: 'Bangers', cursive !important; font-size: 2.5rem !important; text-shadow: 2px 2px 0px var(--border-color);}
    
    /* Divider */
    hr { border-top: 4px dashed var(--border-color) !important; margin: 2rem 0 !important; opacity: 1 !important;}
    
    /* Hide default Streamlit footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
"""
st.markdown(COMIC_CSS, unsafe_allow_html=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="ChooseWisely", page_icon="💥", layout="wide")

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
    <div style='display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 1rem; margin-top: 1rem;'>
        <div style='font-size: 5rem; filter: drop-shadow(5px 5px 0px var(--danger));'>🕵️‍♂️</div>
        <h1 class='comic-title'>CHOOSE WISELY!</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: var(--text-secondary); margin-top:0; font-size: 1.5rem; font-family: \"Bangers\", cursive; letter-spacing: 3px; text-transform: uppercase;'>Interactive Anti-Scam Thriller</p>", unsafe_allow_html=True)
    st.divider()

# ============================================================
# HELPER — Scene Progress Bar
# ============================================================
def show_progress(story_memory: dict):
    if not story_memory: return
    current = story_memory.get("current_scene", 1)
    st.progress(value=min(current / MAX_SCENES, 1.0), text=f"CHAPTER {current} / {MAX_SCENES}")

# ============================================================
# STATE 1: SETUP
# ============================================================
if st.session_state.step == "setup":
    
    if not st.session_state.get("user_name"):
        with st.container():
            st.markdown("""
            <div class="comic-card" style="text-align: center;">
                <h2 style="color: var(--cyan) !important;">WHO ARE YOU?</h2>
                <p>Enter your alias to begin your story.</p>
            </div>
            """, unsafe_allow_html=True)
            
            user_name = st.text_input(
                "Your Name", 
                placeholder="e.g., Alex", 
                max_chars=20,
                key="name_input"
            )
            
            if st.button("ENTER THE SPIDERWEB", type="primary", use_container_width=True):
                if user_name.strip():
                    st.session_state.user_name = user_name.strip().title()
                    st.rerun()
                else:
                    st.warning("You must enter a name!")
        
        st.stop()

    with st.container():
        st.markdown(f"""
        <div class="comic-card">
            <h3 style="color: var(--danger) !important;">GREETINGS, {st.session_state.user_name}...</h3>
            <p>Pick your poison. Which scam scenario will you face today?</p>
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

        if st.button("START THE SIMULATION", type="primary", use_container_width=True):
            if scenario_idea.strip():
                st.session_state.scenario_idea = scenario_idea
                st.session_state.step = "processing_scene_1"
                st.rerun()
            else:
                st.warning("Select a scenario first!")

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
                st.write("💥 ANALYZING YOUR DECISION...")
                time.sleep(1.5)
                st.write("🎲 CALCULATING CONSEQUENCES...")
                time.sleep(1.5)
                st.write("⚠️ YOUR FATE IS SEALED!")
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

    tension_indicator = "🔥" * min(int(tension), 5)
    st.markdown(f"<h2 style='margin-bottom:0.5rem; color: var(--accent) !important;'>CHAPTER {scene_num} <span style='font-size:0.5em; color:var(--danger);'>{tension_indicator}</span></h2>", unsafe_allow_html=True)

    col_vid, col_opts = st.columns([1, 1.2])

    with col_vid:
        if st.session_state.current_video:
            st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
            st.video(st.session_state.current_video)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("VISUALS DOWN. READ CAREFULLY:")
            st.markdown(f"> {scene_data.get('scene_action', '')}")

    with col_opts:
        st.markdown(f"<div class='dialogue-bubble'>\"{scene_data.get('scene_dialogue', '')}\"</div>", unsafe_allow_html=True)

        if st.session_state.story_memory:
            flags_so_far = st.session_state.story_memory.get("red_flags_missed", [])
            if flags_so_far:
                with st.expander("CLUES FOUND SO FAR"):
                    for flag in flags_so_far: st.markdown(f"- {flag}")

        st.markdown("<h3 style='color: var(--cyan) !important;'>WHAT WILL YOU DO?!</h3>", unsafe_allow_html=True)

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
        <div class="comic-card" style="text-align: center; border-color: var(--danger); box-shadow: 8px 8px 0px var(--danger);">
            <h1 style="color: var(--danger) !important; font-size: 4rem; margin-bottom: 0.5rem;">GAME OVER!</h1>
            <p style="font-size: 1.5rem; color: var(--text-primary); margin: 0; text-transform: uppercase;">You fell for the trap!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="comic-card" style="text-align: center; border-color: var(--success); box-shadow: 8px 8px 0px var(--success);">
            <h1 style="color: var(--success) !important; font-size: 4rem; margin-bottom: 0.5rem;">VICTORY!</h1>
            <p style="font-size: 1.5rem; color: var(--text-primary); margin: 0; text-transform: uppercase;">You dodged the bullet!</p>
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
        st.markdown("<h3 style='color: var(--cyan) !important;'>THE FULL STORY</h3>", unsafe_allow_html=True)
        st.caption("Here's how your tale unfolded.")
        st.markdown("<div class='video-wrapper'>", unsafe_allow_html=True)
        st.video(st.session_state.compiled_movie)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with open(st.session_state.compiled_movie, "rb") as f:
            st.download_button(label="GET THE MOVIE", data=f, file_name="ChooseWisely_Sequence.mp4", mime="video/mp4", use_container_width=True)
        st.divider()

    st.markdown("<h2 style='color: var(--accent) !important;'>THE AFTERMATH</h2>", unsafe_allow_html=True)
    debrief = scene_data.get("debrief", {})
    if debrief:
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("CLUES MISSED", debrief.get("total_red_flags_missed", 0))
        with col2: st.metric("MONEY LOST", f"RM{st.session_state.story_memory.get('money_lost', 0)}")
        with col3: st.metric("SURVIVAL RATING", f"{debrief.get('safety_score', 'N/A')}/10")

        st.markdown("<h4 style='color: var(--danger) !important;'>THE TRAPS YOU MISSED</h4>", unsafe_allow_html=True)
        for flag in debrief.get("red_flags_explained", []): st.warning(f"- {flag}")
        
        st.markdown("<h4 style='color: var(--success) !important;'>THE WAY OUT</h4>", unsafe_allow_html=True)
        st.success(debrief.get("what_to_do_instead", "No recommendation."))
        st.caption(f"**THREAT LEVEL:** {debrief.get('scam_type_label', 'Unknown')} | **REPORT TO:** {debrief.get('report_to', 'CCID/B')}")
    else:
        st.warning("Debrief file corrupted or missing.")

    st.divider()
    if st.button("PLAY AGAIN IF YOU DARE", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ============================================================
# STATE 5: ERROR
# ============================================================
elif st.session_state.step == "error":
    st.error("FATAL ERROR!")
    st.markdown(f"**SYSTEM FAILURE:** {st.session_state.error_message}")
    if st.button("REBOOT SYSTEM", type="primary"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
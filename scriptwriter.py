import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

MAX_SCENES = 3  # Hard limit — no infinite branching

# ============================================================
# STORY STATE CHECKER
# ============================================================
def should_continue(story_memory: dict, user_choice: str) -> str:
    """
    Determines what happens next based on current state and user choice.
    """
    current_scene = story_memory.get("current_scene", 1)
    
    # Dangerous choice (choice_A) on Scene 1 = immediate game over
    if user_choice == "choice_A" and current_scene == 1:
        return "game_over"

    # Hard scene limit reached
    if current_scene >= MAX_SCENES:
        return "final_debrief"

    return "continue"

# ============================================================
# MEMORY UPDATER
# ============================================================
def update_memory(story_memory: dict, scene_output: dict, user_choice: str) -> dict:
    """
    Updates story_memory after each scene.
    """
    story_memory["scenes_so_far"].append({
        "scene_number": scene_output.get("scene_number"),
        "action":       scene_output.get("scene_action"),
        "dialogue":     scene_output.get("scene_dialogue"),
        "choice_made":  user_choice
    })

    red_flags = scene_output.get("red_flags_in_this_scene", [])
    story_memory["red_flags_missed"].extend(red_flags)
    story_memory["money_lost"] += scene_output.get("money_lost", 0)
    story_memory["current_scene"] += 1

    if user_choice == "choice_A":
        story_memory["danger_level"] = min(story_memory.get("danger_level", 0) + 1, 3)

    return story_memory

# ============================================================
# MAIN GENERATE FUNCTION
# ============================================================
def generate_scenario(
    scenario_idea: str,
    story_memory:  dict = None,
    user_choice:   str  = None,
    user_name:     str  = "User"  
) -> dict:

    if story_memory is None:
        story_memory = {
            "scam_type":       scenario_idea,
            "current_scene":   1,
            "max_scenes":      MAX_SCENES,
            "scenes_so_far":   [],
            "red_flags_missed": [],
            "money_lost":      0,
            "danger_level":    0,
            "is_game_over":    False,
            "is_final":        False
        }

    if user_choice is not None:
        game_state = should_continue(story_memory, user_choice)
    else:
        game_state = "scene_1"

    is_final   = game_state in ("game_over", "final_debrief")
    is_game_over = game_state == "game_over"

    story_memory["is_game_over"] = is_game_over
    story_memory["is_final"]     = is_final

    memory_context = ""
    if story_memory["scenes_so_far"]:
        memory_context = f"""
STORY MEMORY (stay fully consistent with this):
- User's Name: {user_name}
- Scam Type: {story_memory['scam_type']}
- Current Scene: {story_memory['current_scene']} of {MAX_SCENES}
- Money Lost So Far: RM{story_memory['money_lost']}
- Red Flags Missed: {', '.join(story_memory['red_flags_missed']) or 'None yet'}
- Scenes So Far:
{json.dumps(story_memory['scenes_so_far'], indent=2)}
"""

    # ── 1. SCENE 1 ─────────────────────────────────────────────────────────────
    if game_state == "scene_1":
        system_prompt = f"""
You are an expert cybersecurity educator and screenwriter for "ChooseWisely".
Write Scene 1 of a dramatic, realistic scam scenario. 
Output ONLY valid JSON. No markdown. No extra text.

PERSONALIZATION RULE: The user's name is "{user_name}". You MUST address them by this exact name in the dialogue to make it feel authentic (e.g., "Hello {user_name}, your parcel is held...").

JSON structure:
{{
  "scene_number": 1,
  "voice_type": "scammer",
  "scene_action": "Brief description of the visual action happening on screen",
  "scene_visual_prompt": "Highly detailed cinematic prompt for AI video generation. Include: shot type, lighting, setting, mood, on-screen elements, color grade.",
  "scene_dialogue": "The exact scam message text or narrator voiceover shown to the user (max 30 words). USE THE USER'S NAME.",
  "tension_level": 3,
  "red_flags_in_this_scene": ["red flag 1", "red flag 2"],
  "money_lost": 0,
  "choice_A": "THE MOST DANGEROUS CHOICE (takes the bait completely)",
  "choice_B": "THE UNCERTAIN/RISKY CHOICE (partially suspicious but still vulnerable)",
  "choice_C": "THE SAFE CHOICE (recognizes something is wrong and protects the user)"
}}
"""
        user_prompt = f"Create a dramatic scam scenario about: {scenario_idea}"

        # ── 2. CONTINUE (Mid-Game) ─────────────────────────────────────────────────
    elif game_state == "continue":
        system_prompt = f"""
You are an expert cybersecurity educator and screenwriter for "ChooseWisely".
The user just made a specific choice. You MUST write the consequence scene that DIRECTLY results from that exact choice.
This is Scene {story_memory['current_scene']} of {MAX_SCENES}.

PERSONALIZATION RULE: The user's name is "{user_name}". Reference their name naturally in the dialogue if it fits the emotional reaction.

CRITICAL RULE FOR VISUALS: The "scene_visual_prompt" MUST explicitly show the direct result of the user's choice.

CRITICAL RULE FOR MID-GAME DIALOGUE & VOICE:
For this mid-game consequence scene, you MUST set "voice_type" to "victim".
You MUST write the "scene_dialogue" in the FIRST PERSON (using "I", "my", "me"). 
The victim's reaction MUST perfectly match the specific choice the user just made. DO NOT be repetitive. 
- IF the user made a SAFE choice: The victim expresses relief, suspicion, or decisive protective action.
- IF the user made a DANGEROUS/RISKY choice: The victim expresses panic, confusion, or immediate regret.

CRITICAL RULE FOR CHOICES: You MUST generate exactly 3 logical next steps based ONLY on the user's previous action. Ensure these new choices are completely different and more escalated than previous scenes.
- choice_A MUST be the DANGEROUS next choice.
- choice_B MUST be the UNCERTAIN/RISKY next choice.
- choice_C MUST be the SAFE next choice.

Output ONLY valid JSON. No markdown. No extra text.

JSON structure:
{{
  "scene_number": {story_memory['current_scene']},
  "voice_type": "victim", 
  "scene_action": "Brief description of the visual consequence of the user's specific choice",
  "scene_visual_prompt": "Highly detailed cinematic prompt for AI video showing the EXACT visual consequence of the choice.",
  "scene_dialogue": "The victim's specific first-person reaction to the exact choice made (max 30 words). USE 'I' AND 'MY'.",
  "tension_level": 6,
  "red_flags_in_this_scene": ["red flag 1", "red flag 2"],
  "money_lost": 0,
  "choice_A": "THE DANGEROUS NEXT CHOICE (must be new and specific)",
  "choice_B": "THE UNCERTAIN/RISKY NEXT CHOICE (must be new and specific)",
  "choice_C": "THE SAFE NEXT CHOICE (must be new and specific)"
}}
"""
        user_prompt = (
            f"Scenario: {scenario_idea}. "
            f"The user JUST CHOSE TO: '{user_choice}'. "
            f"Write the DIRECT visual and narrative consequence of this specific action, and provide exactly 3 logical, escalated next choices.{memory_context}"
        )

    # ── 3. GAME OVER (Immediate Scam) ──────────────────────────────────────────
    elif game_state == "game_over":
        system_prompt = f"""
You are an expert cybersecurity educator and screenwriter for "ChooseWisely".
The user made the most dangerous choice and got scammed immediately. 
Write a dramatic Game Over scene that VISUALLY depicts the disastrous consequence.

PERSONALIZATION RULE: The user's name is "{user_name}". Reference their name naturally in the dialogue or debrief.

CRITICAL RULE FOR GAME OVER DIALOGUE & VOICE:
For the Game Over scene, you MUST set "voice_type" to "victim".
You MUST write the "scene_dialogue" in the FIRST PERSON (using "I", "my", "me"). 
The victim is having a moment of sheer panic or realization as they realize they've been scammed.

Output ONLY valid JSON. No markdown. No extra text.

JSON structure:
{{
  "scene_number": 2,
  "voice_type": "victim",
  "scene_action": "Dramatic visual description of the user getting scammed based on their specific bad choice",
  "scene_visual_prompt": "Highly detailed cinematic prompt showing the specific scam consequence.",
  "scene_dialogue": "The victim's first-person panic or realization (max 30 words). USE 'I' AND 'MY'.",
  "tension_level": 10,
  "red_flags_in_this_scene": ["red flag 1", "red flag 2", "red flag 3"],
  "money_lost": 5000,
  "is_game_over": true,
  "debrief": {{
    "outcome": "One sentence describing what happened to the victim based on their choice",
    "red_flags_explained": ["Explanation of red flag 1", "Explanation of red flag 2"],
    "what_to_do_instead": "One clear sentence on the correct action they should have taken instead of their choice",
    "scam_type_label": "Official name of this scam type",
    "report_to": "Which authority to report this to in Malaysia"
  }}
}}
"""
        user_prompt = (
            f"Scenario: {scenario_idea}. "
            f"The user made the most dangerous choice: '{user_choice}'. "
            f"Show the full visual consequence and debrief.{memory_context}"
        )

    # ── 4. FINAL DEBRIEF (End of Game) ─────────────────────────────────────────
    else:  
        system_prompt = f"""
You are an expert cybersecurity educator and screenwriter for "ChooseWisely".
The user has reached the end of the story (Scene {MAX_SCENES}).
Write the final scene showing whether they escaped or partially fell for the scam.
Then write a full personalized debrief based on their entire journey.
No new choices — this is the ending.
Output ONLY valid JSON. No markdown. No extra text.

PERSONALIZATION RULE: The user's name is "{user_name}". Address them directly in the final narrator summary.

CRITICAL RULE FOR FINAL DEBRIEF DIALOGUE & VOICE:
For the final debrief, you MUST set "voice_type" to "narrator".
You MUST write the "scene_dialogue" in the SECOND PERSON (using "You"). 
The narrator is objectively summarizing the user's journey and delivering the final educational takeaway.

JSON structure:
{{
  "scene_number": {story_memory['current_scene']},
  "voice_type": "narrator",
  "scene_action": "Final visual — escape, partial loss, or full consequence",
  "scene_visual_prompt": "Highly detailed cinematic prompt for the final scene",
  "scene_dialogue": "The narrator's second-person summary and educational takeaway (max 30 words). USE 'YOU' AND THE USER'S NAME.",
  "tension_level": 8,
  "red_flags_in_this_scene": [],
  "money_lost": 0,
  "is_final": true,
  "debrief": {{
    "outcome": "One sentence summarizing what happened across the full story",
    "total_red_flags_missed": {len(story_memory['red_flags_missed'])},
    "red_flags_explained": ["Explanation of each red flag the user encountered"],
    "what_to_do_instead": "Clear action steps the user should have taken",
    "scam_type_label": "Official name of this scam type",
    "report_to": "Which authority to report this in Malaysia",
    "safety_score": "A score out of 10 based on how safely the user played"
  }}
}}
"""
        user_prompt = (
            f"Scenario: {scenario_idea}. "
            f"User's final choice: {user_choice}. "
            f"Write the final scene and full personalized debrief.{memory_context}"
        )

    # ── API Call ───────────────────────────────────────────────────────────────
    try:
        response = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        scene_output = json.loads(response.choices[0].message.content)

        if user_choice is not None:
            story_memory = update_memory(story_memory, scene_output, user_choice)

          # ── Attach updated memory to output for orchestrator ───────────────────
        scene_output["story_memory"] = story_memory
        scene_output["game_state"]   = game_state

        # ── SMART VOICE VALIDATION (Trust the AI, but catch mistakes) ──────────
        # We let the AI choose the correct perspective (Narrator vs Victim), 
        # but we step in ONLY if it outputs an invalid or missing voice type.
        valid_voices = ["scammer", "victim", "narrator", "police", "customer_service", "bank"]
        ai_voice = str(scene_output.get("voice_type", "")).lower().strip()
        
        if ai_voice not in valid_voices:
            # AI messed up or forgot the voice_type. Apply a safe fallback.
            if game_state == "scene_1":
                scene_output["voice_type"] = "scammer"
            else:
                scene_output["voice_type"] = "narrator" # Safe fallback for consequences/debriefs
        # ───────────────────────────────────────────────────────────────────────

        return scene_output
    except json.JSONDecodeError as e:
        raise ValueError(f"Scriptwriter returned invalid JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Scriptwriter API call failed: {e}")
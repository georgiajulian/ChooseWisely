import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIG
# ============================================================
MAX_WAIT_SECONDS = 300      # 5 minutes max — wan2.7 can be slow
INITIAL_WAIT     = 25       # Wait before first poll (video won't be ready before this)
POLL_INTERVAL    = 10       # Poll every 10s after initial wait
MAX_RETRIES      = 2        # Retry failed submissions once before giving up

WORKSPACE_ID = os.getenv("DASHSCOPE_WORKSPACE_ID")   # e.g. "ws-abc123"

# Save Token: Set to True to save credits while building the UI
MOCK_MODE = True
MOCK_VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"


def _get_submit_url() -> str:
    """
    Builds the workspace-specific endpoint URL.
    Falls back to public Singapore endpoint if WORKSPACE_ID is not set.
    """
    if WORKSPACE_ID:
        return (
            f"https://{WORKSPACE_ID}.ap-southeast-1.maas.aliyuncs.com"
            f"/api/v1/services/aigc/video-generation/video-synthesis"
        )
    # Fallback — public Singapore endpoint
    return (
        "https://dashscope-intl.aliyuncs.com"
        "/api/v1/services/aigc/video-generation/video-synthesis"
    )


def _get_task_url(task_id: str) -> str:
    """
    Builds the task polling URL using the same workspace endpoint.
    """
    if WORKSPACE_ID:
        return (
            f"https://{WORKSPACE_ID}.ap-southeast-1.maas.aliyuncs.com"
            f"/api/v1/tasks/{task_id}"
        )
    return f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}"


# ============================================================
# TASK POLLER
# ============================================================
def _poll_task(task_id: str, api_key: str) -> str:
    """
    Polls the task endpoint until SUCCEEDED, FAILED, or timeout.

    Returns:
        str  — video URL on success
    Raises:
        TimeoutError — if MAX_WAIT_SECONDS exceeded
        RuntimeError — if task explicitly fails
    """
    task_url     = _get_task_url(task_id)
    task_headers = {"Authorization": f"Bearer {api_key}"}

    elapsed    = 0
    poll_count = 0

    print(f"   ⏳ Waiting {INITIAL_WAIT}s before first poll...")
    time.sleep(INITIAL_WAIT)
    elapsed += INITIAL_WAIT

    while elapsed < MAX_WAIT_SECONDS:
        try:
            task_response = requests.get(task_url, headers=task_headers, timeout=15)
            task_result   = task_response.json()
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Poll request failed (will retry): {e}")
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            continue

        output = task_result.get("output", {})
        status = output.get("task_status", "UNKNOWN")
        poll_count += 1

        print(f"   [{elapsed}s elapsed | poll #{poll_count}] Status: {status}")

        if status == "SUCCEEDED":
            video_url = output.get("video_url")
            if not video_url:
                raise RuntimeError("Task SUCCEEDED but no video_url in response.")
            return video_url

        elif status == "FAILED":
            error_msg = output.get("message", str(task_result))
            raise RuntimeError(f"Video generation task failed: {error_msg}")

        elif status in ("PENDING", "RUNNING"):
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

        else:
            print(f"   ⚠️  Unexpected status '{status}' — continuing to poll...")
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

    raise TimeoutError(
        f"Video generation exceeded {MAX_WAIT_SECONDS}s timeout. "
        f"Task ID '{task_id}' may still be processing on the server."
    )


# ============================================================
# MAIN GENERATE FUNCTION
# ============================================================
def generate_video_clip(
    visual_prompt:  str,
    aspect_ratio:   str  = "9:16",    # "9:16" vertical for mobile short drama
    duration:       int  = 5,          # seconds — keep short to save credits
    enhance_prompt: bool = True        # wan2.7 benefits from prompt_extend
) -> str:
    """
    Submits a video generation task to wan2.7-t2v and returns the video URL.

    Args:
        visual_prompt  : str  — cinematic prompt from Director Agent
        aspect_ratio   : str  — "9:16" (mobile/TikTok) or "16:9" (landscape)
        duration       : int  — clip length in seconds (5 recommended for speed)
        enhance_prompt : bool — let wan2.7 extend/enhance the prompt

    Returns:
        str — publicly accessible video URL (valid for 24 hours)

    Raises:
        ValueError   — missing API key or workspace ID
        TimeoutError — generation exceeded MAX_WAIT_SECONDS
        RuntimeError — API submission failed or task failed
    """
    
    # MOCK MODE CHECK 
    if MOCK_MODE:
        print(" MOCK MODE ACTIVE: Skipping Wan API to save credits. Using placeholder video.")
        print(f"   (Prompt was: {visual_prompt[:50]}...)")
        time.sleep(2) # Fake a 2-second delay so the UI spinner looks natural
        return MOCK_VIDEO_URL

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not found in .env file.")

    if not WORKSPACE_ID:
        print("   ⚠️  DASHSCOPE_WORKSPACE_ID not set — using public fallback endpoint.")

    submit_url = _get_submit_url()

    print(f"\n🎬 Submitting video generation task...")
    print(f"   Endpoint : {submit_url}")
    print(f"   Model    : wan2.7-t2v")
    print(f"   Prompt   : {visual_prompt[:80]}{'...' if len(visual_prompt) > 80 else ''}")
    print(f"   Ratio    : {aspect_ratio} | Duration: {duration}s | Enhance: {enhance_prompt}")

    headers = {
        "X-DashScope-Async": "enable",
        "Authorization":     f"Bearer {api_key}",
        "Content-Type":      "application/json"
    }

    payload = {
        "model": "wan2.7-t2v",
        "input": {
            "prompt": visual_prompt
        },
        "parameters": {
            "resolution":     "720P",
            "ratio":          aspect_ratio,   # "9:16" or "16:9"
            "prompt_extend":  enhance_prompt,
            "watermark":      False,           # No watermark for hackathon demo
            "duration":       duration
        }
    }

    # ── Submit with retry ──────────────────────────────────────────────────────
    task_id    = None
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                submit_url,
                headers = headers,
                json    = payload,
                timeout = 30
            )
            result = response.json()

            if response.status_code == 200 and "output" in result:
                task_id = result["output"]["task_id"]
                print(f"   ✅ Task submitted (attempt {attempt}). Task ID: {task_id}")
                break

            else:
                last_error = f"HTTP {response.status_code}: {result}"
                print(f"   ⚠️  Attempt {attempt}/{MAX_RETRIES} failed: {last_error}")
                if attempt < MAX_RETRIES:
                    print(f"   🔄 Retrying in 5s...")
                    time.sleep(5)

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"   ⚠️  Attempt {attempt}/{MAX_RETRIES} — network error: {e}")
            if attempt < MAX_RETRIES:
                print(f"   🔄 Retrying in 5s...")
                time.sleep(5)

    if task_id is None:
        raise RuntimeError(
            f"Video submission failed after {MAX_RETRIES} attempts. "
            f"Last error: {last_error}"
        )

    # ── Poll for result ────────────────────────────────────────────────────────
    video_url = _poll_task(task_id, api_key)
    print(f"   🎉 Video ready: {video_url}")
    return video_url


# ============================================================
# QUICK TEST (run directly: python video_generator.py)
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ChooseWisely — Video Generator Test (wan2.7-t2v)")
    print("=" * 60)

    test_prompt = (
        "Cinematic vertical shot, close-up of a hand holding a smartphone "
        "in a dim bedroom, a WhatsApp notification appears from 'Pos Malaysia' "
        "saying 'Your parcel is held. Pay RM2.50 now to release it. Click: bit.ly/xR3k', "
        "tense atmosphere, shallow depth of field, dramatic lighting, realistic 4K"
    )

    try:
        url = generate_video_clip(
            visual_prompt  = test_prompt,
            aspect_ratio   = "9:16",
            duration       = 5,
            enhance_prompt = True
        )
        print(f"\n✅ SUCCESS: {url}")

    except TimeoutError as e:
        print(f"\n⏰ TIMEOUT: {e}")
    except RuntimeError as e:
        print(f"\n❌ RUNTIME ERROR: {e}")
    except ValueError as e:
        print(f"\n⚙️  CONFIG ERROR: {e}")
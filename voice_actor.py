import asyncio
import edge_tts
import re

async def _generate_async(text: str, output_file: str, voice: str, rate: str, volume: str):
    """Async helper to generate and save the audio."""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicate.save(output_file)

def generate_voice(text: str, output_file: str, voice_type: str = "narrator") -> bool:
    """
    Generates highly natural AI voiceover using Edge-TTS.
    Automatically strips speaker labels and emojis for clean delivery.
    """
    if not text or not text.strip():
        return False
        
    # 1. CLEAN THE TEXT: Remove speaker labels
    clean_text = re.sub(
        r'^(?:User|Scammer|Victim|Customer Service|Police|Bank|Narrator|Agent)\s*:\s*', 
        '', 
        text, 
        flags=re.IGNORECASE
    ).strip()
    
    # 2. CLEAN THE TEXT: Remove ALL emojis (The Fix!)
    # This regex matches the Unicode ranges for almost all emojis and replaces them with nothing.
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001f926-\U0001f937"  # more emoticons
        "\U00010000-\U0010ffff"  # supplementary characters
        "]+", 
        flags=re.UNICODE
    )
    clean_text = emoji_pattern.sub(r'', clean_text).strip()
    
    # Strip surrounding quotes just in case
    clean_text = clean_text.strip('\'"')
    
    if not clean_text:
        return False

    # 3. VOICE DICTIONARY
    voices = {
        "scammer": ("en-GB-RyanNeural", "+10%", "+10%"),         
        "victim": ("en-GB-SoniaNeural", "+5%", "+0%"),           
        "narrator": ("en-US-GuyNeural", "-5%", "+0%"),           
        "police": ("en-US-ChristopherNeural", "-5%", "+5%"),     
        "customer_service": ("en-US-JennyNeural", "-0%", "+0%"), 
        "bank": ("en-AU-WilliamNeural", "-5%", "+0%")            
    }
    
    voice, rate, volume = voices.get(voice_type, ("en-US-GuyNeural", "-5%", "+0%"))
    
    try:
        print(f"🎙️ Generating {voice_type} voice...")
        print(f"   📝 Cleaned Text: '{clean_text[:60]}...'") 
        
        asyncio.run(_generate_async(clean_text, output_file, voice, rate, volume))
        print(f"   ✅ Saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"   ❌ Voice generation failed: {e}")
        return False
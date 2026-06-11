from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    CompositeAudioClip, 
    concatenate_videoclips,
    concatenate_audioclips
)
import os

def merge_video_and_audio(video_path: str, audio_path: str, output_path: str, sfx_path: str = None) -> str:
    """
    Merges video, voiceover, and scene-specific SFX into a single MP4.
    """
    print(f"🎬 Editing: Combining video, voice, and SFX for this scene...")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    video_clip = VideoFileClip(video_path)
    voice_clip = AudioFileClip(audio_path)

    # Handle Scene-Specific SFX
    if sfx_path and os.path.exists(sfx_path):
        print(f"   🎵 Baking SFX into scene: {os.path.basename(sfx_path)}")
        sfx_clip = AudioFileClip(sfx_path)
        
        # Bulletproof audio looping to match scene length
        if sfx_clip.duration < video_clip.duration:
            repeats = int(video_clip.duration / sfx_clip.duration) + 1
            sfx_clip = concatenate_audioclips([sfx_clip] * repeats)
        
        # Trim to exact scene duration and lower volume to 30%
        sfx_clip = sfx_clip.subclip(0, video_clip.duration)
        sfx_clip = sfx_clip.volumex(0.3)
        
        final_audio = CompositeAudioClip([voice_clip, sfx_clip])
    else:
        final_audio = voice_clip

    final_clip = video_clip.set_audio(final_audio)

    print(f"   💾 Rendering scene to {output_path}...")
    final_clip.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='temp-scene-audio.m4a',
        remove_temp=True,
        logger=None 
    )

    video_clip.close()
    voice_clip.close()
    if sfx_path and os.path.exists(sfx_path):
        sfx_clip.close()
    final_clip.close()
    
    print(f"   🎉 Scene saved successfully!")
    return output_path


# ============================================================
# THE HOLLYWOOD COMPILATION (Just stitches the pre-baked scenes)
# ============================================================
def compile_final_movie(scene_paths: list, output_path: str) -> str:
    """
    Stitches scenes together. (SFX is already perfectly baked into each scene!)
    """
    print(f"🎞️ Compiling final movie from {len(scene_paths)} pre-baked scenes...")
    
    clips = []
    for path in scene_paths:
        if os.path.exists(path):
            clips.append(VideoFileClip(path))
            
    if not clips:
        raise RuntimeError("No valid video scenes found to compile.")

    final_movie = concatenate_videoclips(clips, method="compose")

    print(f"   💾 Rendering full movie to {output_path}...")
    final_movie.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='temp-movie-audio.m4a',
        remove_temp=True,
        logger=None
    )

    for clip in clips:
        clip.close()
    final_movie.close()
    
    print(f"   🎉 Final compiled movie saved!")
    return output_path
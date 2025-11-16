"""
Animated Video Generator for Educational Content
Creates engaging animated videos for lessons
"""

import os
import logging
from typing import Optional, List, Dict
from pathlib import Path
import json

try:
    from PIL import Image, ImageDraw, ImageFont
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, TextClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logging.warning("moviepy/PIL not available. Install with: pip install moviepy pillow")

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib not available. Install with: pip install matplotlib")

logger = logging.getLogger(__name__)


class VideoGenerator:
    """
    Generates animated educational videos
    Creates engaging visual content with animations
    """
    
    def __init__(self, animation_style: str = "cartoon", quality: str = "medium"):
        """
        Initialize video generator
        
        Args:
            animation_style: Style of animation (cartoon, realistic, simple)
            quality: Video quality (low, medium, high)
        """
        self.animation_style = animation_style
        self.quality = quality
        self.fps = {"low": 15, "medium": 24, "high": 30}[quality]
        self.resolution = {"low": (640, 480), "medium": (1280, 720), "high": (1920, 1080)}[quality]
        
        if not MOVIEPY_AVAILABLE:
            logger.warning("moviepy not available. Video generation will be limited.")
    
    def create_lesson_video(self, lesson_content: str, topic: str, grade: int,
                           language: str, output_path: Optional[str] = None,
                           audio_path: Optional[str] = None) -> str:
        """
        Create animated video for a lesson
        
        Args:
            lesson_content: Text content of the lesson
            topic: Lesson topic
            grade: Student grade level
            language: Language code
            output_path: Output video file path
            audio_path: Optional audio narration file
        
        Returns:
            Path to generated video file
        """
        if not MOVIEPY_AVAILABLE:
            logger.warning("Creating placeholder video (moviepy not available)")
            return self._create_placeholder_video(output_path or "lesson_video.mp4")
        
        if output_path is None:
            output_path = f"lesson_{hash(topic) % 10000}.mp4"
        
        logger.info(f"Creating animated video for topic: {topic}")
        
        # Parse content into scenes
        scenes = self._parse_content_to_scenes(lesson_content, grade)
        
        # Generate video clips for each scene
        video_clips = []
        for i, scene in enumerate(scenes):
            clip = self._create_scene_clip(scene, i, topic, grade, language)
            video_clips.append(clip)
        
        # Concatenate all clips
        if video_clips:
            final_video = concatenate_videoclips(video_clips, method="compose")
        else:
            # Create a simple text-based video
            final_video = self._create_text_video(lesson_content, topic, language)
        
        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            try:
                audio = AudioFileClip(audio_path)
                final_video = final_video.set_audio(audio)
            except Exception as e:
                logger.warning(f"Could not add audio: {e}")
        
        # Write video file
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac' if audio_path else None,
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_video.close()
        for clip in video_clips:
            clip.close()
        
        logger.info(f"Video created: {output_path}")
        return output_path
    
    def _parse_content_to_scenes(self, content: str, grade: int) -> List[Dict]:
        """Parse lesson content into visual scenes"""
        # Split content into paragraphs/sentences
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        scenes = []
        for para in paragraphs[:10]:  # Limit to 10 scenes
            scene = {
                "text": para,
                "duration": min(len(para.split()) * 0.5, 10),  # ~0.5 sec per word, max 10 sec
                "visual_type": self._determine_visual_type(para, grade),
                "animation": self._suggest_animation(para, grade)
            }
            scenes.append(scene)
        
        return scenes
    
    def _determine_visual_type(self, text: str, grade: int) -> str:
        """Determine what type of visual to show"""
        text_lower = text.lower()
        
        # Simple keyword-based detection
        if any(word in text_lower for word in ["संख्या", "number", "गिनती", "count", "add", "जोड़"]):
            return "numbers"
        elif any(word in text_lower for word in ["shape", "आकार", "circle", "वृत्त", "square", "वर्ग"]):
            return "shapes"
        elif any(word in text_lower for word in ["story", "कहानी", "character", "पात्र"]):
            return "story"
        elif any(word in text_lower for word in ["example", "उदाहरण", "example", "देखो"]):
            return "example"
        else:
            return "text"
    
    def _suggest_animation(self, text: str, grade: int) -> str:
        """Suggest animation type based on content"""
        if grade <= 3:
            return "simple_bounce"
        elif grade <= 5:
            return "slide_in"
        else:
            return "fade"
    
    def _create_scene_clip(self, scene: Dict, scene_num: int, topic: str,
                          grade: int, language: str):
        """Create a video clip for a scene"""
        duration = scene["duration"]
        visual_type = scene["visual_type"]
        
        # Create background
        bg_clip = self._create_background_clip(duration, grade)
        
        # Create visual element based on type
        if visual_type == "numbers":
            visual_clip = self._create_number_animation(scene["text"], duration, grade)
        elif visual_type == "shapes":
            visual_clip = self._create_shape_animation(scene["text"], duration, grade)
        elif visual_type == "story":
            visual_clip = self._create_story_visual(scene["text"], duration, grade)
        else:
            visual_clip = self._create_text_clip(scene["text"], duration, language, grade)
        
        # Composite background and visual
        final_clip = CompositeVideoClip([bg_clip, visual_clip.set_position('center')])
        final_clip = final_clip.set_duration(duration)
        
        return final_clip
    
    def _create_background_clip(self, duration: float, grade: int):
        """Create background clip"""
        # Create colorful background appropriate for grade
        if grade <= 3:
            # Bright, colorful for younger kids
            bg_color = (255, 240, 200)  # Light yellow
        elif grade <= 5:
            bg_color = (230, 250, 255)  # Light blue
        else:
            bg_color = (255, 255, 255)  # White
        
        bg = ImageClip(self._create_background_image(bg_color), duration=duration)
        return bg.resize(self.resolution)
    
    def _create_background_image(self, color: tuple) -> str:
        """Create background image file"""
        from PIL import Image
        img = Image.new('RGB', self.resolution, color=color)
        path = f"temp_bg_{hash(str(color)) % 1000}.png"
        img.save(path)
        return path
    
    def _create_text_clip(self, text: str, duration: float, language: str, grade: int):
        """Create text overlay clip"""
        # Choose font size based on grade
        fontsize = {1: 40, 2: 45, 3: 50, 4: 45, 5: 40, 6: 35, 7: 32, 8: 30}.get(grade, 35)
        
        # Wrap text for readability
        words = text.split()
        lines = []
        current_line = []
        chars_per_line = 50 if grade <= 3 else 60
        
        for word in words:
            if len(' '.join(current_line + [word])) <= chars_per_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        text_to_display = '\n'.join(lines[:3])  # Max 3 lines
        
        txt_clip = TextClip(
            text_to_display,
            fontsize=fontsize,
            color='black',
            font='Arial-Bold',
            method='caption',
            size=(self.resolution[0] * 0.9, None),
            align='center'
        ).set_duration(duration).set_position('center')
        
        return txt_clip
    
    def _create_number_animation(self, text: str, duration: float, grade: int):
        """Create number animation"""
        # Extract numbers from text
        import re
        numbers = re.findall(r'\d+', text)
        
        if numbers:
            # Create simple number visualization
            num_text = ' + '.join(numbers[:3])  # Show first 3 numbers
            return self._create_text_clip(num_text, duration, "en", grade)
        else:
            return self._create_text_clip(text, duration, "en", grade)
    
    def _create_shape_animation(self, text: str, duration: float, grade: int):
        """Create shape animation"""
        # Create simple shape visualization
        return self._create_text_clip(text, duration, "en", grade)
    
    def _create_story_visual(self, text: str, duration: float, grade: int):
        """Create story visualization"""
        # Create story-themed visual
        return self._create_text_clip(text, duration, "en", grade)
    
    def _create_text_video(self, content: str, topic: str, language: str):
        """Create simple text-based video as fallback"""
        # Split into slides
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()][:5]
        
        clips = []
        for para in paragraphs:
            txt_clip = TextClip(
                para[:100],  # Limit text
                fontsize=40,
                color='black',
                size=self.resolution,
                method='caption'
            ).set_duration(5)
            clips.append(txt_clip)
        
        if clips:
            return concatenate_videoclips(clips, method="compose")
        else:
            # Empty video
            return ImageClip(self._create_background_image((255, 255, 255))).set_duration(10)
    
    def _create_placeholder_video(self, output_path: str) -> str:
        """Create a placeholder video when moviepy is not available"""
        logger.warning("Creating placeholder video file")
        # Create an empty file as placeholder
        Path(output_path).touch()
        return output_path
    
    def add_subtitles(self, video_path: str, subtitles: List[Dict], output_path: str) -> str:
        """Add subtitles to video"""
        if not MOVIEPY_AVAILABLE:
            return video_path
        
        video = VideoFileClip(video_path)
        subtitle_clips = []
        
        for subtitle in subtitles:
            txt_clip = TextClip(
                subtitle["text"],
                fontsize=24,
                color='white',
                stroke_color='black',
                stroke_width=2,
                font='Arial-Bold'
            ).set_start(subtitle["start"]).set_duration(subtitle["duration"]).set_position(('center', 'bottom'))
            subtitle_clips.append(txt_clip)
        
        final_video = CompositeVideoClip([video] + subtitle_clips)
        final_video.write_videofile(output_path, fps=self.fps, verbose=False, logger=None)
        
        video.close()
        final_video.close()
        
        return output_path

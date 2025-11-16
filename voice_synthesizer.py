"""
Voice Synthesis Module
Supports multiple Indian languages with natural-sounding TTS
"""

import os
import logging
from typing import Optional
from pathlib import Path

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logging.warning("gTTS not available. Install with: pip install gtts")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logging.warning("pyttsx3 not available. Install with: pip install pyttsx3")

try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False
    logging.warning("Coqui TTS not available. Install with: pip install TTS")

logger = logging.getLogger(__name__)


class VoiceSynthesizer:
    """
    Multi-language voice synthesizer for educational content
    Supports Indian languages with natural, friendly voices
    """
    
    # Language code mapping for Indian languages
    LANGUAGE_CODES = {
        "hi": "hi",  # Hindi
        "en": "en",  # English
        "te": "te",  # Telugu
        "ta": "ta",  # Tamil
        "mr": "mr",  # Marathi
        "gu": "gu",  # Gujarati
        "bn": "bn",  # Bengali
        "kn": "kn",  # Kannada
        "ml": "ml",  # Malayalam
        "or": "or",  # Odia
    }
    
    def __init__(self, language: str = "hi", voice_style: str = "friendly"):
        """
        Initialize voice synthesizer
        
        Args:
            language: Language code (hi, en, te, etc.)
            voice_style: Voice style (friendly, professional, energetic)
        """
        self.language = language
        self.voice_style = voice_style
        self.tts_engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the best available TTS engine"""
        # Try Coqui TTS first (best quality, supports Indian languages)
        if COQUI_TTS_AVAILABLE:
            try:
                # Use multilingual model
                self.tts_engine = "coqui"
                logger.info("Using Coqui TTS engine")
                return
            except Exception as e:
                logger.warning(f"Coqui TTS initialization failed: {e}")
        
        # Fallback to pyttsx3 (offline, but limited language support)
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_pyttsx3()
                logger.info("Using pyttsx3 engine")
                return
            except Exception as e:
                logger.warning(f"pyttsx3 initialization failed: {e}")
        
        # Fallback to gTTS (requires internet, good language support)
        if GTTS_AVAILABLE:
            self.tts_engine = "gtts"
            logger.info("Using gTTS engine")
            return
        
        logger.error("No TTS engine available!")
        self.tts_engine = None
    
    def _configure_pyttsx3(self):
        """Configure pyttsx3 voice settings"""
        if self.tts_engine and isinstance(self.tts_engine, pyttsx3.Engine):
            # Set voice properties for friendly, engaging tone
            rate = self.tts_engine.getProperty('rate')
            self.tts_engine.setProperty('rate', rate - 20)  # Slightly slower
            
            volume = self.tts_engine.getProperty('volume')
            self.tts_engine.setProperty('volume', volume + 0.1)  # Slightly louder
            
            # Try to find a female voice (usually more friendly)
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
    
    def synthesize(self, text: str, language: Optional[str] = None, 
                   output_path: Optional[str] = None, slow: bool = False) -> str:
        """
        Synthesize speech from text
        
        Args:
            text: Text to convert to speech
            language: Language code (defaults to instance language)
            output_path: Output file path (defaults to auto-generated)
            slow: Whether to speak slowly (for learning)
        
        Returns:
            Path to generated audio file
        """
        if not self.tts_engine:
            raise RuntimeError("No TTS engine available")
        
        lang = language or self.language
        lang_code = self.LANGUAGE_CODES.get(lang, "en")
        
        if output_path is None:
            output_path = f"audio_{hash(text) % 10000}.mp3"
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if self.tts_engine == "coqui":
                return self._synthesize_coqui(text, lang_code, output_path)
            elif self.tts_engine == "gtts":
                return self._synthesize_gtts(text, lang_code, output_path, slow)
            elif isinstance(self.tts_engine, pyttsx3.Engine):
                return self._synthesize_pyttsx3(text, output_path)
            else:
                raise RuntimeError("Unknown TTS engine")
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            # Fallback to gTTS if available
            if GTTS_AVAILABLE and self.tts_engine != "gtts":
                logger.info("Falling back to gTTS")
                return self._synthesize_gtts(text, lang_code, output_path, slow)
            raise
    
    def _synthesize_coqui(self, text: str, lang_code: str, output_path: str) -> str:
        """Synthesize using Coqui TTS"""
        # Note: This requires model download on first use
        # Using multilingual model
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False)
        tts.tts_to_file(text=text, file_path=output_path, language=lang_code)
        return output_path
    
    def _synthesize_gtts(self, text: str, lang_code: str, output_path: str, slow: bool) -> str:
        """Synthesize using Google TTS"""
        tts = gTTS(text=text, lang=lang_code, slow=slow)
        tts.save(output_path)
        return output_path
    
    def _synthesize_pyttsx3(self, text: str, output_path: str) -> str:
        """Synthesize using pyttsx3"""
        # pyttsx3 saves to wav format
        wav_path = output_path.replace('.mp3', '.wav')
        self.tts_engine.save_to_file(text, wav_path)
        self.tts_engine.runAndWait()
        return wav_path
    
    def synthesize_with_emotion(self, text: str, emotion: str = "happy",
                               language: Optional[str] = None,
                               output_path: Optional[str] = None) -> str:
        """
        Synthesize speech with emotional tone
        
        Args:
            text: Text to convert
            emotion: Emotion (happy, excited, calm, encouraging)
            language: Language code
            output_path: Output file path
        
        Returns:
            Path to generated audio file
        """
        # Add emotional markers to text
        emotional_text = self._add_emotional_markers(text, emotion)
        return self.synthesize(emotional_text, language, output_path)
    
    def _add_emotional_markers(self, text: str, emotion: str) -> str:
        """Add emotional context to text (simplified approach)"""
        # In a real implementation, you'd use SSML or prosody markers
        # For now, we'll adjust speech rate and add pauses
        if emotion == "excited":
            # Add exclamation marks for excitement
            text = text.replace(".", "!").replace("।", "!")
        elif emotion == "calm":
            # Add pauses for calm delivery
            text = text.replace(".", "...").replace("।", "...")
        
        return text
    
    def get_available_languages(self) -> list:
        """Get list of supported languages"""
        return list(self.LANGUAGE_CODES.keys())
    
    def set_language(self, language: str):
        """Change the default language"""
        if language in self.LANGUAGE_CODES:
            self.language = language
        else:
            logger.warning(f"Language {language} not supported, keeping {self.language}")

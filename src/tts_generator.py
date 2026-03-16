import os
from pathlib import Path
from typing import List, Optional
from loguru import logger


class TTSGenerator:
    """Generate TTS audio files using gTTS or Chatterbox TTS."""

    def __init__(
        self,
        output_dir: str = "output/audio",
        audio_prompt_path: str = "Korean-sample1.wav",
    ):
        """
        Initialize TTS generator.

        Args:
            output_dir: Base directory for audio output
            audio_prompt_path: Path to audio prompt file (for Chatterbox)
        """
        self.output_dir = Path(output_dir)
        self.audio_prompt_path = audio_prompt_path
        self.use_chatterbox = False
        self.model = None

        # Try to load Chatterbox, fall back to gTTS
        self._initialize_tts()

    def _initialize_tts(self):
        """Initialize TTS engine (Chatterbox or gTTS)."""
        try:
            # Try Chatterbox first
            from chatter_box_tts import ChatterboxTTS

            self.model = ChatterboxTTS()
            self.use_chatterbox = True
            logger.info("Using Chatterbox TTS for audio generation")
        except ImportError:
            # Fall back to gTTS
            logger.info(
                "Chatterbox TTS not available, using gTTS (Google Text-to-Speech)"
            )
            self.use_chatterbox = False

    def generate_audio(self, text: str, output_path: str) -> bool:
        """
        Generate audio file for given text.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Generating audio for: {text[:50]}...")

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if self.use_chatterbox and self.model:
                # Use Chatterbox TTS
                audio = self.model.generate(
                    text=text,
                    language_id="ko",
                    audio_prompt_path=self.audio_prompt_path,
                    cfg_weight=0.3,
                )
                self.model.save(audio, output_path)
            else:
                # Use gTTS
                from gtts import gTTS

                tts = gTTS(text=text, lang="ko")
                tts.save(output_path)

            logger.info(f"Audio saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating audio for '{text[:50]}...': {e}")
            return False

    def generate_word_audio(
        self, word: str, output_dir: Optional[Path] = None
    ) -> Optional[str]:
        """
        Generate audio file for a word.

        Args:
            word: Korean word to convert to speech
            output_dir: Directory to save audio (default: self.output_dir/<word>)

        Returns:
            Path to generated audio file, or None if failed
        """
        if output_dir is None:
            output_dir = self.output_dir / word

        output_path = output_dir / "word.wav"

        success = self.generate_audio(word, str(output_path))
        return str(output_path) if success else None

    def generate_sentence_audios(
        self, word: str, sentences: List[str]
    ) -> List[Optional[str]]:
        """
        Generate audio files for each sentence.

        Args:
            word: Korean word (used for directory name)
            sentences: List of 3 sentences

        Returns:
            List of paths to generated audio files
        """
        word_dir = self.output_dir / word
        os.makedirs(word_dir, exist_ok=True)

        audio_paths = []
        for idx, sentence in enumerate(sentences, 1):
            if not sentence:  # Skip empty sentences
                audio_paths.append(None)
                continue

            output_path = word_dir / f"sentence{idx}.wav"

            if self.generate_audio(sentence, str(output_path)):
                audio_paths.append(str(output_path))
            else:
                audio_paths.append(None)

        return audio_paths


def generate_tts_for_entry(
    word: str,
    sentences: List[str],
    output_dir: str = "output/audio",
    audio_prompt: str = "Korean-sample1.wav",
) -> dict:
    """
    Generate TTS audio for a word and its sentences.

    Args:
        word: Korean word
        sentences: List of 3 example sentences
        output_dir: Output directory for audio files
        audio_prompt: Path to audio prompt file (for Chatterbox)

    Returns:
        Dictionary with word audio path and sentence audio paths
    """
    tts = TTSGenerator(output_dir=output_dir, audio_prompt_path=audio_prompt)

    result = {"word": word, "word_audio": None, "sentence_audios": []}

    try:
        # Generate word audio
        word_audio = tts.generate_word_audio(word)
        result["word_audio"] = word_audio

        # Generate sentence audios
        sentence_audios = tts.generate_sentence_audios(word, sentences)
        result["sentence_audios"] = [audio for audio in sentence_audios if audio]

        logger.info(
            f"Generated TTS for {word}: {len(result['sentence_audios'])} sentences"
        )

    except Exception as e:
        logger.error(f"Failed to generate TTS for {word}: {e}")

    return result

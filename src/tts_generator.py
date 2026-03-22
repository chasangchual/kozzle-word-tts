import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Dict
from loguru import logger


class TTSGenerator:
    """Generate TTS audio files using ChatterBox TTS and/or Qwen3-TTS (mlx_audio)."""

    def __init__(
        self,
        output_dir: str = "output/audio",
        audio_prompt_path: str = "Korean-sample1.wav",
        cfg_weight: float = 0.3,
        qwen3_model_path: str = "models/Qwen3-TTS-12Hz-1.7B-Base-8bit",
        tts_engine: str = "chatterbox",  # "chatterbox", "qwen3", or "both"
    ):
        """
        Initialize TTS generator.

        Args:
            output_dir: Base directory for audio output
            audio_prompt_path: Path to audio prompt file (for Chatterbox/Qwen3 voice cloning)
            cfg_weight: Classifier-free guidance weight for Chatterbox (0.0-1.0)
            qwen3_model_path: Path to Qwen3-TTS model directory
            tts_engine: TTS engine selection - "chatterbox", "qwen3", or "both"
        """
        self.output_dir = Path(output_dir)
        self.audio_prompt_path = audio_prompt_path
        self.cfg_weight = cfg_weight
        self.qwen3_model_path = qwen3_model_path
        self.tts_engine = tts_engine

        # TTS engine state
        self.chatterbox_available = False
        self.qwen3_available = False
        self.chatterbox_model = None
        self.qwen3_model = None

        # Engines to use for generation
        self.engines_to_use: List[str] = []

        # Initialize TTS engines based on selection
        self._initialize_tts()

    def _initialize_tts(self):
        """Initialize TTS engine(s) based on tts_engine selection."""
        if self.tts_engine == "chatterbox":
            if self._try_initialize_chatterbox():
                self.engines_to_use = ["chatterbox"]
            else:
                raise RuntimeError(
                    "ChatterBox TTS requested but not available. "
                    "Install with: uv pip install chatter_box_tts"
                )

        elif self.tts_engine == "qwen3":
            if self._try_initialize_qwen3():
                self.engines_to_use = ["qwen3"]
            else:
                raise RuntimeError(
                    "Qwen3-TTS requested but not available. "
                    "Install with: uv pip install mlx mlx-audio"
                )

        elif self.tts_engine == "both":
            # Try to initialize both engines
            chatterbox_ok = self._try_initialize_chatterbox()
            qwen3_ok = self._try_initialize_qwen3()

            if chatterbox_ok:
                self.engines_to_use.append("chatterbox")
            if qwen3_ok:
                self.engines_to_use.append("qwen3")

            if not self.engines_to_use:
                raise RuntimeError(
                    "No TTS engine available. "
                    "Install ChatterBox TTS or Qwen3-TTS (mlx_audio). "
                    "See README for installation instructions."
                )

            if len(self.engines_to_use) == 1:
                available = self.engines_to_use[0]
                missing = "qwen3" if available == "chatterbox" else "chatterbox"
                logger.warning(
                    f"Only {available} TTS is available. "
                    f"{missing} TTS could not be initialized. "
                    f"Continuing with {available} only."
                )

            logger.info(f"TTS engines to use: {self.engines_to_use}")

        else:
            raise ValueError(
                f"Invalid tts_engine: {self.tts_engine}. "
                f"Must be 'chatterbox', 'qwen3', or 'both'"
            )

    def _try_initialize_chatterbox(self) -> bool:
        """Try to initialize ChatterBox TTS."""
        try:
            from chatter_box_tts import ChatterboxTTS

            self.chatterbox_model = ChatterboxTTS()
            self.chatterbox_available = True
            logger.info("ChatterBox TTS initialized successfully")
            return True
        except ImportError:
            logger.debug("ChatterBox TTS not installed")
            return False
        except Exception as e:
            logger.debug(f"ChatterBox TTS initialization failed: {e}")
            return False

    def _try_initialize_qwen3(self) -> bool:
        """Try to initialize Qwen3-TTS using mlx_audio."""
        try:
            from mlx_audio.tts.utils import load_model

            # Find the model path (handle HuggingFace cache structure)
            model_path = self._get_qwen3_model_path()
            if not model_path:
                logger.warning(f"Qwen3-TTS model not found at: {self.qwen3_model_path}")
                return False

            logger.info(f"Loading Qwen3-TTS model from: {model_path}")
            self.qwen3_model = load_model(model_path)
            self.qwen3_available = True
            logger.info("Qwen3-TTS (mlx_audio) initialized successfully")
            return True
        except ImportError:
            logger.debug("mlx_audio not installed, Qwen3-TTS unavailable")
            return False
        except Exception as e:
            logger.debug(f"Qwen3-TTS initialization failed: {e}")
            return False

    def _get_qwen3_model_path(self) -> Optional[str]:
        """Get the actual model path, handling HuggingFace cache structure."""
        model_path = Path(self.qwen3_model_path)

        if not model_path.exists():
            return None

        # Check for HuggingFace snapshots directory structure
        snapshots_dir = model_path / "snapshots"
        if snapshots_dir.exists():
            subfolders = [
                f
                for f in snapshots_dir.iterdir()
                if f.is_dir() and not f.name.startswith(".")
            ]
            if subfolders:
                return str(subfolders[0])

        return str(model_path)

    def _get_output_dir_for_engine(self, engine: str, word: str) -> Path:
        """
        Get output directory based on engine and mode.

        When tts_engine is "both", creates separate folders for each engine.
        Otherwise, uses the standard output structure.

        Args:
            engine: The TTS engine name ("chatterbox" or "qwen3")
            word: The Korean word being processed

        Returns:
            Path to the output directory for this engine/word combination
        """
        if self.tts_engine == "both":
            return self.output_dir / engine / word
        return self.output_dir / word

    def generate_audio(self, text: str, output_path: str) -> bool:
        """
        Generate audio file for given text using the first available engine.

        Note: For multi-engine support, use generate_audio_all_engines() instead.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file

        Returns:
            True if successful, False otherwise
        """
        if not self.engines_to_use:
            logger.error("No TTS engine initialized")
            return False

        # Use the first available engine
        engine = self.engines_to_use[0]
        return self._generate_with_engine(engine, text, output_path)

    def generate_audio_all_engines(
        self, text: str, word: str, filename: str
    ) -> Dict[str, Optional[str]]:
        """
        Generate audio with all selected engines.

        Args:
            text: Text to convert to speech
            word: Word being processed (for directory structure)
            filename: Base filename (e.g., "word.wav", "sentence1.wav")

        Returns:
            Dictionary mapping engine name to output path (or None if failed)
        """
        results: Dict[str, Optional[str]] = {}

        for engine in self.engines_to_use:
            output_dir = self._get_output_dir_for_engine(engine, word)
            os.makedirs(output_dir, exist_ok=True)
            output_path = output_dir / filename

            success = self._generate_with_engine(engine, text, str(output_path))
            results[engine] = str(output_path) if success else None

        return results

    def _generate_with_engine(self, engine: str, text: str, output_path: str) -> bool:
        """
        Generate audio using a specific engine.

        Args:
            engine: Engine name ("chatterbox" or "qwen3")
            text: Text to convert to speech
            output_path: Path to save audio file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Generating audio with {engine} for: {text[:50]}...")

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if engine == "chatterbox":
                return self._generate_with_chatterbox(text, output_path)
            elif engine == "qwen3":
                return self._generate_with_qwen3(text, output_path)
            else:
                logger.error(f"Unknown engine: {engine}")
                return False

        except Exception as e:
            logger.exception(
                f"Error generating audio with {engine} for '{text[:50]}...'"
            )
            return False

    def _generate_with_chatterbox(self, text: str, output_path: str) -> bool:
        """Generate audio using ChatterBox TTS."""
        try:
            if not self.chatterbox_available or not self.chatterbox_model:
                logger.error("ChatterBox TTS not initialized")
                return False

            audio = self.chatterbox_model.generate(
                text=text,
                language_id="ko",
                audio_prompt_path=self.audio_prompt_path,
                cfg_weight=self.cfg_weight,
            )
            self.chatterbox_model.save(audio, output_path)
            logger.info(f"[ChatterBox] Audio saved to: {output_path}")
            return True
        except Exception as e:
            logger.exception(f"ChatterBox TTS generation failed for '{text[:50]}...'")
            return False

    def _generate_with_qwen3(self, text: str, output_path: str) -> bool:
        """Generate audio using Qwen3-TTS (mlx_audio)."""
        try:
            if not self.qwen3_available or not self.qwen3_model:
                logger.error("Qwen3-TTS not initialized")
                return False

            from mlx_audio.tts.generate import generate_audio

            # Create a temporary directory for mlx_audio output
            with tempfile.TemporaryDirectory() as temp_dir:
                # Prepare reference audio path if it exists
                ref_audio = None
                ref_text = None
                if self.audio_prompt_path and os.path.exists(self.audio_prompt_path):
                    ref_audio = self.audio_prompt_path
                    ref_text = ""  # Empty transcript for voice cloning

                # Generate audio to temp directory
                generate_audio(
                    model=self.qwen3_model,
                    text=text,
                    ref_audio=ref_audio,
                    ref_text=ref_text,
                    output_path=temp_dir,
                )

                # Move the generated audio file to the target path
                source_file = os.path.join(temp_dir, "audio_000.wav")
                if os.path.exists(source_file):
                    shutil.move(source_file, output_path)
                    logger.info(f"[Qwen3-TTS] Audio saved to: {output_path}")
                    return True
                else:
                    logger.error(f"Qwen3-TTS did not generate expected output file")
                    return False

        except Exception as e:
            logger.exception(f"Qwen3-TTS generation failed for '{text[:50]}...'")
            return False

    def generate_word_audio(
        self, word: str, output_dir: Optional[Path] = None
    ) -> Dict[str, Optional[str]]:
        """
        Generate audio file(s) for a word using all selected engines.

        Args:
            word: Korean word to convert to speech
            output_dir: Deprecated - directory is determined by engine selection

        Returns:
            Dictionary mapping engine name to path of generated audio file (or None if failed)
        """
        return self.generate_audio_all_engines(word, word, "word.wav")

    def generate_sentence_audios(
        self, word: str, sentences: List[str]
    ) -> Dict[str, List[Optional[str]]]:
        """
        Generate audio files for each sentence using all selected engines.

        Args:
            word: Korean word (used for directory name)
            sentences: List of 3 sentences

        Returns:
            Dictionary mapping engine name to list of paths to generated audio files
        """
        results: Dict[str, List[Optional[str]]] = {
            engine: [] for engine in self.engines_to_use
        }

        for idx, sentence in enumerate(sentences, 1):
            if not sentence:  # Skip empty sentences
                for engine in self.engines_to_use:
                    results[engine].append(None)
                continue

            filename = f"sentence{idx}.wav"
            audio_results = self.generate_audio_all_engines(sentence, word, filename)

            for engine in self.engines_to_use:
                results[engine].append(audio_results.get(engine))

        return results


def generate_tts_for_entry(
    word: str,
    sentences: List[str],
    output_dir: str = "output/audio",
    audio_prompt: str = "Korean-sample1.wav",
    qwen3_model_path: str = "models/Qwen3-TTS-12Hz-1.7B-Base-8bit",
    tts_engine: str = "chatterbox",
) -> dict:
    """
    Generate TTS audio for a word and its sentences.

    Args:
        word: Korean word
        sentences: List of 3 example sentences
        output_dir: Output directory for audio files
        audio_prompt: Path to audio prompt file (for Chatterbox/Qwen3)
        qwen3_model_path: Path to Qwen3-TTS model directory
        tts_engine: TTS engine selection - "chatterbox", "qwen3", or "both"

    Returns:
        Dictionary with word audio path and sentence audio paths per engine
    """
    result = {"word": word, "word_audio": {}, "sentence_audios": {}}

    try:
        tts = TTSGenerator(
            output_dir=output_dir,
            audio_prompt_path=audio_prompt,
            qwen3_model_path=qwen3_model_path,
            tts_engine=tts_engine,
        )

        # Generate word audio
        word_audio = tts.generate_word_audio(word)
        result["word_audio"] = word_audio

        # Generate sentence audios
        sentence_audios = tts.generate_sentence_audios(word, sentences)
        result["sentence_audios"] = sentence_audios

        # Log summary
        for engine, paths in sentence_audios.items():
            valid_count = len([p for p in paths if p])
            logger.info(
                f"Generated TTS for {word} with {engine}: {valid_count} sentences"
            )

    except Exception as e:
        logger.exception(f"Failed to generate TTS for {word}")

    return result

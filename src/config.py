from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Configuration for the Korean vocabulary learning pipeline."""

    llm_provider: str
    model: str
    # TTS configuration
    qwen3_model_path: str = field(default="models/Qwen3-TTS-12Hz-1.7B-Base-8bit")
    audio_prompt_path: str = field(default="Korean-sample1.wav")
    cfg_weight: float = field(default=0.3)
    tts_engine: str = field(default="chatterbox")  # "chatterbox", "qwen3", or "both"

    def __post_init__(self):
        # Validate provider
        valid_providers = ["ollama", "openai", "anthropic"]
        if self.llm_provider not in valid_providers:
            raise ValueError(f"Invalid provider. Must be one of {valid_providers}")

        # Validate cfg_weight
        if not 0.0 <= self.cfg_weight <= 1.0:
            raise ValueError("cfg_weight must be between 0.0 and 1.0")

        # Validate tts_engine
        valid_tts_engines = ["chatterbox", "qwen3", "both"]
        if self.tts_engine not in valid_tts_engines:
            raise ValueError(f"Invalid tts_engine. Must be one of {valid_tts_engines}")

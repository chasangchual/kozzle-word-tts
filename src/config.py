from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    llm_provider: str
    model: str
    # Add other configuration parameters here as needed
    
    def __post_init__(self):
        # Validate provider
        valid_providers = ["ollama", "openai", "anthropic"]
        if self.llm_provider not in valid_providers:
            raise ValueError(f"Invalid provider. Must be one of {valid_providers}")
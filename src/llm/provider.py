from typing import Optional
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from src.config import Config
import os


def get_llm(config: Config):
    """
    Get LLM instance based on provider configuration.

    Args:
        config: Configuration object with llm_provider and model

    Returns:
        LLM instance (ChatOllama, ChatOpenAI, or ChatAnthropic)
    """
    provider = config.llm_provider.lower()

    if provider == "ollama":
        # Use Ollama base URL from environment or config
        base_url = os.getenv("OLLAMA_BASE_URL", "http://192.168.1.194:11434")
        return ChatOllama(model=config.model, base_url=base_url)
    elif provider == "openai":
        return ChatOpenAI(model=config.model)
    elif provider == "anthropic":
        return ChatAnthropic(model=config.model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# CLI module - not currently used, main.py uses manual argument parsing
# Kept for potential future use with typer if needed

import sys
from pathlib import Path
from typing import Optional
from src.pipeline import process_korean_text
from src.config import Config


def process(
    input_path: str, llm_provider: str = "ollama", model: str = "exaone3.5:7.8b"
):
    """
    Process Korean text files to generate vocabulary learning content.

    This command processes Korean text files, extracts nouns, generates example
    sentences using an LLM, and creates TTS audio files.
    """
    try:
        config = Config(llm_provider=llm_provider, model=model)
        process_korean_text(input_path, config)
        print("Processing completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m src.cli <input_path> [--llm-provider ollama] [--model exaone3.5:7.8b]"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    llm_provider = "ollama"
    model = "exaone3.5:7.8b"

    # Parse optional arguments
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--llm-provider" and i + 1 < len(args):
            llm_provider = args[i + 1]
            i += 2
        elif args[i] == "--model" and i + 1 < len(args):
            model = args[i + 1]
            i += 2
        else:
            i += 1

    process(input_path, llm_provider, model)

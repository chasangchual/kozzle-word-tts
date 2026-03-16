import sys
import os
from src.pipeline import process_korean_text
from src.config import Config

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print(
            "Usage: python main.py <input_path> [--llm-provider ollama] [--model exaone3.5:7.8b] [--no-tts]"
        )
        print(
            "Example: python main.py ./sample_korean.txt --llm-provider ollama --model exaone3.5:7.8b"
        )
        print("\nOptions:")
        print(
            "  --llm-provider <provider>  LLM provider (ollama, openai, anthropic) [default: ollama]"
        )
        print("  --model <model>           Model name [default: exaone3.5:7.8b]")
        print("  --no-tts                   Skip TTS audio generation")
        sys.exit(1)

    input_path = sys.argv[1]
    llm_provider = "ollama"
    model = "exaone3.5:7.8b"
    generate_tts = True

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
        elif args[i] == "--no-tts":
            generate_tts = False
            i += 1
        else:
            i += 1

    # Create output directories
    os.makedirs("output/audio", exist_ok=True)

    # Create config
    config = Config(llm_provider=llm_provider, model=model)

    try:
        result = process_korean_text(input_path, config, generate_tts=generate_tts)
        print(f"\n{'=' * 60}")
        print(f"Processing complete. Found {len(result)} entries.")
        print(f"{'=' * 60}\n")

        for entry in result:
            print(f"Word: {entry['word']}")
            print(f"ID: {entry['id']}")
            print("Sentences:")
            for idx, sentence in enumerate(entry["sentences"], 1):
                print(f"  {idx}. {sentence}")
            print()

        print(f"JSON output saved to: output/result.json")
        if generate_tts:
            print(f"Audio files saved to: output/audio/")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

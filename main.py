import sys
import os
import json
from pathlib import Path
from loguru import logger
from src.pipeline import process_korean_text, generate_tts_audio
from src.config import Config


def configure_logging():
    """Configure loguru for file-based logging with rotation."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure file logging with 10MB rotation
    logger.add(
        log_dir / "app.log",
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention=5,  # Keep last 5 rotated files
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}",
        backtrace=True,  # Include full traceback
        diagnose=True,  # Include variable values in tracebacks
        encoding="utf-8",
    )

    # Configure error-only log for quick error review
    logger.add(
        log_dir / "errors.log",
        rotation="10 MB",
        retention=5,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}",
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
    )

    logger.info("Logging configured: logs/app.log (10MB rotation)")


if __name__ == "__main__":
    # Configure logging first
    configure_logging()

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_path> [OPTIONS]")
        print("       python main.py --generate-audio-from-json <json_path>")
        print("\nExamples:")
        print(
            "  python main.py ./sample_korean.txt --llm-provider ollama --model exaone3.5:7.8b"
        )
        print("  python main.py ./sample_korean.txt --tts-engine both")
        print(
            "  python main.py --generate-audio-from-json output/result.json --tts-engine qwen3"
        )
        print("\nOptions:")
        print(
            "  --llm-provider <provider>          LLM provider (ollama, openai, anthropic) [default: ollama]"
        )
        print(
            "  --model <model>                    Model name [default: exaone3.5:7.8b]"
        )
        print("  --no-tts                           Skip TTS audio generation")
        print(
            "  --tts-engine <engine>              TTS engine: chatterbox, qwen3, or both [default: chatterbox]"
        )
        print(
            "  --audio-prompt <path>              Path to audio prompt file [default: Korean-sample1.wav]"
        )
        print(
            "  --cfg-weight <value>               CFG weight (0.0-1.0) [default: 0.3]"
        )
        print(
            "  --generate-audio-from-json <path>  Generate audio from existing JSON file"
        )
        print(
            "  --qwen3-model-path <path>          Path to Qwen3-TTS model [default: models/Qwen3-TTS-12Hz-1.7B-Base-8bit]"
        )
        sys.exit(1)

    # Check if we're generating audio from JSON
    if sys.argv[1] == "--generate-audio-from-json":
        if len(sys.argv) < 3:
            print("Error: --generate-audio-from-json requires a JSON file path")
            sys.exit(1)

        json_path = sys.argv[2]
        audio_prompt_path = "Korean-sample1.wav"
        cfg_weight = 0.3
        qwen3_model_path = "models/Qwen3-TTS-12Hz-1.7B-Base-8bit"
        tts_engine = "chatterbox"

        # Parse optional arguments after JSON path
        args = sys.argv[3:]
        i = 0
        while i < len(args):
            if args[i] == "--audio-prompt" and i + 1 < len(args):
                audio_prompt_path = args[i + 1]
                i += 2
            elif args[i] == "--cfg-weight" and i + 1 < len(args):
                try:
                    cfg_weight = float(args[i + 1])
                    if not 0.0 <= cfg_weight <= 1.0:
                        print("Warning: cfg-weight should be between 0.0 and 1.0")
                except ValueError:
                    print(f"Error: Invalid cfg-weight value: {args[i + 1]}")
                    sys.exit(1)
                i += 2
            elif args[i] == "--qwen3-model-path" and i + 1 < len(args):
                qwen3_model_path = args[i + 1]
                i += 2
            elif args[i] == "--tts-engine" and i + 1 < len(args):
                tts_engine = args[i + 1]
                if tts_engine not in ["chatterbox", "qwen3", "both"]:
                    print(f"Error: Invalid tts-engine value: {tts_engine}")
                    print("Valid options: chatterbox, qwen3, both")
                    sys.exit(1)
                i += 2
            else:
                i += 1

        try:
            # Create output directories
            os.makedirs("output/audio", exist_ok=True)

            # Read JSON file
            print(f"Reading JSON file: {json_path}")
            with open(json_path, "r", encoding="utf-8") as f:
                entries = json.load(f)

            print(f"Found {len(entries)} vocabulary entries")
            print(f"TTS engine: {tts_engine}")
            print(f"Audio prompt: {audio_prompt_path}")
            print(f"CFG weight: {cfg_weight}")
            print(f"{'=' * 60}")

            # Generate TTS audio for all entries
            generate_tts_audio(
                entries,
                audio_prompt_path=audio_prompt_path,
                cfg_weight=cfg_weight,
                qwen3_model_path=qwen3_model_path,
                tts_engine=tts_engine,
            )

            print(f"\n{'=' * 60}")
            print(f"Audio generation complete!")
            if tts_engine == "both":
                print(
                    f"Audio files saved to: output/audio/chatterbox/ and output/audio/qwen3/"
                )
            else:
                print(f"Audio files saved to: output/audio/")
            print(f"{'=' * 60}\n")

            # Display summary
            for entry in entries:
                print(f"Word: {entry['word']}")
                print(f"  - word.wav")
                print(f"  - sentence1.wav, sentence2.wav, sentence3.wav")

        except FileNotFoundError:
            print(f"Error: JSON file not found: {json_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)

    else:
        # Normal processing mode
        input_path = sys.argv[1]
        llm_provider = "ollama"
        model = "exaone3.5:7.8b"
        generate_tts = True
        audio_prompt_path = "Korean-sample1.wav"
        cfg_weight = 0.3
        qwen3_model_path = "models/Qwen3-TTS-12Hz-1.7B-Base-8bit"
        tts_engine = "chatterbox"

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
            elif args[i] == "--tts-engine" and i + 1 < len(args):
                tts_engine = args[i + 1]
                if tts_engine not in ["chatterbox", "qwen3", "both"]:
                    print(f"Error: Invalid tts-engine value: {tts_engine}")
                    print("Valid options: chatterbox, qwen3, both")
                    sys.exit(1)
                i += 2
            elif args[i] == "--audio-prompt" and i + 1 < len(args):
                audio_prompt_path = args[i + 1]
                i += 2
            elif args[i] == "--cfg-weight" and i + 1 < len(args):
                try:
                    cfg_weight = float(args[i + 1])
                    if not 0.0 <= cfg_weight <= 1.0:
                        print("Warning: cfg-weight should be between 0.0 and 1.0")
                except ValueError:
                    print(f"Error: Invalid cfg-weight value: {args[i + 1]}")
                    sys.exit(1)
                i += 2
            elif args[i] == "--qwen3-model-path" and i + 1 < len(args):
                qwen3_model_path = args[i + 1]
                i += 2
            else:
                i += 1

        # Create output directories
        os.makedirs("output/audio", exist_ok=True)

        # Create config
        config = Config(llm_provider=llm_provider, model=model)

        try:
            result = process_korean_text(
                input_path,
                config,
                generate_tts=generate_tts,
                audio_prompt_path=audio_prompt_path,
                cfg_weight=cfg_weight,
                qwen3_model_path=qwen3_model_path,
                tts_engine=tts_engine,
            )
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
                if tts_engine == "both":
                    print(
                        f"Audio files saved to: output/audio/chatterbox/ and output/audio/qwen3/"
                    )
                else:
                    print(f"Audio files saved to: output/audio/")

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()

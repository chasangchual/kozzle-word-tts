import sys
import os
import json
from src.pipeline import process_korean_text, generate_tts_audio
from src.config import Config

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_path> [OPTIONS]")
        print("       python main.py --generate-audio-from-json <json_path>")
        print("\nExamples:")
        print(
            "  python main.py ./sample_korean.txt --llm-provider ollama --model exaone3.5:7.8b"
        )
        print("  python main.py --generate-audio-from-json output/result.json")
        print("\nOptions:")
        print(
            "  --llm-provider <provider>          LLM provider (ollama, openai, anthropic) [default: ollama]"
        )
        print(
            "  --model <model>                    Model name [default: exaone3.5:7.8b]"
        )
        print("  --no-tts                           Skip TTS audio generation")
        print(
            "  --audio-prompt <path>              Path to audio prompt file [default: Korean-sample1.wav]"
        )
        print(
            "  --cfg-weight <value>               CFG weight (0.0-1.0) [default: 0.3]"
        )
        print(
            "  --generate-audio-from-json <path>  Generate audio from existing JSON file"
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
            print(f"Audio prompt: {audio_prompt_path}")
            print(f"CFG weight: {cfg_weight}")
            print(f"{'=' * 60}")

            # Generate TTS audio for all entries
            generate_tts_audio(
                entries, audio_prompt_path=audio_prompt_path, cfg_weight=cfg_weight
            )

            print(f"\n{'=' * 60}")
            print(f"Audio generation complete!")
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
                print(f"Audio files saved to: output/audio/")

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()

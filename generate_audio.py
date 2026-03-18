#!/usr/bin/env python
"""
Standalone script to generate TTS audio from an existing JSON file.

Usage:
    python generate_audio.py <json_path> [--audio-prompt <path>] [--cfg-weight <value>]

Example:
    python generate_audio.py output/result.json
    python generate_audio.py output/result.json --audio-prompt Korean-sample2.wav --cfg-weight 0.5
"""

import sys
import os
import json
from src.pipeline import generate_tts_audio


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_audio.py <json_path> [OPTIONS]")
        print("\nOptions:")
        print("  --audio-prompt <path>    Path to audio prompt file for voice cloning")
        print("                           [default: Korean-sample1.wav]")
        print("  --cfg-weight <value>     Classifier-free guidance weight (0.0-1.0)")
        print("                           [default: 0.3]")
        print("\nExamples:")
        print("  python generate_audio.py output/result.json")
        print(
            "  python generate_audio.py output/result.json --audio-prompt Korean-sample2.wav"
        )
        print("  python generate_audio.py output/result.json --cfg-weight 0.5")
        print(
            "  python generate_audio.py output/result.json --audio-prompt Korean-sample2.wav --cfg-weight 0.5"
        )
        sys.exit(1)

    json_path = sys.argv[1]
    audio_prompt_path = "Korean-sample1.wav"
    cfg_weight = 0.3

    # Parse optional arguments
    args = sys.argv[2:]
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

    # Validate file exists
    if not os.path.exists(json_path):
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    try:
        # Create output directories
        os.makedirs("output/audio", exist_ok=True)

        # Read JSON file
        print(f"Reading JSON file: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            entries = json.load(f)

        if not isinstance(entries, list):
            print("Error: JSON file must contain a list of vocabulary entries")
            sys.exit(1)

        print(f"Found {len(entries)} vocabulary entries")
        print(f"Audio prompt: {audio_prompt_path}")
        print(f"CFG weight: {cfg_weight}")
        print(f"{'=' * 70}")

        # Validate structure
        for idx, entry in enumerate(entries):
            if "word" not in entry:
                print(f"Warning: Entry {idx} missing 'word' field, skipping")
                continue
            if "sentences" not in entry:
                print(
                    f"Warning: Entry {idx} missing 'sentences' field, using empty list"
                )
                entry["sentences"] = []

        # Generate TTS audio for all entries
        generate_tts_audio(
            entries, audio_prompt_path=audio_prompt_path, cfg_weight=cfg_weight
        )

        print(f"\n{'=' * 70}")
        print(f"Audio generation complete!")
        print(f"Audio files saved to: output/audio/")
        print(f"{'=' * 70}\n")

        # Display summary
        total_files = 0
        for entry in entries:
            word = entry.get("word", "unknown")
            sentences = entry.get("sentences", [])
            sentence_count = len([s for s in sentences if s])
            files = 1 + sentence_count  # word.wav + sentence files
            total_files += files

            print(f"Word: {word}")
            print(f"  - word.wav")
            if sentence_count > 0:
                print(f"  - {sentence_count} sentence audio file(s)")

        print(f"\nTotal audio files generated: {total_files}")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

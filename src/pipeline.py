import uuid
from typing import List, Dict, Any
from loguru import logger
from src.file_loader import load_files, read_file_content
from src.noun_extractor import extract_nouns
from src.llm.provider import get_llm
from src.llm.sentence_chain import generate_sentences
from src.json_writer import write_json_output


def process_korean_text(
    input_path: str, config, generate_tts: bool = True
) -> List[Dict[str, Any]]:
    """
    Main pipeline for processing Korean text and generating vocabulary content.

    Args:
        input_path: Path to input file or directory
        config: Configuration object
        generate_tts: Whether to generate TTS audio (default: True)

    Returns:
        List of vocabulary entries with word and sentences
    """
    logger.info(f"Starting processing of input: {input_path}")

    # Load files
    files = load_files(input_path)

    # Get LLM instance
    llm = get_llm(config)
    logger.info(f"Using LLM provider: {config.llm_provider}, model: {config.model}")

    # Process each file
    all_nouns = set()
    all_entries = []

    for file_path in files:
        try:
            content = read_file_content(file_path)
            logger.info(f"Processing file: {file_path}")

            # Extract nouns
            nouns = extract_nouns(content)
            logger.info(f"Extracted nouns from {file_path}: {nouns}")

            # Add to total list (for deduplication)
            for noun in nouns:
                if noun not in all_nouns:
                    all_nouns.add(noun)

                    # Generate sentences using LLM
                    try:
                        result = generate_sentences(llm, noun)

                        entry = {
                            "id": str(uuid.uuid4()),
                            "word": result["word"],
                            "sentences": result["sentences"],
                        }
                        all_entries.append(entry)

                    except Exception as e:
                        logger.error(f"Failed to generate sentences for {noun}: {e}")
                        # Create entry with placeholder if LLM fails
                        entry = {
                            "id": str(uuid.uuid4()),
                            "word": noun,
                            "sentences": ["", "", ""],
                        }
                        all_entries.append(entry)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            # Continue processing other files instead of failing completely

    # Write JSON output
    try:
        write_json_output(all_entries, "output/result.json")
    except Exception as e:
        logger.error(f"Failed to write JSON output: {e}")

    # Generate TTS audio if requested
    if generate_tts:
        try:
            generate_tts_audio(all_entries)
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            logger.warning("Continuing without TTS audio")

    logger.info(f"Processing completed. Found {len(all_entries)} unique nouns.")
    return all_entries


def generate_tts_audio(entries: List[Dict[str, Any]]) -> None:
    """
    Generate TTS audio for all entries.

    Args:
        entries: List of vocabulary entries
    """
    try:
        from src.tts_generator import TTSGenerator

        logger.info("Starting TTS audio generation...")

        tts = TTSGenerator(
            output_dir="output/audio", audio_prompt_path="Korean-sample1.wav"
        )

        for entry in entries:
            word = entry["word"]
            sentences = entry["sentences"]

            try:
                logger.info(f"Generating TTS for word: {word}")

                # Generate word audio
                word_audio = tts.generate_word_audio(word)
                if word_audio:
                    logger.info(f"Word audio saved: {word_audio}")

                # Generate sentence audios
                audio_paths = tts.generate_sentence_audios(word, sentences)
                logger.info(
                    f"Generated {len([p for p in audio_paths if p])} sentence audios for {word}"
                )

            except Exception as e:
                logger.error(f"Failed to generate TTS for {word}: {e}")
                continue

        logger.info("TTS audio generation completed")

    except ImportError as e:
        logger.warning(f"Chatterbox TTS not installed: {e}")
        logger.warning(
            "Skipping TTS generation. Install with: pip install chatter_box_tts"
        )
    except Exception as e:
        logger.error(f"TTS generation error: {e}")

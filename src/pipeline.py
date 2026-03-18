import uuid
from typing import List, Dict, Any
from loguru import logger
from src.file_loader import load_files, read_file_content
from src.noun_extractor import extract_nouns
from src.llm.provider import get_llm
from src.llm.sentence_chain import generate_sentences
from src.json_writer import write_json_output


def process_korean_text(
    input_path: str,
    config,
    generate_tts: bool = True,
    audio_prompt_path: str = "Korean-sample1.wav",
    cfg_weight: float = 0.3,
) -> List[Dict[str, Any]]:
    """
    Main pipeline for processing Korean text and generating vocabulary content.

    Args:
        input_path: Path to input file or directory
        config: Configuration object
        generate_tts: Whether to generate TTS audio (default: True)
        audio_prompt_path: Path to audio prompt file for voice cloning
        cfg_weight: Classifier-free guidance weight (0.0-1.0)

    Returns:
        List of vocabulary entries with word and sentences
    """
    logger.info(f"Starting processing of input: {input_path}")

    # Load files
    files = load_files(input_path)

    # Get LLM instance
    llm = get_llm(config)
    logger.info(f"Using LLM provider: {config.llm_provider}, model: {config.model}")

    # Process each file and collect all nouns first
    all_nouns_from_files = []
    total_nouns_extracted = 0

    logger.info(f"Found {len(files)} file(s) to process")

    for file_path in files:
        try:
            content = read_file_content(file_path)
            logger.info(f"Processing file: {file_path}")

            # Extract nouns
            nouns = extract_nouns(content)
            logger.info(f"Extracted {len(nouns)} nouns from {file_path}: {nouns}")

            total_nouns_extracted += len(nouns)
            all_nouns_from_files.extend(nouns)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            # Continue processing other files instead of failing completely

    # Remove duplicates and strip whitespace from all nouns
    # Strip whitespace and filter out any empty strings that might result
    cleaned_nouns = [noun.strip() for noun in all_nouns_from_files if noun.strip()]
    unique_nouns = list(set(cleaned_nouns))
    duplicates_removed = total_nouns_extracted - len(unique_nouns)

    logger.info(f"Total nouns extracted: {total_nouns_extracted}")
    logger.info(f"Unique nouns after deduplication: {len(unique_nouns)}")
    logger.info(f"Duplicates removed: {duplicates_removed}")
    logger.info(f"Unique noun list: {unique_nouns}")

    # Generate sentences for each unique noun
    all_entries = []

    for noun in unique_nouns:
        try:
            logger.info(f"Generating sentences for unique noun: {noun}")
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

    # Write JSON output
    try:
        write_json_output(all_entries, "output/result.json")
    except Exception as e:
        logger.error(f"Failed to write JSON output: {e}")

    # Generate TTS audio if requested
    if generate_tts:
        try:
            generate_tts_audio(
                all_entries, audio_prompt_path=audio_prompt_path, cfg_weight=cfg_weight
            )
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            logger.warning("Continuing without TTS audio")

    logger.info(
        f"Processing completed. Generated {len(all_entries)} vocabulary entries from {len(unique_nouns)} unique nouns."
    )
    return all_entries


def generate_tts_audio(
    entries: List[Dict[str, Any]],
    audio_prompt_path: str = "Korean-sample1.wav",
    cfg_weight: float = 0.3,
) -> None:
    """
    Generate TTS audio for all entries.

    Args:
        entries: List of vocabulary entries
        audio_prompt_path: Path to audio prompt file for voice cloning
        cfg_weight: Classifier-free guidance weight (0.0-1.0)
    """
    try:
        from src.tts_generator import TTSGenerator

        logger.info("Starting TTS audio generation...")
        logger.info(f"Audio prompt: {audio_prompt_path}")
        logger.info(f"CFG weight: {cfg_weight}")

        tts = TTSGenerator(
            output_dir="output/audio",
            audio_prompt_path=audio_prompt_path,
            cfg_weight=cfg_weight,
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

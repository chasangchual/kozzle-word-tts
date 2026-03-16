import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger


def write_json_output(
    entries: List[Dict[str, Any]], output_path: str = "output/result.json"
) -> str:
    """
    Write vocabulary entries to JSON file.

    Args:
        entries: List of vocabulary entries with id, word, and sentences
        output_path: Path to output JSON file

    Returns:
        Path to created JSON file
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Write JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON output written to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to write JSON output: {e}")
        raise

from kiwipiepy import Kiwi
from typing import List
from loguru import logger

kiwi = Kiwi()


def extract_nouns(text: str) -> List[str]:
    """
    Extract Korean nouns from text using Kiwi NLP library.
    Only includes nouns with length >= 2 characters.

    Args:
        text: Input Korean text

    Returns:
        List of unique nouns extracted from the text (length >= 2)

    Example:
        >>> extract_nouns("나는 학교에 갔다. 친구와 점심을 먹었다.")
        ['학교', '친구', '점심']
    """
    if not text or not text.strip():
        return []

    try:
        tokens = kiwi.tokenize(text)
        nouns = []

        for token in tokens:
            if token.tag.startswith("N"):
                # Extract alphanumeric characters and strip whitespace
                noun = "".join([char for char in token.form if char.isalnum()]).strip()
                # Only include nouns with length >= 2
                if noun and len(noun) >= 2 and noun not in nouns:
                    nouns.append(noun)

        logger.info(f"Extracted {len(nouns)} nouns (length >= 2): {nouns}")
        return nouns

    except Exception as e:
        logger.error(f"Error extracting nouns from text: {e}")
        raise Exception(f"Failed to extract nouns: {e}")

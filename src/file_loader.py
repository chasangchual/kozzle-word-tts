import os
from pathlib import Path
from typing import List
from loguru import logger

def load_files(input_path: str) -> List[Path]:
    """
    Load all text files from a given path (file or directory).
    
    Args:
        input_path: Path to a file or directory
        
    Returns:
        List of Path objects pointing to text files
    """
    path = Path(input_path)
    
    # Check if path exists
    if not path.exists():
        raise ValueError(f"Path does not exist: {input_path}")
    
    # If it's a file, return it in a list
    if path.is_file():
        return [path]
    
    # If it's a directory, find all text files recursively
    text_files = []
    for file_path in path.rglob("*.txt"):
        if file_path.is_file():
            text_files.append(file_path)
    
    logger.info(f"Discovered {len(text_files)} text files in {input_path}")
    return text_files

def read_file_content(file_path: Path) -> str:
    """
    Read content from a text file with UTF-8 encoding.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if not content.strip():
            logger.warning(f"File {file_path} is empty")
            
        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise Exception(f"Failed to read file {file_path}: {e}")
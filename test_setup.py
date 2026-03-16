import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from file_loader import load_files, read_file_content
from noun_extractor import extract_nouns
from loguru import logger

# Test basic functionality
if __name__ == "__main__":
    # Create a test file
    test_file = "sample_korean.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("나는 학교에 갔다. 친구와 점심을 먹었다.")
    
    # Test file loading
    files = load_files(test_file)
    print(f"Loaded {len(files)} files")
    
    # Test file reading
    content = read_file_content(files[0])
    print(f"File content: {content}")
    
    # Test noun extraction
    nouns = extract_nouns(content)
    print(f"Extracted nouns: {nouns}")
    
    print("Basic tests completed successfully!")
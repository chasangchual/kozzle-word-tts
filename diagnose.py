#!/usr/bin/env python
"""Diagnostic script to check for single-character nouns"""

from src.noun_extractor import extract_nouns
from src.file_loader import load_files, read_file_content
import sys

if len(sys.argv) < 2:
    print("Usage: python diagnose.py <input_path>")
    sys.exit(1)

input_path = sys.argv[1]
files = load_files(input_path)

print(f"Analyzing: {input_path}")
print(f"Found {len(files)} file(s)")
print("=" * 70)

all_nouns = []
for file_path in files:
    content = read_file_content(file_path)
    nouns = extract_nouns(content)
    
    print(f"\nFile: {file_path}")
    print(f"Content: {content[:100]}")
    print(f"Nouns: {nouns}")
    print(f"Lengths: {[(n, len(n)) for n in nouns]}")
    
    # Check for length-1 nouns
    single_char = [n for n in nouns if len(n) == 1]
    if single_char:
        print(f"⚠️  FOUND LENGTH-1 NOUNS: {single_char}")
    
    all_nouns.extend(nouns)

print("\n" + "=" * 70)
print("SUMMARY:")
print(f"Total nouns: {len(all_nouns)}")
print(f"Unique nouns: {len(set(all_nouns))}")

lengths = [len(n) for n in all_nouns]
print(f"Length distribution: {dict((l, lengths.count(l)) for l in set(lengths))}")

single_char_all = [n for n in all_nouns if len(n) == 1]
if single_char_all:
    print(f"\n⚠️  SINGLE-CHARACTER NOUNS FOUND: {set(single_char_all)}")
else:
    print(f"\n✅ No single-character nouns found")

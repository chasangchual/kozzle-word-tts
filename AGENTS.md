# AGENT.md

## Project Overview

This project is a Python 3.11 CLI application for generating Korean
vocabulary learning content from Korean text files.

The application must:

1.  Accept a file or directory path
2.  Read Korean sentences from files
3.  Extract nouns
4.  Generate 3 Korean example sentences for each noun using an LLM
5.  Save results to JSON
6.  Generate TTS audio using Chatterbox TTS

Dependency management must use uv.

LLM access must be provider‑agnostic using LangChain so the application
can switch between:

-   Ollama (default)
-   OpenAI
-   Anthropic

------------------------------------------------------------------------

# Runtime Requirements

- Python version
  - Python 3.11
- Dependency manager
  - uv
- Default LLM
  - Ollama model exaone3.5:7.8b
- TTS engine
  - chatter_box_tts
  - https://github.com/resemble-ai/chatterbox
  - follow installation instruncctions in README.md

------------------------------------------------------------------------

# CLI Interface

- parameters
  - file or directory path
  - --llm-provider 
  - --model 

```
python main.py ./input --llm-provider ollama --model exaone3.5:7.8b
python main.py ./input --llm-provider openai --model gpt-4.1-mini python
main.py ./input --llm-provider anthropic --model claude-sonnet
```

------------------------------------------------------------------------

# File Processing

## Input may be:
- File → process that file.
- Directory → recursively process all text files.
- Files are assumed to contain UTF‑8 encoded Korean sentences.

------------------------------------------------------------------------

# Korean NLP

## extract nouns from the input file
- suggest NLP library to extract nouns

## Example

- Input
```
나는 학교에 갔다. 친구와 점심을 먹었다.
```

- Extracted nouns
```
학교 친구 점심
```

## generate korean 3 sentenses 
- use LLM to generate 3 sentenses

------------------------------------------------------------------------

# Exact LangChain Dependencies

The following packages must appear in pyproject.toml

langchain\>=0.2 langchain-core\>=0.2 langchain-community\>=0.2
langchain-ollama\>=0.1 langchain-openai\>=0.1 langchain-anthropic\>=0.1
pydantic\>=2.0 kiwipiepy loguru chatter_box_tts typer python-dotenv
diskcache

Do not invent package names.

------------------------------------------------------------------------

# Strict Coding Rules (Anti-Hallucination)

The coding agent must follow these rules

1.  Only import libraries listed in pyproject.toml
2.  Do not invent APIs
3.  Do not invent LangChain classes
4.  Use documented LangChain interfaces
5.  All imports must resolve
6.  Prefer simple code over complex abstractions
7.  Keep modules small and focused
8.  Application must run with

uv run python main.py

------------------------------------------------------------------------

# Deterministic Prompt Templates

Use LangChain ChatPromptTemplate with fixed formatting.

Example

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template( """ You are generating Korean
example sentences for vocabulary learning.

Noun: {word}

Requirements: - Produce exactly 3 Korean sentences - Each sentence must
naturally include the noun - Sentences must be easy to understand - No
numbering - No explanations

Return JSON:

{{ "word": "{word}", "sentences":
\["sentence1","sentence2","sentence3"\] }} """ )

Prompt format must not change dynamically.

------------------------------------------------------------------------

# Structured Output using Pydantic

All LLM responses must be validated.

Schema

from pydantic import BaseModel from typing import List

class SentenceOutput(BaseModel): word: str sentences: List\[str\]

Validation rules

-   word must be non empty
-   sentences must contain exactly 3 items

------------------------------------------------------------------------

# PydanticOutputParser Wiring

Use LangChain parser

from langchain.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=SentenceOutput)

The parser must run after the LLM call to enforce schema validation.

------------------------------------------------------------------------

# JSON Output

Final output format

\[ { "id": "`<uuid>`{=html}", "word": "`<noun>`{=html}", "sentence": \[
"`<sentence1>`{=html}", "`<sentence2>`{=html}", "`<sentence3>`{=html}"
\] }\]

Rules

-   id must be uuid4
-   sentence list must contain exactly 3 elements

Output file

output/result.json

If multiple files are processed results must be consolidated.

------------------------------------------------------------------------

# TTS Generation

After JSON generation complete generate audio.

Use

Chatterbox TTS

Repository

https://github.com/resemble-ai/chatterbox

Parameters

language_id="ko" audio_prompt_path="Korean-sample1.wav" cfg_weight=0.3

Each sentence must produce one audio file.

------------------------------------------------------------------------

# Audio Output Layout

output/audio/ `<word>`{=html}/ sentence1.wav sentence2.wav sentence3.wav

------------------------------------------------------------------------

# Project Structure

project-root │ ├─ AGENT.md ├─ README.md ├─ pyproject.toml ├─ main.py │
├─ src/ │ ├─ cli.py │ ├─ config.py │ ├─ pipeline.py │ ├─ file_loader.py
│ ├─ noun_extractor.py │ ├─ json_writer.py │ ├─ tts_generator.py │ └─
llm/ │ ├─ provider.py │ ├─ sentence_chain.py │ └─ schemas.py │ ├─
output/ │ ├─ result.json │ └─ audio/ │ └─ samples/ └─ sample.txt

------------------------------------------------------------------------

# Error Handling

The system must handle

-   invalid path
-   unreadable files
-   empty files
-   LLM failure
-   malformed LLM output
-   TTS failure

Failures must not terminate the pipeline.

------------------------------------------------------------------------

# Logging

Use loguru.

Log events

-   files discovered
-   nouns extracted
-   sentence generation started
-   JSON written
-   TTS generated
-   errors

------------------------------------------------------------------------

# Performance

Implement

-   noun deduplication
-   LLM result caching
-   efficient directory scanning

Concurrency can be added later.

------------------------------------------------------------------------

# Testing

Tests should cover

-   file vs directory input
-   UTF‑8 reading
-   noun extraction
-   JSON schema validation
-   provider factory
-   structured LLM parsing
-   TTS output paths

LLM and TTS must be mocked.

------------------------------------------------------------------------

# README Requirements

README must include

-   project overview
-   prerequisites
-   Ollama installation
-   uv setup
-   CLI usage
-   switching LLM providers
-   environment variables
-   sample output
-   troubleshooting

------------------------------------------------------------------------

# Deliverables

The generated project must include

-   runnable CLI app
-   pyproject.toml configured for uv
-   LangChain provider abstraction
-   Ollama default integration
-   optional OpenAI and Anthropic providers
-   noun extraction module
-   structured output validation with Pydantic
-   RunnableSequence pipeline
-   LangChain caching
-   retry strategy for LLM parsing
-   JSON output
-   Chatterbox TTS integration
-   tests
-   README


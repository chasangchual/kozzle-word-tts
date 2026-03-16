# Korean Vocabulary Learning Tool (kozzle-word-tts)

A Python CLI application for generating Korean vocabulary learning content from Korean text files using LLM and TTS.

## Overview

This tool processes Korean text files to create vocabulary learning materials:

1. **Extracts nouns** from Korean text using kiwipiepy (Korean NLP library)
2. **Generates 3 example sentences** for each noun using LLM (Ollama, OpenAI, or Anthropic)
3. **Creates audio files** for word pronunciation using TTS (Google TTS or Chatterbox)
4. **Outputs structured JSON** with UUIDs, words, and sentences

**Example Output:**
```
Input: "나는 학교에 갔다. 친구와 점심을 먹었다."

Output:
- Word: 학교 (school)
  - Sentences:
    1. 오늘 아침 학교에서 친구들을 만났어요.
    2. 학교 도서관은 조용하고 공부하기 좋아요.
    3. 그녀는 학교를 졸업하고 곧 여행을 떠날 예정이에요.
  - Audio: output/audio/학교/ (word.wav + 3 sentence wav files)
```

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **OS**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB recommended for LLM)
- **Storage**: ~2GB for dependencies + output files

### Required Software

1. **uv package manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Ollama** (for local LLM inference)
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull Korean language model (~8GB)
   ollama pull exaone3.5:7.8b
   
   # Start Ollama server
   ollama serve
   ```

   Or use API providers:
   - **OpenAI**: Set `OPENAI_API_KEY` environment variable
   - **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable

3. **Git** (for cloning repository)
   ```bash
   # Linux
   sudo apt install git
   
   # macOS (comes with Xcode)
   xcode-select --install
   ```

### Optional for TTS
- **PyTorch** (~2GB) - Required only for Chatterbox TTS
- **Audio samples** - Korean voice samples for Chatterbox (already included)

## How to Start

### Quick Start (5 minutes)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kozzle-word-tts
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure Ollama URL** (if different from default)
   
   Create `.env` file:
   ```bash
   echo "OLLAMA_BASE_URL=http://192.168.1.194:11434" > .env
   ```

4. **Run the tool**
   ```bash
   # Basic usage
   uv run python main.py ./sample_korean.txt
   
   # With custom Ollama model
   uv run python main.py ./sample_korean.txt --model exaone3.5:7.8b
   
   # Skip TTS (faster if you don't need audio)
   uv run python main.py ./sample_korean.txt --no-tts
   ```

### Advanced Usage

```bash
# Process entire directory
uv run python main.py ./input/

# Use OpenAI instead of Ollama
export OPENAI_API_KEY=your_api_key
uv run python main.py ./input --llm-provider openai --model gpt-4

# Use Anthropic Claude
export ANTHROPIC_API_KEY=your_api_key
uv run python main.py ./input --llm-provider anthropic --model claude-sonnet

# Custom Ollama server
OLLAMA_BASE_URL=http://192.168.1.194:11434 \
  uv run python main.py ./input
```

### What Happens During Execution

1. **File Processing**: Reads Korean text files (UTF-8)
2. **Noun Extraction**: Uses kiwipiepy to extract nouns
   - Input: "나는 학교에 갔다. 친구와 점심을 먹었다."
   - Output: ['나', '학교', '친구', '점심']
3. **Sentence Generation**: LLM creates 3 sentences per noun
4. **JSON Output**: Saves to `output/result.json`
5. **TTS Audio Generation**: Creates WAV files in `output/audio/`

### Output Structure

```
output/
├── result.json              # Structured vocabulary data
└── audio/                   # Generated audio files
    ├── 학교/
    │   ├── word.wav        # Word pronunciation
    │   ├── sentence1.wav   # Sentence 1 audio
    │   ├── sentence2.wav   # Sentence 2 audio
    │   └── sentence3.wav   # Sentence 3 audio
    ├── 친구/
    └── 점심/
```

## How to Build

### Development Setup

1. **Clone and install development dependencies**
   ```bash
   git clone <repository-url>
   cd kozzle-word-tts
   uv sync --all-extras
   ```

2. **Install pre-commit hooks** (optional)
   ```bash
   # Create virtual environment
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate      # Windows
   ```

3. **Run tests**
   ```bash
   uv run pytest tests/ -v
   
   # With coverage
   uv run pytest tests/ --cov=src
   ```

4. **Lint and format code**
   ```bash
   # Format code
   uv run black src/ tests/
   
   # Sort imports
   uv run isort src/ tests/
   
   # Lint
   uv run ruff check src/ tests/
   ```

### Building the Package

```bash
# Build distribution
uv build

# Output in dist/
# - kozzle_word_tts-0.1.0-py3-none-any.whl
# - kozzle-word-tts-0.1.0.tar.gz
```

### Installing as Package

```bash
# Install in another project
uv pip install kozzle-word-tts

# Use as library
from src.pipeline import process_korean_text
result = process_korean_text(input_path, config)
```

### Project Architecture

```
kozzle-word-tts/
├── main.py                    # CLI entry point
├── pyproject.toml             # Project configuration & dependencies
├── src/
│   ├── cli.py                # Command-line argument parsing
│   ├── config.py             # Configuration management
│   ├── pipeline.py           # Main processing pipeline
│   ├── file_loader.py        # File I/O (UTF-8 Korean text)
│   ├── noun_extractor.py     # Korean noun extraction (kiwipiepy)
│   ├── json_writer.py         # JSON output writer
│   ├── tts_generator.py      # Text-to-speech (gTTS/Chatterbox)
│   └── llm/
│       ├── provider.py       # LLM provider factory (Ollama/OpenAI/Anthropic)
│       ├── sentence_chain.py # Sentence generation chain
│       └── schemas.py         # Pydantic validation schemas
├── tests/                    # Unit tests
├── output/                   # Generated output
│   ├── result.json
│   └── audio/
├── Korean-sample1.wav       # Voice cloning sample
├── Korean-sample2.wav       # Voice cloning sample
└── sample_korean.txt        # Sample input file
```

### Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| langchain | ≥0.2 | LLM abstraction |
| langchain-ollama | ≥0.1 | Ollama integration |
| langchain-openai | ≥0.1 | OpenAI integration |
| langchain-anthropic | ≥0.1 | Anthropic integration |
| kiwipiepy | * | Korean NLP |
| pydantic | ≥2.0 | Data validation |
| loguru | * | Logging |
| typer | * | CLI framework |
| gtts | * | Text-to-speech |
| diskcache | * | LLM caching |

### Configuration

Create `.env` file for environment variables:

```bash
# Ollama configuration
OLLAMA_BASE_URL=http://192.168.1.194:11434

# OpenAI (if using)
OPENAI_API_KEY=sk-...

# Anthropic (if using)
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Custom model
DEFAULT_MODEL=exaone3.5:7.8b
DEFAULT_PROVIDER=ollama
```

## Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
```bash
# Install dependencies
uv sync
```

**"Connection refused" to Ollama**
```bash
# Check if Ollama is running
ollama serve

# Or set custom URL
OLLAMA_BASE_URL=http://192.168.1.194:11434 uv run python main.py ./input
```

**"No audio generated"**
```bash
# TTS requires gTTS (auto-installed) or Chatterbox
# For Chatterbox (higher quality):
uv pip install torch
pip install chatter-box-tts
```

**"Korean text not displaying correctly"**
- Ensure files are UTF-8 encoded
- Use sample_korean.txt as reference

**"Model not found"**
```bash
# Pull the Korean model
ollama pull exaone3.5:7.8b

# List installed models
ollama list
```

### Performance Tips

1. **Use `--no-tts` for faster processing** (skips audio generation)
2. **Run Ollama on GPU** for 10x faster inference
3. **Use caching** - LLM results are cached by default
4. **Batch processing** - Pass directory path instead of single file

## Examples

### Example 1: Basic Usage
```bash
cat > my_korean_text.txt << 'EOF'
나는 학교에 갔다. 친구와 점심을 먹었다.
EOF

uv run python main.py my_korean_text.txt
```

### Example 2: Production Use
```bash
# Process directory with all Korean text files
uv run python main.py ./korean_documents/ --model exaone3.5:7.8b

# Use remote Ollama server
OLLAMA_BASE_URL=http://192.168.1.194:11434 \
  uv run python main.py ./input --model exaone3.5:7.8b
```

### Example 3: Programmatic Use
```python
from src.pipeline import process_korean_text
from src.config import Config

config = Config(llm_provider="ollama", model="exaone3.5:7.8b")
result = process_korean_text("./input", config)

for entry in result:
    print(f"Word: {entry['word']}")
    print(f"Sentences: {entry['sentences']}")
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Support

- **Issues**: Open a GitHub issue
- **Email**: [your-email@example.com]
- **Documentation**: See AGENTS.md for detailed architecture

## Acknowledgments

- **kiwipiepy** - Korean NLP library
- **LangChain** - LLM abstraction layer
- **gTTS/Chatterbox** - Text-to-speech engines
- **Exaone** - Korean language model by LG AI Research
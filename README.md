# Korean Vocabulary Learning Tool (kozzle-word-tts)

A Python 3.11 CLI application for generating Korean vocabulary learning content from Korean text files using LLM and TTS.

## Overview

This tool processes Korean text files to create vocabulary learning materials:

1. **Extracts nouns** (≥2 characters) from Korean text using kiwipiepy (Korean NLP library)
2. **Generates 3 example sentences** for each noun using LLM (Ollama, OpenAI, or Anthropic)
3. **Creates audio files** for word pronunciation using TTS (Google TTS or Chatterbox)
4. **Outputs structured JSON** with UUIDs, words, and sentences

**Example Output:**
```
Input: "나는 학교에 갔다. 친구와 점심을 먹었다."

Extracted Nouns: ['학교', '친구', '점심']
(Single-character nouns like '나' are filtered out)

Output:
- Word: 학교 (school)
  - Sentences:
    1. 오늘 아침 학교에서 친구들을 만났어요.
    2. 학교 도서관은 조용하고 공부하기 좋아요.
    3. 그녀는 학교를 졸업하고 곧 여행을 떠날 예정이에요.
  - Audio: output/audio/학교/ (word.wav + 3 sentence wav files)
```

## Key Features

- **Smart Noun Filtering**: Only extracts nouns with 2+ characters for quality vocabulary learning
- **Whitespace Trimming**: Automatic cleanup of leading/trailing spaces in extracted nouns
- **Duplicate Removal**: Cross-file deduplication to avoid redundant LLM calls
- **Multi-Provider LLM Support**: Switch between Ollama (local), OpenAI, or Anthropic
- **Configurable TTS**: Customize voice samples and generation parameters
- **Audio-Only Mode**: Generate audio from existing JSON without LLM calls
- **Batch Processing**: Process single files or entire directories recursively
- **Error Resilience**: Continues processing even if individual items fail
- **Structured Output**: JSON format with UUID tracking and validation
- **Comprehensive Logging**: Track all operations with loguru

## Prerequisites

### System Requirements
- **Python**: 3.11 (strict requirement, specified in pyproject.toml)
- **OS**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB recommended for LLM)
- **Storage**: ~2GB for dependencies + ~8GB for Ollama model

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
- **ChatterBox TTS**: Requires PyTorch (~2GB)
- **Qwen3-TTS** (Apple Silicon only): Uses MLX framework, requires model download (~3GB)
- **Both engines**: Install both to compare TTS output quality side-by-side
- **Audio samples** - Korean voice samples for voice cloning (already included)

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
   # Basic usage (full pipeline)
   uv run python main.py ./sample_korean.txt
   
   # With custom Ollama model
   uv run python main.py ./sample_korean.txt --model exaone3.5:7.8b
   
   # Skip TTS (faster if you don't need audio)
   uv run python main.py ./sample_korean.txt --no-tts
   
   # Generate audio from existing JSON
   uv run python generate_audio.py output/result.json
   ```

### Advanced Usage

#### **LLM Provider Options**
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

#### **TTS Configuration Options**
```bash
# Select TTS engine: chatterbox (default), qwen3, or both
uv run python main.py ./input.txt --tts-engine chatterbox
uv run python main.py ./input.txt --tts-engine qwen3
uv run python main.py ./input.txt --tts-engine both  # Compare outputs

# Use different voice sample
uv run python main.py ./input.txt \
  --audio-prompt Korean-sample2.wav

# Adjust CFG weight for voice matching (0.0-1.0)
uv run python main.py ./input.txt \
  --cfg-weight 0.5

# Combine LLM and TTS settings
uv run python main.py ./input.txt \
  --llm-provider ollama \
  --model exaone3.5:7.8b \
  --tts-engine both \
  --audio-prompt Korean-sample2.wav \
  --cfg-weight 0.7
```

#### **Audio-Only Generation**
```bash
# Generate audio from existing JSON (no LLM calls)
uv run python generate_audio.py output/result.json

# Generate with both TTS engines for comparison
uv run python generate_audio.py output/result.json --tts-engine both

# Generate with specific engine
uv run python generate_audio.py output/result.json --tts-engine qwen3

# With custom voice sample
uv run python generate_audio.py output/result.json \
  --audio-prompt Korean-sample2.wav

# With custom CFG weight
uv run python generate_audio.py output/result.json \
  --cfg-weight 0.5

# Both parameters with engine selection
uv run python generate_audio.py output/result.json \
  --tts-engine both \
  --audio-prompt Korean-sample2.wav \
  --cfg-weight 0.7

# Via main.py
uv run python main.py --generate-audio-from-json output/result.json \
  --tts-engine both \
  --audio-prompt Korean-sample2.wav \
  --cfg-weight 0.5
```

## CLI Options Reference

### main.py

**Full pipeline processing:**
```bash
uv run python main.py <input_path> [OPTIONS]
```

**Options:**
- `--llm-provider <provider>` - LLM provider: ollama, openai, anthropic (default: ollama)
- `--model <model>` - Model name (default: exaone3.5:7.8b)
- `--no-tts` - Skip TTS audio generation
- `--tts-engine <engine>` - TTS engine: chatterbox, qwen3, or both (default: chatterbox)
- `--audio-prompt <path>` - Audio prompt file for voice cloning (default: Korean-sample1.wav)
- `--cfg-weight <value>` - CFG weight 0.0-1.0 (default: 0.3)
- `--generate-audio-from-json <path>` - Generate audio from existing JSON
- `--qwen3-model-path <path>` - Path to Qwen3-TTS model (default: models/Qwen3-TTS-12Hz-1.7B-Base-8bit)

### generate_audio.py

**Audio generation from JSON:**
```bash
uv run python generate_audio.py <json_path> [OPTIONS]
```

**Options:**
- `--tts-engine <engine>` - TTS engine: chatterbox, qwen3, or both (default: chatterbox)
- `--audio-prompt <path>` - Audio prompt file (default: Korean-sample1.wav)
- `--cfg-weight <value>` - CFG weight 0.0-1.0 (default: 0.3)
- `--qwen3-model-path <path>` - Path to Qwen3-TTS model (default: models/Qwen3-TTS-12Hz-1.7B-Base-8bit)

### TTS Parameters Explained

#### **--tts-engine**
- Select which TTS engine(s) to use for audio generation
- **chatterbox** (default): Use ChatterBox TTS only
- **qwen3**: Use Qwen3-TTS only (Apple Silicon)
- **both**: Generate audio with both engines for comparison
- When `both` is selected, output is organized in separate folders:
  ```
  output/audio/
  ├── chatterbox/<word>/   # ChatterBox TTS output
  └── qwen3/<word>/        # Qwen3-TTS output
  ```

#### **--audio-prompt**
- Path to Korean voice sample WAV file
- Used for voice cloning with both ChatterBox and Qwen3-TTS
- Included samples: `Korean-sample1.wav`, `Korean-sample2.wav`
- You can use your own: record 5-10 seconds of Korean speech

#### **--cfg-weight (Classifier-Free Guidance)**
- Range: 0.0 to 1.0
- Controls how closely TTS matches the prompt voice
- **0.0-0.2**: Very natural, more variation
- **0.3-0.5**: Balanced (recommended)
- **0.6-0.8**: Strict voice matching
- **0.9-1.0**: Maximum control (may sound robotic)
- Used by ChatterBox TTS (ignored by Qwen3-TTS)

## Common Workflows

### Workflow 1: Full Pipeline
```bash
# Process text with everything
uv run python main.py ./input.txt
```

### Workflow 2: Fast Processing + Audio Later
```bash
# Step 1: Process text without audio (faster)
uv run python main.py ./input.txt --no-tts

# Step 2: Generate audio later
uv run python generate_audio.py output/result.json
```

### Workflow 3: Compare TTS Engines
```bash
# Step 1: Get vocabulary JSON quickly
uv run python main.py ./input.txt --no-tts

# Step 2: Generate audio with both engines for comparison
uv run python generate_audio.py output/result.json --tts-engine both

# Step 3: Compare output in:
#   - output/audio/chatterbox/<word>/
#   - output/audio/qwen3/<word>/

# Step 4: Choose your preferred engine for future use
uv run python generate_audio.py output/result.json --tts-engine qwen3
```

### Workflow 4: Experiment with TTS Settings
```bash
# Step 1: Get vocabulary JSON quickly
uv run python main.py ./input.txt --no-tts

# Step 2: Try different voice samples
uv run python generate_audio.py output/result.json --audio-prompt Korean-sample1.wav
uv run python generate_audio.py output/result.json --audio-prompt Korean-sample2.wav

# Step 3: Try different CFG weights
uv run python generate_audio.py output/result.json --cfg-weight 0.1
uv run python generate_audio.py output/result.json --cfg-weight 0.5
uv run python generate_audio.py output/result.json --cfg-weight 0.9

# Step 4: Choose best settings and regenerate
uv run python generate_audio.py output/result.json \
  --audio-prompt Korean-sample2.wav \
  --cfg-weight 0.5
```

### Workflow 5: Manual JSON Editing
```bash
# Step 1: Process with no TTS
uv run python main.py ./input.txt --no-tts

# Step 2: Manually edit output/result.json
# (fix sentences, add custom vocabulary, etc.)

# Step 3: Generate audio from edited JSON
uv run python generate_audio.py output/result.json
```

### Workflow 6: Batch Directory Processing
```bash
# Process all .txt files in directory with deduplication
uv run python main.py ./korean_documents/

# Results automatically deduplicated across all files
```

### What Happens During Execution

1. **File Discovery**: Scans input path (file or directory with recursive .txt search)
2. **UTF-8 File Reading**: Loads Korean text files with proper encoding
3. **Noun Extraction**: Uses kiwipiepy morphological analyzer to extract nouns
   - Input: "나는 학교에 갔다. 친구와 점심을 먹었다."
   - Raw nouns: ['나', '학교', '친구', '점심']
   - **Whitespace trimmed**: Leading/trailing spaces removed
   - **Filtered output (≥2 chars)**: ['학교', '친구', '점심']
4. **Deduplication**: Removes duplicate nouns across all files (saves LLM calls)
5. **Sentence Generation**: LLM creates exactly 3 Korean sentences per noun
   - Uses LangChain with structured Pydantic validation
   - Retry logic (3 attempts) for robustness
   - JSON response parsing with error handling
6. **JSON Output**: Saves to `output/result.json` with UUIDs
7. **TTS Audio Generation**: Creates WAV files in `output/audio/<word>/`
   - word.wav (noun pronunciation)
   - sentence1.wav, sentence2.wav, sentence3.wav
   - Configurable voice sample and CFG weight

### Output Structure

**Single TTS engine (default):**
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

**Both TTS engines (`--tts-engine both`):**
```
output/
├── result.json              # Structured vocabulary data
└── audio/                   # Generated audio files
    ├── chatterbox/          # ChatterBox TTS output
    │   ├── 학교/
    │   │   ├── word.wav
    │   │   ├── sentence1.wav
    │   │   ├── sentence2.wav
    │   │   └── sentence3.wav
    │   └── 친구/
    └── qwen3/               # Qwen3-TTS output
        ├── 학교/
        │   ├── word.wav
        │   ├── sentence1.wav
        │   ├── sentence2.wav
        │   └── sentence3.wav
        └── 친구/
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
├── main.py                    # CLI entry point with full pipeline
├── generate_audio.py          # Standalone audio generation script
├── pyproject.toml             # uv project configuration & dependencies
├── .env                       # Environment variables (Ollama URL, API keys)
├── uv.lock                    # Locked dependencies
├── AGENTS.md                  # Project specifications and requirements
├── src/
│   ├── config.py             # Configuration management
│   ├── pipeline.py           # Main processing orchestration
│   ├── file_loader.py        # File/directory I/O (UTF-8 Korean text)
│   ├── noun_extractor.py     # Korean noun extraction with kiwipiepy
│   ├── json_writer.py        # JSON output writer
│   ├── tts_generator.py      # Text-to-speech (gTTS/Chatterbox)
│   └── llm/
│       ├── provider.py       # LLM provider factory
│       ├── sentence_chain.py # Sentence generation with retry logic
│       └── schemas.py        # Pydantic validation schemas
├── output/                   # Generated output (created on first run)
│   ├── result.json          # Vocabulary entries with UUIDs
│   └── audio/               # TTS audio files organized by word
│       └── <word>/
│           ├── word.wav
│           ├── sentence1.wav
│           ├── sentence2.wav
│           └── sentence3.wav
├── Korean-sample1.wav       # Default Korean voice sample
├── Korean-sample2.wav       # Alternative Korean voice sample
└── sample_korean.txt        # Sample input file
```

**Total Code**: ~690 lines of Python

**Pipeline Flow**:
```
Input → load_files() → extract_nouns() [filter ≥2 chars] → 
deduplicate → generate_sentences() [LLM] → write_json_output() → 
generate_tts_audio() → Output
```

### Key Dependencies

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| **Python** | 3.11 | Runtime (strict) | ✅ Required |
| **langchain** | ≥0.2 | LLM abstraction framework | ✅ Active |
| **langchain-ollama** | ≥0.1 | Ollama integration | ✅ Active |
| **langchain-openai** | ≥0.1 | OpenAI integration | ✅ Active |
| **langchain-anthropic** | ≥0.1 | Anthropic integration | ✅ Active |
| **kiwipiepy** | ≥0.22 | Korean morphological analyzer | ✅ Active |
| **pydantic** | ≥2.0 | Data validation & schemas | ✅ Active |
| **loguru** | ≥0.7 | Structured logging | ✅ Active |
| **mlx-audio** | git | Qwen3-TTS (Apple Silicon) | ✅ Optional |
| **python-dotenv** | ≥1.0 | Environment variable loading | ✅ Active |
| **diskcache** | ≥5.6 | LLM result caching | ⚠️ Imported but not yet implemented |

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

## TTS Engine Setup

The application supports two TTS engines that can be used individually or together for comparison:
1. **ChatterBox TTS** - Cross-platform, requires PyTorch
2. **Qwen3-TTS** - Apple Silicon only, uses MLX framework

**Engine Selection:**
```bash
--tts-engine chatterbox  # Use ChatterBox only (default)
--tts-engine qwen3       # Use Qwen3-TTS only
--tts-engine both        # Generate with both engines for comparison
```

### Option 1: ChatterBox TTS (Cross-platform)

ChatterBox TTS provides high-quality Korean voice cloning using PyTorch.

```bash
# Install PyTorch and ChatterBox
uv pip install torch
pip install chatter-box-tts
```

### Option 2: Qwen3-TTS (Apple Silicon Only - Recommended for Mac)

Qwen3-TTS uses MLX framework optimized for Apple Silicon (M1/M2/M3/M4). It runs 100% locally with excellent performance on Mac.

#### Quick Start (5 minutes)

```bash
# Step 1: Install system dependency
brew install ffmpeg

# Step 2: Install MLX dependencies
uv pip install -e ".[qwen3-tts]"

# Step 3: Create models directory
mkdir -p models

# Step 4: Download the model (~3GB)
pip install huggingface_hub
huggingface-cli download mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
  --local-dir models/Qwen3-TTS-12Hz-1.7B-Base-8bit

# Step 5: Run!
uv run python main.py ./input.txt
```

#### Prerequisites

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10+
- ffmpeg (`brew install ffmpeg`)
- ~6GB RAM for 1.7B model, ~3GB for 0.6B model

#### Manual Installation

If you prefer to install dependencies manually:

```bash
# Install MLX framework
pip install mlx>=0.30

# Install mlx-audio from GitHub
pip install git+https://github.com/Blaizzy/mlx-audio.git
```

#### Model Download Options

**Option A: Using HuggingFace CLI (Recommended)**
```bash
# Install huggingface-cli if needed
pip install huggingface_hub

# Download the 1.7B model (best quality)
huggingface-cli download mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
  --local-dir models/Qwen3-TTS-12Hz-1.7B-Base-8bit

# Or download the 0.6B model (faster, less RAM)
huggingface-cli download mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit \
  --local-dir models/Qwen3-TTS-12Hz-0.6B-Base-8bit
```

**Option B: Manual Download from HuggingFace**

1. Visit [Qwen3-TTS-12Hz-1.7B-Base-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit)
2. Click "Download" to get the model files
3. Place the downloaded folder in your project:

```
models/
└── Qwen3-TTS-12Hz-1.7B-Base-8bit/
    ├── config.json
    ├── model.safetensors
    ├── tokenizer.json
    └── ...
```

#### Available Qwen3-TTS Models

| Model | Download Size | Quality | RAM Usage | Speed |
|-------|---------------|---------|-----------|-------|
| [Qwen3-TTS-12Hz-1.7B-Base-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit) | ~3GB | Best | ~6GB | Normal |
| [Qwen3-TTS-12Hz-0.6B-Base-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit) | ~1GB | Good | ~3GB | Faster |

#### Usage with Custom Model Path

```bash
# Use default path (models/Qwen3-TTS-12Hz-1.7B-Base-8bit)
uv run python main.py ./input.txt

# Use custom model path
uv run python main.py ./input.txt \
  --qwen3-model-path /path/to/your/model

# Use the smaller 0.6B model
uv run python main.py ./input.txt \
  --qwen3-model-path models/Qwen3-TTS-12Hz-0.6B-Base-8bit
```

#### Voice Cloning with Qwen3-TTS

Qwen3-TTS supports voice cloning using a reference audio file:

```bash
# Use your own Korean voice sample for cloning
uv run python main.py ./input.txt \
  --audio-prompt my_korean_voice.wav
```

For best results:
- Use a clean 5-10 second Korean audio clip
- WAV format recommended (auto-converts other formats via ffmpeg)
- Clear speech without background noise

### TTS Engine Behavior

**When `--tts-engine chatterbox` (default):**
- Uses ChatterBox TTS only
- Fails with error if ChatterBox is not available

**When `--tts-engine qwen3`:**
- Uses Qwen3-TTS only
- Fails with error if Qwen3-TTS is not available

**When `--tts-engine both`:**
- Tries to initialize both engines
- Generates audio with all available engines
- If only one engine is available, continues with that engine (logs a warning)
- Fails only if neither engine is available
- Output is organized in separate folders (`chatterbox/` and `qwen3/`)

**Note**: gTTS (Google TTS) has been removed. You must install either ChatterBox or Qwen3-TTS.

---

## Logging

### Log File Locations

All logs are stored in the `logs/` directory:

```
logs/
├── app.log      # All log levels (DEBUG, INFO, WARNING, ERROR)
└── errors.log   # Errors only (for quick troubleshooting)
```

### Log Rotation

- **Rotation Size**: 10MB per file
- **Retention**: Last 5 rotated files are kept
- **Encoding**: UTF-8 (supports Korean text)

Example rotated files:
```
logs/
├── app.log              # Current log file
├── app.log.1            # Previous rotation
├── app.log.2            # Older rotation
├── errors.log           # Current error log
└── errors.log.1         # Previous error rotation
```

### Log Format

```
2026-03-20 14:30:45.123 | INFO     | src.tts_generator:generate_audio:125 | Generating audio for: 학교에서 친구들을 만났어요...
```

Format breakdown:
- `2026-03-20 14:30:45.123` - Timestamp with milliseconds
- `INFO` - Log level (DEBUG, INFO, WARNING, ERROR)
- `src.tts_generator:generate_audio:125` - Module:Function:Line number
- Message text

### Full Stack Traces

All exceptions are logged with:
- Complete stack trace
- Variable values at each frame (for debugging)
- Exception type and message

Example error log:
```
2026-03-20 14:30:45.123 | ERROR    | src.tts_generator:_generate_with_qwen3:185 | Qwen3-TTS generation failed for '학교에서...'
Traceback (most recent call last):
  File "src/tts_generator.py", line 180, in _generate_with_qwen3
    generate_audio(model=self.qwen3_model, text=text, ...)
    │              │                       └ '학교에서 친구들을 만났어요.'
    │              └ <mlx_audio.tts.model.Qwen3TTS object>
    └ <function generate_audio at 0x...>
...
```

### Viewing Logs

```bash
# View recent logs
tail -f logs/app.log

# View only errors
cat logs/errors.log

# Search for specific word
grep "학교" logs/app.log

# View with less (scrollable)
less logs/app.log
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

**"No audio generated"** or **"No TTS engine available"**
```bash
# Option 1: Install ChatterBox TTS (cross-platform)
uv pip install torch
pip install chatter-box-tts

# Option 2: Install Qwen3-TTS (Apple Silicon only)
uv pip install -e ".[qwen3-tts]"
# Then download model to models/Qwen3-TTS-12Hz-1.7B-Base-8bit/
```

**"Qwen3-TTS model not found"**
```bash
# Download the model
huggingface-cli download mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
  --local-dir models/Qwen3-TTS-12Hz-1.7B-Base-8bit

# Or specify custom path
uv run python main.py ./input.txt --qwen3-model-path /path/to/model
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
3. **Batch processing** - Pass directory path instead of single file for deduplication
4. **Noun filtering** - Only processes nouns with ≥2 characters to reduce LLM calls

### Performance Characteristics

- **Noun Extraction**: ~0.5s per file (kiwipiepy with Kiwi model loading)
- **LLM Generation**: ~2-5s per noun (depends on model and hardware)
- **TTS Generation**: ~1-2s per audio file (gTTS) or ~3-5s (Chatterbox)
- **Noun Filtering**: Reduces processing by ~30-40% (filters single-character nouns)

## Examples

### Example 1: Basic Usage
```bash
# Create sample file
cat > my_korean_text.txt << 'EOF'
나는 학교에 갔다. 친구와 점심을 먹었다.
EOF

# Process with full pipeline
uv run python main.py my_korean_text.txt
```

### Example 2: Audio Experimentation
```bash
# Step 1: Process without audio (fast)
uv run python main.py ./input.txt --no-tts

# Step 2: Try different voice samples
uv run python generate_audio.py output/result.json --audio-prompt Korean-sample1.wav
uv run python generate_audio.py output/result.json --audio-prompt Korean-sample2.wav

# Step 3: Try different CFG weights
uv run python generate_audio.py output/result.json --cfg-weight 0.3
uv run python generate_audio.py output/result.json --cfg-weight 0.7

# Step 4: Combine best settings
uv run python generate_audio.py output/result.json \
  --audio-prompt Korean-sample2.wav \
  --cfg-weight 0.5
```

### Example 3: Production Use
```bash
# Process directory with all Korean text files
uv run python main.py ./korean_documents/ --model exaone3.5:7.8b

# Use remote Ollama server
OLLAMA_BASE_URL=http://192.168.1.194:11434 \
  uv run python main.py ./input --model exaone3.5:7.8b

# With custom TTS settings
uv run python main.py ./input \
  --audio-prompt Korean-sample2.wav \
  --cfg-weight 0.5
```

### Example 4: Manual JSON Editing
```bash
# Process and save JSON only
uv run python main.py ./input.txt --no-tts

# Edit output/result.json manually
# (fix sentences, add custom entries, etc.)

# Generate audio from edited JSON
uv run python generate_audio.py output/result.json
```

### Example 5: Programmatic Use
```python
from src.pipeline import process_korean_text, generate_tts_audio
from src.config import Config

# Process text
config = Config(llm_provider="ollama", model="exaone3.5:7.8b")
result = process_korean_text(
    "./input",
    config,
    generate_tts=False,  # Skip TTS in pipeline
    audio_prompt_path="Korean-sample1.wav",
    cfg_weight=0.3
)

# Generate audio separately with custom settings
generate_tts_audio(
    result,
    audio_prompt_path="Korean-sample2.wav",
    cfg_weight=0.5
)

for entry in result:
    print(f"Word: {entry['word']}")
    print(f"Sentences: {entry['sentences']}")
```

## Technical Implementation Details

### Noun Extraction Algorithm (src/noun_extractor.py)

The noun extractor uses **kiwipiepy**, a Python binding for Kiwi (Korean Intelligent Word Identifier):

1. Tokenizes Korean text into morphemes
2. Filters tokens with N-prefix tags (NNG, NNP, NNB, etc.)
3. Strips non-alphanumeric characters
4. **Applies length filter**: Only keeps nouns with ≥2 characters
5. Deduplicates within the same file

**Example**:
```python
from src.noun_extractor import extract_nouns

text = "나는 학교에 갔다. 친구와 점심을 먹었다."
nouns = extract_nouns(text)
# Result: ['학교', '친구', '점심']
# Filtered out: '나' (single character)
```

### LLM Integration (src/llm/)

**Provider Factory Pattern** (src/llm/provider.py:9-30):
```python
# Automatically selects LLM based on config
llm = get_llm(Config(llm_provider="ollama", model="exaone3.5:7.8b"))
```

**Structured Output with Pydantic** (src/llm/schemas.py):
```python
class SentenceOutput(BaseModel):
    word: str
    sentences: List[str] = Field(min_length=3, max_length=3)
```

**Retry Logic** (src/llm/sentence_chain.py:34-105):
- 3 attempts per noun
- Handles JSON parsing errors
- Strips markdown code blocks from LLM responses
- Falls back to empty sentences on total failure

### TTS Implementation (src/tts_generator.py)

**Dual Engine Support with Selection**:
1. **ChatterBox TTS** - High quality voice cloning, requires PyTorch
2. **Qwen3-TTS** (Apple Silicon) - Local MLX-based TTS with voice cloning

**TTS Engine Selection** (`--tts-engine`):
- `chatterbox` (default): Uses ChatterBox TTS only, fails if unavailable
- `qwen3`: Uses Qwen3-TTS only, fails if unavailable
- `both`: Uses both engines, generates audio in separate folders for comparison

**Audio Organization (single engine)**:
```
output/audio/
└── <word>/
    ├── word.wav          # Noun pronunciation
    ├── sentence1.wav     # Example sentence 1
    ├── sentence2.wav     # Example sentence 2
    └── sentence3.wav     # Example sentence 3
```

**Audio Organization (`--tts-engine both`)**:
```
output/audio/
├── chatterbox/
│   └── <word>/
│       ├── word.wav
│       ├── sentence1.wav
│       ├── sentence2.wav
│       └── sentence3.wav
└── qwen3/
    └── <word>/
        ├── word.wav
        ├── sentence1.wav
        ├── sentence2.wav
        └── sentence3.wav
```

### Error Handling Strategy

The application uses **graceful degradation**:

- ❌ **File read error** → Skip file, log error, continue with next
- ❌ **Noun extraction error** → Log error, return empty list
- ❌ **LLM generation failure** → Create entry with empty sentences
- ❌ **TTS generation failure** → Log warning, continue without audio
- ❌ **JSON write failure** → Raise exception (critical)

This ensures the pipeline continues even when individual components fail.

## Recent Changes

### v0.1.0 (Latest - 2026-03-18)

**Feature 1: TTS Configuration Parameters**
- Added `--audio-prompt` parameter to specify voice sample file
- Added `--cfg-weight` parameter to control voice matching (0.0-1.0)
- Allows experimentation with different voice characteristics
- Works with both full pipeline and audio-only generation

**Files Modified**: 
- `src/tts_generator.py` - Added cfg_weight parameter
- `src/pipeline.py` - Pass parameters through pipeline
- `main.py` - CLI argument parsing
- `generate_audio.py` - CLI argument parsing

**Usage**:
```bash
uv run python generate_audio.py output/result.json \
  --audio-prompt Korean-sample2.wav \
  --cfg-weight 0.5
```

---

**Feature 2: Audio-Only Generation**
- New `generate_audio.py` script for generating audio from existing JSON
- Regenerate audio without LLM calls
- Useful for testing TTS settings, recovering from failures, or editing JSON

**Usage**:
```bash
# Generate audio from existing JSON
uv run python generate_audio.py output/result.json

# Or via main.py
uv run python main.py --generate-audio-from-json output/result.json
```

**Benefits**:
- No LLM API calls required
- Fast iteration on audio quality
- Test different voice samples and settings
- Edit JSON manually then generate audio

---

**Feature 3: Cross-File Deduplication**
- Automatic deduplication of nouns across multiple files
- Reduces redundant LLM calls by 30-40%
- Logs deduplication statistics

**Example**:
- File 1: ['학교', '친구', '점심']
- File 2: ['학교', '공부', '도서관']
- Result: ['학교', '친구', '점심', '공부', '도서관'] (duplicates removed)

---

**Feature 4: Whitespace Trimming**
- Automatic trimming of leading/trailing spaces in extracted nouns
- Ensures accurate length filtering
- Prevents whitespace-related bugs

**Files Modified**: 
- `src/noun_extractor.py:33` - Added `.strip()`
- `src/pipeline.py:56-59` - Strip during deduplication

---

**Feature 5: Noun Length Filtering** (2026-03-16)
- Minimum length requirement (≥2 characters) for noun extraction
- Filters out single-character Korean nouns (나, 집, 꽃, etc.)
- Improves vocabulary quality by focusing on substantial words
- Reduces LLM API calls by ~25-30%

**File Modified**: `src/noun_extractor.py:34`

**Impact**:
- Input: "나는 학교에 갔다. 친구와 점심을 먹었다."
- Before: `['나', '학교', '친구', '점심']` (4 nouns)
- After: `['학교', '친구', '점심']` (3 nouns, 25% reduction)

## Project Status

### ✅ Implemented Features
- [x] CLI interface with comprehensive argument parsing
- [x] Multi-file/directory processing with recursive scanning
- [x] Korean noun extraction with kiwipiepy
- [x] Noun length filtering (≥2 characters)
- [x] Whitespace trimming for extracted nouns
- [x] Cross-file deduplication (saves 30-40% LLM calls)
- [x] LLM provider abstraction (Ollama, OpenAI, Anthropic)
- [x] Structured output with Pydantic validation
- [x] LangChain integration for sentence generation
- [x] Retry logic for LLM failures
- [x] JSON output with UUID generation
- [x] TTS audio generation (gTTS + Chatterbox fallback)
- [x] Configurable TTS parameters (audio prompt, CFG weight)
- [x] Audio-only generation from existing JSON
- [x] Comprehensive error handling
- [x] Structured logging with loguru
- [x] UTF-8 file handling
- [x] Environment variable configuration

### ⚠️ Known Limitations
- [ ] **No automated tests** - Test framework configured but no test files
- [ ] **LLM caching not implemented** - diskcache imported but unused
- [ ] **Basic CLI parsing** - Uses sys.argv instead of typer
- [ ] **No progress indicators** - Silent processing for large batches
- [ ] **No concurrent processing** - Sequential LLM calls

### 🚀 Future Enhancements
- Add comprehensive unit tests
- Implement LLM result caching with diskcache
- Add progress bars for batch processing
- Support concurrent LLM calls for better performance
- Add configurable noun length threshold
- Support custom noun filtering rules
- Add output format options (CSV, XLSX)

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
- **ChatterBox/Qwen3-TTS** - Text-to-speech engines
- **Exaone** - Korean language model by LG AI Research
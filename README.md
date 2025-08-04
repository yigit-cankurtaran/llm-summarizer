# Log Summary Tool

A privacy-focused local tool that processes your personal notes, messages, and tasks to create compressed bullet-point summaries. Designed with BYOK/BYOM (Bring Your Own Key/Model) functionality for complete data privacy.

## Features

- **Text File Processing**: Scans `.md` and `.txt` files for user content
- **Book Processing**: Extracts and summarizes content from PDF and EPUB files
- **Flexible Date Filtering**: Process files by date range (last week, specific months, years, or custom ranges)
- **AI-Powered Summaries**: Generate intelligent bullet-point summaries using your choice of AI provider
- **Multiple AI Providers**: Support for OpenAI, Ollama (local), and custom API endpoints
- **Privacy First**: All processing can be done locally with no external API calls required
- **Configurable Output**: Choose number of bullet points and output format

## Supported File Types

### Text Files
- `.md` (Markdown files)
- `.txt` (Text files)

### Books
- `.pdf` (PDF documents)
- `.epub` (EPUB e-books)
- `.mobi`, `.azw`, `.azw3` (planned support)

## Installation

### Prerequisites
- Python 3.13.5 or higher

### Basic Installation
```bash
git clone <repository-url>
cd log-summary
pip install -r requirements.txt
```

### Optional Dependencies

For **OpenAI API** support:
```bash
pip install openai
export OPENAI_API_KEY="your-api-key-here"
```

For **Ollama** local models:
```bash
# Install Ollama from https://ollama.ai
pip install ollama
# Pull a model (e.g., llama3.2)
ollama pull llama3.2
```

For **PDF processing**:
```bash
pip install PyMuPDF
```

For **EPUB processing**:
```bash
pip install ebooklib beautifulsoup4
```

## Usage

### Basic Examples

```bash
# Summarize text files from current directory (last week, 5 bullets)
python log_summary.py

# Summarize a specific PDF file
python log_summary.py /path/to/file.pdf --book

# Summarize all text files in a directory
python log_summary.py /path/to/logs

# Summarize files from May 2025
python log_summary.py --timeframe 2025-05

# Generate 10 bullet points instead of default 5
python log_summary.py --bullets 10

# Save output to a file
python log_summary.py --output summary.md
```

### Content Types

```bash
# Process text files (.txt, .md) - default behavior
python log_summary.py --text

# Process book files (.pdf, .epub)
python log_summary.py --book

# Process books from specific directory
python log_summary.py /path/to/books --book
```

### AI Provider Options

```bash
# Use OpenAI (requires API key)
python log_summary.py --ai-provider openai

# Use Ollama local models
python log_summary.py --ai-provider ollama

# Use specific Ollama model
python log_summary.py --ai-provider ollama --ollama-model llama3.3

# Use custom API endpoint
python log_summary.py --custom-api-url http://localhost:8000/v1/chat/completions

# No AI - basic text extraction only
python log_summary.py --no-ai
```

### Date/Time Filtering

The tool supports various date formats in filenames:

```bash
# Files from specific month
python log_summary.py --timeframe 2025-05

# Files from specific year
python log_summary.py --timeframe 2025

# Files from specific date
python log_summary.py --timeframe 2025-05-15

# Default: last 7 days (no timeframe specified)
python log_summary.py
```

### Supported Date Formats in Filenames
- `YYYY-MM-DD` (ISO format)
- `DD-MM-YYYY`  
- `DD/MM/YYYY`
- `YYYY_MM_DD`
- Other common formats

## Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export CUSTOM_API_KEY="your-custom-api-key"  # For custom endpoints
```

### AI Provider Priority

When using `--ai-provider auto` (default), the tool tries providers in this order:
1. OpenAI (if API key is available)
2. Ollama (if service is running)
3. Basic text extraction (fallback)

## Output Format

The tool generates summaries with the following structure:

```markdown
# Log Summary

**Generated:** 2025-01-15 14:30:22
**Timeframe:** 2025-05
**Files processed:** 3
**Files:** daily_log_2025-05-01.md, meeting_notes_2025-05-02.txt, project_notes_2025-05-03.md

## Summary (5 key points)

• Key insight or task from your files
• Important meeting outcome or decision
• Project milestone or progress update
• Personal note or reflection
• Action item or next step
```

## Privacy and Security

- **Local Processing**: Can run entirely offline with Ollama
- **BYOK/BYOM**: Bring your own API keys and models
- **No Data Retention**: Your files are only processed locally
- **Open Source**: Full transparency of data handling

## Troubleshooting

### No AI services available
If you see "No AI services available. Using basic summarization":
- Install required dependencies: `pip install openai ollama requests`
- Set up API keys or start Ollama service
- Use `--no-ai` flag for basic text extraction

### Date parsing issues
If files aren't being found:
- Ensure filenames contain recognizable date patterns
- Check that files are in supported formats (.md, .txt for text mode)
- Use absolute paths for directories outside current location

### Book processing issues
For PDF/EPUB processing:
- Install book processing dependencies
- Ensure files are not password-protected or corrupted

## Contributing

This project is designed for personal use and privacy. Feel free to fork and modify for your specific needs.

## License

[Add your license information here]

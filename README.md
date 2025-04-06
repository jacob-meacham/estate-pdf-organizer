# Estate PDF Organizer

A tool for organizing estate documents using LLMs to detect document boundaries and classify them.

## Features

- Detects document boundaries within PDFs using LLMs
- Classifies documents into categories based on a configurable taxonomy
- Organizes documents into category-specific directories
- Supports dry-run mode for previewing changes
- Handles multiple documents within a single PDF

## Installation

1. Install [uv](https://github.com/astral-sh/uv) if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone this repository and install dependencies:
   ```bash
   git clone https://github.com/yourusername/estate-pdf-organizer.git
   cd estate-pdf-organizer
   uv venv
   uv pip install -e .
   ```

3. Install Tesseract OCR:
   - On macOS: `brew install tesseract`
   - On Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - On Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki

## Usage

1. Create a taxonomy file (YAML) defining your document types and their characteristics.
2. Run the organizer:
   ```bash
   estate-pdf-organizer input_dir output_dir --taxonomy taxonomy.yaml
   ```

### Command Line Options

- `input_dir`: Directory containing input PDFs
- `output_dir`: Directory to store organized documents
- `--taxonomy`: Path to YAML file containing document taxonomy
- `--openai-api-key`: OpenAI API key (or use OPENAI_API_KEY environment variable)
- `--overwrite`: Overwrite existing files in output directory
- `--dry-run`: Show what would be done without making changes
- `--window-size`: Number of pages to consider for document boundary detection (default: 5)

### Taxonomy File

The taxonomy file defines the list of document categories. Example:

```yaml
categories:
  - Will
  - Trust
  - Deed
  - Power of Attorney
  - Financial Statement
  - Tax Return
  - Insurance Policy
  - Other
```

The LLM will automatically classify documents based on their content, so no additional keywords or descriptions are needed.

### Example

```bash
# Set OpenAI API key
export OPENAI_API_KEY=your-api-key

# Run the organizer
estate-pdf-organizer ./input_pdfs ./organized taxonomy.yaml --dry-run
```

## Development

### Setup

1. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Running Tests and Linting

The project uses `uv` for dependency management. Here are the commands for development:

1. Run tests:
   ```bash
   pytest
   ```

2. Run linting:
   ```bash
   ruff check .
   ```

### Project Structure

- `src/estate_pdf_organizer/`: Main package code
  - `classifier.py`: Document classification using LLMs
  - `organizer.py`: Document organization and file management
  - `processor.py`: PDF processing and text extraction
  - `cli.py`: Command line interface
- `tests/`: Test files
- `pyproject.toml`: Project configuration and dependencies

## License

MIT License 
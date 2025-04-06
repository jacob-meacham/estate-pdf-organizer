# Estate PDF Organizer

A tool for organizing estate documents using LLMs to detect document boundaries and classify them.

## Features

- Detects document boundaries within PDFs using LLMs
- Classifies documents into categories based on a configurable taxonomy
- Organizes documents into category-specific directories
- Supports dry-run mode for previewing changes
- Handles multiple documents within a single PDF

## Installation

First, install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the package:
```bash
uv pip install estate-pdf-organizer
```

## Usage

### Command Line Interface

The tool provides a command-line interface for processing PDFs:

```bash
estate-pdf-organizer input_directory output_directory taxonomy.yaml [options]
```

#### Required Arguments:
- `input_directory`: Directory containing input PDFs
- `output_directory`: Directory to store organized documents
- `taxonomy.yaml`: Path to YAML file containing document taxonomy

#### Options:
- `--openai-api-key`: OpenAI API key. If not provided, will use OPENAI_API_KEY environment variable.
- `--dry-run`: Show what would be done without making changes
- `--window-size`: Number of pages to analyze at once (default: 3)

### Taxonomy File

The taxonomy file defines the list of document categories. Example:

```yaml
- Will
- Trust
- Power of Attorney
- Deed
- Financial Statement
- Tax Return
- Insurance Policy
- Unorganized
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

1. Clone the repository
2. Install `uv` if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   cd estate-pdf-organizer
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[test,lint]"
   ```

### Running Tests

```bash
pytest
```

### Running the Linter

```bash
ruff check .
```

To automatically fix linting issues:
```bash
ruff check --fix .
```

## License

MIT 
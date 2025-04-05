# Estate PDF Organizer

A tool for processing and organizing estate documents using LLMs. This tool helps estate executors manage large collections of scanned documents by automatically classifying and organizing them based on their content.

## Features

- Process multiple PDFs containing scanned documents
- Automatic document boundary detection
- LLM-powered document classification
- Dry-run mode for previewing changes
- Detailed logging and metadata tracking
- YAML-based configuration and taxonomy

## Installation

```bash
pip install -e .
```

## Usage

1. Create a taxonomy file (e.g., `taxonomy.yaml`):
```yaml
categories:
  - Important Documents
  - Financial
  - Property
  - Unorganized
```

2. Process documents:
```bash
# Dry run to preview changes
estate-pdf-organizer process --input-dir ./scanned_docs --taxonomy ./taxonomy.yaml --dry-run

# Process documents for real
estate-pdf-organizer process --input-dir ./scanned_docs --taxonomy ./taxonomy.yaml --output-dir ./organized_docs
```

## Configuration

Configuration can be provided via command line arguments or a config file. See `estate-pdf-organizer --help` for details.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Project Structure

```
estate_pdf_organizer/
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── config.py           # Configuration management
│   ├── pdf_processor.py    # PDF handling
│   ├── classifier.py       # Document classification
│   ├── organizer.py        # File organization
│   └── utils.py            # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_pdf_processor.py
│   ├── test_classifier.py
│   └── test_organizer.py
├── pyproject.toml
└── README.md
``` 
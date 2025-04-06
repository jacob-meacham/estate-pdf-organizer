"""Command line interface for the Estate PDF Organizer."""

import argparse
import os
from pathlib import Path

from .classifier import LLMClassifier
from .processor import EstatePDFProcessor


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Organize estate documents by classifying them."
    )
    
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing input PDFs"
    )
    
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory to store organized documents"
    )
    
    parser.add_argument(
        "--taxonomy",
        type=Path,
        required=True,
        help="Path to YAML file containing document taxonomy"
    )
    
    parser.add_argument(
        "--openai-api-key",
        type=str,
        help="OpenAI API key. If not provided, will use OPENAI_API_KEY environment variable."
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in output directory"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    parser.add_argument(
        "--window-size",
        type=int,
        default=5,
        help="Number of pages to consider for document boundary detection (default: 5)"
    )
    
    parser.add_argument(
        "--keep-blank-pages",
        action="store_true",
        help="Keep blank pages in the PDFs (default: remove blank pages)"
    )
    
    args = parser.parse_args()
    
    # Get OpenAI API key from argument or environment variable
    api_key = args.openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key must be provided either via --openai-api-key argument "
            "or OPENAI_API_KEY environment variable"
        )
    
    # Create output directory if it doesn't exist
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the processor
    classifier = LLMClassifier(args.taxonomy, api_key=api_key)
    processor = EstatePDFProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        classifier=classifier,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        window_size=args.window_size,
        remove_blank_pages=not args.keep_blank_pages
    )
    
    # Process the PDFs
    processor.process_directory()

if __name__ == "__main__":
    main() 
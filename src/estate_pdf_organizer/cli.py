"""Command-line interface for the Estate PDF Organizer."""

import click
from pathlib import Path
from typing import Optional
from loguru import logger

@click.group()
def cli():
    """Estate PDF Organizer - Process and organize estate documents using LLMs."""
    pass

@cli.command()
@click.argument('input-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('taxonomy', type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
              help='Directory to store organized documents')
@click.option('--dry-run', is_flag=True, help='Preview changes without making them')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files in output directory')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help='Logging level')
def process(input_dir: Path, taxonomy: Path, output_dir: Optional[Path], 
           dry_run: bool, overwrite: bool, log_level: str):
    """Process and organize PDF documents from INPUT_DIR using the taxonomy in TAXONOMY."""
    # Configure logging
    logger.remove()
    logger.add(lambda msg: click.echo(msg), level=log_level)
    
    try:
        # Set default output directory if not provided
        if output_dir is None:
            output_dir = input_dir / "organized"
            logger.info(f"Using default output directory: {output_dir}")
            
        # Process documents
        logger.info(f"Processing documents from {input_dir}")
        logger.info(f"Using taxonomy from {taxonomy}")
        if dry_run:
            logger.info("Running in dry-run mode")
        if overwrite:
            logger.warning("Overwrite mode enabled - existing files will be overwritten")
            
        # TODO: Implement actual processing logic
        logger.info("Processing complete")
        
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli() 
"""File organization module for the Estate PDF Organizer."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from pypdf import PdfReader, PdfWriter


@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    source_pdf: str
    start_page: int
    end_page: int
    document_type: str
    filename: str
    confidence: float
    output_path: str | None = None

class DocumentOrganizer:
    """Organizes documents into categories."""
    
    def __init__(self, output_dir: Path, overwrite: bool = False):
        """Initialize the document organizer.
        
        Args:
            output_dir: Directory to store organized documents
            overwrite: Whether to overwrite existing files
        """
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.metadata = []
        self.unprocessed_pages = {}  # Track unprocessed pages by source PDF
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Unorganized directory
        (self.output_dir / "Unorganized").mkdir(exist_ok=True)
    
    def add_document(self, metadata: DocumentMetadata) -> None:
        """Add a document to be organized.
        
        Args:
            metadata: Document metadata
        """
        self.metadata.append(metadata)
    
    def add_unprocessed_pages(self, source_pdf: str, pages: list[int]) -> None:
        """Add unprocessed pages to the metadata.
        
        Args:
            source_pdf: Path to the source PDF
            pages: List of unprocessed page numbers
        """
        self.unprocessed_pages[source_pdf] = pages
    
    def organize_document(
        self,
        pdf_reader: PdfReader,
        source_pdf_path: str,
        start_page: int,
        end_page: int,
        document_type: str,
        dry_run: bool = False,
        suggested_filename: str | None = None,
    ) -> DocumentMetadata:
        """Organize a single document by extracting specified page range.
        
        Args:
            pdf_reader: Already opened PDF reader instance
            source_pdf_path: Path to the source PDF file (for metadata)
            start_page: First page to extract (1-based)
            end_page: Last page to extract (1-based)
            document_type: Type of document (e.g., "will", "trust", "deed")
            dry_run: If True, only return metadata without creating files
            suggested_filename: Optional filename suggested by the classifier
            
        Returns:
            DocumentMetadata object for the extracted document
            
        Raises:
            ValueError: If page range is invalid or output file exists
        """
        # Validate page range
        total_pages = len(pdf_reader.pages)
        if start_page < 1:
            raise ValueError("Start page must be at least 1")
        if end_page > total_pages:
            raise ValueError(f"End page {end_page} exceeds total pages ({total_pages})")
        if start_page > end_page:
            raise ValueError(f"Start page {start_page} is greater than end page {end_page}")
        
        # Create output filename
        if suggested_filename:
            output_filename = suggested_filename
        else:
            base = os.path.splitext(os.path.basename(source_pdf_path))[0]
            output_filename = f"{base}_pages_{start_page}-{end_page}.pdf"
        
        # Create output path in the appropriate category directory
        category_dir = self.output_dir / document_type
        category_dir.mkdir(exist_ok=True)
        output_path = category_dir / output_filename
        
        # Check for existing output file
        if not dry_run and not self.overwrite and output_path.exists():
            raise ValueError(
                f"Output file already exists: {output_path}. "
                "Use --overwrite to allow overwriting existing files."
            )
        
        # Create output PDF
        pdf_writer = PdfWriter()
        
        # Add pages to the new PDF (0-based indexing)
        for page_num in range(start_page - 1, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        # Save the new PDF if not in dry run mode
        if not dry_run:
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
        
        # Create metadata
        doc_metadata = DocumentMetadata(
            source_pdf=source_pdf_path,
            start_page=start_page,
            end_page=end_page,
            document_type=document_type,
            filename=output_filename,
            confidence=1.0,
            output_path=str(output_path)
        )
        
        # Add to internal tracking
        self.metadata.append(doc_metadata)
        
        return doc_metadata
    
    def save_metadata(self, output_path: Path) -> None:
        """Save metadata to a YAML file.
        
        Args:
            output_path: Path to save metadata file
        """
        metadata = {
            "documents": [
                {
                    "source_pdf": doc.source_pdf,
                    "start_page": doc.start_page,
                    "end_page": doc.end_page,
                    "document_type": doc.document_type,
                    "filename": doc.filename,
                    "confidence": doc.confidence,
                    "output_path": doc.output_path
                }
                for doc in self.metadata
            ],
            "unprocessed_pages": {
                source_pdf: pages
                for source_pdf, pages in self.unprocessed_pages.items()
            }
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(metadata, f, default_flow_style=False) 
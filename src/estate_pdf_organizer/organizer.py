"""File organization module for the Estate PDF Organizer."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import yaml
from pypdf import PdfReader, PdfWriter
import os

@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    original_pdf: str
    start_page: int
    end_page: int
    category: str
    filename: str
    confidence: float
    output_path: Optional[str] = None

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
    
    def organize_document(
        self,
        source_pdf: str,
        page_ranges: List[Tuple[int, int]],
        document_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        dry_run: bool = False,
    ) -> List[DocumentMetadata]:
        """Organize a PDF document by extracting specified page ranges.
        
        Args:
            source_pdf: Path to the source PDF file
            page_ranges: List of (start_page, end_page) tuples (1-based)
            document_type: Type of document (e.g., "will", "trust", "deed")
            metadata: Optional metadata to include with the document
            dry_run: If True, only return metadata without creating files
            
        Returns:
            List of DocumentMetadata objects for each extracted document
            
        Raises:
            ValueError: If page ranges are invalid or output files exist
            RuntimeError: If there's an error processing the PDF
        """
        if not os.path.exists(source_pdf):
            raise ValueError(f"Source PDF file not found: {source_pdf}")
            
        # Validate all page ranges first
        with open(source_pdf, 'rb') as f:
            pdf_reader = PdfReader(f)
            total_pages = len(pdf_reader.pages)
            
            for start_page, end_page in page_ranges:
                if start_page < 1:
                    raise ValueError("Start page must be at least 1")
                if end_page > total_pages:
                    raise ValueError(f"End page {end_page} exceeds total pages ({total_pages})")
                if start_page > end_page:
                    raise ValueError(f"Start page {start_page} is greater than end page {end_page}")
        
        # Check for existing output files
        if not dry_run and not self.overwrite:
            for start_page, end_page in page_ranges:
                output_path = os.path.join(
                    self.output_dir,
                    f"{os.path.splitext(os.path.basename(source_pdf))[0]}_pages_{start_page}-{end_page}.pdf"
                )
                if os.path.exists(output_path):
                    raise ValueError(
                        f"Output file already exists: {output_path}. "
                        "Use --overwrite to allow overwriting existing files."
                    )
        
        # Read the PDF once
        with open(source_pdf, 'rb') as f:
            pdf_reader = PdfReader(f)
            results = []
            
            for start_page, end_page in page_ranges:
                # Create output PDF
                pdf_writer = PdfWriter()
                
                # Add pages to the new PDF (0-based indexing)
                for page_num in range(start_page - 1, end_page):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # Create output filename
                output_filename = f"{os.path.splitext(os.path.basename(source_pdf))[0]}_pages_{start_page}-{end_page}.pdf"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Save the new PDF if not in dry run mode
                if not dry_run:
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                
                # Create metadata
                doc_metadata = DocumentMetadata(
                    original_pdf=source_pdf,
                    start_page=start_page,
                    end_page=end_page,
                    category=document_type,
                    filename=output_filename,
                    confidence=1.0,
                    output_path=output_path
                )
                results.append(doc_metadata)
                
                # Add to internal tracking
                self.metadata.append(doc_metadata)
        
        return results
    
    def save_metadata(self, output_path: Optional[Path] = None) -> None:
        """Save document metadata to YAML file.
        
        Args:
            output_path: Path to save metadata to. If None, saves to metadata.yaml
                in output directory.
        """
        if output_path is None:
            output_path = self.output_dir / "metadata.yaml"
            
        metadata_dict = {
            "documents": [
                {
                    "original_pdf": doc.original_pdf,
                    "start_page": doc.start_page,
                    "end_page": doc.end_page,
                    "category": doc.category,
                    "filename": doc.filename,
                    "confidence": doc.confidence,
                    "output_path": doc.output_path
                }
                for doc in self.metadata
            ]
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(metadata_dict, f) 
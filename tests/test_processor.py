"""Tests for the PDF processor module."""

import tempfile
from pathlib import Path

import yaml

from estate_pdf_organizer.classifier import ClassificationResult
from estate_pdf_organizer.processor import EstatePDFProcessor


class MockClassifier:
    """Mock classifier for testing."""
    
    def __init__(self, taxonomy_path: Path):
        """Initialize the mock classifier.
        
        Args:
            taxonomy_path: Path to taxonomy file (not used in mock)
        """
        self._boundaries = [3, 5, 7]  # Default boundary pages
    
    @property
    def boundaries(self):
        return self._boundaries
    
    @boundaries.setter
    def boundaries(self, value):
        self._boundaries = value
    
    def classify(self, text: str) -> [ClassificationResult]:
        """Mock classification that returns boundaries at specific pages."""
        # Extract the current page number from the text
        # The text format is "[PAGE N]\n..." for each page
        current_page = int(text.split('\n')[0].split(' ')[1].strip(']'))
        
        # If we're at a boundary page, return a document
        if current_page in self._boundaries:
            # Find the next boundary or end of window
            next_boundary = min([b for b in self._boundaries if b > current_page], default=current_page + 1)
            return [ClassificationResult(
                document_type="Will",
                confidence=0.95,
                page_start=current_page,
                page_end=next_boundary - 1,
                suggested_filename=f"will_{current_page}.pdf"
            )]
        else:
            # For non-boundary pages, return a single page document
            return [ClassificationResult(
                document_type="Will",
                confidence=0.95,
                page_start=current_page,
                page_end=current_page,
                suggested_filename=f"will_{current_page}.pdf"
            )]

def create_test_taxonomy(taxonomy_path: Path) -> None:
    """Create a test taxonomy file.
    
    Args:
        taxonomy_path: Path to create taxonomy file at
    """
    taxonomy = {
        "categories": [
            "Will",
            "Trust",
            "Deed",
            "Power of Attorney",
            "Financial Statement",
            "Tax Return",
            "Insurance Policy",
            "Other"
        ]
    }
    
    with open(taxonomy_path, 'w') as f:
        yaml.dump(taxonomy, f)

def create_test_pdf(pdf_path: Path, num_pages: int) -> None:
    """Create a test PDF file with the specified number of pages.
    
    Args:
        pdf_path: Path to create PDF file at
        num_pages: Number of pages to create
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    for i in range(num_pages):
        c.drawString(100, height - 100, f"Test Page {i + 1}")
        c.showPage()
    
    c.save()

def test_process_pdf():
    """Test processing a single PDF file."""
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir, \
         tempfile.TemporaryDirectory() as taxonomy_dir:
        
        # Create a test taxonomy file
        taxonomy_path = Path(taxonomy_dir) / "taxonomy.yaml"
        create_test_taxonomy(taxonomy_path)
        
        # Create a test PDF with 10 pages
        pdf_path = Path(input_dir) / "test.pdf"
        create_test_pdf(pdf_path, num_pages=10)
        
        # Create a mock classifier
        mock_classifier = MockClassifier(taxonomy_path)
        
        # Test dry run mode
        processor = EstatePDFProcessor(
            input_dir=Path(input_dir),
            output_dir=Path(output_dir),
            classifier=mock_classifier,
            overwrite=True,
            dry_run=True,
            window_size=3
        )
        
        processor.process_pdf(pdf_path)
        
        # Verify that no files were created in dry run mode
        assert len(list(Path(output_dir).glob("**/*.pdf"))) == 0

def test_process_directory():
    """Test processing a directory of PDFs."""
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir, \
         tempfile.TemporaryDirectory() as taxonomy_dir:
        
        # Create a test taxonomy file
        taxonomy_path = Path(taxonomy_dir) / "taxonomy.yaml"
        create_test_taxonomy(taxonomy_path)
        
        # Create two test PDFs
        for i in range(2):
            pdf_path = Path(input_dir) / f"test_{i}.pdf"
            create_test_pdf(pdf_path, num_pages=10)
        
        # Create a mock classifier
        mock_classifier = MockClassifier(taxonomy_path)
        
        # Test dry run mode
        processor = EstatePDFProcessor(
            input_dir=Path(input_dir),
            output_dir=Path(output_dir),
            classifier=mock_classifier,
            overwrite=True,
            dry_run=True,
            window_size=3
        )
        
        processor.process_directory()
        
        # Verify that no files were created in dry run mode
        assert len(list(Path(output_dir).glob("**/*.pdf"))) == 0

def test_multiple_documents_per_window():
    """Test handling multiple documents within a single window."""
    with tempfile.TemporaryDirectory() as input_dir, \
         tempfile.TemporaryDirectory() as output_dir, \
         tempfile.TemporaryDirectory() as taxonomy_dir:
        
        # Create a test taxonomy file
        taxonomy_path = Path(taxonomy_dir) / "taxonomy.yaml"
        create_test_taxonomy(taxonomy_path)
        
        # Create a test PDF with 10 pages
        pdf_path = Path(input_dir) / "test.pdf"
        create_test_pdf(pdf_path, num_pages=10)
        
        # Create a mock classifier that returns boundaries at pages 3, 5, and 7
        mock_classifier = MockClassifier(taxonomy_path)
        mock_classifier.boundaries = [3, 5, 7]
        
        processor = EstatePDFProcessor(
            input_dir=Path(input_dir),
            output_dir=Path(output_dir),
            classifier=mock_classifier,
            overwrite=True,
            dry_run=False,
            window_size=3
        )
        
        processor.process_pdf(pdf_path)
        
        # Verify that the correct number of documents were created
        will_files = list(Path(output_dir).glob("Will/*.pdf"))
        unorganized_files = list(Path(output_dir).glob("Unorganized/*.pdf"))
        assert len(will_files) == 3  # Documents ending at pages 3, 5, and 7
        assert len(unorganized_files) == 1  # Remaining pages 8-10 
"""Tests for the organizer module."""

from pathlib import Path
import tempfile
import yaml
from pypdf import PdfWriter, PdfReader
import pdfplumber
import pytest
from estate_pdf_organizer.organizer import DocumentOrganizer, DocumentMetadata

def test_document_metadata():
    """Test DocumentMetadata dataclass."""
    metadata = DocumentMetadata(
        original_pdf="test.pdf",
        start_page=1,
        end_page=3,
        category="Important Documents",
        filename="will.pdf",
        confidence=0.95
    )
    assert metadata.original_pdf == "test.pdf"
    assert metadata.start_page == 1
    assert metadata.end_page == 3
    assert metadata.category == "Important Documents"
    assert metadata.filename == "will.pdf"
    assert metadata.confidence == 0.95
    assert metadata.output_path is None

def test_document_organizer_initialization():
    """Test DocumentOrganizer initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        organizer = DocumentOrganizer(Path(temp_dir))
        assert organizer.output_dir == Path(temp_dir)
        assert len(organizer.metadata) == 0
        assert (Path(temp_dir) / "Unorganized").exists()

def test_add_document():
    """Test adding documents to the organizer."""
    with tempfile.TemporaryDirectory() as temp_dir:
        organizer = DocumentOrganizer(Path(temp_dir))
        metadata = DocumentMetadata(
            original_pdf="test.pdf",
            start_page=1,
            end_page=3,
            category="Important Documents",
            filename="will.pdf",
            confidence=0.95
        )
        organizer.add_document(metadata)
        assert len(organizer.metadata) == 1
        assert organizer.metadata[0] == metadata

def test_organize_document_dry_run():
    """Test document organization in dry-run mode."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file with 3 pages
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        for i in range(3):
            writer.add_blank_page(width=612, height=792)  # Standard letter size
        with open(pdf_path, 'wb') as f:
            writer.write(f)
    
        organizer = DocumentOrganizer(Path(output_dir))
        page_ranges = [(1, 3)]
        document_type = "Important Documents"
        
        results = organizer.organize_document(
            source_pdf=str(pdf_path),
            page_ranges=page_ranges,
            document_type=document_type,
            dry_run=True
        )
        
        # Verify metadata was created but no PDF files were written
        assert len(results) == 1
        assert results[0].original_pdf == str(pdf_path)
        assert results[0].start_page == 1
        assert results[0].end_page == 3
        assert results[0].category == document_type
        assert len(list(Path(output_dir).glob("**/*.pdf"))) == 0  # No PDF files should be created

def test_organize_document_with_real_pdf():
    """Test document organization with a real PDF file."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file with 3 pages
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        for i in range(3):
            # Add a blank page
            writer.add_blank_page(width=612, height=792)  # Standard letter size
        with open(pdf_path, 'wb') as f:
            writer.write(f)
    
        organizer = DocumentOrganizer(Path(output_dir))
        page_ranges = [(1, 2)]  # Extract first two pages
        document_type = "Important Documents"
        
        # Extract pages
        results = organizer.organize_document(
            source_pdf=str(pdf_path),
            page_ranges=page_ranges,
            document_type=document_type
        )
        
        # Verify the output
        assert len(results) == 1
        output_file = Path(results[0].output_path)
        assert output_file.exists()
        
        # Verify the extracted PDF has 2 pages
        reader = PdfReader(str(output_file))
        assert len(reader.pages) == 2

def test_save_metadata():
    """Test saving metadata to YAML file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        organizer = DocumentOrganizer(Path(temp_dir))
        metadata = DocumentMetadata(
            original_pdf="test.pdf",
            start_page=1,
            end_page=3,
            category="Important Documents",
            filename="will.pdf",
            confidence=0.95,
            output_path="output/Important Documents/will.pdf"
        )
        organizer.add_document(metadata)
        organizer.save_metadata()
        
        metadata_path = Path(temp_dir) / "metadata.yaml"
        assert metadata_path.exists()
        
        with open(metadata_path) as f:
            saved_metadata = yaml.safe_load(f)
            assert len(saved_metadata["documents"]) == 1
            assert saved_metadata["documents"][0]["original_pdf"] == "test.pdf"
            assert saved_metadata["documents"][0]["start_page"] == 1
            assert saved_metadata["documents"][0]["end_page"] == 3
            assert saved_metadata["documents"][0]["category"] == "Important Documents"
            assert saved_metadata["documents"][0]["filename"] == "will.pdf"
            assert saved_metadata["documents"][0]["confidence"] == 0.95
            assert saved_metadata["documents"][0]["output_path"] == "output/Important Documents/will.pdf"

def test_organize_document_invalid_page_range():
    """Test document organization with invalid page ranges."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file with 3 pages
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        for i in range(3):
            writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)
    
        organizer = DocumentOrganizer(Path(output_dir))
        
        # Test start page < 1
        with pytest.raises(ValueError, match="Start page must be at least 1"):
            organizer.organize_document(
                source_pdf=str(pdf_path),
                page_ranges=[(0, 2)],  # Invalid start page
                document_type="Important Documents"
            )
        
        # Test end page > total pages
        with pytest.raises(ValueError, match="End page 4 exceeds total pages"):
            organizer.organize_document(
                source_pdf=str(pdf_path),
                page_ranges=[(1, 4)],  # Invalid end page
                document_type="Important Documents"
            )
        
        # Test start page > end page
        with pytest.raises(ValueError, match="Start page 3 is greater than end page 2"):
            organizer.organize_document(
                source_pdf=str(pdf_path),
                page_ranges=[(3, 2)],  # Invalid range
                document_type="Important Documents"
            )

def test_organize_document_with_existing_output():
    """Test document organization when output file already exists."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)
    
        # Create output file
        output_path = Path(output_dir) / "test_pages_1-1.pdf"
        output_path.touch()
    
        organizer = DocumentOrganizer(Path(output_dir), overwrite=False)
        
        # Should raise error when overwrite=False
        with pytest.raises(ValueError, match="Output file already exists"):
            organizer.organize_document(
                source_pdf=str(pdf_path),
                page_ranges=[(1, 1)],
                document_type="Important Documents"
            )
        
        # Should succeed when overwrite=True
        organizer = DocumentOrganizer(Path(output_dir), overwrite=True)
        results = organizer.organize_document(
            source_pdf=str(pdf_path),
            page_ranges=[(1, 1)],
            document_type="Important Documents"
        )
        assert len(results) == 1
        assert Path(results[0].output_path).exists() 
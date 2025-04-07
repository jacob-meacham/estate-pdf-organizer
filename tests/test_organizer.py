"""Tests for the document organizer module."""

import tempfile
from pathlib import Path

import yaml
from pypdf import PdfReader, PdfWriter

from estate_pdf_organizer.organizer import DocumentMetadata, DocumentOrganizer


def test_document_metadata():
    """Test DocumentMetadata dataclass."""
    metadata = DocumentMetadata(
        source_pdf="test.pdf",
        start_page=1,
        end_page=3,
        document_type="Important Documents",
        filename="will.pdf",
        confidence=0.95
    )
    
    assert metadata.source_pdf == "test.pdf"
    assert metadata.start_page == 1
    assert metadata.end_page == 3
    assert metadata.document_type == "Important Documents"
    assert metadata.filename == "will.pdf"
    assert metadata.confidence == 0.95
    assert metadata.output_path is None

def test_document_organizer_initialization():
    """Test initializing the document organizer."""
    with tempfile.TemporaryDirectory() as temp_dir:
        organizer = DocumentOrganizer(Path(temp_dir))
        assert organizer.output_dir == Path(temp_dir)
        assert not organizer.overwrite
        assert len(organizer.metadata) == 0
        
        # Verify output directory was created
        assert Path(temp_dir).exists()
        assert (Path(temp_dir) / "Unorganized").exists()

def test_add_document():
    """Test adding documents to the organizer."""
    with tempfile.TemporaryDirectory() as temp_dir:
        organizer = DocumentOrganizer(Path(temp_dir))
        metadata = DocumentMetadata(
            source_pdf="test.pdf",
            start_page=1,
            end_page=3,
            document_type="Important Documents",
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
        
        # Open the PDF for reading
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            
            organizer = DocumentOrganizer(Path(output_dir))
            document_type = "Important Documents"
            
            result = organizer.organize_document(
                pdf_reader=pdf_reader,
                source_pdf_path=str(pdf_path),
                start_page=1,
                end_page=3,
                document_type=document_type,
                dry_run=True
            )
            
            # Verify metadata was created but no PDF files were written
            assert result.source_pdf == str(pdf_path)
            assert result.start_page == 1
            assert result.end_page == 3
            assert result.document_type == document_type
            assert not any(Path(output_dir).glob("**/*.pdf"))

def test_organize_document_with_real_pdf():
    """Test organizing a document with a real PDF file."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file with 3 pages
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        for i in range(3):
            writer.add_blank_page(width=612, height=792)  # Standard letter size
        with open(pdf_path, 'wb') as f:
            writer.write(f)
        
        # Open the PDF for reading
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            
            organizer = DocumentOrganizer(Path(output_dir))
            document_type = "Important Documents"
            
            result = organizer.organize_document(
                pdf_reader=pdf_reader,
                source_pdf_path=str(pdf_path),
                start_page=1,
                end_page=3,
                document_type=document_type
            )
            
            # Verify metadata was created
            assert result.source_pdf == str(pdf_path)
            assert result.start_page == 1
            assert result.end_page == 3
            assert result.document_type == document_type
            
            # Verify PDF file was created
            output_path = Path(result.output_path)
            assert output_path.exists()
            
            # Verify PDF content
            with open(output_path, 'rb') as f:
                output_reader = PdfReader(f)
                assert len(output_reader.pages) == 3

def test_save_metadata():
    """Test saving metadata to YAML file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        organizer = DocumentOrganizer(Path(temp_dir))
        metadata = DocumentMetadata(
            source_pdf="test.pdf",
            start_page=1,
            end_page=3,
            document_type="Important Documents",
            filename="will.pdf",
            confidence=0.95,
            output_path="output/Important Documents/will.pdf"
        )
        
        organizer.add_document(metadata)
        
        # Save metadata
        metadata_path = Path(temp_dir) / "metadata.yaml"
        organizer.save_metadata(metadata_path)
        
        # Verify metadata file was created
        assert metadata_path.exists()
        
        # Load and verify metadata
        with open(metadata_path) as f:
            loaded_metadata = yaml.safe_load(f)
        
        assert "documents" in loaded_metadata
        assert len(loaded_metadata["documents"]) == 1
        doc = loaded_metadata["documents"][0]
        assert doc["source_pdf"] == metadata.source_pdf
        assert doc["start_page"] == metadata.start_page
        assert doc["end_page"] == metadata.end_page
        assert doc["document_type"] == metadata.document_type
        assert doc["filename"] == metadata.filename
        assert doc["confidence"] == metadata.confidence
        assert doc["output_path"] == metadata.output_path

def test_organize_document_invalid_page_range():
    """Test organizing a document with invalid page ranges."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file with 3 pages
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        for i in range(3):
            writer.add_blank_page(width=612, height=792)  # Standard letter size
        with open(pdf_path, 'wb') as f:
            writer.write(f)
        
        # Open the PDF for reading
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            
            organizer = DocumentOrganizer(Path(output_dir))
            document_type = "Important Documents"
            
            # Test start page < 1
            try:
                organizer.organize_document(
                    pdf_reader=pdf_reader,
                    source_pdf_path=str(pdf_path),
                    start_page=0,
                    end_page=3,
                    document_type=document_type
                )
                assert False, "Expected ValueError for start_page < 1"
            except ValueError:
                pass
            
            # Test end page > total pages
            try:
                organizer.organize_document(
                    pdf_reader=pdf_reader,
                    source_pdf_path=str(pdf_path),
                    start_page=1,
                    end_page=4,
                    document_type=document_type
                )
                assert False, "Expected ValueError for end_page > total pages"
            except ValueError:
                pass
            
            # Test start page > end page
            try:
                organizer.organize_document(
                    pdf_reader=pdf_reader,
                    source_pdf_path=str(pdf_path),
                    start_page=3,
                    end_page=1,
                    document_type=document_type
                )
                assert False, "Expected ValueError for start_page > end_page"
            except ValueError:
                pass

def test_organize_document_with_existing_output():
    """Test organizing a document when output file already exists."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file with 3 pages
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        for i in range(3):
            writer.add_blank_page(width=612, height=792)  # Standard letter size
        with open(pdf_path, 'wb') as f:
            writer.write(f)
        
        # Create output directory and file
        document_type = "Important Documents"
        output_dir_path = Path(output_dir) / document_type
        output_dir_path.mkdir(parents=True)
        output_path = output_dir_path / "test_pages_1-3.pdf"
        with open(output_path, 'w') as f:
            f.write("dummy file")
        
        # Open the PDF for reading
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            
            organizer = DocumentOrganizer(Path(output_dir))
            
            # Test with existing file - should create a new file with _1 suffix
            result = organizer.organize_document(
                pdf_reader=pdf_reader,
                source_pdf_path=str(pdf_path),
                start_page=1,
                end_page=3,
                document_type=document_type
            )
            
            # Verify both files exist
            assert output_path.exists()
            assert Path(result.output_path).exists()
            assert result.output_path != str(output_path)
            assert result.filename == "test_pages_1-3_1.pdf"
            
            # Verify PDF content
            with open(result.output_path, 'rb') as f:
                output_reader = PdfReader(f)
                assert len(output_reader.pages) == 3

def test_organize_document_with_duplicate_filename():
    """Test organizing a document with a duplicate filename."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Create a simple PDF file with 3 pages
        pdf_path = Path(input_dir) / "test.pdf"
        writer = PdfWriter()
        for i in range(3):
            writer.add_blank_page(width=612, height=792)  # Standard letter size
        with open(pdf_path, 'wb') as f:
            writer.write(f)
        
        # Open the PDF for reading
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            
            organizer = DocumentOrganizer(Path(output_dir))
            document_type = "Important Documents"
            
            # First document
            organizer.organize_document(
                pdf_reader=pdf_reader,
                source_pdf_path=str(pdf_path),
                start_page=1,
                end_page=1,
                document_type=document_type,
                suggested_filename="test_doc.pdf"
            )
            
            # Second document with same suggested filename
            organizer.organize_document(
                pdf_reader=pdf_reader,
                source_pdf_path=str(pdf_path),
                start_page=2,
                end_page=2,
                document_type=document_type,
                suggested_filename="test_doc.pdf"
            )
            
            # Verify both files exist with correct names
            assert (Path(output_dir) / document_type / "test_doc.pdf").exists()
            assert (Path(output_dir) / document_type / "test_doc_1.pdf").exists()
            
            # Verify metadata
            assert len(organizer.metadata) == 2
            assert organizer.metadata[0].filename == "test_doc.pdf"
            assert organizer.metadata[1].filename == "test_doc_1.pdf" 
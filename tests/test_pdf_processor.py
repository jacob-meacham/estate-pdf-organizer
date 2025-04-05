"""Tests for the PDF processor module."""

from pathlib import Path
from estate_pdf_organizer.pdf_processor import PDFProcessor, DocumentChunk

def test_document_chunk():
    """Test DocumentChunk dataclass."""
    chunk = DocumentChunk(start_page=1, end_page=3, text="Test document")
    assert chunk.start_page == 1
    assert chunk.end_page == 3
    assert chunk.text == "Test document"

def test_pdf_processor_initialization():
    """Test PDFProcessor initialization."""
    processor = PDFProcessor(window_size=3)
    assert processor.window_size == 3

def test_get_text_windows():
    """Test text window generation."""
    processor = PDFProcessor(window_size=2)
    texts = ["Page 1", "Page 2", "Page 3"]
    windows = list(processor.get_text_windows(texts))
    
    assert len(windows) == 2
    assert windows[0].start_page == 1
    assert windows[0].end_page == 2
    assert windows[0].text == "Page 1\nPage 2"
    assert windows[1].start_page == 2
    assert windows[1].end_page == 3
    assert windows[1].text == "Page 2\nPage 3" 
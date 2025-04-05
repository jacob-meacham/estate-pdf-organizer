"""PDF processing module for the Estate PDF Organizer."""

import pdfplumber
from pathlib import Path
from typing import List, Tuple, Generator
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a PDF with its page range."""
    start_page: int
    end_page: int
    text: str

class PDFProcessor:
    """Handles PDF processing and document boundary detection."""
    
    def __init__(self, window_size: int = 3):
        """Initialize the PDF processor.
        
        Args:
            window_size: Number of pages to consider when detecting document boundaries
        """
        if window_size < 1:
            raise ValueError("Window size must be at least 1")
        self.window_size = window_size

    def extract_text(self, pdf_path: Path) -> List[str]:
        """Extract text from all pages of a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of text content for each page
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            pdfplumber.PDFSyntaxError: If the PDF is corrupted or invalid
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        texts = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texts.append(page.extract_text() or "")
        except Exception as e:
            raise RuntimeError(f"Error processing PDF {pdf_path}: {str(e)}")
            
        if not texts:
            raise ValueError(f"PDF {pdf_path} contains no text")
            
        return texts

    def get_text_windows(self, texts: List[str]) -> Generator[DocumentChunk, None, None]:
        """Generate sliding windows of text from the PDF.
        
        Args:
            texts: List of text content for each page
            
        Yields:
            DocumentChunk objects containing the text and page range for each window
        """
        if len(texts) < self.window_size:
            # If PDF has fewer pages than window size, treat it as a single document
            yield DocumentChunk(
                start_page=1,
                end_page=len(texts),
                text="\n".join(texts)
            )
            return
            
        for i in range(len(texts) - self.window_size + 1):
            window_text = "\n".join(texts[i:i + self.window_size])
            yield DocumentChunk(
                start_page=i + 1,
                end_page=i + self.window_size,
                text=window_text
            )

    def process_pdf(self, pdf_path: Path) -> List[Tuple[int, int]]:
        """Process a PDF and detect document boundaries.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of (start_page, end_page) tuples representing document boundaries
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the PDF contains no text
            RuntimeError: If there's an error processing the PDF
        """
        texts = self.extract_text(pdf_path)
        return [(i + 1, i + 1) for i in range(len(texts))] 
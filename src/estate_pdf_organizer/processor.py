"""Main processor module for the Estate PDF Organizer."""

import io
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter

from .classifier import DocumentClassifier
from .organizer import DocumentOrganizer


def read_pdf(pdf_path: Path) -> tuple[PdfReader, int, list]:
    """Read a PDF file and return its reader, page count, and page images.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (PdfReader, total_pages, page_images)
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the PDF is invalid
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    try:
        reader = PdfReader(pdf_path)
        # Convert PDF to images for OCR
        images = convert_from_path(pdf_path)
        return reader, len(reader.pages), images
    except Exception as err:
        raise ValueError(f"Error reading PDF {pdf_path}: {err!s}") from err

def extract_text_from_page(page_image) -> str:
    """Extract text from a page image using OCR.
    
    Args:
        page_image: PIL Image object of the page
        
    Returns:
        Extracted text from the page
    """
    # Configure Tesseract to use English language and optimize for document text
    custom_config = r'--oem 3 --psm 6 -l eng'
    return pytesseract.image_to_string(page_image, config=custom_config)

def remove_blank_pages(reader: PdfReader, images: list) -> tuple[PdfReader, list, list[int]]:
    """Remove blank pages from a PDF in memory.
    
    A page is considered blank if it has no text content after OCR.
    
    Args:
        reader: PdfReader instance
        images: List of page images
        
    Returns:
        Tuple of (new PdfReader, new images list, list of removed page numbers)
    """
    writer = PdfWriter()
    new_images = []
    removed_pages = []
    
    for i, (page, image) in enumerate(zip(reader.pages, images, strict=False), 1):
        # Extract text using OCR
        text = extract_text_from_page(image)
        
        if not text.strip():
            removed_pages.append(i)
        else:
            writer.add_page(page)
            new_images.append(image)
    
    # Create a new PdfReader from the writer's content
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    new_reader = PdfReader(output)
    
    return new_reader, new_images, removed_pages

def extract_text_from_pages(images: list, start_page: int, end_page: int) -> str:
    """Extract text from a range of pages using OCR.
    
    Args:
        images: List of page images
        start_page: One-indexed start page
        end_page: One-indexed end page (inclusive)
        
    Returns:
        Combined text from the specified pages, with page numbers included
        
    Raises:
        ValueError: If page range is invalid
    """
    if start_page < 1 or end_page > len(images):
        raise ValueError(f"Invalid page range: {start_page}-{end_page}")
        
    texts = []
    for i in range(start_page - 1, end_page):
        page_num = i + 1
        page_text = extract_text_from_page(images[i]) or ""
        texts.append(f"[PAGE {page_num}]\n{page_text}")
    return "\n\n".join(texts)

class EstatePDFProcessor:
    """Main processor for organizing estate documents."""
    
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        classifier: DocumentClassifier,
        overwrite: bool = False,
        dry_run: bool = False,
        window_size: int = 10,
        remove_blank_pages: bool = True,
    ):
        """Initialize the processor.
        
        Args:
            input_dir: Directory containing input PDFs
            output_dir: Directory to store organized documents
            classifier: classifier to use.
            overwrite: Whether to overwrite existing files
            dry_run: If True, only show what would be done without making changes
            window_size: Number of pages to consider for document boundary detection
            remove_blank_pages: Whether to remove blank pages before processing
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.dry_run = dry_run
        self.window_size = window_size
        self.remove_blank_pages = remove_blank_pages
        
        # Initialize components
        self.classifier = classifier
        self.organizer = DocumentOrganizer(output_dir, overwrite)
    
    def process_directory(self) -> None:
        """Process all PDFs in the input directory."""
        # Get all PDF files in input directory
        pdf_files = list(self.input_dir.glob("*.pdf"))
        
        for pdf_path in pdf_files:
            print(f"\nProcessing {pdf_path.name}...")
            self.process_pdf(pdf_path)
            
        # Save all metadata
        if not self.dry_run:
            metadata_path = self.output_dir / f"{pdf_path.stem}_metadata.yaml"
            self.organizer.save_metadata(metadata_path)
    
    def process_pdf(self, pdf_path: Path) -> None:
        """Process a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file to process
        """
        # Read PDF and convert to images
        reader, total_pages, images = read_pdf(pdf_path)
        
        # Remove blank pages if enabled
        if self.remove_blank_pages:
            reader, images, removed_pages = remove_blank_pages(reader, images)
            if removed_pages:
                print(f"  Removed {len(removed_pages)} blank pages: {removed_pages}")
            total_pages = len(reader.pages)
        
        # Process the PDF in windows to find document boundaries
        current_page = 1
        last_boundary = 0  # Track the last boundary we found
        
        while current_page <= total_pages:
            # Calculate window end page
            window_end = min(current_page + self.window_size - 1, total_pages)
            
            # Extract text for the current window
            window_text = extract_text_from_pages(images, current_page, window_end)
            
            # Classify the window to find document boundaries and types
            classifications = self.classifier.classify(window_text)

            for c in classifications:
                # Organize the document
                self.organizer.organize_document(
                    pdf_reader=reader,
                    source_pdf_path=str(pdf_path),
                    start_page=c.page_start,
                    end_page=c.page_end,
                    document_type=c.document_type,
                    dry_run=self.dry_run,
                    suggested_filename=c.suggested_filename
                )

                msg = f"  Found {c.document_type}"
                msg += f" (pages {c.page_start}-{c.page_end})"
                print(msg)

                current_page = c.page_end + 1

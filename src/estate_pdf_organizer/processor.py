"""Main processor module for the Estate PDF Organizer."""

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .classifier import DocumentClassifier
from .organizer import DocumentOrganizer


def read_pdf(pdf_path: Path) -> tuple[PdfReader, int]:
    """Read a PDF file and return its reader and page count.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (PdfReader, total_pages)
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the PDF is invalid
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    try:
        reader = PdfReader(pdf_path)
        return reader, len(reader.pages)
    except Exception as err:
        raise ValueError(f"Error reading PDF {pdf_path}: {err!s}") from err

def remove_blank_pages(pdf_path: Path) -> tuple[Path, list[int]]:
    """Remove blank pages from a PDF file.
    
    A page is considered blank if it has no text content and no images.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (Path to new PDF with blank pages removed, list of removed page numbers)
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    removed_pages = []
    
    for i, page in enumerate(reader.pages, 1):
        # Extract text and check if page has any content
        text = page.extract_text()
        images = page.images
        
        if not text.strip() and not images:
            removed_pages.append(i)
        else:
            writer.add_page(page)
    
    if removed_pages:
        # Create new PDF without blank pages
        new_pdf_path = pdf_path.parent / f"{pdf_path.stem}_no_blank{pdf_path.suffix}"
        with open(new_pdf_path, 'wb') as output_file:
            writer.write(output_file)
        return new_pdf_path, removed_pages
    
    return pdf_path, []

def extract_text_from_pages(reader: PdfReader, start_page: int, end_page: int) -> str:
    """Extract text from a range of pages in a PDF.
    
    Args:
        reader: PdfReader instance
        start_page: One-indexed start page
        end_page: One-indexed end page (inclusive)
        
    Returns:
        Combined text from the specified pages, with page numbers included
        
    Raises:
        ValueError: If page range is invalid
    """
    if start_page < 1 or end_page > len(reader.pages):
        raise ValueError(f"Invalid page range: {start_page}-{end_page}")
        
    texts = []
    for i in range(start_page - 1, end_page):
        page_num = i + 1
        page_text = reader.pages[i].extract_text() or ""
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
        # Remove blank pages if enabled
        if self.remove_blank_pages:
            pdf_path, removed_pages = remove_blank_pages(pdf_path)
            if removed_pages:
                print(f"  Removed {len(removed_pages)} blank pages: {removed_pages}")
        
        # Open the PDF
        reader, total_pages = read_pdf(pdf_path)
        
        # Process the PDF in windows to find document boundaries
        current_page = 1
        last_boundary = 0  # Track the last boundary we found
        
        while current_page <= total_pages:
            # Calculate window end page
            window_end = min(current_page + self.window_size - 1, total_pages)
            
            # Extract text for the current window
            window_text = extract_text_from_pages(reader, current_page, window_end)
            
            # Classify the window to find document boundaries and types
            classification = self.classifier.classify(window_text)
            
            # If we found a document boundary, extract and organize it
            if classification.is_boundary:
                # Use the boundary page from the classification
                document_end = classification.boundary_page
                
                # Only process if this is a new boundary
                if document_end > last_boundary:
                    # Organize the document
                    self.organizer.organize_document(
                        pdf_reader=reader,
                        source_pdf_path=str(pdf_path),
                        start_page=current_page,
                        end_page=document_end,
                        document_type=classification.document_type,
                        dry_run=self.dry_run,
                        suggested_filename=classification.suggested_filename
                    )
                    
                    msg = f"  Found {classification.document_type}"
                    msg += f" (pages {current_page}-{document_end})"
                    print(msg)
                    
                    # Update tracking variables
                    last_boundary = document_end
                    current_page = document_end + 1
                else:
                    # Skip this boundary as we've already processed it
                    current_page += 1
            else:
                # If we're at the end of the PDF and haven't found a boundary,
                # treat the remaining pages as a document
                if current_page == total_pages and last_boundary < total_pages:
                    self.organizer.organize_document(
                        pdf_reader=reader,
                        source_pdf_path=str(pdf_path),
                        start_page=last_boundary + 1,
                        end_page=total_pages,
                        document_type="Unorganized",
                        dry_run=self.dry_run
                    )
                    print(f"  Found Unorganized document (pages {last_boundary + 1}-{total_pages})")
                # Move to the next page if no boundary found
                current_page += 1
    
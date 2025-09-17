# app/ingestion/pdf_extractor.py

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib
from pathlib import Path

import pdfplumber
from pdfplumber.pdf import PDF

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Comprehensive PDF text extraction with multiple extraction methods and metadata handling.
    """
    
    def __init__(self, extraction_method: str = "pdfplumber"):
        """
        Initialize PDF extractor.
        
        Args:
            extraction_method: Method to use for extraction ("pdfplumber", "pypdf2", "pymupdf")
        """
        self.extraction_method = extraction_method
        self.supported_methods = ["pdfplumber", "pypdf2", "pymupdf"]
        
        if extraction_method not in self.supported_methods:
            raise ValueError(f"Unsupported extraction method. Choose from: {self.supported_methods}")
    
    def extract_text(self, pdf_path: str, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Extract text from PDF file with comprehensive metadata.
        
        Args:
            pdf_path: Path to the PDF file
            include_metadata: Whether to include PDF metadata
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Get file metadata
            file_stats = os.stat(pdf_path)
            file_hash = self._calculate_file_hash(pdf_path)
            
            # Extract text based on method
            if self.extraction_method == "pdfplumber":
                text, page_count = self._extract_with_pdfplumber(pdf_path)
            
            result = {
                "text": text,
                "page_count": page_count,
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "file_size": file_stats.st_size,
                "file_hash": file_hash,
                "extraction_method": self.extraction_method,
                "extraction_timestamp": datetime.now().isoformat(),
                "text_length": len(text),
                "word_count": len(text.split()) if text else 0
            }
            
            # Add PDF metadata if requested
            if include_metadata:
                pdf_metadata = self._extract_pdf_metadata(pdf_path)
                result["pdf_metadata"] = pdf_metadata
            
            logger.info(f"Successfully extracted text from {pdf_path} ({page_count} pages, {result['word_count']} words)")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
    
    def _extract_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get("Title", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "subject": pdf.metadata.get("Subject", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                        "producer": pdf.metadata.get("Producer", ""),
                        "creation_date": pdf.metadata.get("CreationDate", ""),
                        "modification_date": pdf.metadata.get("ModDate", ""),
                        "keywords": pdf.metadata.get("Keywords", ""),
                        "pdf_version": pdf.metadata.get("PDFVersion", "")
                    }
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {e}")
        
        return metadata
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[str, int]:
        """
        Extract text from PDF using pdfplumber.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        text = ""
        page_count = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                logger.info(f"Extracted text from {page_count} pages using pdfplumber")
                return text.strip(), page_count
                
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            raise
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of the file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def extract_text_from_pages(self, pdf_path: str, page_numbers: List[int]) -> Dict[str, Any]:
        """
        Extract text from specific pages only.
        
        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to extract (1-indexed)
            
        Returns:
            Dictionary containing extracted text from specified pages
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        text = ""
        extracted_pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num in page_numbers:
                    if 1 <= page_num <= total_pages:
                        try:
                            page = pdf.pages[page_num - 1]  # Convert to 0-indexed
                            page_text = page.extract_text()
                            if page_text:
                                text += f"\n--- Page {page_num} ---\n{page_text}\n"
                                extracted_pages.append(page_num)
                        except Exception as e:
                            logger.warning(f"Error extracting page {page_num}: {e}")
                    else:
                        logger.warning(f"Page {page_num} is out of range (1-{total_pages})")
            
            result = {
                "text": text.strip(),
                "extracted_pages": extracted_pages,
                "requested_pages": page_numbers,
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "extraction_method": self.extraction_method,
                "extraction_timestamp": datetime.now().isoformat(),
                "text_length": len(text),
                "word_count": len(text.split()) if text else 0
            }
            
            logger.info(f"Extracted text from pages {extracted_pages} of {pdf_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting pages from {pdf_path}: {e}")
            raise
    
    def batch_extract(self, pdf_directory: str, output_format: str = "dict") -> List[Dict[str, Any]]:
        """
        Extract text from all PDF files in a directory.
        
        Args:
            pdf_directory: Directory containing PDF files
            output_format: Output format ("dict" or "json")
            
        Returns:
            List of extraction results for all PDF files
        """
        if not os.path.isdir(pdf_directory):
            raise ValueError(f"Directory not found: {pdf_directory}")
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_directory}")
            return []
        
        results = []
        successful_extractions = 0
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            try:
                result = self.extract_text(pdf_path)
                results.append(result)
                successful_extractions += 1
            except Exception as e:
                logger.error(f"Failed to extract {pdf_file}: {e}")
                results.append({
                    "file_name": pdf_file,
                    "file_path": pdf_path,
                    "error": str(e),
                    "extraction_timestamp": datetime.now().isoformat()
                })
        
        logger.info(f"Batch extraction completed: {successful_extractions}/{len(pdf_files)} successful")
        return results
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a PDF file without extracting text.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            file_stats = os.stat(pdf_path)
            
            with pdfplumber.open(pdf_path) as pdf:
                info = {
                    "file_name": os.path.basename(pdf_path),
                    "file_path": pdf_path,
                    "file_size": file_stats.st_size,
                    "page_count": len(pdf.pages),
                    "pdf_version": pdf.metadata.get("PDFVersion", "") if pdf.metadata else "",
                    "creation_date": pdf.metadata.get("CreationDate", "") if pdf.metadata else "",
                    "modification_date": pdf.metadata.get("ModDate", "") if pdf.metadata else "",
                    "title": pdf.metadata.get("Title", "") if pdf.metadata else "",
                    "author": pdf.metadata.get("Author", "") if pdf.metadata else "",
                    "subject": pdf.metadata.get("Subject", "") if pdf.metadata else "",
                    "creator": pdf.metadata.get("Creator", "") if pdf.metadata else "",
                    "producer": pdf.metadata.get("Producer", "") if pdf.metadata else "",
                    "keywords": pdf.metadata.get("Keywords", "") if pdf.metadata else "",
                    "file_hash": self._calculate_file_hash(pdf_path),
                    "info_timestamp": datetime.now().isoformat()
                }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info for {pdf_path}: {e}")
            raise

# Example usage and testing functions
def example_usage():
    """
    Example usage of PDFExtractor.
    """
    # Initialize extractor with different methods
    extractors = {
        "pdfplumber": PDFExtractor("pdfplumber"),
        "pypdf2": PDFExtractor("pypdf2"),
        "pymupdf": PDFExtractor("pymupdf")
    }
    
    # Example PDF path (replace with actual path)
    pdf_path = "example.pdf"
    
    print("PDF Extraction Examples")
    print("=" * 50)
    
    # Test each extraction method
    for method, extractor in extractors.items():
        print(f"\nTesting {method} extraction method:")
        try:
            result = extractor.extract_text(pdf_path)
            print(f"  - Pages: {result['page_count']}")
            print(f"  - Words: {result['word_count']}")
            print(f"  - Text length: {result['text_length']}")
            print(f"  - Author: {result.get('pdf_metadata', {}).get('author', 'Unknown')}")
        except Exception as e:
            print(f"  - Error: {e}")
    
    # Extract specific pages
    print(f"\nExtracting specific pages (1, 3, 5):")
    try:
        extractor = PDFExtractor()
        result = extractor.extract_text_from_pages(pdf_path, [1, 3, 5])
        print(f"  - Extracted from pages: {result['extracted_pages']}")
        print(f"  - Words extracted: {result['word_count']}")
    except Exception as e:
        print(f"  - Error: {e}")
    
    # Get PDF information
    print(f"\nGetting PDF information:")
    try:
        extractor = PDFExtractor()
        info = extractor.get_pdf_info(pdf_path)
        print(f"  - Title: {info.get('title', 'Unknown')}")
        print(f"  - Author: {info.get('author', 'Unknown')}")
        print(f"  - Pages: {info['page_count']}")
        print(f"  - File size: {info['file_size']} bytes")
    except Exception as e:
        print(f"  - Error: {e}")

def test_batch_extraction():
    """
    Test batch extraction functionality.
    """
    pdf_directory = "pdf_documents"  # Replace with actual directory
    
    print("\nBatch PDF Extraction Test")
    print("=" * 50)
    
    extractor = PDFExtractor()
    
    try:
        results = extractor.batch_extract(pdf_directory)
        
        print(f"Processed {len(results)} PDF files:")
        for result in results:
            if "error" in result:
                print(f"  ❌ {result['file_name']}: {result['error']}")
            else:
                print(f"  ✅ {result['file_name']}: {result['page_count']} pages, {result['word_count']} words")
                
    except Exception as e:
        print(f"Batch extraction error: {e}")

if __name__ == "__main__":
    # Run examples if script is executed directly
    print("Running PDF extraction examples...")
    example_usage()
    
    print("\n" + "=" * 80)
    print("Running batch extraction test...")
    test_batch_extraction()
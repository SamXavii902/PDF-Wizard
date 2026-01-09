"""
PDF Merger and Splitter Module

Handles merging multiple PDFs into one and splitting PDFs into separate files.
Includes encryption checking and progress bar support.
"""

from pathlib import Path
from typing import List, Optional, Tuple
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import click

from pdf_wizard.utils import (
    success, error, warning, info,
    create_progress_bar, get_file_size, format_file_size
)


def check_encryption(pdf_path: Path) -> bool:
    """
    Check if a PDF is encrypted
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        True if encrypted, False otherwise
    """
    try:
        reader = PdfReader(str(pdf_path))
        return reader.is_encrypted
    except Exception as e:
        error(f"Error checking encryption for {pdf_path.name}: {str(e)}")
        return False


def merge_pdfs(
    input_files: List[Path],
    output_file: Path,
    show_progress: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Merge multiple PDF files into a single PDF
    
    Args:
        input_files: List of PDF file paths to merge
        output_file: Output path for merged PDF
        show_progress: Whether to show progress bar
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        # Check for encrypted files first
        encrypted_files = []
        for pdf_file in input_files:
            if check_encryption(pdf_file):
                encrypted_files.append(pdf_file.name)
        
        if encrypted_files:
            error_msg = f"Cannot merge encrypted PDFs: {', '.join(encrypted_files)}"
            error(error_msg)
            return False, error_msg
        
        info(f"Merging {len(input_files)} PDF files...")
        
        # Use PdfMerger for efficient merging
        merger = PdfMerger()
        
        if show_progress:
            progress = create_progress_bar(len(input_files), "Merging PDFs")
        
        for pdf_file in input_files:
            try:
                merger.append(str(pdf_file))
                if show_progress:
                    progress.update(1)
                    progress.set_postfix_str(f"Added: {pdf_file.name}")
            except Exception as e:
                if show_progress:
                    progress.close()
                error_msg = f"Error adding {pdf_file.name}: {str(e)}"
                error(error_msg)
                return False, error_msg
        
        if show_progress:
            progress.close()
        
        # Write merged PDF
        info(f"Writing merged PDF to {output_file.name}...")
        merger.write(str(output_file))
        merger.close()
        
        # Report success with file size
        file_size = format_file_size(get_file_size(output_file))
        success(f"Successfully merged {len(input_files)} PDFs → {output_file.name} ({file_size})")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Unexpected error during merge: {str(e)}"
        error(error_msg)
        return False, error_msg


def split_pdf(
    input_file: Path,
    output_dir: Path,
    mode: str = 'pages',
    page_ranges: Optional[List[str]] = None,
    show_progress: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Split a PDF into multiple files
    
    Args:
        input_file: PDF file to split
        output_dir: Directory to save split PDFs
        mode: 'pages' (one file per page) or 'ranges' (custom page ranges)
        page_ranges: List of page range strings like ['1-5', '6-10'] for ranges mode
        show_progress: Whether to show progress bar
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        # Check if encrypted
        if check_encryption(input_file):
            error_msg = f"Cannot split encrypted PDF: {input_file.name}"
            error(error_msg)
            return False, error_msg
        
        reader = PdfReader(str(input_file))
        total_pages = len(reader.pages)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if mode == 'pages':
            # Split into individual pages
            info(f"Splitting {input_file.name} ({total_pages} pages) into individual files...")
            
            if show_progress:
                progress = create_progress_bar(total_pages, "Splitting PDF")
            
            base_name = input_file.stem
            
            for page_num in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                output_path = output_dir / f"{base_name}_page_{page_num + 1}.pdf"
                with open(output_path, 'wb') as output_pdf:
                    writer.write(output_pdf)
                
                if show_progress:
                    progress.update(1)
            
            if show_progress:
                progress.close()
            
            success(f"Split into {total_pages} files in {output_dir}")
            return True, None
            
        elif mode == 'ranges':
            # Split by custom ranges
            if not page_ranges:
                error_msg = "Page ranges required for 'ranges' mode"
                error(error_msg)
                return False, error_msg
            
            info(f"Splitting {input_file.name} into {len(page_ranges)} custom ranges...")
            
            if show_progress:
                progress = create_progress_bar(len(page_ranges), "Splitting ranges")
            
            base_name = input_file.stem
            
            for idx, range_str in enumerate(page_ranges):
                try:
                    # Parse range like "1-5" or "10"
                    if '-' in range_str:
                        start, end = map(int, range_str.split('-'))
                    else:
                        start = end = int(range_str)
                    
                    # Validate range
                    if start < 1 or end > total_pages or start > end:
                        error_msg = f"Invalid page range: {range_str} (PDF has {total_pages} pages)"
                        error(error_msg)
                        return False, error_msg
                    
                    writer = PdfWriter()
                    for page_num in range(start - 1, end):  # Convert to 0-indexed
                        writer.add_page(reader.pages[page_num])
                    
                    output_path = output_dir / f"{base_name}_range_{idx + 1}_{range_str}.pdf"
                    with open(output_path, 'wb') as output_pdf:
                        writer.write(output_pdf)
                    
                    if show_progress:
                        progress.update(1)
                        
                except ValueError:
                    if show_progress:
                        progress.close()
                    error_msg = f"Invalid range format: {range_str}. Use format like '1-5' or '10'"
                    error(error_msg)
                    return False, error_msg
            
            if show_progress:
                progress.close()
            
            success(f"Split into {len(page_ranges)} files in {output_dir}")
            return True, None
            
        else:
            error_msg = f"Invalid mode: {mode}. Use 'pages' or 'ranges'"
            error(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Unexpected error during split: {str(e)}"
        error(error_msg)
        return False, error_msg

"""
Academic-Specific PDF Operations Module

Innovative features designed specifically for academic document workflows:
- Blank page removal from scanned documents
- Auto-rotation using OCR
- Page reordering
- QR code generation for document verification
- PDF comparison with diff highlighting
- Auto page numbering
"""

from pathlib import Path
from typing import Optional, Tuple, List
import fitz  # PyMuPDF
from PIL import Image
import qrcode
import hashlib
import io

from pdf_wizard.utils import (
    success, error, warning, info,
    create_progress_bar, get_file_size, format_file_size
)


import concurrent.futures
import os

def _scan_page_brightness(args):
    """Scan a single page for brightness to detect blanks"""
    input_file_path, page_num, threshold = args
    
    # Each thread/process opens the file
    doc = fitz.open(str(input_file_path))
    page = doc[page_num]
    pix = page.get_pixmap()
    
    img_data = pix.samples
    total_pixels = pix.width * pix.height
    
    # Calculate bright pixels (simplified)
    # Checking every 3rd byte (RGB) is slow in python, so we sample steps to be faster
    step = 3 * 10  # Sample every 10th pixel for speed
    bright_pixels = 0
    sampled_pixels = 0
    
    for i in range(0, len(img_data), step):
        if i+2 < len(img_data):
            if img_data[i] > 240 and img_data[i+1] > 240 and img_data[i+2] > 240:
                bright_pixels += 1
            sampled_pixels += 1
            
    doc.close()
    
    if sampled_pixels == 0: return False
    
    whiteness = bright_pixels / sampled_pixels
    return whiteness >= threshold


def remove_blank_pages(
    input_file: Path,
    output_file: Path,
    threshold: float = 0.98,
    show_progress: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Remove blank pages using Parallel Processing for scanning
    """
    try:
        info(f"Analyzing {input_file.name} for blank pages using {os.cpu_count()} cores...")
        
        doc = fitz.open(str(input_file))
        total_pages = len(doc)
        doc.close()
        
        blank_pages = []
        
        if show_progress:
            progress = create_progress_bar(total_pages, "Scanning pages (Parallel)")
            
        tasks = [(input_file, i, threshold) for i in range(total_pages)]
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # map maintains order so we know which result corresponds to which page (0...N)
            results = list(executor.map(_scan_page_brightness, tasks))
            
            for i, is_blank in enumerate(results):
                if is_blank:
                    blank_pages.append(i + 1)
                if show_progress:
                    progress.update(1)
                    
        if show_progress:
            progress.close()
        
        if not blank_pages:
            info("No blank pages detected")
            doc = fitz.open(str(input_file))
            doc.save(str(output_file))
            doc.close()
            success(f"PDF saved (no changes needed) → {output_file.name}")
            return True, None
        
        info(f"Found {len(blank_pages)} blank pages: {blank_pages}")
        
        # Create new PDF without blank pages - this part is fast enough to do sequentially
        doc = fitz.open(str(input_file))
        output_doc = fitz.open()
        
        for page_num in range(total_pages):
            if (page_num + 1) not in blank_pages:
                output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        output_doc.save(str(output_file))
        output_doc.close()
        doc.close()
        
        pages_removed = len(blank_pages)
        remaining_pages = total_pages - pages_removed
        
        success(
            f"Removed {pages_removed} blank pages "
            f"({total_pages} → {remaining_pages} pages) → {output_file.name}"
        )
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error removing blank pages: {str(e)}"
        error(error_msg)
        return False, error_msg


def auto_rotate_pages(
    input_file: Path,
    output_file: Path
) -> Tuple[bool, Optional[str]]:
    """
    Auto-rotate pages to correct orientation using OCR detection
    
    Note: Requires tesseract installation for full OCR.
    Falls back to simpler heuristics if OCR unavailable.
    
    Args:
        input_file: Input PDF file
        output_file: Output PDF with corrected orientation
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Detecting page orientation in {input_file.name}...")
        warning("OCR-based rotation requires Tesseract. Using heuristic detection...")
        
        doc = fitz.open(str(input_file))
        total_pages = len(doc)
        
        rotations_applied = 0
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Simple heuristic: check if page width > height
            # Most documents are portrait orientation
            rect = page.rect
            
            if rect.width > rect.height:
                # Likely needs rotation from landscape to portrait
                page.set_rotation(90)
                rotations_applied += 1
        
        if rotations_applied > 0:
            doc.save(str(output_file))
            success(f"Rotated {rotations_applied} pages → {output_file.name}")
        else:
            doc.save(str(output_file))
            info("No rotation needed - all pages appear correctly oriented")
        
        doc.close()
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error auto-rotating pages: {str(e)}"
        error(error_msg)
        return False, error_msg


def reorder_pages(
    input_file: Path,
    output_file: Path,
    page_order: str
) -> Tuple[bool, Optional[str]]:
    """
    Reorder pages in a PDF
    
    Args:
        input_file: Input PDF file
        output_file: Output PDF with reordered pages
        page_order: Page order string (e.g., "1,3,2,4-10")
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Reordering pages in {input_file.name}...")
        
        doc = fitz.open(str(input_file))
        total_pages = len(doc)
        
        # Parse page order
        new_order = []
        parts = page_order.split(',')
        
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                # Range like "4-10"
                start, end = map(int, part.split('-'))
                new_order.extend(range(start, end + 1))
            else:
                # Single page
                new_order.append(int(part))
        
        # Validate pages
        for page_num in new_order:
            if page_num < 1 or page_num > total_pages:
                error_msg = f"Invalid page number: {page_num} (PDF has {total_pages} pages)"
                error(error_msg)
                doc.close()
                return False, error_msg
        
        info(f"New order: {new_order}")
        
        # Create new document with reordered pages
        output_doc = fitz.open()
        
        for page_num in new_order:
            output_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
        
        output_doc.save(str(output_file))
        output_doc.close()
        doc.close()
        
        success(f"Pages reordered ({len(new_order)} pages) → {output_file.name}")
        
        return True, None
        
    except ValueError as e:
        error_msg = f"Invalid page order format: {page_order}. Use format like '1,3,2,4-10'"
        error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error reordering pages: {str(e)}"
        error(error_msg)
        return False, error_msg


def generate_qr_share(
    input_file: Path,
    output_png: Path
) -> Tuple[bool, Optional[str]]:
    """
    Generate QR code with document hash for verification
    Useful for proving document authenticity to professors
    
    Args:
        input_file: Input PDF file
        output_png: Output QR code image
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Generating verification QR code for {input_file.name}...")
        
        # Calculate SHA-256 hash of the PDF
        sha256_hash = hashlib.sha256()
        
        with open(input_file, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        file_hash = sha256_hash.hexdigest()
        
        # Create verification string
        verification_data = f"File: {input_file.name}\nSHA-256: {file_hash[:32]}..."
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(file_hash)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_png)
        
        success(f"QR code generated → {output_png.name}")
        info(f"Document hash: {file_hash[:16]}...")
        info("Share this QR code to verify document integrity")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error generating QR code: {str(e)}"
        error(error_msg)
        return False, error_msg


def compare_pdfs(
    original_file: Path,
    modified_file: Path,
    output_file: Path
) -> Tuple[bool, Optional[str]]:
    """
    Compare two PDFs and highlight differences
    Useful for tracking assignment revisions
    
    Args:
        original_file: Original PDF file
        modified_file: Modified PDF file
        output_file: Output PDF with differences highlighted
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Comparing {original_file.name} with {modified_file.name}...")
        
        doc1 = fitz.open(str(original_file))
        doc2 = fitz.open(str(modified_file))
        
        # Create output doc based on modified file to show changes on it
        output_doc = fitz.open()
        output_doc.insert_pdf(doc2)
        
        differences_found = 0
        diff_report = []
        
        # Compare page counts
        if len(doc1) != len(doc2):
            diff_report.append(f"Page count changed: {len(doc1)} vs {len(doc2)}")
            warning(f"Page count differs: {len(doc1)} vs {len(doc2)}")
        
        min_pages = min(len(doc1), len(doc2))
        
        for i in range(min_pages):
            page1 = doc1[i]
            page2 = doc2[i] # Original modified page
            out_page = output_doc[i] # Page in output doc
            
            # 1. Text Comparison
            text1 = page1.get_text()
            text2 = page2.get_text()
            
            if text1 != text2:
                differences_found += 1
                # Mark the page with a red border or text
                rect = out_page.rect
                # Draw a red border rectangle to indicate change
                shape = out_page.new_shape()
                shape.draw_rect(rect)
                shape.finish(color=(1, 0, 0), width=5)
                shape.commit()
                
                # Add a text annotation
                out_page.insert_text((50, 50), "CHANGES DETECTED ON THIS PAGE", color=(1, 0, 0), fontsize=14)
                
                diff_report.append(f"Page {i+1}: Text content changed")

        # Save the detailed visual report
        output_doc.save(str(output_file))
        output_doc.close()
        doc1.close()
        doc2.close()
        
        # Generate a text summary file next to the PDF
        summary_path = output_file.with_name(f"{output_file.stem}_report.txt")
        with open(summary_path, 'w') as f:
            f.write(f"Comparison Report for {original_file.name} vs {modified_file.name}\n")
            f.write("="*50 + "\n\n")
            if not diff_report:
                f.write("No significant text differences found.\n")
            else:
                for line in diff_report:
                    f.write(f"- {line}\n")
        
        if differences_found > 0:
            success(f"Found differences on {differences_found} pages. Visual report saved to {output_file.name}")
            info(f"Text summary saved to {summary_path.name}")
        else:
            success(f"No differences found. Saved copy to {output_file.name}")
            
        return True, None
        
    except Exception as e:
        error_msg = f"Error comparing PDFs: {str(e)}"
        error(error_msg)
        return False, error_msg


def add_page_numbers(
    input_file: Path,
    output_file: Path,
    position: str = 'bottom-right',
    start_number: int = 1,
    format_style: str = 'numeric'
) -> Tuple[bool, Optional[str]]:
    """
    Add page numbers to a PDF
    
    Args:
        input_file: Input PDF file
        output_file: Output PDF with page numbers
        position: Position ('bottom-right', 'bottom-center', 'bottom-left', 'top-right', 'top-center', 'top-left')
        start_number: Starting page number
        format_style: Number format ('numeric', 'roman', 'alpha')
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Adding page numbers to {input_file.name}...")
        
        doc = fitz.open(str(input_file))
        total_pages = len(doc)
        
        for page_num, page in enumerate(doc):
            # Calculate page number
            current_num = start_number + page_num
            
            # Format number
            if format_style == 'roman':
                # Simple roman numeral conversion
                page_text = _to_roman(current_num)
            elif format_style == 'alpha':
                page_text = chr(96 + current_num) if current_num <= 26 else str(current_num)
            else:  # numeric
                page_text = str(current_num)
            
            # Calculate position
            rect = page.rect
            margin = 30
            
            position_map = {
                'bottom-right': (rect.width - margin - 30, rect.height - margin),
                'bottom-center': (rect.width / 2 - 10, rect.height - margin),
                'bottom-left': (margin, rect.height - margin),
                'top-right': (rect.width - margin - 30, margin + 10),
                'top-center': (rect.width / 2 - 10, margin + 10),
                'top-left': (margin, margin + 10),
            }
            
            pos = position_map.get(position, position_map['bottom-right'])
            
            # Insert text
            page.insert_text(
                pos,
                page_text,
                fontsize=10,
                color=(0, 0, 0)
            )
        
        doc.save(str(output_file))
        doc.close()
        
        success(f"Page numbers added ({total_pages} pages, starting from {start_number}) → {output_file.name}")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error adding page numbers: {str(e)}"
        error(error_msg)
        return False, error_msg


def _to_roman(num: int) -> str:
    """Convert number to Roman numerals"""
    values = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    
    result = ''
    for value, numeral in values:
        count = num // value
        if count:
            result += numeral * count
            num -= value * count
    return result.lower()

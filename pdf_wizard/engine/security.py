"""
PDF Security Module

Handles password protection and watermarking for PDFs.
"""

from pathlib import Path
from typing import Optional, Tuple
from PyPDF2 import PdfReader, PdfWriter
import click

from pdf_wizard.utils import (
    success, error, warning, info,
    get_file_size, format_file_size
)


def add_password(
    input_file: Path,
    output_file: Path,
    user_password: str,
    owner_password: Optional[str] = None,
    allow_printing: bool = True,
    allow_commenting: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Add password protection to a PDF
    
    Args:
        input_file: Input PDF file
        output_file: Output protected PDF file
        user_password: Password required to open the PDF
        owner_password: Password for permission restrictions (optional)
        allow_printing: Whether to allow printing
        allow_commenting: Whether to allow commenting/annotations
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Adding password protection to {input_file.name}...")
        
        reader = PdfReader(str(input_file))
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Copy metadata if exists
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        
        # Set owner password (defaults to user password if not provided)
        if not owner_password:
            owner_password = user_password
        
        # Encrypt with permissions
        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            permissions_flag=(
                (4 if allow_printing else 0) |  # Printing
                (32 if allow_commenting else 0)  # Commenting
            )
        )
        
        # Write protected PDF
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        file_size = format_file_size(get_file_size(output_file))
        success(f"Password protection added → {output_file.name} ({file_size})")
        info(f"User password: {'*' * len(user_password)}")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error adding password protection: {str(e)}"
        error(error_msg)
        return False, error_msg


def add_watermark(
    input_file: Path,
    watermark_pdf: Path,
    output_file: Path,
    opacity: float = 0.3
) -> Tuple[bool, Optional[str]]:
    """
    Add a watermark to every page of a PDF
    
    Args:
        input_file: Input PDF file
        watermark_pdf: PDF file containing the watermark
        output_file: Output watermarked PDF file
        opacity: Watermark opacity (0.0 to 1.0, where 0.3 is subtle)
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Adding watermark to {input_file.name}...")
        
        # Read input PDF
        reader = PdfReader(str(input_file))
        watermark_reader = PdfReader(str(watermark_pdf))
        
        if len(watermark_reader.pages) == 0:
            error_msg = "Watermark PDF has no pages"
            error(error_msg)
            return False, error_msg
        
        # Get the watermark page (use first page)
        watermark_page = watermark_reader.pages[0]
        
        writer = PdfWriter()
        
        # Apply watermark to each page
        for page_num, page in enumerate(reader.pages):
            # Merge watermark onto page
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        # Copy metadata
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        
        # Write output
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        file_size = format_file_size(get_file_size(output_file))
        success(f"Watermark applied to {len(reader.pages)} pages → {output_file.name} ({file_size})")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error adding watermark: {str(e)}"
        error(error_msg)
        return False, error_msg


def create_text_watermark(
    text: str,
    output_file: Path,
    font_size: int = 60,
    rotation: int = 45
) -> Tuple[bool, Optional[str]]:
    """
    Create a text-based watermark PDF
    
    Note: This is a simple implementation. For production use,
    consider using reportlab or similar library for better text rendering.
    
    Args:
        text: Watermark text
        output_file: Output PDF path
        font_size: Font size for watermark
        rotation: Rotation angle in degrees
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        # For text watermarks, we need reportlab
        # This is a placeholder - will use PyMuPDF instead for better control
        from io import BytesIO
        import fitz  # PyMuPDF
        
        # Create a simple watermark PDF
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4 size
        
        # Add text with rotation
        text_point = fitz.Point(297, 421)  # Center of A4
        
        # Insert rotated text
        page.insert_text(
            text_point,
            text,
            fontsize=font_size,
            rotate=rotation,
            color=(0.8, 0.8, 0.8),  # Light gray
            overlay=True
        )
        
        doc.save(str(output_file))
        doc.close()
        
        success(f"Text watermark created → {output_file.name}")
        return True, None
        
    except ImportError:
        error_msg = "PyMuPDF (fitz) required for text watermarks. Install with: pip install PyMuPDF"
        error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error creating text watermark: {str(e)}"
        error(error_msg)
        return False, error_msg


def check_encryption(pdf_path: Path) -> bool:
    """
    Check if a PDF is encrypted/password protected
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        True if encrypted, False otherwise
    """
    try:
        reader = PdfReader(str(pdf_path))
        return reader.is_encrypted
    except Exception:
        return False


def remove_password(
    input_file: Path,
    output_file: Path,
    password: str
) -> Tuple[bool, Optional[str]]:
    """
    Remove password protection from a PDF
    
    Args:
        input_file: Encrypted PDF file
        output_file: Output unencrypted PDF
        password: Password to decrypt the PDF
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Removing password from {input_file.name}...")
        
        reader = PdfReader(str(input_file))
        
        if not reader.is_encrypted:
            warning(f"{input_file.name} is not encrypted")
            # Just copy the file
            with open(output_file, 'wb') as out_f:
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                writer.write(out_f)
            return True, None
        
        # Decrypt
        if not reader.decrypt(password):
            error_msg = "Invalid password"
            error(error_msg)
            return False, error_msg
        
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Copy metadata
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        
        # Write unencrypted PDF
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        success(f"Password removed → {output_file.name}")
        return True, None
        
    except Exception as e:
        error_msg = f"Error removing password: {str(e)}"
        error(error_msg)
        return False, error_msg

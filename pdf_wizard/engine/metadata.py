"""
PDF Metadata Module

Handles viewing and stripping metadata from PDFs for privacy.
"""

from pathlib import Path
from typing import Optional, Tuple, Dict, List
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

from pdf_wizard.utils import (
    success, error, warning, info,
    get_file_size, format_file_size
)


def view_metadata(pdf_path: Path) -> Dict[str, str]:
    """
    View metadata information from a PDF
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Dictionary of metadata fields
    """
    try:
        reader = PdfReader(str(pdf_path))
        
        metadata = {}
        
        if reader.metadata:
            for key, value in reader.metadata.items():
                # Clean up key (remove leading slash)
                clean_key = key.lstrip('/')
                metadata[clean_key] = str(value) if value else "N/A"
        
        # Add file info
        metadata['PageCount'] = str(len(reader.pages))
        metadata['FileSize'] = format_file_size(get_file_size(pdf_path))
        metadata['IsEncrypted'] = str(reader.is_encrypted)
        
        return metadata
        
    except Exception as e:
        error(f"Error reading metadata: {str(e)}")
        return {}


def display_metadata(pdf_path: Path) -> None:
    """
    Display metadata in a formatted way
    
    Args:
        pdf_path: Path to PDF file
    """
    info(f"Metadata for: {pdf_path.name}")
    print()
    
    metadata = view_metadata(pdf_path)
    
    if not metadata:
        warning("No metadata found or error reading file")
        return
    
    # Common metadata fields to display first
    priority_fields = [
        'Title', 'Author', 'Subject', 'Creator', 'Producer',
        'CreationDate', 'ModDate', 'PageCount', 'FileSize', 'IsEncrypted'
    ]
    
    # Display priority fields first
    for field in priority_fields:
        if field in metadata:
            print(f"  {field:15} : {metadata[field]}")
    
    # Display any remaining fields
    for field, value in metadata.items():
        if field not in priority_fields:
            print(f"  {field:15} : {value}")
    
    print()


def strip_metadata(
    input_file: Path,
    output_file: Path,
    fields: str = 'all',
    fields_to_strip: Optional[List[str]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Remove metadata from a PDF for privacy
    
    Args:
        input_file: Input PDF file
        output_file: Output PDF with metadata stripped
        fields: 'all' to strip all metadata, or 'selective' to strip specific fields
        fields_to_strip: List of field names to strip (for selective mode)
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Stripping metadata from {input_file.name}...")
        
        reader = PdfReader(str(input_file))
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        if fields == 'all':
            # Don't copy any metadata - creates a clean PDF
            info("Removing all metadata fields")
        elif fields == 'selective' and fields_to_strip:
            # Copy metadata but exclude specified fields
            if reader.metadata:
                new_metadata = {}
                for key, value in reader.metadata.items():
                    clean_key = key.lstrip('/')
                    if clean_key not in fields_to_strip:
                        new_metadata[key] = value
                
                if new_metadata:
                    writer.add_metadata(new_metadata)
                    info(f"Removed {len(fields_to_strip)} metadata fields")
        else:
            # Invalid options
            error_msg = "Invalid fields option. Use 'all' or specify fields_to_strip for 'selective'"
            error(error_msg)
            return False, error_msg
        
        # Write output
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        file_size = format_file_size(get_file_size(output_file))
        success(f"Metadata stripped → {output_file.name} ({file_size})")
        
        # Show what was removed
        if fields == 'all' and reader.metadata:
            removed_fields = [key.lstrip('/') for key in reader.metadata.keys()]
            info(f"Removed fields: {', '.join(removed_fields)}")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error stripping metadata: {str(e)}"
        error(error_msg)
        return False, error_msg


def add_metadata(
    input_file: Path,
    output_file: Path,
    metadata: Dict[str, str]
) -> Tuple[bool, Optional[str]]:
    """
    Add or update metadata in a PDF
    
    Args:
        input_file: Input PDF file
        output_file: Output PDF with updated metadata
        metadata: Dictionary of metadata fields to add/update
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Adding metadata to {input_file.name}...")
        
        reader = PdfReader(str(input_file))
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Start with existing metadata
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        
        # Add/update new metadata
        writer.add_metadata(metadata)
        
        # Write output
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        success(f"Metadata updated → {output_file.name}")
        info(f"Updated fields: {', '.join(metadata.keys())}")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error adding metadata: {str(e)}"
        error(error_msg)
        return False, error_msg

"""
Image Processing Module

Handles image resizing, compression, and conversion for academic applications.
Perfect for passport photos, diagrams, and document submissions with size limits.
"""

from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image
import fitz  # PyMuPDF
import io

from pdf_wizard.utils import (
    success, error, warning, info,
    create_progress_bar, get_file_size, format_file_size
)


def resize_image(
    input_file: Path,
    output_file: Path,
    target_size_kb: Optional[int] = None,
    dimensions: Optional[Tuple[int, int]] = None,
    output_format: str = 'JPEG',
    max_iterations: int = 10
) -> Tuple[bool, Optional[str]]:
    """
    Resize and compress image to meet size and/or dimension requirements
    Perfect for passport photos and application forms
    
    Args:
        input_file: Input image file
        output_file: Output image file
        target_size_kb: Target file size in KB (e.g., 50 for 50KB)
        dimensions: Target dimensions (width, height) in pixels
        output_format: Output format ('JPEG', 'PNG')
        max_iterations: Maximum attempts to hit target size
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        original_size = get_file_size(input_file)
        info(f"Processing {input_file.name} ({format_file_size(original_size)})...")
        
        # Open image
        img = Image.open(input_file)
        original_dimensions = img.size
        
        # Handle transparency for JPEG
        if output_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Step 1: Resize to dimensions if specified
        if dimensions:
            target_width, target_height = dimensions
            info(f"Resizing from {original_dimensions[0]}x{original_dimensions[1]} to {target_width}x{target_height}...")
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Step 2: Compress to target size if specified
        if target_size_kb:
            target_bytes = target_size_kb * 1024
            info(f"Compressing to ≤{target_size_kb} KB...")
            
            # For PNG, we just maximize compression
            if output_format.upper() == 'PNG':
                # PNG is lossless, so quality param doesn't apply the same way
                img.save(output_file, format='PNG', optimize=True, compress_level=9)
                final_size = get_file_size(output_file)
                if final_size > target_bytes:
                    # If still too big, warn user. Converting to JPEG is the only real way to get small sizes
                    warning(f"PNG compression limit reached ({format_file_size(final_size)}). Try JPEG for smaller sizes.")
            else:
                # JPEG Binary search for optimal quality
                # We start much lower to guarantee hitting the target
                quality_low, quality_high = 5, 95
                best_quality = 5  # Default to low if we fail
                
                found_solution = False
                
                # First check if 95 works (high quality)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95, optimize=True)
                if buffer.tell() <= target_bytes:
                    best_quality = 95
                    found_solution = True
                else:
                    # Search
                    for attempt in range(max_iterations):
                        quality = (quality_low + quality_high) // 2
                        
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG', quality=quality, optimize=True)
                        current_size = buffer.tell()
                        
                        if current_size <= target_bytes:
                            best_quality = quality # valid, try higher
                            quality_low = quality + 1
                            found_solution = True
                        else:
                            quality_high = quality - 1
                        
                        if quality_high < quality_low:
                            break
                
                # Save with best found
                if not found_solution:
                    # Even lowest quality was too big? Resize it down?
                    # For now just save at lowest quality
                    best_quality = 5
                    warning("Could not meet target size even at lowest quality.")

                with open(output_file, 'wb') as f:
                    img.save(f, format='JPEG', quality=best_quality, optimize=True)
                
            final_size = get_file_size(output_file)
            success(f"Image processed: {format_file_size(original_size)} → {format_file_size(final_size)}")
            
        else:
            # Just save with high quality
            img.save(output_file, format=output_format, quality=90, optimize=True)
            final_size = get_file_size(output_file)
            success(f"Image saved: {format_file_size(original_size)} → {format_file_size(final_size)}")
        
        # Show dimensions if changed
        if dimensions:
            final_img = Image.open(output_file)
            info(f"Final dimensions: {final_img.width}x{final_img.height}")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        error(error_msg)
        return False, error_msg


def compress_image(
    input_file: Path,
    output_file: Path,
    target_size_kb: int,
    preserve_transparency: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Compress image to target file size
    
    Args:
        input_file: Input image file
        output_file: Output compressed image
        target_size_kb: Target size in KB
        preserve_transparency: Keep transparency (forces PNG format)
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    output_format = 'PNG' if preserve_transparency else 'JPEG'
    return resize_image(input_file, output_file, target_size_kb=target_size_kb, output_format=output_format)


import concurrent.futures
import os

# ... (previous imports)

def _process_single_image(args):
    """Helper for batch image processing to enable pickling"""
    img_file, output_dir, target_size_kb, dimensions, output_format = args
    output_path = output_dir / f"{img_file.stem}.{output_format.lower()}"
    return resize_image(
        img_file, output_path, target_size_kb, dimensions, output_format
    )

def batch_image_resize(
    input_dir: Path,
    output_dir: Path,
    target_size_kb: Optional[int] = None,
    dimensions: Optional[Tuple[int, int]] = None,
    output_format: str = 'JPEG'
) -> Tuple[bool, Optional[str]]:
    """
    Batch process multiple images using Parallel Processing
    """
    try:
        # Find all images
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_dir.glob(ext))
            image_files.extend(input_dir.glob(ext.upper()))
        
        if not image_files:
            error_msg = f"No images found in {input_dir}"
            error(error_msg)
            return False, error_msg
        
        info(f"Processing {len(image_files)} images using {os.cpu_count()} CPU cores...")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare arguments for parallel processing
        tasks = [
            (f, output_dir, target_size_kb, dimensions, output_format) 
            for f in image_files
        ]
        
        processed = 0
        failed = 0
        
        progress = create_progress_bar(len(image_files), "Processing images (Parallel)")
        
        # Use ProcessPoolExecutor to use all CPU cores
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Map returns results in order
            results = list(executor.map(_process_single_image, tasks))
            
            for success_flag, _ in results:
                if success_flag:
                    processed += 1
                else:
                    failed += 1
                progress.update(1)
                
        progress.close()
        
        if failed == 0:
            success(f"Batch processing complete: {processed} images processed")
        else:
            warning(f"Batch processing complete: {processed} succeeded, {failed} failed")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error in batch processing: {str(e)}"
        error(error_msg)
        return False, error_msg


def image_to_pdf(
    image_files: List[Path],
    output_pdf: Path
) -> Tuple[bool, Optional[str]]:
    """
    Convert one or more images to a PDF
    
    Args:
        image_files: List of image file paths
        output_pdf: Output PDF path
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        info(f"Converting {len(image_files)} images to PDF...")
        
        # Open first image to get document started
        first_img = Image.open(image_files[0])
        
        # Convert all images to RGB
        images = []
        for img_path in image_files:
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        
        # Save as PDF
        first_img = images[0]
        other_images = images[1:] if len(images) > 1 else None
        
        if other_images:
            first_img.save(
                output_pdf,
                save_all=True,
                append_images=other_images,
                resolution=100.0,
                quality=90
            )
        else:
            first_img.save(output_pdf, resolution=100.0, quality=90)
        
        file_size = format_file_size(get_file_size(output_pdf))
        success(f"Created PDF with {len(image_files)} images → {output_pdf.name} ({file_size})")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Error converting images to PDF: {str(e)}"
        error(error_msg)
        return False, error_msg


def _process_pdf_page_chunk(args):
    """Render a chunk of pages to images"""
    input_pdf_path, output_dir, output_format, dpi, page_indices = args
    
    doc = fitz.open(str(input_pdf_path))
    processed_count = 0
    
    for page_num in page_indices:
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        
        output_path = output_dir / f"{Path(input_pdf_path).stem}_page_{page_num + 1}.{output_format.lower()}"
        
        if output_format.upper() == 'PNG':
            pix.save(output_path)
        else:
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(output_path, format=output_format, quality=90)
        
        processed_count += 1
        
    doc.close()
    return processed_count

def pdf_to_images(
    input_pdf: Path,
    output_dir: Path,
    output_format: str = 'PNG',
    dpi: int = 300
) -> Tuple[bool, Optional[str]]:
    """
    Extract all pages from a PDF as images using Parallel Processing
    """
    try:
        info(f"Extracting pages from {input_pdf.name} at {dpi} DPI using {os.cpu_count()} cores...")
        
        doc = fitz.open(str(input_pdf))
        page_count = len(doc)
        doc.close() # Close in main thread, workers will open their own
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine chunk size for workers
        num_cores = os.cpu_count() or 4
        chunk_size = max(1, page_count // num_cores)
        
        # Create chunks of page indices
        chunks = []
        for i in range(0, page_count, chunk_size):
            # Create a range of page numbers for this chunk
            page_indices = list(range(i, min(i + chunk_size, page_count)))
            chunks.append((input_pdf, output_dir, output_format, dpi, page_indices))
            
        progress = create_progress_bar(page_count, "Extracting pages (Parallel)")
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # We use submit here to update progress bar as chunks complete
            futures = [executor.submit(_process_pdf_page_chunk, chunk) for chunk in chunks]
            
            completed_pages = 0
            for future in concurrent.futures.as_completed(futures):
                count = future.result()
                completed_pages += count
                progress.update(count)
                
        progress.close()
        
        success(f"Extracted {page_count} pages to {output_dir}")
        return True, None
        
    except Exception as e:
        error_msg = f"Error extracting images from PDF: {str(e)}"
        error(error_msg)
        return False, error_msg

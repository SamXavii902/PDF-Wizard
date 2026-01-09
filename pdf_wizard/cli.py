"""
PDF Wizard CLI - Command Line Interface

Main entry point for the PDF Wizard tool.
Provides all commands for PDF and image manipulation.
"""

import click
from pathlib import Path
import sys

from pdf_wizard.controller import Controller
from pdf_wizard.utils import parse_size_string, info, success
from pdf_wizard import __version__


@click.group()
@click.version_option(version=__version__, prog_name="PDF Wizard CLI")
def cli():
    """
    🧙 PDF Wizard CLI - Your Swiss Army Knife for Academic PDFs
    
    A modular, privacy-focused tool for PDF manipulation.
    All processing happens locally - your documents never leave your machine.
    
    Examples:
    
        pdf-wizard merge file1.pdf file2.pdf -o combined.pdf
        
        pdf-wizard compress large.pdf -o small.pdf --target-size 2.0
        
        pdf-wizard resize-image photo.jpg -o passport.jpg --dimensions 600x600 --target-size 50
    """
    pass


# ============================================================================
# PDF OPERATIONS
# ============================================================================

@cli.command()
@click.argument('input_files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('-o', '--output', required=True, help='Output PDF file')
def merge(input_files, output):
    """
    Merge multiple PDF files into one
    
    Example: pdf-wizard merge file1.pdf file2.pdf file3.pdf -o combined.pdf
    """
    Controller.merge_pdfs(list(input_files), output)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output-dir', required=True, help='Output directory for split files')
@click.option('--mode', type=click.Choice(['pages', 'ranges']), default='pages',
              help='Split mode: pages (one file per page) or ranges (custom ranges)')
@click.option('--ranges', help='Page ranges for split (e.g., "1-5,6-10,11-15")')
def split(input_file, output_dir, mode, ranges):
    """
    Split a PDF into multiple files
    
    Examples:
        pdf-wizard split document.pdf -o output/
        pdf-wizard split document.pdf -o output/ --mode ranges --ranges "1-5,6-10"
    """
    range_list = ranges.split(',') if ranges else None
    Controller.split_pdf(input_file, output_dir, mode, range_list)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output protected PDF')
@click.option('-p', '--password', required=True, help='Password to protect the PDF')
@click.option('--owner-password', help='Owner password (optional, defaults to user password)')
def protect(input_file, output, password, owner_password):
    """
    Add password protection to a PDF
    
    Example: pdf-wizard protect document.pdf -o protected.pdf -p mypassword
    """
    Controller.protect_pdf(input_file, output, password, owner_password)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output PDF with watermark')
@click.option('-w', '--watermark', required=True, type=click.Path(exists=True),
              help='Watermark PDF file')
def watermark(input_file, output, watermark):
    """
    Add a watermark to every page of a PDF
    
    Example: pdf-wizard watermark document.pdf -o watermarked.pdf -w watermark.pdf
    """
    Controller.watermark_pdf(input_file, watermark, output)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output compressed PDF')
@click.option('-t', '--target-size', default='2.0',
              help='Target size (e.g., "2.0" for 2MB, "500KB", "1.5MB")')
@click.option('-q', '--quality', type=click.Choice(['low', 'medium', 'high']),
              default='medium', help='Compression quality preset')
def compress(input_file, output, target_size, quality):
    """
    Compress PDF to meet custom size target using smart 3-stage compression
    
    Examples:
        pdf-wizard compress large.pdf -o small.pdf --target-size 2.0
        pdf-wizard compress thesis.pdf -o compressed.pdf -t 1.5MB -q medium
        pdf-wizard compress report.pdf -o tiny.pdf -t 500KB -q low
    """
    try:
        size_mb = parse_size_string(target_size)
        Controller.compress_pdf(input_file, output, size_mb, quality)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output PDF with metadata stripped')
def strip_metadata(input_file, output):
    """
    Remove all metadata from PDF for privacy
    
    Example: pdf-wizard strip-metadata document.pdf -o clean.pdf
    """
    Controller.strip_metadata_pdf(input_file, output)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def view_metadata(input_file):
    """
    View PDF metadata information
    
    Example: pdf-wizard view-metadata document.pdf
    """
    Controller.view_metadata_pdf(input_file)


# ============================================================================
# IMAGE OPERATIONS
# ============================================================================

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output image file')
@click.option('-s', '--target-size', type=int, help='Target file size in KB (e.g., 50 for 50KB)')
@click.option('-d', '--dimensions', help='Target dimensions (e.g., "600x600")')
@click.option('-f', '--format', type=click.Choice(['JPEG', 'PNG']),
              default='JPEG', help='Output format')
def resize_image(input_file, output, target_size, dimensions, format):
    """
    Resize and compress an image - perfect for passport photos and applications
    
    Examples:
        pdf-wizard resize-image photo.jpg -o passport.jpg -s 50 -d 600x600
        pdf-wizard resize-image large.png -o compressed.jpg -s 100 -f JPEG
        pdf-wizard resize-image diagram.png -o resized.png -d 1024x768
    """
    Controller.resize_image_file(input_file, output, target_size, dimensions, format)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output compressed image')
@click.option('-s', '--target-size', type=int, required=True,
              help='Target file size in KB')
@click.option('--preserve-transparency', is_flag=True,
              help='Preserve transparency (forces PNG format)')
def compress_image(input_file, output, target_size, preserve_transparency):
    """
    Compress an image to target file size
    
    Example: pdf-wizard compress-image large.png -o small.jpg -s 100
    """
    from pdf_wizard.engine.image_processor import compress_image as comp_img
    from pdf_wizard.utils import validate_file_exists
    
    try:
        img_path = validate_file_exists(input_file)
        output_path = Path(output)
        comp_img(img_path, output_path, target_size, preserve_transparency)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('image_files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('-o', '--output', required=True, help='Output PDF file')
def img2pdf(image_files, output):
    """
    Convert one or more images to a PDF
    
    Example: pdf-wizard img2pdf image1.jpg image2.jpg image3.jpg -o combined.pdf
    """
    Controller.image_to_pdf_convert(list(image_files), output)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output-dir', required=True, help='Output directory for images')
@click.option('-f', '--format', type=click.Choice(['PNG', 'JPEG']),
              default='PNG', help='Output image format')
@click.option('--dpi', type=int, default=300, help='Resolution in DPI')
def pdf2img(input_file, output_dir, format, dpi):
    """
    Extract PDF pages as images
    
    Example: pdf-wizard pdf2img document.pdf -o images/ --format PNG --dpi 300
    """
    Controller.pdf_to_images_convert(input_file, output_dir, format, dpi)


# ============================================================================
# ACADEMIC-SPECIFIC OPERATIONS
# ============================================================================

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output PDF with blank pages removed')
@click.option('-t', '--threshold', type=float, default=0.98,
              help='Whiteness threshold (0.0-1.0, default 0.98)')
def remove_blanks(input_file, output, threshold):
    """
    Remove blank pages from scanned PDF
    
    Example: pdf-wizard remove-blanks scanned.pdf -o clean.pdf
    """
    Controller.remove_blank_pages_pdf(input_file, output, threshold)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output PDF with corrected orientation')
def auto_rotate(input_file, output):
    """
    Auto-rotate pages to correct orientation
    
    Example: pdf-wizard auto-rotate tilted.pdf -o corrected.pdf
    """
    Controller.auto_rotate_pdf(input_file, output)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output PDF with reordered pages')
@click.option('--order', required=True, help='New page order (e.g., "1,3,2,4-10")')
def reorder(input_file, output, order):
    """
    Reorder pages in a PDF
    
    Example: pdf-wizard reorder document.pdf -o reordered.pdf --order "1,3,2,4-10"
    """
    Controller.reorder_pdf_pages(input_file, output, order)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output QR code PNG file')
def qr_share(input_file, output):
    """
    Generate QR code with document hash for verification
    
    Example: pdf-wizard qr-share thesis.pdf -o verification_qr.png
    """
    Controller.generate_qr_code(input_file, output)


@cli.command()
@click.argument('original', type=click.Path(exists=True))
@click.argument('modified', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output comparison PDF')
def compare(original, modified, output):
    """
    Compare two PDFs and show differences
    
    Example: pdf-wizard compare draft_v1.pdf draft_v2.pdf -o diff.pdf
    """
    Controller.compare_pdfs_files(original, modified, output)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='Output PDF with page numbers')
@click.option('--position', type=click.Choice([
    'bottom-right', 'bottom-center', 'bottom-left',
    'top-right', 'top-center', 'top-left'
]), default='bottom-right', help='Page number position')
@click.option('--start', type=int, default=1, help='Starting page number')
@click.option('--format', 'number_format', type=click.Choice(['numeric', 'roman', 'alpha']),
              default='numeric', help='Number format')
def add_numbers(input_file, output, position, start, number_format):
    """
    Add page numbers to a PDF
    
    Example: pdf-wizard add-numbers document.pdf -o numbered.pdf --position bottom-right
    """
    Controller.add_page_numbers_pdf(input_file, output, position, start, number_format)


# ============================================================================
# HELP & INFO
# ============================================================================

@cli.command()
def examples():
    """Show example commands for common tasks"""
    examples_text = """
    🎯 PDF WIZARD - COMMON EXAMPLES
    
    📄 PDF Operations:
      Merge PDFs:
        pdf-wizard merge lab1.pdf lab2.pdf lab3.pdf -o complete_lab.pdf
      
      Compress to 2MB:
        pdf-wizard compress thesis.pdf -o compressed.pdf --target-size 2.0
      
      Compress to 500KB (aggressive):
        pdf-wizard compress report.pdf -o small.pdf -t 500KB -q low
      
      Password protect:
        pdf-wizard protect sensitive.pdf -o protected.pdf -p mypassword
      
      Remove metadata for privacy:
        pdf-wizard strip-metadata document.pdf -o anonymous.pdf
    
    📸 Image Operations:
      Passport photo (50KB, 600x600px):
        pdf-wizard resize-image photo.jpg -o passport.jpg -s 50 -d 600x600
      
      Compress image to 100KB:
        pdf-wizard resize-image diagram.png -o small.jpg -s 100
      
      Convert images to PDF:
        pdf-wizard img2pdf page1.jpg page2.jpg page3.jpg -o document.pdf
    
    🎓 Academic Features:
      Remove blank pages from scan:
        pdf-wizard remove-blanks scanned_notebook.pdf -o clean.pdf
      
      Reorder pages (swap pages 2 and 3):
        pdf-wizard reorder assignment.pdf -o fixed.pdf --order "1,3,2,4-10"
      
      Generate verification QR code:
        pdf-wizard qr-share final_thesis.pdf -o qr_code.png
      
      Add page numbers:
        pdf-wizard add-numbers report.pdf -o numbered.pdf --position bottom-right
      
      Compare two versions:
        pdf-wizard compare draft1.pdf draft2.pdf -o differences.pdf
    
    💡 Pro Tips:
      - All operations are offline - your data never leaves your machine
      - Use --help on any command for more options
      - Compression targets: "2MB", "500KB", or just "1.5" (assumes MB)
      - Quality presets: low (aggressive), medium (balanced), high (minimal loss)
    """
    click.echo(examples_text)


if __name__ == '__main__':
    cli()

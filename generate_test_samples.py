"""
Generate Sample PDFs for Testing using PyMuPDF
Creates various test PDFs with different characteristics
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw
from pathlib import Path
import os

# Create test_samples directory
SAMPLES_DIR = Path("test_samples")
SAMPLES_DIR.mkdir(exist_ok=True)

def create_text_pdf(filename, pages=5, lines_per_page=30):
    """Create a text-only PDF"""
    print(f"Creating {filename}...")
    
    filepath = SAMPLES_DIR / filename
    doc = fitz.open()
    
    for page_num in range(pages):
        page = doc.new_page(width=595, height=842)  # A4 size
        
        # Title
        page.insert_text((100, 100), f"Page {page_num + 1} of {pages}", 
                        fontsize=14, fontname="helv")
        
        # Content lines
        y = 150
        for i in range(lines_per_page):
            text = f"Line {i+1}: This is sample text for testing PDF manipulation features."
            page.insert_text((100, y), text, fontsize=10, fontname="helv")
            y += 15
            if y > 800:
                break
    
    doc.save(str(filepath))
    doc.close()
    
    size = os.path.getsize(filepath)
    print(f"  ✓ Created {filename} ({size / 1024:.1f} KB, {pages} pages)")

def create_image_pdf(filename, pages=3):
    """Create a PDF with embedded images"""
    print(f"Creating {filename}...")
    
    # Create temporary images
    temp_images = []
    for i in range(2):
        img = Image.new('RGB', (400, 300), color=(100 + i*50, 150, 200 - i*30))
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 350, 250], outline=(255, 255, 255), width=3)
        draw.text((150, 130), f"Image {i+1}", fill=(255, 255, 255))
        
        img_path = SAMPLES_DIR / f"temp_img_{i}.jpg"
        img.save(img_path, 'JPEG', quality=85)
        temp_images.append(img_path)
    
    # Create PDF
    filepath = SAMPLES_DIR / filename
    doc = fitz.open()
    
    for page_num in range(pages):
        page = doc.new_page(width=595, height=842)
        page.insert_text((100, 100), f"Image Page {page_num + 1}", 
                        fontsize=14, fontname="helvb")
        
        y_pos = 150
        for img_path in temp_images:
            page.insert_image(fitz.Rect(100, y_pos, 400, y_pos + 200), 
                            filename=str(img_path))
            y_pos += 250
    
    doc.save(str(filepath))
    doc.close()
    
    # Clean up temp images
    for img_path in temp_images:
        img_path.unlink()
    
    size = os.path.getsize(filepath)
    print(f"  ✓ Created {filename} ({size / 1024:.1f} KB, {pages} pages)")

def create_blank_pages_pdf(filename):
    """Create PDF with blank pages for removal testing"""
    print(f"Creating {filename}...")
    
    filepath = SAMPLES_DIR / filename
    doc = fitz.open()
    
    # Page 1: Content
    page = doc.new_page()
    page.insert_text((100, 100), "Page 1: This page has content", fontsize=12)
    
    # Page 2: Blank
    doc.new_page()
    
    # Page 3: Content
    page = doc.new_page()
    page.insert_text((100, 100), "Page 3: More content here", fontsize=12)
    
    # Page 4: Blank
    doc.new_page()
    
    # Page 5: Content
    page = doc.new_page()
    page.insert_text((100, 100), "Page 5: Final content page", fontsize=12)
    
    doc.save(str(filepath))
    doc.close()
    
    size = os.path.getsize(filepath)
    print(f"  ✓ Created {filename} ({size / 1024:.1f} KB, 5 pages with 2 blanks)")

def create_test_images():
    """Create test images for image processing"""
    print("Creating test images...")
    
    # Large image
    img_large = Image.new('RGB', (1600, 1600), color=(120, 160, 200))
    draw = ImageDraw.Draw(img_large)
    draw.ellipse([400, 400, 1200, 1200], fill=(200, 150, 150))
    draw.text((680, 760), "LARGE", fill=(255, 255, 255))
    large_path = SAMPLES_DIR / "large_image.jpg"
    img_large.save(large_path, 'JPEG', quality=95)
    print(f"  ✓ large_image.jpg ({os.path.getsize(large_path) / 1024:.1f} KB)")
    
    #Photo for passport test
    img_photo = Image.new('RGB', (1200, 1200), color=(220, 200, 180))
    draw = ImageDraw.Draw(img_photo)
    draw.ellipse([200, 200, 1000, 1000], fill=(255, 220, 200), outline=(100, 100, 100), width=5)
    draw.rectangle([500, 450, 700, 550], fill=(80, 80, 80))  # Eyes
    draw.arc([400, 600, 800, 750], 0, 180, fill=(100, 100, 100), width=3)  # Smile
    photo_path = SAMPLES_DIR / "photo_test.jpg"
    img_photo.save(photo_path, 'JPEG', quality=90)
    print(f"  ✓ photo_test.jpg ({os.path.getsize(photo_path) / 1024:.1f} KB)")
    
    # Small images for img2pdf
    for i in range(3):
        img = Image.new('RGB', (600, 400), color=(80 + i*50, 120 + i*30, 180 - i*40))
        draw = ImageDraw.Draw(img)
        draw.text((250, 180), f"Page {i+1}", fill=(255, 255, 255))
        img_path = SAMPLES_DIR / f"page_{i+1}.jpg"
        img.save(img_path, 'JPEG', quality=85)
    print(f"  ✓ page_1.jpg, page_2.jpg, page_3.jpg")

def main():
    print("="*70)
    print("GENERATING TEST SAMPLES FOR PDF WIZARD CLI")
    print("="*70)
    print()
    
    # Text PDFs of various sizes
    create_text_pdf("small_text.pdf", pages=3, lines_per_page=15)
    create_text_pdf("medium_text.pdf", pages=10, lines_per_page=30)
    create_text_pdf("large_text.pdf", pages=30, lines_per_page=40)
    
    # Image PDFs
    create_image_pdf("small_images.pdf", pages=2)
    create_image_pdf("large_images.pdf", pages=8)
    
    # Special test PDF
    create_blank_pages_pdf("with_blanks.pdf")
    
    # Test images
    create_test_images()
    
    print()
    print("="*70)
    print(f"✓ ALL TEST SAMPLES GENERATED IN: {SAMPLES_DIR.absolute()}")
    print("="*70)
    
    # List all files
    print("\nGenerated files:")
    for file in sorted(SAMPLES_DIR.iterdir()):
        if file.is_file():
            size = os.path.getsize(file) / 1024
            print(f"  - {file.name:30s} ({size:7.1f} KB)")

if __name__ == "__main__":
   main()

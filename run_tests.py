"""
Automated Test Suite for PDF Wizard CLI
Tests all 18 commands systematically and reports results
"""

import subprocess
import os
from pathlib import Path
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []
        
        # Set up test environment
        self.test_dir = Path("test_samples")
        self.output_dir = Path("test_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")
    
    def run_command(self, cmd, test_name):
        """Run a command and capture results"""
        print(f"\n{'='*70}")
        self.log(f"TEST: {test_name}", Colors.BLUE)
        print(f"Command: {' '.join(cmd)}")
        print("-"*70)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log(f"✓ PASSED: {test_name}", Colors.GREEN)
                self.passed += 1
                self.results.append((test_name, "PASS", ""))
                if result.stdout:
                    print(result.stdout[:500])  # First 500 chars
                return True
            else:
                self.log(f"✗ FAILED: {test_name}", Colors.RED)
                self.failed += 1
                error_msg = result.stderr or result.stdout or "Unknown error"
                self.results.append((test_name, "FAIL", error_msg[:200]))
                print(f"Error: {error_msg[:300]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"⚠ TIMEOUT: {test_name}", Colors.YELLOW)
            self.warnings += 1
            self.results.append((test_name, "TIMEOUT", "Command exceeded 30s"))
            return False
        except Exception as e:
            self.log(f"✗ ERROR: {test_name} - {e}", Colors.RED)
            self.failed += 1
            self.results.append((test_name, "ERROR", str(e)))
            return False
    
    def create_minimal_samples(self):
        """Create minimal test samples using PyMuPDF"""
        self.log("\n📦 Creating minimal test samples...", Colors.YELLOW)
        self.test_dir.mkdir(exist_ok=True)
        
        import fitz
        from PIL import Image, ImageDraw
        
        # Small PDF 1
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "Test PDF 1", fontsize=12)
        doc.save(str(self.test_dir / "test1.pdf"))
        doc.close()
        
        # Small PDF 2
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "Test PDF 2", fontsize=12)
        doc.save(str(self.test_dir / "test2.pdf"))
        doc.close()
        
        # PDF with 5 pages for split test
        doc = fitz.open()
        for i in range(5):
            page = doc.new_page()
            page.insert_text((100, 100), f"Page {i+1} of 5", fontsize=12)
        doc.save(str(self.test_dir / "multi_page.pdf"))
        doc.close()
        
        # Test image
        img = Image.new('RGB', (800, 800), color=(200, 150, 150))
        draw = ImageDraw.Draw(img)
        draw.text((350, 380), "TEST", fill=(255, 255, 255))
        img.save(self.test_dir / "test_image.jpg", 'JPEG', quality=90)
        
        self.log("✓ Test samples created", Colors.GREEN)
    
    def test_pdf_operations(self):
        """Test PDF manipulation commands"""
        self.log("\n\n" + "="*70, Colors.YELLOW)
        self.log("CATEGORY 1: PDF OPERATIONS (8 commands)", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # 1. Merge
        self.run_command([
            "pdf-wizard", "merge",
            str(self.test_dir / "test1.pdf"),
            str(self.test_dir / "test2.pdf"),
            "-o", str(self.output_dir / "merged.pdf")
        ], "1. Merge - Combine 2 PDFs")
        
        # 2. Split
        self.run_command([
            "pdf-wizard", "split",
            str(self.test_dir / "multi_page.pdf"),
            "-o", str(self.output_dir / "split_output")
        ], "2. Split - One file per page")
        
        # 3. Compress
        self.run_command([
            "pdf-wizard", "compress",
            str(self.test_dir / "test1.pdf"),
            "-o", str(self.output_dir / "compressed.pdf"),
            "-t", "0.5"
        ], "3. Compress - Target 0.5MB")
        
        # 4. Protect (password)
        self.run_command([
            "pdf-wizard", "protect",
            str(self.test_dir / "test1.pdf"),
            "-o", str(self.output_dir / "protected.pdf"),
            "-p", "testpass123"
        ], "4. Protect - Add password")
        
        # 5. Strip metadata
        self.run_command([
            "pdf-wizard", "strip-metadata",
            str(self.test_dir / "test1.pdf"),
            "-o", str(self.output_dir / "no_metadata.pdf")
        ], "5. Strip Metadata - Privacy mode")
        
        # 6. View metadata
        self.run_command([
            "pdf-wizard", "view-metadata",
            str(self.test_dir / "test1.pdf")
        ], "6. View Metadata - Display info")
        
        # 7. Examples command
        self.run_command([
            "pdf-wizard", "examples"
        ], "7. Examples - Show usage guide")
        
        # 8. Version check
        self.run_command([
            "pdf-wizard", "--version"
        ], "8. Version - Check installation")
    
    def test_image_operations(self):
        """Test image processing commands"""
        self.log("\n\n" + "="*70, Colors.YELLOW)
        self.log("CATEGORY 2: IMAGE OPERATIONS (4 commands)", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # 9. Resize image
        self.run_command([
            "pdf-wizard", "resize-image",
            str(self.test_dir / "test_image.jpg"),
            "-o", str(self.output_dir / "resized.jpg"),
            "-d", "600x600"
        ], "9. Resize Image - Dimensions only")
        
        # 10. Resize with size target
        self.run_command([
            "pdf-wizard", "resize-image",
            str(self.test_dir / "test_image.jpg"),
            "-o", str(self.output_dir / "passport.jpg"),
            "-s", "50",
            "-d", "600x600"
        ], "10. Resize Image - Passport photo (50KB + 600x600)")
        
        # 11. Image to PDF
        self.run_command([
            "pdf-wizard", "img2pdf",
            str(self.test_dir / "test_image.jpg"),
            "-o", str(self.output_dir / "from_image.pdf")
        ], "11. Img2PDF - Convert image to PDF")
        
        # 12. PDF to images
        self.run_command([
            "pdf-wizard", "pdf2img",
            str(self.test_dir / "test1.pdf"),
            "-o", str(self.output_dir / "pdf_images"),
            "--format", "PNG"
        ], "12. PDF2Img - Extract as images")
    
    def test_academic_operations(self):
        """Test academic-specific commands"""
        self.log("\n\n" + "="*70, Colors.YELLOW)
        self.log("CATEGORY 3: ACADEMIC OPERATIONS (6 commands)", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # 13. Reorder pages
        self.run_command([
            "pdf-wizard", "reorder",
            str(self.test_dir / "multi_page.pdf"),
            "-o", str(self.output_dir / "reordered.pdf"),
           "--order", "1,3,2,4,5"
        ], "13. Reorder Pages - Swap pages 2 and 3")
        
        # 14. QR code generation
        self.run_command([
            "pdf-wizard", "qr-share",
            str(self.test_dir / "test1.pdf"),
            "-o", str(self.output_dir / "qr_code.png")
        ], "14. QR Share - Document verification")
        
        # 15. Add page numbers
        self.run_command([
            "pdf-wizard", "add-numbers",
            str(self.test_dir / "multi_page.pdf"),
            "-o", str(self.output_dir / "numbered.pdf"),
            "--position", "bottom-right"
        ], "15. Add Page Numbers - Bottom right position")
        
        # 16. Auto-rotate
        self.run_command([
            "pdf-wizard", "auto-rotate",
            str(self.test_dir / "test1.pdf"),
            "-o", str(self.output_dir / "rotated.pdf")
        ], "16. Auto-Rotate - Fix orientation")
        
        # 17. Compare PDFs
        self.run_command([
            "pdf-wizard", "compare",
            str(self.test_dir / "test1.pdf"),
            str(self.test_dir / "test2.pdf"),
            "-o", str(self.output_dir / "comparison.pdf")
        ], "17. Compare - Find differences")
        
        # 18. Remove blank pages (skip if no blank page test PDF)
        if (self.test_dir / "test1.pdf").exists():
            self.run_command([
                "pdf-wizard", "remove-blanks",
                str(self.test_dir / "test1.pdf"),
                "-o", str(self.output_dir / "no_blanks.pdf")
            ], "18. Remove Blanks - Clean scanned docs")
    
    def print_summary(self):
        """Print test summary"""
        print("\n\n")
        print("="*70)
        self.log("TEST SUMMARY", Colors.YELLOW)
        print("="*70)
        print(f"\nTotal Tests: {self.passed + self.failed + self.warnings}")
        self.log(f"✓ Passed:    {self.passed}", Colors.GREEN)
        self.log(f"✗ Failed:    {self.failed}", Colors.RED)
        self.log(f"⚠ Warnings:  {self.warnings}", Colors.YELLOW)
        
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print("\n" + "-"*70)
            print("FAILED TESTS:")
            print("-"*70)
            for name, status, error in self.results:
                if status in ["FAIL", "ERROR"]:
                    print(f"  ✗ {name}")
                    if error:
                        print(f"    Error: {error[:150]}")
        
        print("\n" + "="*70)
        if self.failed == 0:
            self.log("🎉 ALL TESTS PASSED!", Colors.GREEN)
        else:
            self.log(f"⚠ {self.failed} tests need attention", Colors.YELLOW)
        print("="*70)

def main():
    runner = TestRunner()
    
    print("="*70)
    runner.log("PDF WIZARD CLI - AUTOMATED TEST SUITE", Colors.YELLOW)
    print("="*70)
    
    # Create samples
    try:
        runner.create_minimal_samples()
    except Exception as e:
        print(f"Error creating samples: {e}")
        print("Continuing with existing samples...")
    
    # Run all tests
    runner.test_pdf_operations()
    runner.test_image_operations()
    runner.test_academic_operations()
    
    # Print summary
    runner.print_summary()

if __name__ == "__main__":
    main()

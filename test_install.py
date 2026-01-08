"""
Quick Test Script for PDF Wizard CLI

Run this to verify the installation is working correctly.
"""

import sys

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from pdf_wizard import cli
        print("✅ CLI import successful")
        
        from pdf_wizard import controller
        print("✅ Controller import successful")
        
        from pdf_wizard.engine import merger, security, metadata, compressor, image_processor, academic
        print("✅ All engine modules import successful")
        
        from pdf_wizard import utils
        print("✅ Utils import successful")
        
        print("\n✨ All imports successful! PDF Wizard is ready to use.")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False

def show_version():
    """Display version information"""
    try:
        from pdf_wizard import __version__
        print(f"\n📦 PDF Wizard CLI version: {__version__}")
    except:
        print("\n⚠️  Could not determine version")

def show_next_steps():
    """Show what to do next"""
    print("\n" + "="*60)
    print("🚀 NEXT STEPS - Try These Commands:")
    print("="*60)
    print("\n1. Check version:")
    print("   pdf-wizard --version")
    print("\n2. View all commands:")
    print("   pdf-wizard --help")
    print("\n3. See examples:")
    print("   pdf-wizard examples")
    print("\n4. Test with your PDFs:")
    print("   pdf-wizard merge file1.pdf file2.pdf -o combined.pdf")
    print("   pdf-wizard compress large.pdf -o small.pdf -t 2.0")
    print("\n5. Image processing:")
    print("   pdf-wizard resize-image photo.jpg -o passport.jpg -s 50 -d 600x600")
    print("\n" + "="*60)

if __name__ == "__main__":
    print("="*60)
    print("📋 PDF WIZARD CLI - Installation Verification")
    print("="*60)
    print()
    
    success = test_imports()
    
    if success:
        show_version()
        show_next_steps()
        sys.exit(0)
    else:
        print("\n❌ Installation verification failed. Please check the error messages above.")
        sys.exit(1)

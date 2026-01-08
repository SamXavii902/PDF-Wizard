# 🧙 PDF Wizard CLI

> **Your Swiss Army Knife for Academic PDFs** - A modular, privacy-focused command-line tool for PDF manipulation designed specifically for academic use.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Why PDF Wizard?

Unlike online converters that expose your sensitive documents, **PDF Wizard runs entirely on your local machine**. Your lab reports, transcripts, and personal documents **never leave your computer**.

### 🎯 Key Features

- **🔒 Privacy-First**: 100% offline processing - zero network requests
- **📦 Smart Compression**: 3-stage intelligent compression to meet any size limit (500KB, 1.5MB, 2MB, etc.)
- **📸 Passport Photo Optimizer**: Resize & compress images to exact dimensions AND file size
- **🎓 Academic Innovations**: Blank page removal, auto-rotation, QR verification, and more
- **⚡ Batch Processing**: Process multiple files at once
- **🎨 Beautiful UX**: Colorful terminal output with real-time progress bars

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-wizard-cli.git
cd pdf-wizard-cli

# Install with pip
pip install -e .

# Verify installation
pdf-wizard --version
```

### Your First Commands

```bash
# Merge multiple PDFs
pdf-wizard merge file1.pdf file2.pdf file3.pdf -o combined.pdf

# Compress PDF to 2MB
pdf-wizard compress large.pdf -o small.pdf --target-size 2.0

# Create a passport photo (50KB, 600x600px)
pdf-wizard resize-image photo.jpg -o passport.jpg -s 50 -d 600x600
```

---

## 📚 Complete Feature Guide

### 📄 PDF Operations

#### Merge PDFs
```bash
pdf-wizard merge lab1.pdf lab2.pdf lab3.pdf -o complete_lab.pdf
```

#### Split PDF
```bash
# One file per page
pdf-wizard split document.pdf -o output_folder/

# Custom page ranges
pdf-wizard split document.pdf -o output_folder/ --mode ranges --ranges "1-5,6-10,11-15"
```

#### Compress with Custom Size Target
```bash
# For 2MB university portal
pdf-wizard compress thesis.pdf -o compressed.pdf --target-size 2.0

# For 500KB submission limit
pdf-wizard compress report.pdf -o tiny.pdf -t 500KB -q low

# High quality, moderate compression
pdf-wizard compress scan.pdf -o optimized.pdf -t 1.5MB -q high
```

**Quality Presets:**
- `low` - Aggressive compression (smallest size)
- `medium` - Balanced (default)
- `high` - Minimal loss (best quality)

#### Password Protection
```bash
pdf-wizard protect sensitive.pdf -o protected.pdf -p mypassword
```

#### Watermark
```bash
pdf-wizard watermark document.pdf -o watermarked.pdf -w watermark_file.pdf
```

#### Privacy Mode - Strip Metadata
```bash
pdf-wizard strip-metadata document.pdf -o clean.pdf
```

#### View Metadata
```bash
pdf-wizard view-metadata document.pdf
```

---

### 📸 Image Operations

#### Passport Photo Optimization
```bash
# Perfect for college applications: 50KB, 600x600px
pdf-wizard resize-image photo.jpg -o passport.jpg -s 50 -d 600x600

# Just resize dimensions
pdf-wizard resize-image large.jpg -o resized.jpg -d 1024x768

# Just compress to size
pdf-wizard resize-image photo.png -o compressed.jpg -s 100
```

#### Image Compression
```bash
pdf-wizard compress-image large.png -o small.jpg -s 100
```

#### Image ↔ PDF Conversion
```bash
# Multiple images to PDF
pdf-wizard img2pdf page1.jpg page2.jpg page3.jpg -o document.pdf

# PDF pages to images
pdf-wizard pdf2img document.pdf -o images/ --format PNG --dpi 300
```

---

### 🎓 Academic-Specific Features

#### Remove Blank Pages
Perfect for scanned lab notebooks that have extra blank pages:
```bash
pdf-wizard remove-blanks scanned_notebook.pdf -o clean.pdf
```

#### Auto-Rotate Pages
Fix tilted scanned documents:
```bash
pdf-wizard auto-rotate tilted_scan.pdf -o corrected.pdf
```

#### Reorder Pages
```bash
# Swap pages 2 and 3
pdf-wizard reorder document.pdf -o fixed.pdf --order "1,3,2,4-10"
```

#### QR Code Document Verification
Generate a QR code with your document's hash - share with professors to prove authenticity:
```bash
pdf-wizard qr-share final_thesis.pdf -o verification_qr.png
```

#### Compare PDF Versions
Track changes between assignment drafts:
```bash
pdf-wizard compare draft_v1.pdf draft_v2.pdf -o differences.pdf
```

#### Add Page Numbers
```bash
pdf-wizard add-numbers report.pdf -o numbered.pdf --position bottom-right --start 1
```

**Positions:** `bottom-right`, `bottom-center`, `bottom-left`, `top-right`, `top-center`, `top-left`

**Formats:** `numeric` (1,2,3), `roman` (i,ii,iii), `alpha` (a,b,c)

---

## 🎯 Real-World Examples

### Use Case 1: University Application
```bash
# Step 1: Optimize passport photo
pdf-wizard resize-image photo.jpg -o passport.jpg -s 50 -d 600x600

# Step 2: Compress marksheet to 500KB
pdf-wizard compress marksheet.pdf -o compressed_marksheet.pdf -t 500KB

# Step 3: Merge all documents
pdf-wizard merge passport.pdf compressed_marksheet.pdf certificates.pdf -o complete_application.pdf

# Step 4: Strip metadata for privacy
pdf-wizard strip-metadata complete_application.pdf -o final_application.pdf
```

### Use Case 2: Lab Report Submission
```bash
# Clean up scanned notebook
pdf-wizard remove-blanks scanned_lab.pdf -o step1.pdf
pdf-wizard auto-rotate step1.pdf -o step2.pdf
pdf-wizard add-numbers step2.pdf -o step3.pdf --position bottom-right

# Compress to 2MB portal limit
pdf-wizard compress step3.pdf -o final_lab.pdf -t 2.0

# Generate verification QR
pdf-wizard qr-share final_lab.pdf -o verification.png
```

### Use Case 3: Research Paper Revision
```bash
# Compare versions
pdf-wizard compare paper_v1.pdf paper_v2.pdf -o diff.pdf

# Prepare final version
pdf-wizard strip-metadata paper_final.pdf -o paper_clean.pdf
pdf-wizard split paper_clean.pdf -o sections/ --mode ranges --ranges "1-5,6-10,11-15"
```

---

## 🏗️ Architecture

PDF Wizard follows a modular 3-layer design:

```
pdf-wizard-cli/
├── pdf_wizard/
│   ├── cli.py              # Interface Layer - Command parsing
│   ├── controller.py       # Dispatcher Layer - Routing logic
│   ├── utils.py            # Helper functions
│   └── engine/             # Core Engine - PDF operations
│       ├── merger.py       # Merge & Split
│       ├── security.py     # Password & Watermark
│       ├── compressor.py   # Smart 3-stage compression
│       ├── image_processor.py  # Image optimization
│       ├── metadata.py     # Metadata operations
│       └── academic.py     # Academic features
├── tests/                  # Test files
├── requirements.txt
└── setup.py
```

---

## 🛠️ Technical Details

### Smart Compression System

PDF Wizard uses a sophisticated 3-stage approach:

1. **Image Downsampling** - Intelligently reduces image DPI based on target size
2. **Object Removal** - Strips metadata, duplicate fonts, and thumbnails
3. **Lossless Compression** - Compresses text streams without quality loss

The system iteratively adjusts compression levels to hit your exact target size (±5% tolerance).

### Privacy Guarantees

- ✅ **Zero network requests** - confirmed via network monitoring
- ✅ **All processing is local** - files never uploaded
- ✅ **Metadata stripping** - removes identifying information
- ✅ **No telemetry** - no data collection of any kind

---

## 📦 Dependencies

- **PyPDF2** - Core PDF operations
- **PyMuPDF (fitz)** - Advanced compression & image manipulation
- **Pillow** - Image processing
- **click** - CLI framework
- **tqdm** - Progress bars
- **qrcode** - QR code generation
- **python-dotenv** - Environment configuration

### Optional
- **pytesseract** - For OCR-based auto-rotation (requires Tesseract installation)

---

## 🎨 Examples Command

Get quick examples for any operation:

```bash
pdf-wizard examples
```

This displays a comprehensive guide with real-world command examples.

---

## 💡 Pro Tips

1. **Compression targets are flexible**: Use `"2MB"`, `"500KB"`, or just `"1.5"` (assumes MB)
2. **Quality matters**: Use `high` quality for important submissions, `low` for drafts
3. **Batch operations**: Process entire folders efficiently
4. **Chain commands**: Use output of one command as input to another
5. **Check file size first**: Use `view-metadata` to see current size before compressing

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

Built with ❤️ for students who deserve better tools for their academic work.

Special thanks to the open-source community for the amazing libraries that make this possible.

---

## 📞 Support

Having issues? Have questions?

1. Check the examples: `pdf-wizard examples`
2. Use `--help` on any command: `pdf-wizard compress --help`
3. Open an issue on GitHub

---

**Made with 🧙 by Vamsi** | [GitHub](https://github.com/yourusername) | [Portfolio](https://yoursite.com)

"""
PDF Wizard Engine - Core PDF manipulation modules

This package contains all the specialized engines for PDF operations:
- merger: PDF merge and split operations
- security: Password protection and watermarking
- compressor: Smart 3-stage compression system
- image_processor: Image resizing, compression, and conversion
- metadata: Metadata viewing and stripping
- academic: Academic-specific features (blank page removal, auto-rotation, etc.)
"""

__all__ = [
    "merger",
    "security",
    "compressor",
    "image_processor",
    "metadata",
    "academic"
]

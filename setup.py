"""
PDF Wizard CLI - Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="pdf-wizard-cli",
    version="1.0.0",
    author="Vamsi",
    description="High-performance, privacy-focused PDF manipulation tool for academic purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf-wizard-cli",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.0",
        "PyMuPDF>=1.23.0",
        "click>=8.1.0",
        "Pillow>=10.0.0",
        "tqdm>=4.65.0",
        "qrcode[pil]>=7.4.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        'ocr': ['pytesseract>=0.3.10'],
    },
    entry_points={
        'console_scripts': [
            'pdf-wizard=pdf_wizard.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    keywords='pdf merge split compress watermark academic passport-photo',
)

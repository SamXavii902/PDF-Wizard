"""
PDF Wizard CLI - A Swiss Army Knife for Academic PDF Operations

A modular, privacy-focused command-line tool for PDF manipulation designed 
for academic use, ensuring sensitive documents never leave your local machine.
"""

__version__ = "1.0.0"
__author__ = "Vamsi"
__description__ = "High-performance, privacy-focused PDF manipulation tool for academic purposes"

from pdf_wizard.cli import cli

__all__ = ["cli"]

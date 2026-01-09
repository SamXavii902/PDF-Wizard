"""
Utility functions for PDF Wizard CLI

Contains helper functions for path validation, file size formatting,
progress bars, and colored terminal output.
"""

import os
from pathlib import Path
from typing import Optional, List
import click
from tqdm import tqdm


class Colors:
    """ANSI color codes for terminal output"""
    SUCCESS = '\033[92m'  # Green
    ERROR = '\033[91m'    # Red
    WARNING = '\033[93m'  # Yellow
    INFO = '\033[94m'     # Blue
    RESET = '\033[0m'     # Reset


def success(message: str) -> None:
    """Print success message in green"""
    click.echo(f"{Colors.SUCCESS}✓ {message}{Colors.RESET}")


def error(message: str) -> None:
    """Print error message in red"""
    click.echo(f"{Colors.ERROR}✗ {message}{Colors.RESET}", err=True)


def warning(message: str) -> None:
    """Print warning message in yellow"""
    click.echo(f"{Colors.WARNING}⚠ {message}{Colors.RESET}")


def info(message: str) -> None:
    """Print info message in blue"""
    click.echo(f"{Colors.INFO}ℹ {message}{Colors.RESET}")


def validate_file_exists(file_path: str, extension: Optional[str] = None) -> Path:
    """
    Validate that a file exists and optionally check its extension
    
    Args:
        file_path: Path to the file
        extension: Expected extension (e.g., '.pdf', '.jpg')
    
    Returns:
        Path object of the validated file
    
    Raises:
        click.BadParameter if file doesn't exist or has wrong extension
    """
    path = Path(file_path)
    
    if not path.exists():
        raise click.BadParameter(f"File does not exist: {file_path}")
    
    if not path.is_file():
        raise click.BadParameter(f"Path is not a file: {file_path}")
    
    if extension and path.suffix.lower() != extension.lower():
        raise click.BadParameter(
            f"Expected {extension} file, got {path.suffix}: {file_path}"
        )
    
    return path


def validate_directory_exists(dir_path: str, create_if_missing: bool = False) -> Path:
    """
    Validate that a directory exists, optionally creating it
    
    Args:
        dir_path: Path to the directory
        create_if_missing: If True, create the directory if it doesn't exist
    
    Returns:
        Path object of the validated directory
    
    Raises:
        click.BadParameter if directory doesn't exist and create_if_missing is False
    """
    path = Path(dir_path)
    
    if not path.exists():
        if create_if_missing:
            path.mkdir(parents=True, exist_ok=True)
            info(f"Created directory: {dir_path}")
        else:
            raise click.BadParameter(f"Directory does not exist: {dir_path}")
    
    if not path.is_dir():
        raise click.BadParameter(f"Path is not a directory: {dir_path}")
    
    return path


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string like "1.5 MB" or "500 KB"
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to the file
    
    Returns:
        File size in bytes
    """
    return file_path.stat().st_size


def create_progress_bar(total: int, desc: str = "Processing") -> tqdm:
    """
    Create a styled progress bar
    
    Args:
        total: Total number of items
        desc: Description to display
    
    Returns:
        tqdm progress bar object
    """
    return tqdm(
        total=total,
        desc=desc,
        unit="item",
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
        colour='green'
    )


def find_files_in_directory(directory: Path, pattern: str = "*.pdf") -> List[Path]:
    """
    Find all files matching a pattern in a directory
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., "*.pdf", "*.jpg")
    
    Returns:
        List of Path objects matching the pattern
    """
    return sorted(directory.glob(pattern))


def safe_filename(filename: str, output_dir: Path) -> Path:
    """
    Generate a safe output filename, avoiding conflicts
    
    Args:
        filename: Desired output filename
        output_dir: Output directory
    
    Returns:
        Path object with a unique filename
    """
    output_path = output_dir / filename
    
    if not output_path.exists():
        return output_path
    
    # Add counter if file exists
    base = output_path.stem
    ext = output_path.suffix
    counter = 1
    
    while output_path.exists():
        output_path = output_dir / f"{base}_{counter}{ext}"
        counter += 1
    
    return output_path


def parse_size_string(size_str: str) -> float:
    """
    Parse size string like "2MB", "500KB", "1.5" into MB
    
    Args:
        size_str: Size string (e.g., "2", "2MB", "500KB")
    
    Returns:
        Size in MB as float
    
    Raises:
        ValueError if format is invalid
    """
    size_str = size_str.strip().upper()
    
    # If just a number, assume MB
    try:
        return float(size_str)
    except ValueError:
        pass
    
    # Parse with unit
    if size_str.endswith('MB'):
        return float(size_str[:-2])
    elif size_str.endswith('KB'):
        return float(size_str[:-2]) / 1024
    elif size_str.endswith('GB'):
        return float(size_str[:-2]) * 1024
    else:
        raise ValueError(
            f"Invalid size format: {size_str}. Use format like '2MB', '500KB', or just '1.5' (assumes MB)"
        )

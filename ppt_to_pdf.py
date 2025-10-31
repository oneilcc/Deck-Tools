#!/usr/bin/env python3
"""
PowerPoint to PDF Converter

This script scans a directory for PowerPoint presentations (.ppt, .pptx)
and converts them to PDF format using LibreOffice in headless mode.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


# Supported PowerPoint file extensions
POWERPOINT_EXTENSIONS = {'.ppt', '.pptx', '.pptm', '.odp'}


def is_powerpoint_file(file_path):
    """Check if a file is a PowerPoint presentation based on extension."""
    return file_path.suffix.lower() in POWERPOINT_EXTENSIONS


def check_libreoffice_installed():
    """Check if LibreOffice is installed and available."""
    try:
        result = subprocess.run(
            ['libreoffice', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def convert_to_pdf(input_file, output_dir=None):
    """
    Convert a PowerPoint file to PDF using LibreOffice.

    Args:
        input_file: Path to the PowerPoint file
        output_dir: Directory to save the PDF (defaults to same as input)

    Returns:
        True if conversion succeeded, False otherwise
    """
    input_path = Path(input_file).resolve()

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return False

    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Converting: {input_path.name}")

    try:
        # Run LibreOffice in headless mode to convert to PDF
        result = subprocess.run(
            [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(input_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            pdf_name = input_path.stem + '.pdf'
            pdf_path = output_dir / pdf_name
            if pdf_path.exists():
                print(f"  ✓ Created: {pdf_name}")
                return True
            else:
                print(f"  ✗ Failed: PDF not created")
                return False
        else:
            print(f"  ✗ Failed: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ✗ Failed: Conversion timeout")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {str(e)}")
        return False


def process_directory(directory, output_dir=None, recursive=False):
    """
    Process all PowerPoint files in a directory.

    Args:
        directory: Directory to scan for PowerPoint files
        output_dir: Directory to save PDFs (defaults to same as input)
        recursive: If True, scan subdirectories recursively

    Returns:
        Tuple of (successful_count, failed_count)
    """
    dir_path = Path(directory).resolve()

    if not dir_path.is_dir():
        print(f"Error: Not a directory: {directory}")
        return 0, 0

    # Find all PowerPoint files
    if recursive:
        pattern = '**/*'
    else:
        pattern = '*'

    ppt_files = [
        f for f in dir_path.glob(pattern)
        if f.is_file() and is_powerpoint_file(f)
    ]

    if not ppt_files:
        print(f"No PowerPoint files found in: {directory}")
        return 0, 0

    print(f"Found {len(ppt_files)} PowerPoint file(s)\n")

    successful = 0
    failed = 0

    for ppt_file in ppt_files:
        if convert_to_pdf(ppt_file, output_dir):
            successful += 1
        else:
            failed += 1

    return successful, failed


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert PowerPoint presentations to PDF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/presentations
  %(prog)s /path/to/presentations -o /path/to/output
  %(prog)s /path/to/presentations --recursive
        """
    )

    parser.add_argument(
        'directory',
        help='Directory containing PowerPoint files'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory for PDF files (default: same as input)',
        default=None
    )
    parser.add_argument(
        '-r', '--recursive',
        help='Process subdirectories recursively',
        action='store_true'
    )

    args = parser.parse_args()

    # Check if LibreOffice is available
    if not check_libreoffice_installed():
        print("Error: LibreOffice is not installed or not in PATH")
        print("Please install LibreOffice: sudo apt-get install libreoffice")
        sys.exit(1)

    # Process the directory
    successful, failed = process_directory(
        args.directory,
        args.output,
        args.recursive
    )

    # Print summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {successful + failed}")
    print(f"{'='*50}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()

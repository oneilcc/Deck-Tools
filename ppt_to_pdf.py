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
import platform
from pathlib import Path


# Supported PowerPoint file extensions
POWERPOINT_EXTENSIONS = {'.ppt', '.pptx', '.pptm', '.odp'}


def find_libreoffice_executable():
    """
    Find the LibreOffice executable based on the operating system.

    Returns:
        str: Path to the LibreOffice executable, or None if not found
    """
    system = platform.system()

    # List of possible LibreOffice executable locations
    possible_paths = []

    if system == 'Darwin':  # macOS
        possible_paths = [
            '/opt/homebrew/bin/soffice',  # ARM Mac (M1/M2/M3)
            '/usr/local/bin/soffice',      # Intel Mac
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',  # Direct app
        ]
    elif system == 'Linux':
        possible_paths = [
            'soffice',         # Usually in PATH
            'libreoffice',     # Alternative command
            '/usr/bin/soffice',
            '/usr/bin/libreoffice',
        ]
    elif system == 'Windows':
        possible_paths = [
            'soffice.exe',     # Usually in PATH
            'libreoffice.exe',
            r'C:\Program Files\LibreOffice\program\soffice.exe',
            r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
        ]

    # Try each path
    for path in possible_paths:
        try:
            # For simple command names, try to find them in PATH
            if os.path.sep not in path and not path.endswith('.exe'):
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            # For absolute paths, check if file exists
            elif Path(path).exists():
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            continue

    return None


def is_powerpoint_file(file_path):
    """Check if a file is a PowerPoint presentation based on extension."""
    return file_path.suffix.lower() in POWERPOINT_EXTENSIONS


def check_libreoffice_installed():
    """Check if LibreOffice is installed and available."""
    return find_libreoffice_executable() is not None


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

    # Get the LibreOffice executable
    libreoffice_exe = find_libreoffice_executable()
    if not libreoffice_exe:
        print(f"  ✗ Failed: LibreOffice executable not found")
        return False

    try:
        # Run LibreOffice in headless mode to convert to PDF
        result = subprocess.run(
            [
                libreoffice_exe,
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
        print("Error: LibreOffice is not installed or not found")
        print("\nInstall LibreOffice:")
        print("  macOS:   brew install --cask libreoffice")
        print("  Linux:   sudo apt-get install libreoffice")
        print("  Windows: https://www.libreoffice.org/download/")
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

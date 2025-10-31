#!/usr/bin/env python3
"""
PDF Splitter

This script splits large PDF files into smaller chunks, useful for systems
that have page limits (e.g., Notion's 100-page limit).
"""

import sys
import argparse
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: pypdf library not found")
    print("Install it with: pip install pypdf")
    sys.exit(1)


def split_pdf(input_file, max_pages=100, output_dir=None):
    """
    Split a PDF file into multiple smaller files.

    Args:
        input_file: Path to the input PDF file
        max_pages: Maximum pages per output file (default: 100)
        output_dir: Directory to save split PDFs (defaults to same as input)

    Returns:
        List of created file paths, or None if failed
    """
    input_path = Path(input_file).resolve()

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return None

    if not input_path.suffix.lower() == '.pdf':
        print(f"Error: Not a PDF file: {input_path}")
        return None

    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing: {input_path.name}")

    try:
        # Read the PDF
        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)

        print(f"  Total pages: {total_pages}")

        # If the PDF is already under the limit, no need to split
        if total_pages <= max_pages:
            print(f"  ✓ No splitting needed (under {max_pages} pages)")
            return [input_path]

        # Calculate number of output files needed
        num_files = (total_pages + max_pages - 1) // max_pages
        print(f"  Splitting into {num_files} file(s)...")

        created_files = []
        base_name = input_path.stem

        # Split the PDF
        for file_num in range(num_files):
            start_page = file_num * max_pages
            end_page = min(start_page + max_pages, total_pages)

            # Create a new PDF writer for this chunk
            writer = PdfWriter()

            # Add pages to this chunk
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            # Generate output filename
            if num_files > 1:
                output_filename = f"{base_name}_part{file_num + 1:02d}.pdf"
            else:
                output_filename = f"{base_name}.pdf"

            output_path = output_dir / output_filename

            # Write the PDF chunk
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            created_files.append(output_path)
            print(f"    ✓ Created: {output_filename} (pages {start_page + 1}-{end_page})")

        print(f"  ✓ Successfully split into {len(created_files)} file(s)")
        return created_files

    except Exception as e:
        print(f"  ✗ Failed: {str(e)}")
        return None


def process_directory(directory, max_pages=100, output_dir=None, recursive=False):
    """
    Process all PDF files in a directory.

    Args:
        directory: Directory to scan for PDF files
        max_pages: Maximum pages per output file
        output_dir: Directory to save split PDFs (defaults to same as input)
        recursive: If True, scan subdirectories recursively

    Returns:
        Tuple of (successful_count, failed_count)
    """
    dir_path = Path(directory).resolve()

    if not dir_path.is_dir():
        print(f"Error: Not a directory: {directory}")
        return 0, 0

    # Find all PDF files
    if recursive:
        pattern = '**/*.pdf'
    else:
        pattern = '*.pdf'

    pdf_files = list(dir_path.glob(pattern))

    # Filter out any files that look like they were already split
    original_files = [
        f for f in pdf_files
        if not ('_part' in f.stem and f.stem[-2:].isdigit())
    ]

    if not original_files:
        print(f"No PDF files found in: {directory}")
        return 0, 0

    print(f"Found {len(original_files)} PDF file(s)\n")

    successful = 0
    failed = 0

    for pdf_file in original_files:
        result = split_pdf(pdf_file, max_pages, output_dir)
        if result is not None:
            successful += 1
        else:
            failed += 1
        print()  # Empty line between files

    return successful, failed


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Split large PDF files into smaller chunks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s presentation.pdf
  %(prog)s presentation.pdf --max-pages 50
  %(prog)s /path/to/pdfs --directory
  %(prog)s /path/to/pdfs --directory --recursive -o /path/to/output
        """
    )

    parser.add_argument(
        'input',
        help='PDF file or directory containing PDF files'
    )
    parser.add_argument(
        '-m', '--max-pages',
        type=int,
        default=100,
        help='Maximum pages per output file (default: 100)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory for split PDF files (default: same as input)',
        default=None
    )
    parser.add_argument(
        '-d', '--directory',
        help='Process all PDFs in a directory',
        action='store_true'
    )
    parser.add_argument(
        '-r', '--recursive',
        help='Process subdirectories recursively (requires --directory)',
        action='store_true'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.max_pages < 1:
        print("Error: --max-pages must be at least 1")
        sys.exit(1)

    if args.recursive and not args.directory:
        print("Error: --recursive requires --directory flag")
        sys.exit(1)

    input_path = Path(args.input)

    # Process based on mode
    if args.directory or input_path.is_dir():
        # Directory mode
        successful, failed = process_directory(
            input_path,
            args.max_pages,
            args.output,
            args.recursive
        )

        # Print summary
        print(f"{'='*50}")
        print(f"Summary:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {successful + failed}")
        print(f"{'='*50}")

        sys.exit(0 if failed == 0 else 1)
    else:
        # Single file mode
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            sys.exit(1)

        result = split_pdf(input_path, args.max_pages, args.output)
        sys.exit(0 if result is not None else 1)


if __name__ == '__main__':
    main()

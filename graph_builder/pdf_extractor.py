#!/usr/bin/env python3
"""
PDF Slide Deck Extractor

Extracts text content from PDF slide decks, maintaining slide structure.
"""

import pdfplumber
from pathlib import Path
from typing import List, Dict, Optional
import re
from dataclasses import dataclass, asdict


@dataclass
class Slide:
    """Represents a single slide from a presentation."""
    slide_number: int
    title: Optional[str]
    content: str
    raw_text: str


@dataclass
class Presentation:
    """Represents a complete presentation."""
    filename: str
    filepath: str
    title: str
    total_slides: int
    slides: List[Slide]
    metadata: Dict


def extract_title_from_text(text: str) -> Optional[str]:
    """
    Extract likely title from slide text.
    Assumes title is first line or largest/bold text.
    """
    if not text or not text.strip():
        return None

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None

    # First non-empty line is often the title
    title = lines[0]

    # Limit title length
    if len(title) > 150:
        title = title[:150] + "..."

    return title


def clean_slide_text(text: str) -> str:
    """Clean and normalize slide text."""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove page numbers and common footers
    text = re.sub(r'\b(?:Page|Slide)\s+\d+\b', '', text, flags=re.IGNORECASE)

    return text.strip()


def extract_presentation_title(pdf_path: Path, first_slide_text: str = None) -> str:
    """
    Extract presentation title from filename or first slide.
    """
    # Try to get from first slide
    if first_slide_text:
        title = extract_title_from_text(first_slide_text)
        if title and len(title) > 10:  # Reasonable title length
            return title

    # Fall back to filename
    return pdf_path.stem.replace('_', ' ').replace('-', ' ').title()


def extract_slides_from_pdf(pdf_path: Path) -> Presentation:
    """
    Extract all slides from a PDF presentation.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Presentation object with all extracted slides
    """
    slides = []

    with pdfplumber.open(pdf_path) as pdf:
        metadata = pdf.metadata or {}

        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text from page
            raw_text = page.extract_text() or ""

            # Clean the text
            cleaned_text = clean_slide_text(raw_text)

            # Extract title (first line usually)
            title = extract_title_from_text(raw_text)

            # Create slide object
            slide = Slide(
                slide_number=page_num,
                title=title,
                content=cleaned_text,
                raw_text=raw_text
            )

            slides.append(slide)

        # Determine presentation title
        first_slide_text = slides[0].raw_text if slides else None
        pres_title = extract_presentation_title(pdf_path, first_slide_text)

        presentation = Presentation(
            filename=pdf_path.name,
            filepath=str(pdf_path.absolute()),
            title=pres_title,
            total_slides=len(slides),
            slides=slides,
            metadata=metadata
        )

    return presentation


def extract_from_directory(directory: Path, recursive: bool = True) -> List[Presentation]:
    """
    Extract all presentations from a directory.

    Args:
        directory: Directory containing PDF files
        recursive: Whether to search subdirectories

    Returns:
        List of Presentation objects
    """
    presentations = []

    # Find all PDF files
    if recursive:
        pdf_files = list(directory.rglob("*.pdf"))
    else:
        pdf_files = list(directory.glob("*.pdf"))

    # Filter out split PDFs (those with _partXX in the name)
    pdf_files = [
        f for f in pdf_files
        if not re.search(r'_part\d+\.pdf$', f.name, re.IGNORECASE)
    ]

    print(f"Found {len(pdf_files)} PDF presentation(s)")

    for pdf_file in pdf_files:
        try:
            print(f"Processing: {pdf_file.name}")
            presentation = extract_slides_from_pdf(pdf_file)
            presentations.append(presentation)
            print(f"  ✓ Extracted {presentation.total_slides} slides")
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            continue

    return presentations


def main():
    """Command-line interface for testing."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Extract text from PDF slide decks')
    parser.add_argument('input', help='PDF file or directory')
    parser.add_argument('-o', '--output', help='Output JSON file')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Process subdirectories recursively')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        # Single file
        presentation = extract_slides_from_pdf(input_path)
        presentations = [presentation]
    elif input_path.is_dir():
        # Directory
        presentations = extract_from_directory(input_path, args.recursive)
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        return 1

    # Output results
    if args.output:
        output_data = {
            'presentations': [
                {
                    **asdict(p),
                    'slides': [asdict(s) for s in p.slides]
                }
                for p in presentations
            ]
        }

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nSaved to: {args.output}")
    else:
        # Print summary
        print(f"\n{'='*60}")
        print(f"Extracted {len(presentations)} presentation(s)")
        total_slides = sum(p.total_slides for p in presentations)
        print(f"Total slides: {total_slides}")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()

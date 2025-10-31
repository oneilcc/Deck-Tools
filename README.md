# Deck-Tools

A collection of utilities for working with PowerPoint presentations and PDFs.

## Tools

1. [PowerPoint to PDF Converter](#powerpoint-to-pdf-converter) - Convert PowerPoint files to PDF
2. [PDF Splitter](#pdf-splitter) - Split large PDFs into smaller chunks

---

## PowerPoint to PDF Converter

Convert all PowerPoint presentations in a directory to PDF format.

### Requirements

- Python 3.6 or higher
- LibreOffice (used for PDF conversion)

#### Install LibreOffice

**Debian/Ubuntu:**
```bash
sudo apt-get install libreoffice
```

**macOS:**
```bash
brew install --cask libreoffice
```

**Windows:**
Download and install from [https://www.libreoffice.org/](https://www.libreoffice.org/)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/oneilcc/Deck-Tools.git
cd Deck-Tools
```

2. Make the script executable (Linux/macOS):
```bash
chmod +x ppt_to_pdf.py
```

### Usage

**Basic usage:**
```bash
python3 ppt_to_pdf.py /path/to/presentations
```

**Specify output directory:**
```bash
python3 ppt_to_pdf.py /path/to/presentations -o /path/to/output
```

**Process subdirectories recursively:**
```bash
python3 ppt_to_pdf.py /path/to/presentations --recursive
```

**Help:**
```bash
python3 ppt_to_pdf.py --help
```

### Supported Formats

The script can convert the following PowerPoint formats:
- `.ppt` (PowerPoint 97-2003)
- `.pptx` (PowerPoint 2007+)
- `.pptm` (PowerPoint Macro-Enabled)
- `.odp` (OpenDocument Presentation)

### Features

- Automatically detects PowerPoint files by extension
- Converts multiple files in batch
- Optional recursive directory scanning
- Progress reporting with success/failure counts
- Preserves original files (non-destructive)
- Custom output directory support

### Examples

Convert all PowerPoint files in the current directory:
```bash
python3 ppt_to_pdf.py .
```

Convert all PowerPoint files in a directory and its subdirectories:
```bash
python3 ppt_to_pdf.py ~/Documents/Presentations --recursive
```

Convert to a specific output folder:
```bash
python3 ppt_to_pdf.py ~/Documents/Presentations -o ~/Documents/PDFs
```

### Troubleshooting

**"LibreOffice is not installed" error:**
Make sure LibreOffice is installed and available in your system's PATH.

**Conversion timeout:**
Some large or complex presentations may take longer to convert. The default timeout is 60 seconds per file.

**Permission errors:**
Ensure you have read permissions for the input directory and write permissions for the output directory.

---

## PDF Splitter

Split large PDF files into smaller chunks. Useful for systems with page limits (e.g., Notion's 100-page limit).

### Requirements

- Python 3.6 or higher
- pypdf library

### Installation

1. Install Python dependencies:
```bash
pip install pypdf
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

2. Make the script executable (Linux/macOS):
```bash
chmod +x split_pdf.py
```

### Usage

**Split a single PDF file:**
```bash
python3 split_pdf.py presentation.pdf
```

**Specify maximum pages per file:**
```bash
python3 split_pdf.py presentation.pdf --max-pages 50
```

**Split all PDFs in a directory:**
```bash
python3 split_pdf.py /path/to/pdfs --directory
```

**Process subdirectories recursively:**
```bash
python3 split_pdf.py /path/to/pdfs --directory --recursive
```

**Specify output directory:**
```bash
python3 split_pdf.py presentation.pdf -o /path/to/output
```

**Help:**
```bash
python3 split_pdf.py --help
```

### Features

- Split large PDFs into smaller files based on page count
- Configurable maximum pages per output file (default: 100)
- Batch processing of multiple PDFs
- Optional recursive directory scanning
- Smart naming: output files are named `filename_part01.pdf`, `filename_part02.pdf`, etc.
- Skips PDFs that are already under the page limit
- Preserves original files (non-destructive)
- Progress reporting

### Examples

Split a 250-page PDF into 3 files (100 pages each):
```bash
python3 split_pdf.py large_presentation.pdf
# Creates: large_presentation_part01.pdf (pages 1-100)
#          large_presentation_part02.pdf (pages 101-200)
#          large_presentation_part03.pdf (pages 201-250)
```

Split PDFs with 50-page chunks for easier uploading:
```bash
python3 split_pdf.py document.pdf --max-pages 50
```

Process all PDFs in a folder and its subfolders:
```bash
python3 split_pdf.py ~/Documents/PDFs --directory --recursive -o ~/Documents/Split_PDFs
```

### Use Cases

- **Notion**: Upload PDFs over 100 pages by splitting them first
- **Email attachments**: Split large PDFs to meet size/page limits
- **Document management**: Break up large documents into logical sections
- **Web uploads**: Work around upload size restrictions

### Troubleshooting

**"pypdf library not found" error:**
Install the library with: `pip install pypdf`

**Permission errors:**
Ensure you have read permissions for the input file and write permissions for the output directory.
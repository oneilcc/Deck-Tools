# Deck-Tools

A collection of utilities for working with PowerPoint presentations.

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
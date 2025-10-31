# Deck-Tools

A collection of utilities for working with PowerPoint presentations and PDFs.

## Quick Start - GUI Interface

For the easiest experience, use the graphical interface:

**macOS:**
1. Double-click `launch_gui.command` in Finder
2. If prompted, allow the file to run (System Preferences → Security & Privacy)

**All Platforms:**
```bash
python3 deck_tools_gui.py
```

The GUI provides an easy-to-use interface for both tools with file/folder selection, progress tracking, and output display.

---

## Tools

1. [PowerPoint to PDF Converter](#powerpoint-to-pdf-converter) - Convert PowerPoint files to PDF
2. [PDF Splitter](#pdf-splitter) - Split large PDFs into smaller chunks
3. [GUI Interface](#gui-interface) - Graphical interface for easy access

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

---

## GUI Interface

A user-friendly graphical interface for running both tools without using the command line.

### Requirements

- Python 3.6 or higher with tkinter (usually included)
- All requirements for the tools you want to use (LibreOffice for PPT conversion, pypdf for PDF splitting)

### Installation

No additional installation required - tkinter is included with Python on most systems.

### Launching the GUI

**macOS (Easiest):**
1. Open Finder and navigate to the Deck-Tools folder
2. Double-click `launch_gui.command`
3. If macOS asks for permission, go to System Preferences → Security & Privacy and allow the file to run
4. The GUI will open automatically

**All Platforms:**
```bash
cd Deck-Tools
python3 deck_tools_gui.py
```

### Using the GUI

The GUI has three tabs:

#### Convert & Split Tab (Recommended)

**The complete workflow - perfect for preparing presentations for Notion!**

This tab runs both operations automatically:
1. Click "Browse..." to select the directory containing your PowerPoint files
2. Check "Process subdirectories recursively" to include all subfolders (recommended)
3. Set "Maximum pages per PDF" (default: 100 for Notion compatibility)
4. Click "▶ Run Complete Workflow"
5. Watch the progress in the output console:
   - **Step 1**: All PowerPoint files are converted to PDF
   - **Step 2**: Any PDFs over the page limit are automatically split
6. Done! Your files are ready to upload to Notion

#### PowerPoint to PDF Tab

For converting PowerPoint files only:
1. Click "Browse..." to select the directory containing PowerPoint files
2. Check "Process subdirectories recursively" if you want to include subfolders
3. (Optional) Select an output directory, or leave empty to save PDFs next to original files
4. Click "Convert to PDF"
5. Watch the progress in the output console at the bottom

#### PDF Splitter Tab

For splitting existing PDFs only:
1. Choose mode: "Single PDF File" or "Directory of PDFs"
2. Click "Browse..." to select your file or directory
3. Set "Maximum pages per file" (default: 100 for Notion compatibility)
4. For directory mode: Check "Process subdirectories recursively" if needed
5. (Optional) Select an output directory, or leave empty to save split PDFs next to originals
6. Click "Split PDFs"
7. Watch the progress in the output console at the bottom

### Features

- **Complete workflow**: Convert & Split tab runs both operations sequentially
- **Easy file selection**: Browse buttons for all inputs
- **Real-time progress**: See output as the scripts run with step-by-step feedback
- **Tab-based interface**: Switch between workflow, conversion, and splitting
- **Smart defaults**: Pre-configured with sensible settings (100 pages for Notion)
- **Error messages**: Clear notifications if something goes wrong
- **Output console**: View detailed logs of all operations
- **Non-blocking**: GUI stays responsive while processing
- **Sequential execution**: Workflow ensures conversion completes before splitting starts

### Screenshots

The GUI includes:
- Clean, organized layout with tabs
- File/directory browser dialogs
- Configurable options for each tool
- Scrollable output console showing progress
- Success/error message boxes

### Tips

- **Use the "Convert & Split" tab** for the most common workflow - it's the easiest!
- The output console shows the exact command being run for each step
- You can clear the output console between operations
- All operations run in background threads, so the GUI stays responsive
- For macOS users: Keep the `launch_gui.command` file in your Dock for quick access
- The workflow tab is perfect for preparing entire presentation folders for Notion upload
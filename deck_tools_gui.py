#!/usr/bin/env python3
"""
Deck-Tools GUI

A simple graphical interface for PowerPoint to PDF conversion and PDF splitting tools.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import subprocess
import sys
from pathlib import Path


class DeckToolsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Deck-Tools")
        self.root.geometry("800x700")

        # Set minimum window size
        self.root.minsize(700, 600)

        # Configure style
        style = ttk.Style()
        style.theme_use('default')

        # Create main container
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Deck-Tools", font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # PowerPoint to PDF tab
        self.ppt_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.ppt_frame, text="PowerPoint to PDF")
        self.create_ppt_tab()

        # PDF Splitter tab
        self.split_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.split_frame, text="PDF Splitter")
        self.create_split_tab()

        # Output console
        console_label = ttk.Label(main_frame, text="Output:", font=('Helvetica', 12, 'bold'))
        console_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))

        self.output_text = scrolledtext.ScrolledText(main_frame, height=15, width=80,
                                                      state='disabled', wrap=tk.WORD)
        self.output_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Clear button
        clear_btn = ttk.Button(main_frame, text="Clear Output", command=self.clear_output)
        clear_btn.grid(row=4, column=0, pady=(5, 0), sticky=tk.E)

    def create_ppt_tab(self):
        """Create PowerPoint to PDF conversion tab."""
        # Directory selection
        dir_frame = ttk.LabelFrame(self.ppt_frame, text="Input Directory", padding="10")
        dir_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)

        self.ppt_dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.ppt_dir_var, width=50)
        dir_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))

        dir_btn = ttk.Button(dir_frame, text="Browse...",
                            command=lambda: self.browse_directory(self.ppt_dir_var))
        dir_btn.grid(row=0, column=1, sticky=tk.E)

        # Options
        options_frame = ttk.LabelFrame(self.ppt_frame, text="Options", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.ppt_recursive_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(options_frame, text="Process subdirectories recursively",
                                         variable=self.ppt_recursive_var)
        recursive_check.grid(row=0, column=0, sticky=tk.W)

        # Output directory (optional)
        output_frame = ttk.LabelFrame(self.ppt_frame, text="Output Directory (Optional)", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        output_frame.columnconfigure(1, weight=1)

        self.ppt_output_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.ppt_output_var, width=50)
        output_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))

        output_btn = ttk.Button(output_frame, text="Browse...",
                               command=lambda: self.browse_directory(self.ppt_output_var))
        output_btn.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(output_frame, text="Leave empty to save PDFs in same location as source files",
                 foreground='gray').grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # Convert button
        self.ppt_convert_btn = ttk.Button(self.ppt_frame, text="Convert to PDF",
                                         command=self.run_ppt_conversion)
        self.ppt_convert_btn.grid(row=3, column=0, columnspan=3, pady=(10, 0))

    def create_split_tab(self):
        """Create PDF splitter tab."""
        # Mode selection
        mode_frame = ttk.LabelFrame(self.split_frame, text="Mode", padding="10")
        mode_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.split_mode_var = tk.StringVar(value="directory")

        file_radio = ttk.Radiobutton(mode_frame, text="Single PDF File",
                                     variable=self.split_mode_var, value="file",
                                     command=self.update_split_mode)
        file_radio.grid(row=0, column=0, padx=(0, 20), sticky=tk.W)

        dir_radio = ttk.Radiobutton(mode_frame, text="Directory of PDFs",
                                    variable=self.split_mode_var, value="directory",
                                    command=self.update_split_mode)
        dir_radio.grid(row=0, column=1, sticky=tk.W)

        # Input selection
        input_frame = ttk.LabelFrame(self.split_frame, text="Input", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        self.split_input_var = tk.StringVar()
        self.split_input_entry = ttk.Entry(input_frame, textvariable=self.split_input_var, width=50)
        self.split_input_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))

        self.split_browse_btn = ttk.Button(input_frame, text="Browse...",
                                          command=self.browse_split_input)
        self.split_browse_btn.grid(row=0, column=1, sticky=tk.E)

        # Options
        options_frame = ttk.LabelFrame(self.split_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Max pages
        max_pages_frame = ttk.Frame(options_frame)
        max_pages_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Label(max_pages_frame, text="Maximum pages per file:").grid(row=0, column=0, padx=(0, 10))
        self.split_max_pages_var = tk.StringVar(value="100")
        max_pages_spin = ttk.Spinbox(max_pages_frame, from_=1, to=1000,
                                    textvariable=self.split_max_pages_var, width=10)
        max_pages_spin.grid(row=0, column=1)

        # Recursive option
        self.split_recursive_var = tk.BooleanVar(value=True)
        self.split_recursive_check = ttk.Checkbutton(options_frame,
                                                     text="Process subdirectories recursively",
                                                     variable=self.split_recursive_var)
        self.split_recursive_check.grid(row=1, column=0, sticky=tk.W)

        # Output directory (optional)
        output_frame = ttk.LabelFrame(self.split_frame, text="Output Directory (Optional)", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        output_frame.columnconfigure(1, weight=1)

        self.split_output_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.split_output_var, width=50)
        output_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))

        output_btn = ttk.Button(output_frame, text="Browse...",
                               command=lambda: self.browse_directory(self.split_output_var))
        output_btn.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(output_frame, text="Leave empty to save split PDFs in same location as source files",
                 foreground='gray').grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # Split button
        self.split_btn = ttk.Button(self.split_frame, text="Split PDFs",
                                    command=self.run_pdf_split)
        self.split_btn.grid(row=4, column=0, columnspan=3, pady=(10, 0))

        # Initial mode setup
        self.update_split_mode()

    def update_split_mode(self):
        """Update UI based on selected split mode."""
        if self.split_mode_var.get() == "file":
            self.split_recursive_check.config(state='disabled')
        else:
            self.split_recursive_check.config(state='normal')

    def browse_directory(self, var):
        """Browse for a directory."""
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)

    def browse_split_input(self):
        """Browse for input based on split mode."""
        if self.split_mode_var.get() == "file":
            filename = filedialog.askopenfilename(
                title="Select PDF file",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if filename:
                self.split_input_var.set(filename)
        else:
            directory = filedialog.askdirectory(title="Select directory containing PDFs")
            if directory:
                self.split_input_var.set(directory)

    def append_output(self, text):
        """Append text to output console."""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def clear_output(self):
        """Clear the output console."""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')

    def run_command(self, cmd, button):
        """Run a command in a separate thread."""
        def run():
            button.config(state='disabled')
            try:
                self.append_output(f"$ {' '.join(cmd)}\n\n")

                # Get the script directory
                script_dir = Path(__file__).parent

                # Run the command
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(script_dir),
                    bufsize=1
                )

                # Stream output
                for line in process.stdout:
                    self.append_output(line)

                process.wait()

                if process.returncode == 0:
                    self.append_output("\n✓ Completed successfully!\n\n")
                    messagebox.showinfo("Success", "Operation completed successfully!")
                else:
                    self.append_output(f"\n✗ Failed with exit code {process.returncode}\n\n")
                    messagebox.showerror("Error", f"Operation failed with exit code {process.returncode}")

            except Exception as e:
                self.append_output(f"\n✗ Error: {str(e)}\n\n")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
            finally:
                button.config(state='normal')

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def run_ppt_conversion(self):
        """Run PowerPoint to PDF conversion."""
        directory = self.ppt_dir_var.get()

        if not directory:
            messagebox.showerror("Error", "Please select an input directory")
            return

        if not Path(directory).exists():
            messagebox.showerror("Error", "Input directory does not exist")
            return

        # Build command
        cmd = [sys.executable, "ppt_to_pdf.py", directory]

        if self.ppt_recursive_var.get():
            cmd.append("--recursive")

        output_dir = self.ppt_output_var.get()
        if output_dir:
            cmd.extend(["-o", output_dir])

        self.run_command(cmd, self.ppt_convert_btn)

    def run_pdf_split(self):
        """Run PDF splitting."""
        input_path = self.split_input_var.get()

        if not input_path:
            messagebox.showerror("Error", "Please select an input file or directory")
            return

        if not Path(input_path).exists():
            messagebox.showerror("Error", "Input path does not exist")
            return

        # Build command
        cmd = [sys.executable, "split_pdf.py", input_path]

        # Add max pages
        try:
            max_pages = int(self.split_max_pages_var.get())
            cmd.extend(["--max-pages", str(max_pages)])
        except ValueError:
            messagebox.showerror("Error", "Invalid maximum pages value")
            return

        # Add directory flag if in directory mode
        if self.split_mode_var.get() == "directory":
            cmd.append("--directory")

            if self.split_recursive_var.get():
                cmd.append("--recursive")

        # Add output directory if specified
        output_dir = self.split_output_var.get()
        if output_dir:
            cmd.extend(["-o", output_dir])

        self.run_command(cmd, self.split_btn)


def main():
    root = tk.Tk()
    app = DeckToolsGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

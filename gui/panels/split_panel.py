"""
Split Panel - GUI for splitting PDFs
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class SplitPanel(ctk.CTkFrame):
    """Panel for splitting PDFs"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG_PRIMARY, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        self.input_file = ""
        self.output_dir = ""
        self.split_mode = ctk.StringVar(value="pages")
        
        self.create_widgets()
        
        # Enable Drag & Drop
        self.input_entry.drop_target_register('DND_Files')
        self.input_entry.dnd_bind('<<Drop>>', self.drop_file)
        
    def drop_file(self, event):
        """Handle file drop event"""
        try:
            files = parse_dropped_files(event.data)
            if files:
                file = files[0]
                if file.lower().endswith('.pdf'):
                    self.input_file = file
                    self.input_entry.delete(0, "end")
                    self.input_entry.insert(0, file)
                    
                    # Auto-set output dir
                    p = Path(file)
                    folder_name = f"{p.stem}_split"
                    output_dir = str(p.parent / folder_name)
                    self.output_dir = output_dir
                    self.output_entry.delete(0, "end")
                    self.output_entry.insert(0, output_dir)
                    
                    self.status_label.configure(text=f"Selected: {p.name}", text_color=theme.INFO)
                else:
                    self.status_label.configure(text="Please drop a PDF file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="Split PDF", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Split PDF into individual pages or page ranges",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        # Input
        input_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        input_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            input_frame, text="Input PDF", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        path_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = ctk.CTkEntry(
            path_frame, placeholder_text="Choose PDF to split...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=35, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            path_frame, text="📁", command=self.browse_input,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=50, height=35, fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_SIDEBAR, corner_radius=8
        ).pack(side="left")
        
        # Split Settings
        settings_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        settings_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            settings_frame, text="Split Mode", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        # Radio buttons
        radio_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        radio_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkRadioButton(
            radio_frame, text="Split One Page Per File", variable=self.split_mode, value="pages",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.TEXT_PRIMARY, hover_color=theme.get_accent(), fg_color=theme.get_accent(),
            command=self.toggle_range_input
        ).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkRadioButton(
            radio_frame, text="Custom Page Ranges", variable=self.split_mode, value="ranges",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.TEXT_PRIMARY, hover_color=theme.get_accent(), fg_color=theme.get_accent(),
            command=self.toggle_range_input
        ).pack(anchor="w")
        
        # Range input
        self.range_input_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        # Don't pack initially
        
        ctk.CTkLabel(
            self.range_input_frame, text="Ranges (e.g., 1-4, 5-8):", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.range_entry = ctk.CTkEntry(
            self.range_input_frame, placeholder_text="1-4, 5-8, 9-end",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=200, height=32, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.range_entry.pack(side="left", fill="x", expand=True)
        
        # Output directory
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            output_frame, text="Output Directory", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        output_path_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.output_entry = ctk.CTkEntry(
            output_path_frame, placeholder_text="Choose output folder...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=35, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            output_path_frame, text="📁", command=self.browse_output,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=50, height=35, fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_SIDEBAR, corner_radius=8
        ).pack(side="left")
        
        # Split button
        self.split_btn = ctk.CTkButton(
            self, text="✂️ SPLIT PDF", command=self.split_pdf,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"), height=45,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.split_btn.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select a PDF to split", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def toggle_range_input(self):
        if self.split_mode.get() == "ranges":
            self.range_input_frame.pack(fill="x", padx=20, pady=(10, 15))
        else:
            self.range_input_frame.pack_forget()
            
    def browse_input(self):
        file = filedialog.askopenfilename(title="Select PDF to split", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.input_file = file
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Auto-populate output dir if empty
            if not self.output_dir:
                output_dir = str(Path(file).parent)
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, output_dir)
                self.output_dir = output_dir
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_dir = folder
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)
            
    def split_pdf(self):
        if not self.input_file or not self.output_dir:
            messagebox.showerror("Error", "Please select input PDF and output directory")
            return
            
        mode = self.split_mode.get()
        ranges = None
        
        if mode == "ranges":
            range_str = self.range_entry.get().strip()
            if not range_str:
                messagebox.showerror("Error", "Please enter page ranges")
                return
            # Controller.split_pdf parses the string if passed as list of strings?
            # Actually, let's pass a list of strings as Controller expects split string
            # wait, CLI does ranges.split(','), so it passes ['1-4', '5-8'] to Controller
            # Controller.split_pdf(..., ranges: List[str])
            ranges = [r.strip() for r in range_str.split(',')]
            
        self.split_btn.configure(state="disabled", text="Splitting...")
        self.status_label.configure(text="Splitting PDF...", text_color=theme.INFO)
        
        threading.Thread(target=self._do_split, args=(mode, ranges)).start()
        
    def _do_split(self, mode, ranges):
        try:
            success = Controller.split_pdf(self.input_file, self.output_dir, mode, ranges)
            self.after(0, self._complete, success)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success):
        self.split_btn.configure(state="normal", text="✂️ SPLIT PDF")
        if success:
            self.status_label.configure(text="✓ PDF split successfully", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"PDF split completed!\n\nOutput: {self.output_dir}")
        else:
            self.status_label.configure(text="✗ Split failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.split_btn.configure(state="normal", text="✂️ SPLIT PDF")
        self.status_label.configure(text=f"✗ Error", text_color=theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")


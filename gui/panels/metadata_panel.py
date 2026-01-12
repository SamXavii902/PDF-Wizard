"""
Metadata Panel - View or strip PDF metadata
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class MetadataPanel(ctk.CTkFrame):
    """Panel for metadata operations"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG_PRIMARY, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Textbox expands
        self.input_file = ""
        
        self.create_widgets()
        
        # Enable Drag & Drop (on the whole info frame actually, or create a drop area)
        # For consistency, we don't have an input entry visible until browsing... 
        # Wait, create_widgets has input_file logic but no persistent entry showing path?
        # Looking at Step 582, create_widgets HAS NO Input Entry! It has a button.
        # We should enable drop on the info_textbox then.
        self.info_textbox.drop_target_register('DND_Files')
        self.info_textbox.dnd_bind('<<Drop>>', self.drop_file)
        
    def drop_file(self, event):
        """Handle file drop event"""
        try:
            files = parse_dropped_files(event.data)
            if files:
                file = files[0]
                if file.lower().endswith('.pdf'):
                    self.input_file = file
                    self.status_label.configure(text=f"Selected: {Path(file).name}", text_color=theme.INFO)
                    threading.Thread(target=self._view_metadata).start()
                else:
                    self.status_label.configure(text="Please drop a PDF file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="PDF Metadata", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="View or remove PDF metadata for privacy",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        # Info display
        info_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        info_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 15))
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            info_frame, text="Metadata Information", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        self.info_textbox = ctk.CTkTextbox(
            info_frame, fg_color=theme.BG_TERTIARY,
            text_color=theme.TEXT_PRIMARY, font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12)
        )
        self.info_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        self.info_textbox.insert("1.0", "Select a PDF file to view its metadata...")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 10))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(
            btn_frame, text="📂 Select PDF", command=self.browse_file,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"), height=42,
            fg_color=theme.BG_TERTIARY, hover_color=theme.BG_SIDEBAR,
            corner_radius=10
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        ctk.CTkButton(
            btn_frame, text="🗑️ Strip Metadata", command=self.strip_metadata,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"), height=42,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        ).grid(row=0, column=1, sticky="ew")
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="No file selected", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def browse_file(self):
        file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.input_file = file
            self.status_label.configure(text=f"Selected: {Path(file).name}", text_color=theme.INFO)
            threading.Thread(target=self._view_metadata).start()
            
    def _view_metadata(self):
        try:
            info = Controller.view_metadata(self.input_file)
            self.after(0, self._display_metadata, info)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _display_metadata(self, info):
        self.info_textbox.delete("1.0", "end")
        if info:
            self.info_textbox.insert("1.0", info)
        else:
            self.info_textbox.insert("1.0", "No metadata found or unable to read metadata.")
            
    def strip_metadata(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
            
        p = Path(self.input_file)
        initial = f"{p.stem}_clean{p.suffix}"
        
        output = filedialog.asksaveasfilename(
            title="Save clean PDF as", defaultextension=".pdf",
            initialfile=initial,
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output:
            self.status_label.configure(text="Stripping metadata...", text_color=theme.INFO)
            threading.Thread(target=self._do_strip, args=(output,)).start()
            
    def _do_strip(self, output):
        try:
            success = Controller.strip_metadata(self.input_file, output)
            self.after(0, self._strip_complete, success, output)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _strip_complete(self, success, output):
        if success:
            self.status_label.configure(text=f"✓ Metadata stripped", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"Metadata removed!\n\nOutput: {output}")
        else:
            self.status_label.configure(text="✗ Strip failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.status_label.configure(text="✗ Error", text_color=theme.ERROR)
        self.info_textbox.delete("1.0", "end")
        self.info_textbox.insert("1.0", f"Error: {error_msg}")

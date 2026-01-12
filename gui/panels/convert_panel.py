"""
Convert Panel - Convert images to PDF or PDF pages to images
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class ConvertPanel(ctk.CTkFrame):
    """Panel for file format conversion"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG_PRIMARY, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        self.input_file = ""
        self.output_file = ""
        self.mode = "img2pdf"  # or "pdf2img"
        
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
                # Validate based on mode
                valid = False
                if self.mode == "img2pdf":
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        valid = True
                else: # pdf2img
                    if file.lower().endswith('.pdf'):
                        valid = True
                        
                if valid:
                    self.input_file = file
                    self.input_entry.delete(0, "end")
                    self.input_entry.insert(0, file)
                    self.status_label.configure(text=f"Selected: {Path(file).name}", text_color=theme.INFO)
                else:
                    msg = "Please drop an image file" if self.mode == "img2pdf" else "Please drop a PDF file"
                    self.status_label.configure(text=msg, text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="Convert Files", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Convert images to PDF or extract PDF pages as images",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        # Mode selection
        mode_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        mode_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            mode_frame, text="Conversion Type", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        btn_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.img2pdf_btn = ctk.CTkButton(
            btn_frame, text="🖼️ → 📄 Images to PDF", command=lambda: self.set_mode("img2pdf"),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            height=38, corner_radius=8
        )
        self.img2pdf_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.pdf2img_btn = ctk.CTkButton(
            btn_frame, text="📄 → 🖼️ PDF to Images", command=lambda: self.set_mode("pdf2img"),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.BG_TERTIARY, hover_color=theme.get_accent_hover(),
            height=38, corner_radius=8
        )
        self.pdf2img_btn.pack(side="left", fill="x", expand=True)
        
        # Input
        input_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        input_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        self.input_label = ctk.CTkLabel(
            input_frame, text="Input Images", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        )
        self.input_label.pack(fill="x", padx=20, pady=(15, 10))
        
        path_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = ctk.CTkEntry(
            path_frame, placeholder_text="Choose files...",
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
        
        # Output
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        self.output_label = ctk.CTkLabel(
            output_frame, text="Output PDF", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        )
        self.output_label.pack(fill="x", padx=20, pady=(15, 10))
        
        output_path_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.output_entry = ctk.CTkEntry(
            output_path_frame, placeholder_text="Choose output location...",
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
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            self, text="🔄 CONVERT", command=self.convert_files,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"), height=45,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.convert_btn.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select images to convert", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def set_mode(self, mode):
        self.mode = mode
        if mode == "img2pdf":
            self.img2pdf_btn.configure(fg_color=theme.get_accent())
            self.pdf2img_btn.configure(fg_color=theme.BG_TERTIARY)
            self.input_label.configure(text="Input Images")
            self.output_label.configure(text="Output PDF")
            self.input_entry.configure(placeholder_text="Choose image files...")
            self.output_entry.configure(placeholder_text="Save PDF as...")
        else:
            self.img2pdf_btn.configure(fg_color=theme.BG_TERTIARY)
            self.pdf2img_btn.configure(fg_color=theme.get_accent())
            self.input_label.configure(text="Input PDF")
            self.output_label.configure(text="Output Directory")
            self.input_entry.configure(placeholder_text="Choose PDF file...")
            self.output_entry.configure(placeholder_text="Choose output folder...")
            
    def browse_input(self):
        if self.mode == "img2pdf":
            files = filedialog.askopenfilenames(
                title="Select images", filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
            )
            if files:
                self.input_files = list(files)
                self.input_entry.delete(0, "end")
                self.input_entry.insert(0, f"{len(files)} images selected")
        else:
            file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF files", "*.pdf")])
            if file:
                self.input_files = [file]
                self.input_entry.delete(0, "end")
                self.input_entry.insert(0, file)
            
    def browse_output(self):
        if self.mode == "img2pdf":
            file = filedialog.asksaveasfilename(
                title="Save PDF as", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")]
            )
            if file:
                self.output_path = file
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, file)
        else:
            folder = filedialog.askdirectory(title="Select output folder")
            if folder:
                self.output_path = folder
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, folder)
            
    def convert_files(self):
        if not self.input_files or not self.output_path:
            messagebox.showerror("Error", "Please select input and output")
            return
            
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.status_label.configure(text="Converting...", text_color=theme.INFO)
        
        threading.Thread(target=self._do_convert).start()
        
    def _do_convert(self):
        try:
            if self.mode == "img2pdf":
                success = Controller.images_to_pdf(self.input_files, self.output_path)
            else:
                success = Controller.pdf_to_images(self.input_files[0], self.output_path)
            self.after(0, self._complete, success)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success):
        self.convert_btn.configure(state="normal", text="🔄 CONVERT")
        if success:
            self.status_label.configure(text="✓ Conversion successful", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"Files converted!\n\nOutput: {self.output_path}")
        else:
            self.status_label.configure(text="✗ Conversion failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.convert_btn.configure(state="normal", text="🔄 CONVERT")
        self.status_label.configure(text="✗ Error", text_color=theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

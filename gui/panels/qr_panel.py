"""
QR Generator Panel - Create QR codes for PDF verification
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class QRPanel(ctk.CTkFrame):
    """Panel for generating QR codes"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG_PRIMARY, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        self.input_file = ""
        self.output_file = ""
        
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
                    
                    # Auto-set output
                    if not self.output_file:
                         output = str(Path(file).with_suffix('.png')).replace('.pdf', '_qr.png')
                         self.output_entry.delete(0, "end")
                         self.output_entry.insert(0, output)
                         self.output_file = output
                else:
                    self.status_label.configure(text="Please drop a PDF file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="QR Code Generator", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Generate QR code with document hash for verification",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        # Input PDF
        input_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        input_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            input_frame, text="Document to Verify", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        path_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = ctk.CTkEntry(
            path_frame, placeholder_text="Choose PDF file...",
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
        
        # Output QR code
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            output_frame, text="Output QR Code", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
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
        
        # Generate button
        self.gen_btn = ctk.CTkButton(
            self, text="📱 GENERATE QR CODE", command=self.generate_qr,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"), height=45,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.gen_btn.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select a PDF to generate QR code", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def browse_input(self):
        file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.input_file = file
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Auto-populate output
            if not self.output_file:
                output = str(Path(file).with_suffix('.png')).replace('.pdf', '_qr.png')
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, output)
                self.output_file = output
            
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save QR code as", defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")]
        )
        if file:
            self.output_file = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def generate_qr(self):
        if not self.input_file or not self.output_file:
            messagebox.showerror("Error", "Please select input PDF and output location")
            return
            
        self.gen_btn.configure(state="disabled", text="Generating...")
        self.status_label.configure(text="Generating QR code...", text_color=theme.INFO)
        
        threading.Thread(target=self._do_generate).start()
        
    def _do_generate(self):
        try:
            success = Controller.generate_qr_code(self.input_file, self.output_file)
            self.after(0, self._complete, success)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success):
        self.gen_btn.configure(state="normal", text="📱 GENERATE QR CODE")
        if success:
            self.status_label.configure(text="✓ QR code generated successfully", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"QR code created!\n\nOutput: {self.output_file}")
        else:
            self.status_label.configure(text="✗ Generation failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.gen_btn.configure(state="normal", text="📱 GENERATE QR CODE")
        self.status_label.configure(text="✗ Error", text_color=theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

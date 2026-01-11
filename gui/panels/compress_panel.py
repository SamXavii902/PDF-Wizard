"""
Compress Panel - GUI for PDF compression

Features:
- File selection
- Quality presets (Low/Medium/High)
- Custom target size input
- Real-time compression
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class CompressPanel(ctk.CTkFrame):
    """Panel for compressing PDFs"""
    
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=theme.BG_PRIMARY,
            corner_radius=0
        )
        
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
                    p = Path(file)
                    output = str(p.with_name(f"{p.stem}_compressed{p.suffix}"))
                    self.output_entry.delete(0, "end")
                    self.output_entry.insert(0, output)
                    self.output_file = output
                    
                    self.status_label.configure(text=f"Selected: {p.name}", text_color=theme.INFO)
                else:
                    self.status_label.configure(text="Please drop a PDF file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        """Create all panel widgets"""
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Compress PDF",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        header.pack(fill="x", padx=30, pady=(30, 10))
        
        subtitle = ctk.CTkLabel(
            self,
            text="Smart 3-stage compression to meet custom size targets",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14),
            text_color=theme.TEXT_SECONDARY,
            anchor="w"
        )
        subtitle.pack(fill="x", padx=30, pady=(0, 30))
        
        # Input file section
        input_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        input_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="Input PDF",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        input_label.pack(fill="x", padx=20, pady=(20, 10))
        
        input_path_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_path_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.input_entry = ctk.CTkEntry(
            input_path_frame,
            placeholder_text="Choose PDF to compress...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=40,
            fg_color=theme.BG_TERTIARY,
            border_color=theme.BORDER
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_input_btn = ctk.CTkButton(
            input_path_frame,
            text="📁 Browse",
            command=self.browse_input,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=100,
            height=40,
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_SIDEBAR,
            corner_radius=8
        )
        browse_input_btn.pack(side="left")
        
        # Compression settings section
        settings_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        settings_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        settings_label = ctk.CTkLabel(
            settings_frame,
            text="Compression Settings",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        settings_label.pack(fill="x", padx=20, pady=(20, 15))
        
        # Quality preset
        quality_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        quality_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        quality_label = ctk.CTkLabel(
            quality_frame,
            text="Quality:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            text_color=theme.TEXT_PRIMARY,
            width=120,
            anchor="w"
        )
        quality_label.pack(side="left")
        
        self.quality_var = ctk.StringVar(value="medium")
        quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            values=["low", "medium", "high"],
            variable=self.quality_var,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            dropdown_font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.BG_TERTIARY,
            button_color=theme.BG_TERTIARY,
            button_hover_color=theme.get_accent(),
            dropdown_fg_color=theme.BG_TERTIARY,
            width=200
        )
        quality_menu.pack(side="left")
        
        quality_hint = ctk.CTkLabel(
            quality_frame,
            text="  low = aggressive, high = minimal loss",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=11),
            text_color=theme.TEXT_SECONDARY
        )
        quality_hint.pack(side="left", padx=10)
        
        # Target size
        target_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        target_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        target_label = ctk.CTkLabel(
            target_frame,
            text="Target Size:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            text_color=theme.TEXT_PRIMARY,
            width=120,
            anchor="w"
        )
        target_label.pack(side="left")
        
        self.target_entry = ctk.CTkEntry(
            target_frame,
            placeholder_text="2.0",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=100,
            height=35,
            fg_color=theme.BG_TERTIARY,
            border_color=theme.BORDER
        )
        self.target_entry.pack(side="left")
        self.target_entry.insert(0, "2.0")
        
        unit_label = ctk.CTkLabel(
            target_frame,
            text=" MB  (or use KB like '500KB')",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=11),
            text_color=theme.TEXT_SECONDARY
        )
        unit_label.pack(side="left", padx=10)
        
        # Output file section
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Output File",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        output_label.pack(fill="x", padx=20, pady=(20, 10))
        
        output_path_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_path_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.output_entry = ctk.CTkEntry(
            output_path_frame,
            placeholder_text="Choose output location...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=40,
            fg_color=theme.BG_TERTIARY,
            border_color=theme.BORDER
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_output_btn = ctk.CTkButton(
            output_path_frame,
            text="📁 Browse",
            command=self.browse_output,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=100,
            height=40,
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_SIDEBAR,
            corner_radius=8
        )
        browse_output_btn.pack(side="left")
        
        # Action section
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        self.compress_btn = ctk.CTkButton(
            action_frame,
            text="⚡ COMPRESS PDF",
            command=self.compress_pdf,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=16, weight="bold"),
            height=50,
            fg_color=theme.get_accent(),
            hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.compress_btn.pack(fill="x")
        
        # Status
        self.status_label = ctk.CTkLabel(
            self,
            text="Select a PDF file to compress",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.pack(fill="x", padx=30, pady=(0, 20))
        
    def browse_input(self):
        """Browse for input PDF file"""
        file = filedialog.askopenfilename(
            title="Select PDF to compress",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file:
            self.input_file = file
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Auto-populate output
            if not self.output_file:
                # Python 3.8 compatible replacement for with_stem
                # original: output = str(Path(file).with_stem(Path(file).stem + "_compressed"))
                p = Path(file)
                output = str(p.with_name(f"{p.stem}_compressed{p.suffix}"))
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, output)
                self.output_file = output
            
    def browse_output(self):
        """Browse for output file location"""
        file = filedialog.asksaveasfilename(
            title="Save compressed PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file:
            self.output_file = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def update_status(self, message, color=None):
        """Update the status label"""
        self.status_label.configure(
            text=message,
            text_color=color or theme.TEXT_SECONDARY
        )
        
    def compress_pdf(self):
        """Execute compression"""
        # Validation
        if not self.input_file:
            messagebox.showerror("Error", "Please select an input PDF file")
            return
            
        if not self.output_file:
            messagebox.showerror("Error", "Please choose an output location")
            return
            
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target size")
            return
            
        # Disable button
        self.compress_btn.configure(state="disabled", text="Compressing...")
        self.update_status("Compressing PDF...", theme.INFO)
        
        # Run in thread
        thread = threading.Thread(
            target=self._do_compress,
            args=(target, self.quality_var.get())
        )
        thread.start()
        
    def _do_compress(self, target_size, quality):
        """Perform compression in background thread"""
        try:
            success = Controller.compress_pdf(
                self.input_file,
                self.output_file,
                float(target_size) if target_size.replace('.', '').isdigit() else target_size,
                quality
            )
            
            self.after(0, self._compress_complete, success)
            
        except Exception as e:
            self.after(0, self._compress_error, str(e))
            
    def _compress_complete(self, success):
        """Called when compression completes"""
        self.compress_btn.configure(state="normal", text="⚡ COMPRESS PDF")
        
        if success:
            self.update_status(f"✓ Successfully compressed to {Path(self.output_file).name}", theme.SUCCESS)
            messagebox.showinfo("Success", f"PDF compressed successfully!\n\nOutput: {self.output_file}")
        else:
            self.update_status("✗ Compression failed", theme.ERROR)
            
    def _compress_error(self, error_msg):
        """Called when an error occurs"""
        self.compress_btn.configure(state="normal", text="⚡ COMPRESS PDF")
        self.update_status(f"✗ Error: {error_msg[:50]}...", theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

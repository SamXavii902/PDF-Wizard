"""
Compress Image Panel - Compress images to target file size
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class CompressImagePanel(ctk.CTkFrame):
    """Panel for compressing images"""
    
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
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.input_file = file
                    self.input_entry.delete(0, "end")
                    self.input_entry.insert(0, file)
                    
                    # Auto-set output (logic copied from current impl)
                    if not self.output_file:
                        p = Path(file)
                        output = str(p.with_name(f"{p.stem}_compressed{p.suffix}"))
                        self.output_entry.delete(0, "end")
                        self.output_entry.insert(0, output)
                        self.output_file = output
                else:
                    self.status_label.configure(text="Please drop an image file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="Compress Image", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Reduce image file size while maintaining quality",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        # Input
        input_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        input_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            input_frame, text="Input Image", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        path_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = ctk.CTkEntry(
            path_frame, placeholder_text="Choose image file...",
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
        
        # Settings
        settings_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        settings_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            settings_frame, text="Compression Settings", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        # Target size
        size_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        size_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            size_frame, text="Target Size:", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            text_color=theme.TEXT_PRIMARY, width=120, anchor="w"
        ).pack(side="left")
        
        self.size_entry = ctk.CTkEntry(
            size_frame, placeholder_text="100", width=100,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=32, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.size_entry.pack(side="left")
        self.size_entry.insert(0, "100")
        
        ctk.CTkLabel(
            size_frame, text=" KB", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=11),
            text_color=theme.TEXT_SECONDARY
        ).pack(side="left", padx=10)
        
        # Quality
        quality_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        quality_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            quality_frame, text="Quality:", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            text_color=theme.TEXT_PRIMARY, width=120, anchor="w"
        ).pack(side="left")
        
        self.quality_slider = ctk.CTkSlider(
            quality_frame, from_=1, to=100, number_of_steps=99,
            fg_color=theme.BG_TERTIARY, progress_color=theme.get_accent()
        )
        self.quality_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.quality_slider.set(85)
        
        self.quality_label = ctk.CTkLabel(
            quality_frame, text="85%", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_PRIMARY, width=40
        )
        self.quality_label.pack(side="left")
        
        self.quality_slider.configure(command=self.update_quality_label)
        
        # Output
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            output_frame, text="Output File", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
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
        
        # Compress button
        self.compress_btn = ctk.CTkButton(
            self, text="🗜️ COMPRESS IMAGE", command=self.compress_image,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"), height=45,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.compress_btn.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select an image to compress", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def update_quality_label(self, value):
        self.quality_label.configure(text=f"{int(value)}%")
        
    def browse_input(self):
        file = filedialog.askopenfilename(
            title="Select image", filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if file:
            self.input_file = file
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            if not self.output_file:
                # Python 3.8 compatible replacement for with_stem
                p = Path(file)
                output = str(p.with_name(f"{p.stem}_compressed{p.suffix}"))
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, output)
                self.output_file = output
            
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save compressed image as", defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
        )
        if file:
            self.output_file = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def compress_image(self):
        if not self.input_file or not self.output_file:
            messagebox.showerror("Error", "Please select input and output files")
            return
            
        target_kb = self.size_entry.get().strip()
        if not target_kb:
            messagebox.showerror("Error", "Please enter target size")
            return
            
        self.compress_btn.configure(state="disabled", text="Compressing...")
        self.status_label.configure(text="Compressing image...", text_color=theme.INFO)
        
        quality = int(self.quality_slider.get())
        threading.Thread(target=self._do_compress, args=(int(target_kb), quality)).start()
        
    def _do_compress(self, target_kb, quality):
        try:
            success = Controller.compress_image(
                self.input_file, self.output_file, target_kb, quality
            )
            self.after(0, self._complete, success)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success):
        self.compress_btn.configure(state="normal", text="🗜️ COMPRESS IMAGE")
        if success:
            self.status_label.configure(text="✓ Image compressed successfully", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"Image compressed!\n\nOutput: {self.output_file}")
        else:
            self.status_label.configure(text="✗ Compression failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.compress_btn.configure(state="normal", text="🗜️ COMPRESS IMAGE")
        self.status_label.configure(text="✗ Error", text_color=theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

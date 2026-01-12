"""
Image Resize Panel - GUI for resizing images (including passport photos)
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class ResizeImagePanel(ctk.CTkFrame):
    """Panel for resizing images"""
    
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
                    
                    # Auto-set output
                    p = Path(file)
                    output = str(p.with_name(f"{p.stem}_resized{p.suffix}"))
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
            self, text="Resize Image", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Perfect for passport photos - resize with dimensions + file size targets",
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
            settings_frame, text="Resize Settings", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        # Dimensions
        dim_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        dim_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            dim_frame, text="Dimensions:", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            text_color=theme.TEXT_PRIMARY, width=120, anchor="w"
        ).pack(side="left")
        
        self.dims_entry = ctk.CTkEntry(
            dim_frame, placeholder_text="600x600", width=150,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=32, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.dims_entry.pack(side="left")
        self.dims_entry.insert(0, "600x600")
        
        ctk.CTkLabel(
            dim_frame, text="  (e.g., 600x600 for passport)", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=11),
            text_color=theme.TEXT_SECONDARY
        ).pack(side="left", padx=10)
        
        # File size (optional)
        size_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        size_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            size_frame, text="Max File Size:", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            text_color=theme.TEXT_PRIMARY, width=120, anchor="w"
        ).pack(side="left")
        
        self.size_entry = ctk.CTkEntry(
            size_frame, placeholder_text="50", width=80,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=32, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.size_entry.pack(side="left")
        
        ctk.CTkLabel(
            size_frame, text=" KB (optional, for passport photos)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=11), text_color=theme.TEXT_SECONDARY
        ).pack(side="left", padx=10)
        
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
        
        # Resize button
        self.resize_btn = ctk.CTkButton(
            self, text="📐 RESIZE IMAGE", command=self.resize_image,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"), height=45,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.resize_btn.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select an image to resize", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def browse_input(self):
        file = filedialog.askopenfilename(
            title="Select image", filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if file:
            self.input_file = file
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Auto-populate output
            if not self.output_file:
                # Python 3.8 compatible replacement for with_stem
                p = Path(file)
                output = str(p.with_name(f"{p.stem}_resized{p.suffix}"))
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, output)
                self.output_file = output
            
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save resized image as", defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
        )
        if file:
            self.output_file = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def resize_image(self):
        if not self.input_file or not self.output_file:
            messagebox.showerror("Error", "Please select input and output files")
            return
            
        dims = self.dims_entry.get().strip()
        if not dims:
            messagebox.showerror("Error", "Please enter dimensions")
            return
            
        self.resize_btn.configure(state="disabled", text="Resizing...")
        self.status_label.configure(text="Resizing image...", text_color=theme.INFO)
        
        size_kb = self.size_entry.get().strip()
        threading.Thread(target=self._do_resize, args=(dims, size_kb)).start()
        
    def _do_resize(self, dimensions, max_size_kb):
        try:
            success = Controller.resize_image(
                self.input_file, self.output_file, dimensions,
                int(max_size_kb) if max_size_kb else None
            )
            self.after(0, self._complete, success)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success):
        self.resize_btn.configure(state="normal", text="📐 RESIZE IMAGE")
        if success:
            self.status_label.configure(text=f"✓ Image resized successfully", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"Image resized!\n\nOutput: {self.output_file}")
        else:
            self.status_label.configure(text="✗ Resize failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.resize_btn.configure(state="normal", text="📐 RESIZE IMAGE")
        self.status_label.configure(text="✗ Error", text_color=theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

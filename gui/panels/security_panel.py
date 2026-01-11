"""
Security Panel - Add password protection or watermarks to PDFs
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class SecurityPanel(ctk.CTkFrame):
    """Panel for password protection and watermarking"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG_PRIMARY, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        
        self.mode = "password" # password or watermark
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
                    suffix = "_protected" if self.mode == "password" else "_watermarked"
                    output = str(p.with_name(f"{p.stem}{suffix}{p.suffix}"))
                    self.output_entry.delete(0, "end")
                    self.output_entry.insert(0, output)
                    self.output_file = output
                    
                    self.status_label.configure(text=f"Selected: {p.name}", text_color=theme.INFO)
                else:
                    self.status_label.configure(text="Please drop a PDF file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="PDF Security", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Add password protection or watermark to PDFs",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        # Mode selection
        mode_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        mode_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            mode_frame, text="Security Type", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        btn_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.password_btn = ctk.CTkButton(
            btn_frame, text="🔒 Password Protection", command=lambda: self.set_mode("password"),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            height=38, corner_radius=8
        )
        self.password_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.watermark_btn = ctk.CTkButton(
            btn_frame, text="🏷️ Watermark", command=lambda: self.set_mode("watermark"),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.BG_TERTIARY, hover_color=theme.get_accent_hover(),
            height=38, corner_radius=8
        )
        self.watermark_btn.pack(side="left", fill="x", expand=True)
        
        # Input
        input_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        input_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            input_frame, text="Input PDF", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        path_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = ctk.CTkEntry(
            path_frame, placeholder_text="Choose PDF...",
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
        
        # Settings (password or watermark text)
        settings_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        settings_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        self.settings_label = ctk.CTkLabel(
            settings_frame, text="Password", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        )
        self.settings_label.pack(fill="x", padx=20, pady=(15, 10))
        
        self.settings_entry = ctk.CTkEntry(
            settings_frame, placeholder_text="Enter password...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=35, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER, show="*"
        )
        self.settings_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Output
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 15))
        
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
        
        # Apply button
        self.apply_btn = ctk.CTkButton(
            self, text="🔒 APPLY PROTECTION", command=self.apply_security,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"), height=45,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.apply_btn.grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select a PDF and enter password", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=7, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def set_mode(self, mode):
        self.mode = mode
        if mode == "password":
            self.password_btn.configure(fg_color=theme.get_accent())
            self.watermark_btn.configure(fg_color=theme.BG_TERTIARY)
            self.settings_label.configure(text="Password")
            self.settings_entry.configure(placeholder_text="Enter password...", show="*")
            self.apply_btn.configure(text="🔒 APPLY PROTECTION")
        else:
            self.password_btn.configure(fg_color=theme.BG_TERTIARY)
            self.watermark_btn.configure(fg_color=theme.get_accent())
            self.settings_label.configure(text="Watermark Text")
            self.settings_entry.configure(placeholder_text="Enter watermark text...", show="")
            self.apply_btn.configure(text="🏷️ ADD WATERMARK")
            
    def browse_input(self):
        file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.input_file = file
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            if not self.output_file:
                suffix = "_protected" if self.mode == "password" else "_watermarked"
                # Python 3.8 compatible replacement for with_stem
                p = Path(file)
                output = str(p.with_name(f"{p.stem}{suffix}{p.suffix}"))
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, output)
                self.output_file = output
            
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save as", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")]
        )
        if file:
            self.output_file = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def apply_security(self):
        if not self.input_file or not self.output_file:
            messagebox.showerror("Error", "Please select input and output files")
            return
            
        value = self.settings_entry.get().strip()
        if not value:
            msg = "password" if self.mode == "password" else "watermark text"
            messagebox.showerror("Error", f"Please enter {msg}")
            return
            
        self.apply_btn.configure(state="disabled", text="Applying...")
        self.status_label.configure(text="Processing...", text_color=theme.INFO)
        
        threading.Thread(target=self._do_apply, args=(value,)).start()
        
    def _do_apply(self, value):
        try:
            if self.mode == "password":
                success = Controller.add_password(self.input_file, self.output_file, value)
            else:
                success = Controller.add_watermark(self.input_file, self.output_file, value)
            self.after(0, self._complete, success)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success):
        self.apply_btn.configure(state="normal", text="🔒 APPLY PROTECTION" if self.mode == "password" else "🏷️ ADD WATERMARK")
        if success:
            action = "protected" if self.mode == "password" else "watermarked"
            self.status_label.configure(text=f"✓ PDF {action} successfully", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"PDF {action}!\n\nOutput: {self.output_file}")
        else:
            self.status_label.configure(text="✗ Operation failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.apply_btn.configure(state="normal", text="🔒 APPLY PROTECTION" if self.mode == "password" else "🏷️ ADD WATERMARK")
        self.status_label.configure(text="✗ Error", text_color=theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

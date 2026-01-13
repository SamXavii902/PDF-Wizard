"""
Compare Panel - Compare two PDFs and highlight differences
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class ComparePanel(ctk.CTkFrame):
    """Panel for comparing PDFs"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG_PRIMARY, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.file1 = ""
        self.file2 = ""
        self.output_file = ""
        
        self.create_widgets()
        
        # Enable Drag & Drop
        self.pdf1_entry.drop_target_register('DND_Files')
        self.pdf1_entry.dnd_bind('<<Drop>>', self.drop_file1)
        
        self.pdf2_entry.drop_target_register('DND_Files')
        self.pdf2_entry.dnd_bind('<<Drop>>', self.drop_file2)
        
    def drop_file1(self, event):
        self._handle_drop(event, 1)
        
    def drop_file2(self, event):
        self._handle_drop(event, 2)
        
    def _handle_drop(self, event, num):
        try:
            files = parse_dropped_files(event.data)
            if files:
                file = files[0]
                if file.lower().endswith('.pdf'):
                    if num == 1:
                        self.file1 = file
                        self.pdf1_entry.delete(0, "end")
                        self.pdf1_entry.insert(0, file)
                    else:
                        self.file2 = file
                        self.pdf2_entry.delete(0, "end")
                        self.pdf2_entry.insert(0, file)
                else:
                    self.status_label.configure(text="Please drop a PDF file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="Compare PDFs", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Compare two PDF files and identify differences",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        # PDF 1
        pdf1_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        pdf1_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            pdf1_frame, text="First PDF", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        path1_frame = ctk.CTkFrame(pdf1_frame, fg_color="transparent")
        path1_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.pdf1_entry = ctk.CTkEntry(
            path1_frame, placeholder_text="Choose first PDF...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=35, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.pdf1_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            path1_frame, text="📁", command=self.browse_pdf1,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=50, height=35, fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_SIDEBAR, corner_radius=8
        ).pack(side="left")
        
        # PDF 2
        pdf2_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        pdf2_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            pdf2_frame, text="Second PDF", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        path2_frame = ctk.CTkFrame(pdf2_frame, fg_color="transparent")
        path2_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.pdf2_entry = ctk.CTkEntry(
            path2_frame, placeholder_text="Choose second PDF...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=35, fg_color=theme.BG_TERTIARY, border_color=theme.BORDER
        )
        self.pdf2_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            path2_frame, text="📁", command=self.browse_pdf2,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=50, height=35, fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_SIDEBAR, corner_radius=8
        ).pack(side="left")
        
        # Output
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            output_frame, text="Comparison Report", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))
        
        output_path_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.output_entry = ctk.CTkEntry(
            output_path_frame, placeholder_text="Save comparison report as...",
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
        
        # Compare button
        self.compare_btn = ctk.CTkButton(
            self, text="🔍 COMPARE PDFS", command=self.compare_pdfs,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"), height=45,
            fg_color=theme.get_accent(), hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.compare_btn.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select two PDFs to compare", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def browse_pdf1(self):
        file = filedialog.askopenfilename(title="Select first PDF", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.pdf1 = file
            self.pdf1_entry.delete(0, "end")
            self.pdf1_entry.insert(0, file)
            
    def browse_pdf2(self):
        file = filedialog.askopenfilename(title="Select second PDF", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.pdf2 = file
            self.pdf2_entry.delete(0, "end")
            self.pdf2_entry.insert(0, file)
            
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save comparison report as", defaultextension=".pdf",
            initialfile="comparison_report.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file:
            self.output_file = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def compare_pdfs(self):
        if not self.pdf1 or not self.pdf2:
            messagebox.showerror("Error", "Please select both PDF files")
            return
            
        if not self.output_file:
            return
            
        self.compare_btn.configure(state="disabled", text="Comparing...")
        self.status_label.configure(text="Comparing PDFs...", text_color=theme.INFO)
        
        threading.Thread(target=self._do_compare).start()
        
    def _do_compare(self):
        try:
            success = Controller.compare_pdfs(self.pdf1, self.pdf2, self.output_file)
            self.after(0, self._complete, success)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success):
        self.compare_btn.configure(state="normal", text="⚖️ COMPARE PDFS")
        if success:
            self.status_label.configure(text="✓ Comparison successful", text_color=theme.SUCCESS)
            
            # Check for report file
            p = Path(self.output_file)
            report = p.with_name(f"{p.stem}_report.txt")
            
            msg = f"Comparison complete!\n\nVisual Report: {self.output_file}"
            if report.exists():
                msg += f"\nText Summary: {report}"
                
            messagebox.showinfo("Success", msg)
        else:
            self.status_label.configure(text="✗ Comparison failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

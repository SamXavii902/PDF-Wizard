"""
Merge Panel - GUI for merging multiple PDFs

Features:
- Drag & drop file list
- Reorder files
- Output path picker
- Merge execution
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class MergePanel(ctk.CTkFrame):
    """Panel for merging PDFs"""
    
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=theme.BG_PRIMARY,
            corner_radius=0
        )
        
        # Configure grid for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # File list expands
        
        self.files = []
        self.output_path = ""
        
        self.create_widgets()
        
        # Enable Drag & Drop
        self.file_listbox.drop_target_register('DND_Files')
        self.file_listbox.dnd_bind('<<Drop>>', self.drop_files)
        
    def drop_files(self, event):
        """Handle file drop event"""
        try:
            # Parse dropped files (handle paths with spaces and {})
            files = parse_dropped_files(event.data)
            valid_files = [f for f in files if f.lower().endswith('.pdf')]
            
            if valid_files:
                self.files.extend(valid_files)
                self.update_file_list()
                self.update_status(f"Added {len(valid_files)} file(s) via drag & drop")
            else:
                self.update_status("No valid PDF files dropped", theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
            
    def create_widgets(self):
        """Create all panel widgets"""
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Merge PDFs",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 5))
        
        subtitle = ctk.CTkLabel(
            self,
            text="Combine multiple PDF files into a single document",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14),
            text_color=theme.TEXT_SECONDARY,
            anchor="w"
        )
        subtitle.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        
        # Files section (expandable)
        files_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        files_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 15))
        files_frame.grid_columnconfigure(0, weight=1)
        files_frame.grid_rowconfigure(1, weight=1)
        
        # Files header
        files_header = ctk.CTkLabel(
            files_frame,
            text="Files to Merge",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        files_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        # File list
        self.file_listbox = ctk.CTkTextbox(
            files_frame,
            fg_color=theme.BG_TERTIARY,
            text_color=theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12)
        )
        self.file_listbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        
        # File buttons
        btn_frame = ctk.CTkFrame(files_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="+ Add Files",
            command=self.add_files,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.get_accent(),
            hover_color=theme.get_accent_hover(),
            height=35,
            corner_radius=8
        )
        add_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear All",
            command=self.clear_files,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.ERROR,
            height=35,
            corner_radius=8
        )
        clear_btn.pack(side="left")
        
        # Output section
        output_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        output_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Output File",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        output_label.pack(fill="x", padx=20, pady=(15, 10))
        
        output_path_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.output_entry = ctk.CTkEntry(
            output_path_frame,
            placeholder_text="Choose output location...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            height=35,
            fg_color=theme.BG_TERTIARY,
            border_color=theme.BORDER
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            output_path_frame,
            text="📁",
            command=self.browse_output,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            width=50,
            height=35,
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_SIDEBAR,
            corner_radius=8
        )
        browse_btn.pack(side="left")
        
        # Action section
        self.merge_btn = ctk.CTkButton(
            self,
            text="🔗 MERGE PDFS",
            command=self.merge_pdfs,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=15, weight="bold"),
            height=45,
            fg_color=theme.get_accent(),
            hover_color=theme.get_accent_hover(),
            corner_radius=10
        )
        self.merge_btn.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Add PDF files to begin",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 15))
        
    def add_files(self):
        """Open file dialog to add PDF files"""
        files = filedialog.askopenfilenames(
            title="Select PDF files to merge",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            self.files.extend(files)
            self.update_file_list()
            self.update_status(f"Added {len(files)} file(s)")
            
    def clear_files(self):
        """Clear all files from the list"""
        self.files = []
        self.update_file_list()
        self.update_status("Files cleared")
        
    def update_file_list(self):
        """Update the file listbox display"""
        self.file_listbox.delete("1.0", "end")
        
        if not self.files:
            self.file_listbox.insert("1.0", "No files added yet.\nClick '+ Add Files' or drag PDFs here.")
        else:
            for i, file in enumerate(self.files, 1):
                filename = Path(file).name
                self.file_listbox.insert("end", f"{i}. {filename}\n")
                
    def browse_output(self):
        """Browse for output file location"""
        initial_file = None
        # Auto-populate output if no path is set and files are present
        if not self.output_path and self.files:
            # Python 3.8 compatible replacement for with_stem
            # original: output = str(Path(self.files[0]).with_stem("merged_output"))
            p = Path(self.files[0])
            initial_file = str(p.with_name(f"merged_output{p.suffix}"))

        file = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=initial_file
        )
        
        if file:
            self.output_path = file
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def update_status(self, message, color=None):
        """Update the status label"""
        self.status_label.configure(
            text=message,
            text_color=color or theme.TEXT_SECONDARY
        )
        
    def merge_pdfs(self):
        """Execute the merge operation"""
        # Validation
        if len(self.files) < 2:
            messagebox.showerror("Error", "Please add at least 2 PDF files to merge")
            return
            
        if not self.output_path:
            messagebox.showerror("Error", "Please choose an output location")
            return
            
        # Disable button during operation
        self.merge_btn.configure(state="disabled", text="Merging...")
        self.update_status("Merging PDFs...", theme.INFO)
        
        # Run in thread to keep UI responsive
        thread = threading.Thread(target=self._do_merge)
        thread.start()
        
    def _do_merge(self):
        """Perform the merge in a background thread"""
        try:
            # Call the controller
            success = Controller.merge_pdfs(self.files, self.output_path)
            
            # Update UI on main thread
            self.after(0, self._merge_complete, success)
            
        except Exception as e:
            self.after(0, self._merge_error, str(e))
            
    def _merge_complete(self, success):
        """Called when merge completes successfully"""
        self.merge_btn.configure(state="normal", text="🔗 MERGE PDFS")
        
        if success:
            self.update_status(f"✓ Successfully merged to {Path(self.output_path).name}", theme.SUCCESS)
            messagebox.showinfo("Success", f"PDFs merged successfully!\n\nOutput: {self.output_path}")
        else:
            self.update_status("✗ Merge failed", theme.ERROR)
            messagebox.showerror("Error", "Failed to merge PDFs. Check console for details.")
            
    def _merge_error(self, error_msg):
        """Called when an error occurs"""
        self.merge_btn.configure(state="normal", text="🔗 MERGE PDFS")
        self.update_status(f"✗ Error: {error_msg[:50]}...", theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

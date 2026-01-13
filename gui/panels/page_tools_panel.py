"""
Page Tools Panel - Academic PDF operations (reorder, auto-rotate, remove blanks, add numbers)
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from gui.theme import theme
from pdf_wizard.controller import Controller


from gui.dnd import parse_dropped_files

class PageToolsPanel(ctk.CTkFrame):
    """Panel for page manipulation tools"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG_PRIMARY, corner_radius=0)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
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
                    self.status_label.configure(text=f"Selected: {Path(file).name}", text_color=theme.INFO)
                else:
                    self.status_label.configure(text="Please drop a PDF file", text_color=theme.WARNING)
        except Exception as e:
            print(f"Drop error: {e}")
        
    def create_widgets(self):
        # Header
        ctk.CTkLabel(
            self, text="Page Tools", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=28, weight="bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=30, pady=(30, 5))
        
        ctk.CTkLabel(
            self, text="Academic PDF tools: reorder, rotate, remove blanks, add page numbers",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14), text_color=theme.TEXT_SECONDARY, anchor="w"
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=30, pady=(0, 20))
        
        # Input
        input_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=10)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(
            input_frame, text="Input PDF", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"),
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
        
        # Tool buttons - Grid layout (2 columns)
        # Row 1
        self.create_tool_button(
            3, 0, "🗑️ Remove Blank Pages", 
            lambda: self.run_tool("remove_blanks", "Remove Blank Pages")
        )
        self.create_tool_button(
            3, 1, "🔄 Auto-Rotate Pages", 
            lambda: self.run_tool("auto_rotate", "Auto-Rotate Pages")
        )
        
        # Row 2
        self.create_tool_button(
            4, 0, "🔢 Add Page Numbers", 
            lambda: self.run_tool("add_numbers", "Add Page Numbers")
        )
        self.create_tool_button(
            4, 1, "📑 Reorder Pages", 
            lambda: self.reorder_pages()
        )
        
        # Status
        self.status_label = ctk.CTkLabel(
            self, text="Select a PDF and choose a tool", font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12),
            text_color=theme.TEXT_SECONDARY
        )
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=30, pady=(15, 15))
        
    def create_tool_button(self, row, col, text, command):
        """Helper to create a tool button"""
        btn = ctk.CTkButton(
            self, text=text, command=command,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=14, weight="bold"), height=60,
            fg_color=theme.BG_SECONDARY, hover_color=theme.get_accent(),
            corner_radius=10, border_width=2, border_color=theme.BORDER
        )
        btn.grid(row=row, column=col, sticky="ew", padx=(30 if col == 0 else 8, 8 if col == 0 else 30), pady=8)
        
    def browse_input(self):
        file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF files", "*.pdf")])
        if file:
            self.input_file = file
            self.input_entry.delete(0, "end" )
            self.input_entry.insert(0, file)
            self.status_label.configure(text=f"Selected: {Path(file).name}", text_color=theme.INFO)
            
    def reorder_pages(self):
        """Handle page reordering with dialog"""
        if not self.input_file:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
            
        # Simple dialog for page order
        order = ctk.CTkInputDialog(
            text="Enter new page order (e.g., '1,3,2,4,5'):",
            title="Reorder Pages"
        ).get_input()
        
        if order:
            # Python 3.8 compatible replacement for with_stem based initialfile
            p = Path(self.input_file)
            initial = f"{p.stem}_reordered{p.suffix}"
            
            output = filedialog.asksaveasfilename(
                title="Save reordered PDF as", defaultextension=".pdf",
                initialfile=initial,
                filetypes=[("PDF files", "*.pdf")]
            )
            
            if output:
                self.status_label.configure(text="Reordering pages...", text_color=theme.INFO)
                threading.Thread(target=self._do_reorder, args=(order, output)).start()
                
    def _do_reorder(self, order, output):
        try:
            success = Controller.reorder_pages(self.input_file, output, order)
            self.after(0, self._complete, success, output, "reordered")
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def run_tool(self, tool_name, display_name):
        """Run a specific tool"""
        if not self.input_file:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
            
        suffix_map = {
            "remove_blanks": "_no_blanks",
            "auto_rotate": "_rotated",
            "add_numbers": "_numbered"
        }
        
        p = Path(self.input_file)
        suffix = suffix_map.get(tool_name, "_modified")
        initial = f"{p.stem}{suffix}{p.suffix}"
        
        output = filedialog.asksaveasfilename(
            title=f"Save {display_name.lower()} PDF as", defaultextension=".pdf",
            initialfile=initial,
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output:
            self.status_label.configure(text=f"Processing with {display_name}...", text_color=theme.INFO)
            threading.Thread(target=self._do_tool, args=(tool_name, output)).start()
            
    def _do_tool(self, tool_name, output):
        try:
            if tool_name == "remove_blanks":
                success = Controller.remove_blank_pages(self.input_file, output)
            elif tool_name == "auto_rotate":
                success = Controller.auto_rotate(self.input_file, output)
            elif tool_name == "add_numbers":
                success = Controller.add_page_numbers(self.input_file, output)
            else:
                success = False
                
            self.after(0, self._complete, success, output, tool_name)
        except Exception as e:
            self.after(0, self._error, str(e))
            
    def _complete(self, success, output, tool_name):
        if success:
            self.status_label.configure(text=f"✓ Operation completed successfully", text_color=theme.SUCCESS)
            messagebox.showinfo("Success", f"PDF processed!\n\nOutput: {output}")
        else:
            self.status_label.configure(text="✗ Operation failed", text_color=theme.ERROR)
            
    def _error(self, error_msg):
        self.status_label.configure(text="✗ Error", text_color=theme.ERROR)
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")

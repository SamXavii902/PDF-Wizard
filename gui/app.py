"""
PDF Wizard GUI - Main Application Window

Modern dark-themed GUI with Windows accent colors
"""

import customtkinter as ctk
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.theme import theme, PDFWizardTheme
from gui.panels.merge_panel import MergePanel
from gui.panels.compress_panel import CompressPanel
from gui.panels.split_panel import SplitPanel
from gui.panels.resize_image_panel import ResizeImagePanel
from gui.panels.qr_panel import QRPanel
from gui.panels.security_panel import SecurityPanel
from gui.panels.metadata_panel import MetadataPanel
from gui.panels.convert_panel import ConvertPanel
from gui.panels.compress_image_panel import CompressImagePanel
from gui.panels.page_tools_panel import PageToolsPanel
from gui.panels.compare_panel import ComparePanel

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # We'll override with custom colors


from tkinterdnd2 import TkinterDnD

class PDFWizardGUI(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        # Window configuration
        self.title("PDF Wizard")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Configure colors
        self.configure(fg_color=theme.BG_PRIMARY)
        
        # Set window icon (if available)
        try:
            self.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Current panel reference
        self.current_panel = None
        
        # Create UI
        self.create_layout()
        self.show_panel("merge")
        
    def create_layout(self):
        """Create the main layout with sidebar and content area"""
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ==== SIDEBAR ====
        self.sidebar = ctk.CTkFrame(
            self,
            width=200,
            corner_radius=0,
            fg_color=theme.BG_SIDEBAR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)  # Push settings to bottom
        
        # App title
        title = ctk.CTkLabel(
            self.sidebar,
            text="🧙 PDF Wizard",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=20, weight="bold"),
            text_color=theme.TEXT_PRIMARY
        )
        title.grid(row=0, column=0, padx=20, pady=20)
        
        # PDF Operations section
        self.create_section_header(self.sidebar, 1, "📄 PDF Operations")
        self.create_nav_button(self.sidebar, 2, "Merge", "merge")
        self.create_nav_button(self.sidebar, 3, "Split", "split")
        self.create_nav_button(self.sidebar, 4, "Compress", "compress")
        self.create_nav_button(self.sidebar, 5, "Security", "security")
        self.create_nav_button(self.sidebar, 6, "Metadata", "metadata")
        
        # Image Processing section
        self.create_section_header(self.sidebar, 8, "📸 Image Processing")
        self.create_nav_button(self.sidebar, 9, "Resize", "resize")
        self.create_nav_button(self.sidebar, 10, "Compress Image", "compress_image")
        self.create_nav_button(self.sidebar, 11, "Convert", "convert")
        
        # Academic Tools section
        self.create_section_header(self.sidebar, 13, "🎓 Academic Tools")
        self.create_nav_button(self.sidebar, 14, "Page Tools", "page_tools")
        self.create_nav_button(self.sidebar, 15, "QR Generator", "qr")
        self.create_nav_button(self.sidebar, 16, "Compare", "compare")
        
        # Settings at bottom
        self.create_nav_button(self.sidebar, 21, "⚙️ Settings", "settings")
        
        # ==== CONTENT AREA ====
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=theme.BG_PRIMARY
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        
    def create_section_header(self, parent, row, text):
        """Create a section header in the sidebar"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=12, weight="bold"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w"
        )
        label.grid(row=row, column=0, padx=20, pady=(15, 5), sticky="w")
        
    def create_nav_button(self, parent, row, text, panel_name):
        """Create a navigation button"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=lambda: self.show_panel(panel_name),
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=13),
            fg_color="transparent",
            text_color=theme.TEXT_PRIMARY,
            hover_color=theme.BG_TERTIARY,
            anchor="w",
            height=35,
            corner_radius=5
        )
        btn.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
        
    def show_panel(self, panel_name):
        """Switch to a different panel"""
        # Clear current panel
        if self.current_panel:
            self.current_panel.destroy()
        
        # Create new panel
        if panel_name == "merge":
            self.current_panel = MergePanel(self.content)
        elif panel_name == "split":
            self.current_panel = SplitPanel(self.content)
        elif panel_name == "compress":
            self.current_panel = CompressPanel(self.content)
        elif panel_name == "security":
            self.current_panel = SecurityPanel(self.content)
        elif panel_name == "metadata":
            self.current_panel = MetadataPanel(self.content)
        elif panel_name == "resize":
            self.current_panel = ResizeImagePanel(self.content)
        elif panel_name == "compress_image":
            self.current_panel = CompressImagePanel(self.content)
        elif panel_name == "convert":
            self.current_panel = ConvertPanel(self.content)
        elif panel_name == "page_tools":
            self.current_panel = PageToolsPanel(self.content)
        elif panel_name == "qr":
            self.current_panel = QRPanel(self.content)
        elif panel_name == "compare":
            self.current_panel = ComparePanel(self.content)
        elif panel_name == "settings":
            self.current_panel = self.create_placeholder("Settings")
        
        self.current_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
    def create_placeholder(self, title):
        """Create a placeholder panel for features not yet implemented"""
        frame = ctk.CTkFrame(self.content, fg_color=theme.BG_PRIMARY)
        
        label = ctk.CTkLabel(
            frame,
            text=f"{title}\n\n(Coming soon...)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY,size=24),
            text_color=theme.TEXT_SECONDARY
        )
        label.pack(expand=True)
        
        return frame


def main():
    """Entry point for the GUI"""
    app = PDFWizardGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

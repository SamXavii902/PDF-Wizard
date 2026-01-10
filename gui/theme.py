"""
PDF Wizard GUI - Theme System with Windows Accent Colors

Provides dark theme with Windows accent color integration
"""

import winreg
from typing import Tuple

class PDFWizardTheme:
    """Theme configuration for PDF Wizard GUI"""
    
    def __init__(self):
        self.accent_color = self.get_windows_accent_color()
        self.accent_hover = self.lighten_color(self.accent_color, 20)
        
    @staticmethod
    def get_windows_accent_color() -> str:
        """Get Windows 10/11 accent color from registry"""
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r'SOFTWARE\Microsoft\Windows\DWM')
            accent_color_dword = winreg.QueryValueEx(key, 'AccentColor')[0]
            winreg.CloseKey(key)
            
            # Convert DWORD to RGB (format: 0xAABBGGRR)
            r = (accent_color_dword >> 0) & 0xff
            g = (accent_color_dword >> 8) & 0xff
            b = (accent_color_dword >> 16) & 0xff
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            # Fallback to pink if can't read registry
            return "#e91e63"
    
    @staticmethod
    def lighten_color(hex_color: str, percent: int) -> str:
        """Lighten a hex color by a percentage"""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        r = min(255, int(r + (255 - r) * percent / 100))
        g = min(255, int(g + (255 - g) * percent / 100))
        b = min(255, int(b + (255 - b) * percent / 100))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # Color Palette (Dark Theme like reference UI)
    BG_PRIMARY = "#1e1e1e"      # Main background
    BG_SECONDARY = "#2d2d2d"    # Panel backgrounds  
    BG_TERTIARY = "#3d3d3d"     # Hover states
    BG_SIDEBAR = "#252525"      # Sidebar background
    
    TEXT_PRIMARY = "#ffffff"     # Main text
    TEXT_SECONDARY = "#b0b0b0"  # Secondary text
    TEXT_DISABLED = "#707070"   # Disabled text
    
    BORDER = "#404040"           # Borders
    BORDER_LIGHT = "#505050"    # Lighter borders
    
    SUCCESS = "#4caf50"          # Success messages
    ERROR = "#f44336"            # Error messages
    WARNING = "#ff9800"          # Warnings
    INFO = "#2196f3"             # Info messages
    
    def get_accent(self) -> str:
        """Get the accent color"""
        return self.accent_color
    
    def get_accent_hover(self) -> str:
        """Get the accent hover color"""
        return self.accent_hover
        
    # Font Configuration
    FONT_FAMILY = "DM Sans"

# Global theme instance
theme = PDFWizardTheme()


# CustomTkinter color configuration
CTK_THEME = {
    "CTk": {
        "fg_color": [theme.BG_PRIMARY, theme.BG_PRIMARY]
    },
    "CTkFrame": {
        "fg_color": [theme.BG_SECONDARY, theme.BG_SECONDARY],
        "border_color": [theme.BORDER, theme.BORDER]
    },
    "CTkButton": {
        "fg_color": [theme.get_accent(), theme.get_accent()],
        "hover_color": [theme.get_accent_hover(), theme.get_accent_hover()],
        "text_color": [theme.TEXT_PRIMARY, theme.TEXT_PRIMARY],
        "border_color": [theme.get_accent(), theme.get_accent()]
    },
    "CTkLabel": {
        "text_color": [theme.TEXT_PRIMARY, theme.TEXT_PRIMARY]
    },
    "CTkEntry": {
        "fg_color": [theme.BG_TERTIARY, theme.BG_TERTIARY],
        "text_color": [theme.TEXT_PRIMARY, theme.TEXT_PRIMARY],
        "border_color": [theme.BORDER, theme.BORDER]
    },
    "CTkTextbox": {
        "fg_color": [theme.BG_TERTIARY, theme.BG_TERTIARY],
        "text_color": [theme.TEXT_PRIMARY, theme.TEXT_PRIMARY],
        "border_color": [theme.BORDER, theme.BORDER]
    },
    "CTkSwitch": {
        "progress_color": [theme.get_accent(), theme.get_accent()],
        "button_color": [theme.TEXT_PRIMARY, theme.TEXT_PRIMARY],
        "button_hover_color": [theme.BG_TERTIARY, theme.BG_TERTIARY]
    },
    "CTkProgressBar": {
        "progress_color": [theme.get_accent(), theme.get_accent()],
        "fg_color": [theme.BG_TERTIARY, theme.BG_TERTIARY]
    },
    "CTkOptionMenu": {
        "fg_color": [theme.BG_TERTIARY, theme.BG_TERTIARY],
        "button_color": [theme.BG_TERTIARY, theme.BG_TERTIARY],
        "button_hover_color": [theme.get_accent(), theme.get_accent()],
        "text_color": [theme.TEXT_PRIMARY, theme.TEXT_PRIMARY]
    }
}

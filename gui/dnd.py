
import re

def parse_dropped_files(data):
    """Parse TkinterDnD dropped file list
    
    Handles paths with spaces (wrapped in {}) and simple space-separated paths.
    """
    files = []
    if not data:
        return files
        
    # Check if data contains curly braces (indicated paths with spaces)
    if '{' in data:
         # Regex to match content inside {} or single words
         pattern = r'\{(.+?)\}|([^ ]+)'
         for match in re.finditer(pattern, data):
             path = match.group(1) or match.group(2)
             if path:
                 files.append(path)
    else:
         # simple space separated (if no spaces in paths)
         files = data.split()
         
    return files

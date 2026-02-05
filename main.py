import tkinter as tk
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_window import AuthWindow
from record_store import RecordStoreApp

class VinylFlowApp:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("VinylFlow - Record Store Management")
        
        # Set window size and position
        self.setup_window()
        
        # Initialize current app
        self.current_app = None

        # Show auth window
        self.show_auth_window()
        
        # Start main loop
        self.root.mainloop()
    
    def setup_window(self):
        """Setup main window size and position"""
        # Set minimum size
        self.root.minsize(1200, 700)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window size (90% of screen)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Calculate position to center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window geometry
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Set window icon (if you have one)
        try:
            self.root.iconbitmap('vinylflow.ico')
        except:
            pass
        
        # Configure grid for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def show_auth_window(self):
        """Show authentication window"""
        # Clear the main window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.current_app = AuthWindow(self.root, self.on_auth_success)
    
    def on_auth_success(self, is_owner, user):
        """Handle successful authentication"""
        # Clear the main window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.current_app = RecordStoreApp(self.root, is_owner=is_owner, user=user, logout_callback=self.show_auth_window)

if __name__ == "__main__":
    app = VinylFlowApp()
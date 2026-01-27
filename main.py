import tkinter as tk
from tkinter import font as tkfont, messagebox
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_window import AuthWindow
from record_store import RecordStoreApp

class VinylFlowApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window initially
        
        # Set application-wide font
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        
        # Show authentication window
        self.show_auth_window()
        
        # Start the application
        self.root.mainloop()
    
    def show_auth_window(self):
        """Show authentication window"""
        auth_window = tk.Toplevel(self.root)
        auth_window.title("VinylFlow - Login")
        auth_window.geometry("600x500")
        auth_window.resizable(False, False)
        
        # Center window
        self.center_window(auth_window)
        
        # Create auth interface
        self.auth = AuthWindow(auth_window, self.on_auth_success)
        
        # Handle close
        def on_auth_close():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                auth_window.destroy()
                self.root.destroy()
        
        auth_window.protocol("WM_DELETE_WINDOW", on_auth_close)
    
    def on_auth_success(self, is_owner, user):
        """Callback for successful authentication"""
        # Create a new window for the application
        app_window = tk.Toplevel(self.root)
        app_window.title(f"VinylFlow - Record Store {'Manager' if is_owner else 'Customer'}")
        app_window.geometry("1200x800")
        app_window.minsize(1000, 600)
        
        # Center the window
        self.center_window(app_window)
        
        # Create the application
        app = RecordStoreApp(app_window, is_owner=is_owner, user=user, logout_callback=self.on_logout)
        
        # Handle window close
        def on_app_close():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                app_window.destroy()
        
        app_window.protocol("WM_DELETE_WINDOW", on_app_close)
    
    def on_logout(self):
        """Handle logout from app"""
        # Destroy all app windows
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        
        # Show auth window again
        self.show_auth_window()
    
    def center_window(self, window):
        """Center window on screen"""
        window.update_idletasks()
        width = window.winfo_width() or 600
        height = window.winfo_height() or 500
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    app = VinylFlowApp()
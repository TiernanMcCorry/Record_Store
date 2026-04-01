import tkinter as tk
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_window import AuthWindow
from record_store import RecordStoreApp

class VinylFlowApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FirstPress Vinyl - Record Store Management")
        self.setup_window()
        self.current_app = None
        self.show_auth_window()
        self.root.mainloop()
    
    def setup_window(self):
        self.root.minsize(1200, 700)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def show_auth_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.current_app = AuthWindow(self.root, self.on_auth_success)
    
    def on_auth_success(self, is_owner, user):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.current_app = RecordStoreApp(self.root, is_owner=is_owner, user=user, logout_callback=self.show_auth_window)

if __name__ == "__main__":
    app = VinylFlowApp()

import tkinter as tk
from tkinter import ttk
from config import FONTS, COLORS

class ModernButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.style = ttk.Style()
        self.style.configure('Modern.TButton', 
                           font=FONTS['button'],
                           padding=6)
        self.configure(style='Modern.TButton')

class ModernEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **{'font': FONTS['entry'], **kwargs})

class ModernLabel(ttk.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **{'font': FONTS['label'], **kwargs})
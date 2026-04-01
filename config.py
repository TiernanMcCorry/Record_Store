# config.py

# Vinyl-themed colors (deep charcoal, gold, brown)
VINYL_COLORS = {
    'primary': '#c4a747',           # Rich gold
    'primary_light': '#d4b86a',
    'primary_dark': '#a8883a',
    'secondary': '#8b5a2b',          # Brown
    'success': '#2d6a4f',            # Dark green
    'danger': '#bc4742',             # Terracotta
    'warning': '#e9c46a',            # Light gold
    'info': '#2a9d8f',               # Teal
    'light': '#3c2a1f',              # Dark brown
    'light_gray': '#5c4b3a',
    'dark': '#f0e6d2',               # Cream
    'dark_gray': '#d4c5b0',
    'white': '#1e1a16',              # Charcoal background
    'gray': '#6b5b4c',
    'bg': '#1e1a16',                 # Dark charcoal
    'fg': '#f0e6d2',                 # Cream
    'entry_bg': '#2d241c',
    'entry_border': '#5c4b3a',
    'tree_bg': '#2d241c',
    'tree_fg': '#f0e6d2',
    'tree_heading_bg': '#3c2a1f',
    'tree_heading_fg': '#c4a747',
    'tree_selected_bg': '#c4a747',
    'tree_selected_fg': '#1e1a16',
    'card_bg': '#2d241c',
    'card_shadow': '#00000030',
    'border': '#5c4b3a',
    'sidebar_bg': '#2d241c',
    'sidebar_fg': '#d4c5b0',
    'sidebar_active': '#c4a747',
    'accent': '#e9c46a',
    'gradient_start': '#c4a747',
    'gradient_end': '#8b5a2b',
}
# Color schemes - Modern Dark Mode as default
DARK_COLORS = {
    'primary': '#8b5cf6',           # Modern purple
    'primary_light': '#a78bfa',
    'primary_dark': '#7c3aed',
    'secondary': '#64748b',         # Slate
    'success': '#10b981',          # Emerald
    'danger': '#ef4444',           # Red
    'warning': '#f59e0b',          # Amber
    'info': '#06b6d4',             # Cyan
    'light': '#1e293b',            # Dark blue-gray
    'light_gray': '#334155',
    'dark': '#f8fafc',             # Light text
    'dark_gray': '#cbd5e1',
    'white': '#0f172a',            # Very dark blue
    'gray': '#475569',
    'bg': '#0f172a',               # App background
    'fg': '#f1f5f9',               # Text color
    'entry_bg': '#1e293b',
    'entry_border': '#475569',
    'tree_bg': '#1e293b',
    'tree_fg': '#f1f5f9',
    'tree_heading_bg': '#334155',
    'tree_heading_fg': '#cbd5e1',
    'tree_selected_bg': '#7c3aed',
    'tree_selected_fg': '#ffffff',
    'card_bg': '#1e293b',
    'card_shadow': '#00000030',
    'border': '#334155',
    'sidebar_bg': '#1e293b',
    'sidebar_fg': '#cbd5e1',
    'sidebar_active': '#8b5cf6',
    'accent': '#f97316',           # Orange accent
    'gradient_start': '#8b5cf6',
    'gradient_end': '#ec4899',
}

LIGHT_COLORS = {
    'primary': '#7c3aed',
    'primary_light': '#8b5cf6',
    'primary_dark': '#6d28d9',
    'secondary': '#64748b',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'info': '#06b6d4',
    'light': '#f8fafc',
    'light_gray': '#f1f5f9',
    'dark': '#1e293b',
    'dark_gray': '#64748b',
    'white': '#ffffff',
    'gray': '#e2e8f0',
    'bg': '#f8fafc',
    'fg': '#1e293b',
    'entry_bg': '#ffffff',
    'entry_border': '#cbd5e1',
    'tree_bg': '#ffffff',
    'tree_fg': '#1e293b',
    'tree_heading_bg': '#f1f5f9',
    'tree_heading_fg': '#64748b',
    'tree_selected_bg': '#ede9fe',
    'tree_selected_fg': '#7c3aed',
    'card_bg': '#ffffff',
    'card_shadow': '#00000010',
    'border': '#e2e8f0',
    'sidebar_bg': '#1e293b',
    'sidebar_fg': '#cbd5e1',
    'sidebar_active': '#8b5cf6',
    'accent': '#f97316',
    'gradient_start': '#7c3aed',
    'gradient_end': '#ec4899',
}

# Default to dark mode for modern look
COLORS = DARK_COLORS.copy()


FONTS = {
    'h1': ('Inter', 32, 'bold'),
    'h2': ('Inter', 28, 'bold'),
    'h3': ('Inter', 24, 'bold'),
    'h4': ('Inter', 20, 'bold'),
    'h5': ('Inter', 18, 'bold'),
    'h6': ('Inter', 16, 'bold'),
    'body_large': ('Inter', 15),
    'body': ('Inter', 14),
    'body_small': ('Inter', 13),
    'caption': ('Inter', 12),
    'caption_small': ('Inter', 11),
    'button_large': ('Inter', 15, 'bold'),
    'button': ('Inter', 14, 'bold'),
    'button_small': ('Inter', 13, 'bold'),
    'code': ('JetBrains Mono', 13),
    'mono': ('JetBrains Mono', 12),
    'label': ('Inter', 10, 'bold'),
    'title': ('Inter', 24, 'bold'),
    'subtitle': ('Inter', 12),
    'small': ('Inter', 9),
    'heading': ('Inter', 16, 'bold'),
    'entry': ('Inter', 10),
    'status': ('Inter', 9),
}

# Modern shadow system
SHADOWS = {
    'none': '0 0 #0000',
    'xs': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    'sm': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    'base': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    'md': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    'lg': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    'xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
}

# Border radius system
RADIUS = {
    'none': '0',
    'sm': '4px',
    'base': '8px',
    'md': '12px',
    'lg': '16px',
    'xl': '24px',
    'full': '9999px',
}


def set_theme(theme):
    global COLORS
    if theme == 'dark':
        COLORS.update(DARK_COLORS)
    elif theme == 'light':
        COLORS.update(LIGHT_COLORS)
    else:
        COLORS.update(VINYL_COLORS)
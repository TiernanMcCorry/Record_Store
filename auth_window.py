import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from config import COLORS, FONTS, LIGHT_COLORS, DARK_COLORS
from datetime import datetime

class AuthWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        
        # Owner credentials
        self.owner_username = "FP"
        self.owner_password = "1539"
        
        # Customers file
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.customers_file = os.path.join(self.base_dir, "customers.json")
        self.customers = self.load_customers()
        
        # Setup window
        self.root.configure(bg=COLORS['bg'])
        self.create_styles()
        self.create_widgets()
    
    def create_styles(self):
        """Create custom styles for auth window"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure button styles
        self.style.configure('Primary.TButton',
                           background=COLORS['primary'],
                           foreground=COLORS['white'],
                           borderwidth=0,
                           padding=10,
                           font=FONTS['button'])
        
        self.style.configure('Secondary.TButton',
                           background=COLORS['secondary'],
                           foreground=COLORS['white'],
                           borderwidth=0,
                           padding=10,
                           font=FONTS['button'])
        
        self.style.configure('Success.TButton',
                           background=COLORS['success'],
                           foreground=COLORS['white'],
                           borderwidth=0,
                           padding=10,
                           font=FONTS['button'])
        
        self.style.configure('Danger.TButton',
                           background=COLORS['danger'],
                           foreground=COLORS['white'],
                           borderwidth=0,
                           padding=10,
                           font=FONTS['button'])
        
        self.style.map('Primary.TButton',
                      background=[('active', COLORS['primary_dark'])])
        self.style.map('Secondary.TButton',
                      background=[('active', COLORS['secondary'])])
        self.style.map('Success.TButton',
                      background=[('active', COLORS['success'])])
        self.style.map('Danger.TButton',
                      background=[('active', COLORS['danger'])])
    
    def create_widgets(self):
        """Create auth widgets"""
        # Header
        header_frame = tk.Frame(self.root, 
                              bg=COLORS['primary'],
                              height=100)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(header_frame, bg=COLORS['primary'])
        logo_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(logo_frame,
                text="💿",
                font=('Segoe UI Emoji', 36),
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left', padx=10)
        
        title_frame = tk.Frame(logo_frame, bg=COLORS['primary'])
        title_frame.pack(side='left')
        
        tk.Label(title_frame,
                text="VinylFlow",
                font=FONTS['title'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack()
        
        tk.Label(title_frame,
                text="Record Store Management",
                font=FONTS['subtitle'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg=COLORS['bg'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_customer_login_tab(notebook)
        self.create_customer_signup_tab(notebook)
        self.create_owner_login_tab(notebook)
        
        # Set initial tab
        notebook.select(0)
    
    def create_customer_login_tab(self, notebook):
        """Create customer login tab"""
        tab = tk.Frame(notebook, bg=COLORS['bg'])
        notebook.add(tab, text="👤 Customer Login")
        
        # Form container
        form_container = tk.Frame(tab, bg=COLORS['card_bg'],
                                relief='solid', borderwidth=1,
                                padx=30, pady=30)
        form_container.place(relx=0.5, rely=0.5, anchor='center', width=400, height=350)
        
        # Title
        tk.Label(form_container,
                text="Customer Login",
                font=FONTS['heading'],
                bg=COLORS['card_bg'],
                fg=COLORS['primary']).pack(pady=(0, 30))
        
        # Username
        tk.Label(form_container,
                text="Username",
                font=FONTS['label'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).pack(anchor='w', pady=(10, 5))
        
        self.cust_username = tk.Entry(form_container,
                                     font=FONTS['entry'],
                                     bg=COLORS['entry_bg'],
                                     fg=COLORS['fg'])
        self.cust_username.pack(fill='x', pady=(0, 20))
        
        # Password
        tk.Label(form_container,
                text="Password",
                font=FONTS['label'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).pack(anchor='w', pady=(5, 5))
        
        self.cust_password = tk.Entry(form_container,
                                     font=FONTS['entry'],
                                     bg=COLORS['entry_bg'],
                                     fg=COLORS['fg'],
                                     show="●")
        self.cust_password.pack(fill='x', pady=(0, 30))
        
        # Login button
        login_btn = tk.Button(form_container,
                            text="Login to Account",
                            font=FONTS['button'],
                            bg=COLORS['primary'],
                            fg=COLORS['white'],
                            relief='flat',
                            command=self.customer_login,
                            cursor='hand2',
                            padx=20,
                            pady=10)
        login_btn.pack(fill='x', pady=(0, 20))
        
        # Guest button
        guest_btn = tk.Button(form_container,
                            text="Continue as Guest",
                            font=FONTS['button'],
                            bg=COLORS['secondary'],
                            fg=COLORS['white'],
                            relief='flat',
                            command=lambda: self.on_login_success(is_owner=False, 
                                                                 user={'username': 'guest', 'is_guest': True}),
                            cursor='hand2',
                            padx=20,
                            pady=10)
        guest_btn.pack(fill='x')
        
        # Error message
        self.login_error = tk.Label(form_container,
                                  text="",
                                  font=FONTS['status'],
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['danger'])
        self.login_error.pack(pady=(20, 0))
        
        # Bind Enter key
        self.cust_password.bind('<Return>', lambda e: self.customer_login())
    
    def create_customer_signup_tab(self, notebook):
        """Create customer signup tab"""
        tab = tk.Frame(notebook, bg=COLORS['bg'])
        notebook.add(tab, text="📝 Customer Sign Up")
        
        # Scrollable container
        container = tk.Frame(tab, bg=COLORS['bg'])
        container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 5))
        scrollbar.pack(side="right", fill="y")
        
        # Form container
        form_container = tk.Frame(scrollable_frame, bg=COLORS['card_bg'],
                                relief='solid', borderwidth=1,
                                padx=30, pady=30)
        form_container.pack(fill='x', padx=20, pady=20)
        
        # Title
        tk.Label(form_container,
                text="Create New Account",
                font=FONTS['heading'],
                bg=COLORS['card_bg'],
                fg=COLORS['primary']).pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Username", "signup_username"),
            ("Email Address", "signup_email"),
            ("Full Name", "signup_name"),
            ("Password", "signup_password", True),
            ("Confirm Password", "signup_confirm", True),
            ("Address", "signup_address"),
            ("Phone Number", "signup_phone"),
        ]
        
        self.signup_entries = {}
        
        for label, field_name, *args in fields:
            is_password = len(args) > 0 and args[0]
            
            tk.Label(form_container,
                    text=label,
                    font=FONTS['label'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['fg']).pack(anchor='w', pady=(10, 5))
            
            if is_password:
                entry = tk.Entry(form_container,
                               font=FONTS['entry'],
                               bg=COLORS['entry_bg'],
                               fg=COLORS['fg'],
                               show="●")
            else:
                entry = tk.Entry(form_container,
                               font=FONTS['entry'],
                               bg=COLORS['entry_bg'],
                               fg=COLORS['fg'])
            
            entry.pack(fill='x', pady=(0, 10))
            self.signup_entries[field_name] = entry
        
        # Terms checkbox
        self.terms_var = tk.BooleanVar()
        terms_frame = tk.Frame(form_container, bg=COLORS['card_bg'])
        terms_frame.pack(fill='x', pady=10)
        
        terms_check = tk.Checkbutton(terms_frame,
                                   text="I agree to the Terms and Conditions",
                                   variable=self.terms_var,
                                   font=FONTS['small'],
                                   bg=COLORS['card_bg'],
                                   fg=COLORS['fg'])
        terms_check.pack(anchor='w')
        
        # Error message
        self.signup_error = tk.Label(form_container,
                                   text="",
                                   font=FONTS['status'],
                                   bg=COLORS['card_bg'],
                                   fg=COLORS['danger'])
        self.signup_error.pack(pady=(5, 0))
        
        # Signup button
        signup_btn = tk.Button(form_container,
                             text="Create Account",
                             font=FONTS['button'],
                             bg=COLORS['success'],
                             fg=COLORS['white'],
                             relief='flat',
                             command=self.customer_signup,
                             cursor='hand2',
                             padx=20,
                             pady=10)
        signup_btn.pack(fill='x', pady=(10, 0))
    
    def create_owner_login_tab(self, notebook):
        """Create owner login tab"""
        tab = tk.Frame(notebook, bg=COLORS['bg'])
        notebook.add(tab, text="🔐 Owner Login")
        
        # Form container
        form_container = tk.Frame(tab, bg=COLORS['card_bg'],
                                relief='solid', borderwidth=1,
                                padx=30, pady=30)
        form_container.place(relx=0.5, rely=0.5, anchor='center', width=400, height=350)
        
        # Title
        tk.Label(form_container,
                text="⚠️ Owner Access",
                font=FONTS['heading'],
                bg=COLORS['card_bg'],
                fg=COLORS['danger']).pack(pady=(0, 20))
        
        # Description
        tk.Label(form_container,
                text="Restricted access to store management functions.",
                font=FONTS['small'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).pack(pady=(0, 30))
        
        # Username
        tk.Label(form_container,
                text="Owner Username",
                font=FONTS['label'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).pack(anchor='w', pady=(10, 5))
        
        self.owner_username_entry = tk.Entry(form_container,
                                           font=FONTS['entry'],
                                           bg=COLORS['entry_bg'],
                                           fg=COLORS['fg'])
        self.owner_username_entry.insert(0, "FP")
        self.owner_username_entry.pack(fill='x', pady=(0, 20))
        
        # Password
        tk.Label(form_container,
                text="Owner Password",
                font=FONTS['label'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).pack(anchor='w', pady=(5, 5))
        
        self.owner_password_entry = tk.Entry(form_container,
                                           font=FONTS['entry'],
                                           bg=COLORS['entry_bg'],
                                           fg=COLORS['fg'],
                                           show="●")
        self.owner_password_entry.insert(0, "1539")
        self.owner_password_entry.pack(fill='x', pady=(0, 30))
        
        # Login button
        login_btn = tk.Button(form_container,
                            text="Login as Owner",
                            font=FONTS['button'],
                            bg=COLORS['danger'],
                            fg=COLORS['white'],
                            relief='flat',
                            command=self.owner_login,
                            cursor='hand2',
                            padx=20,
                            pady=10)
        login_btn.pack(fill='x')
        
        # Error message
        self.owner_error = tk.Label(form_container,
                                  text="",
                                  font=FONTS['status'],
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['danger'])
        self.owner_error.pack(pady=(20, 0))
        
        # Bind Enter key
        self.owner_password_entry.bind('<Return>', lambda e: self.owner_login())
    
    def load_customers(self):
        """Load customers from JSON file"""
        if os.path.exists(self.customers_file):
            try:
                with open(self.customers_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_customers(self):
        """Save customers to JSON file"""
        with open(self.customers_file, 'w') as f:
            json.dump(self.customers, f, indent=4)
    
    def customer_login(self):
        """Handle customer login"""
        username = self.cust_username.get().strip()
        password = self.cust_password.get().strip()
        
        if not username or not password:
            self.login_error.config(text="Please enter username and password")
            return
        
        # Simple authentication (in production, use hashed passwords)
        for customer in self.customers:
            if (customer['username'] == username and 
                customer['password'] == password and
                customer.get('is_active', True)):
                
                self.root.destroy()
                self.on_login_success(is_owner=False, user=customer)
                return
        
        self.login_error.config(text="Invalid username or password")
    
    def customer_signup(self):
        """Handle customer signup"""
        # Get form data
        data = {
            'username': self.signup_entries['signup_username'].get().strip(),
            'email': self.signup_entries['signup_email'].get().strip(),
            'full_name': self.signup_entries['signup_name'].get().strip(),
            'password': self.signup_entries['signup_password'].get().strip(),
            'confirm_password': self.signup_entries['signup_confirm'].get().strip(),
            'address': self.signup_entries['signup_address'].get().strip(),
            'phone': self.signup_entries['signup_phone'].get().strip(),
        }
        
        # Validation
        errors = []
        
        if not all([data['username'], data['email'], data['password']]):
            errors.append("All required fields must be filled")
        
        if data['password'] != data['confirm_password']:
            errors.append("Passwords do not match")
        
        if len(data['password']) < 6:
            errors.append("Password must be at least 6 characters")
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors.append("Invalid email address")
        
        if not self.terms_var.get():
            errors.append("You must agree to the terms and conditions")
        
        # Check if username exists
        for customer in self.customers:
            if customer['username'] == data['username']:
                errors.append("Username already exists")
                break
        
        if errors:
            self.signup_error.config(text="\n".join(errors))
            return
        
        # Create customer record
        customer = {
            'id': len(self.customers) + 1,
            'username': data['username'],
            'password': data['password'],  # Note: In production, use hashed password
            'email': data['email'],
            'full_name': data['full_name'],
            'address': data['address'],
            'phone': data['phone'],
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_active': True
        }
        
        self.customers.append(customer)
        self.save_customers()
        
        messagebox.showinfo("Success", "Account created successfully!")
        self.root.destroy()
        self.on_login_success(is_owner=False, user=customer)
    
    def owner_login(self):
        """Handle owner login"""
        username = self.owner_username_entry.get().strip()
        password = self.owner_password_entry.get().strip()
        
        if username == self.owner_username and password == self.owner_password:
            self.root.destroy()
            self.on_login_success(is_owner=True, user={'username': 'owner', 'is_owner': True})
        else:
            self.owner_error.config(text="Invalid owner credentials")
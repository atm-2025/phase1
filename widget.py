import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import sys
import keyboard
import threading
import pyautogui
import time
import json
import os
from datetime import datetime
# Add pywin32 import for window focus
try:
    import win32gui
    import win32con
    import win32api
except ImportError:
    win32gui = win32con = win32api = None

# Get the directory where the script is located
WIDGET_DIR = os.path.dirname(os.path.abspath(__file__))

# -- Configuration --
MAX_HISTORY = 100  # Maximum number of history items to keep

CONFIG = {
    'fonts': {
        'title': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 8)
    },
    'dimensions': {
        'width': 650,
        'height': 90,
        'border_radius': 15
    },
    'colors': {
        'bg': '#1a1a2e',
        'fg': '#ffffff',
        'accent': '#0f3460',
        'secondary': '#16213e',
        'success': '#00d4aa',
        'warning': '#ff6b6b',
        'border': '#e94560'
    }
}

# -- File Paths --
HISTORY_FILE = os.path.join(WIDGET_DIR, "search_history.json")
SETTINGS_FILE = os.path.join(WIDGET_DIR, "widget_settings.json")

# -- History Management --
def load_history():
    """Load search history from file"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def save_history(history):
    """Save search history to file"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except:
        pass

# Load existing history
history = load_history()

# -- Engines with URL patterns and icons --
engine_data = [
    ("1. Google 🔍", "https://www.google.com/search?q={}"),
    ("2. YouTube ▶️", "https://www.youtube.com/results?search_query={}"),
    ("3. ChatGPT 🤖", "https://chat.openai.com/"),
    ("4. Gemini 🌟", "https://gemini.google.com/"),
    ("5. Bing 🌀", "https://www.bing.com/search?q={}"),
    ("6. Facebook 📘", "https://www.facebook.com/search/top/?q={}"),
    ("7. LinkedIn 💼", "https://www.linkedin.com/search/results/all/?keywords={}"),
    ("8. Instagram 📸", "https://www.instagram.com/explore/tags/{}/"),
    ("9. Twitter 🐦", "https://twitter.com/search?q={}"),
    ("10. Reddit 👽", "https://www.reddit.com/search/?q={}"),
    ("11. Pinterest 📌", "https://www.pinterest.com/search/pins/?q={}"),
    ("12. Quora ❓", "https://www.quora.com/search?q={}"),
    ("13. Amazon 🛒", "https://www.amazon.com/s?k={}"),
    ("14. StackOverflow 💡", "https://stackoverflow.com/search?q={}"),
    ("15. Wikipedia 📚", "https://en.wikipedia.org/wiki/{}"),
    ("16. DuckDuckGo 🔐", "https://duckduckgo.com/?q={}"),
    ("17. Yahoo 🗞️", "https://search.yahoo.com/search?p={}"),
    ("18. Snapchat 👻", "https://www.snapchat.com/add/{}"),
    ("19. Spotify 🎵", "https://open.spotify.com/search/{}"),
    ("20. Netflix 🍿", "https://www.netflix.com/search?q={}")
]

engines = [e[0] for e in engine_data]

class PremiumSearchWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.settings = self.load_settings()
        self.last_toggle_time = 0  # For debounce
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        self.start_hotkey_listener()
        
    def load_settings(self):
        """Load user settings"""
        default_settings = {
            'hotkey': 'right ctrl+left',
            'default_engine': 0,
            'auto_focus': True,
            'start_minimized': False,
            'max_history': 100,
            'transparency': 0.95
        }
        
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    return {**default_settings, **json.load(f)}
        except:
            pass
        return default_settings
        
    def save_settings(self):
        """Save user settings"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
        
    def setup_window(self):
        """Configure main window with premium styling"""
        self.root.title("Premium Search Widget")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{CONFIG['dimensions']['width']}x{CONFIG['dimensions']['height']}+100+100")
        self.root.configure(bg=CONFIG['colors']['bg'])
        
        # Apply transparency setting
        self.root.attributes('-alpha', self.settings['transparency'])
        
    def create_widgets(self):
        """Create and organize all UI elements"""
        # Main container with gradient effect
        self.main_frame = tk.Frame(
            self.root,
            bg=CONFIG['colors']['bg'],
            relief="flat",
            bd=0
        )
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create inner frame with border
        self.inner_frame = tk.Frame(
            self.main_frame,
            bg=CONFIG['colors']['secondary'],
            relief="flat",
            bd=1,
            highlightbackground=CONFIG['colors']['border'],
            highlightthickness=1
        )
        self.inner_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Search input section
        self.create_search_section()
        
        # Engine selector section
        self.create_engine_section()
        
        # Action buttons section
        self.create_action_section()
        
    def create_search_section(self):
        """Create the search input area"""
        search_frame = tk.Frame(self.inner_frame, bg=CONFIG['colors']['secondary'])
        search_frame.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=6)
        
        # Search entry with premium styling
        self.entry = tk.Entry(
            search_frame,
            font=CONFIG['fonts']['body'],
            bg=CONFIG['colors']['bg'],
            fg=CONFIG['colors']['fg'],
            insertbackground=CONFIG['colors']['success'],
            relief="flat",
            bd=0,
            highlightbackground=CONFIG['colors']['accent'],
            highlightthickness=1
        )
        self.entry.pack(fill="x", pady=(0, 4))
        
        # Search button
        self.search_btn = tk.Button(
            search_frame,
            text="🔍 Search",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['success'],
            fg=CONFIG['colors']['bg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=CONFIG['colors']['accent'],
            activeforeground=CONFIG['colors']['fg']
        )
        self.search_btn.pack(fill="x")
        
    def create_engine_section(self):
        """Create the engine selector area"""
        engine_frame = tk.Frame(self.inner_frame, bg=CONFIG['colors']['secondary'])
        engine_frame.pack(side="left", fill="y", padx=4, pady=6)
        
        # Engine variable
        self.engine_var = tk.StringVar(value=engines[self.settings['default_engine']])
        
        # Engine dropdown with custom styling
        self.dropdown = ttk.Combobox(
            engine_frame,
            textvariable=self.engine_var,
            values=engines,
            font=CONFIG['fonts']['small'],
            state="readonly",
            width=15
        )
        self.dropdown.pack(fill="x", pady=(0, 4))
        
        # Quick navigation buttons
        nav_frame = tk.Frame(engine_frame, bg=CONFIG['colors']['secondary'])
        nav_frame.pack(fill="x")
        
        tk.Button(
            nav_frame,
            text="◀",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['accent'],
            fg=CONFIG['colors']['fg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.prev_engine
        ).pack(side="left", fill="x", expand=True, padx=(0, 1))
        
        tk.Button(
            nav_frame,
            text="▶",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['accent'],
            fg=CONFIG['colors']['fg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.next_engine
        ).pack(side="left", fill="x", expand=True, padx=(1, 0))
        
    def create_action_section(self):
        """Create the action buttons area"""
        action_frame = tk.Frame(self.inner_frame, bg=CONFIG['colors']['secondary'])
        action_frame.pack(side="right", fill="y", padx=(4, 8), pady=6)
        
        # Close button
        self.close_btn = tk.Button(
            action_frame,
            text="❌",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['warning'],
            fg=CONFIG['colors']['fg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.quit_app,
            width=3
        )
        self.close_btn.pack(fill="x", pady=(0, 2))
        
        # History button
        self.hist_btn = tk.Button(
            action_frame,
            text="📜",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['accent'],
            fg=CONFIG['colors']['fg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.show_history
        )
        self.hist_btn.pack(fill="x", pady=(0, 2))
        
        # Settings button
        self.settings_btn = tk.Button(
            action_frame,
            text="⚙️",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['accent'],
            fg=CONFIG['colors']['fg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.show_settings
        )
        self.settings_btn.pack(fill="x", pady=(0, 2))
        
        # Minimize button
        self.minimize_btn = tk.Button(
            action_frame,
            text="➖",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['accent'],
            fg=CONFIG['colors']['fg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.toggle_visibility
        )
        self.minimize_btn.pack(fill="x")
        
    def setup_bindings(self):
        """Setup all keyboard and mouse bindings"""
        # Window dragging
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        
        # Search functionality
        self.entry.bind("<Return>", self.search)
        self.entry.bind("<Down>", self.next_engine)
        self.entry.bind("<Up>", self.prev_engine)
        
        # Button commands
        self.search_btn.config(command=self.search)
        
        # Auto-focus
        if self.settings['auto_focus']:
            self.root.after(100, lambda: self.entry.focus_set())
        
    def start_move(self, event):
        """Start window dragging"""
        self.root.x = event.x
        self.root.y = event.y
        
    def do_move(self, event):
        """Handle window dragging"""
        x = self.root.winfo_x() + (event.x - self.root.x)
        y = self.root.winfo_y() + (event.y - self.root.y)
        self.root.geometry(f"+{x}+{y}")
        
    def search(self, event=None):
        """Perform search with current engine"""
        query = self.entry.get().strip()
        if not query:
            return
            
        chosen_engine = self.engine_var.get()
        
        # Handle quick selection with backtick
        if "`" in query:
            try:
                base, idx_str = query.rsplit("`", 1)
                idx = int(idx_str)
                if 1 <= idx <= len(engine_data):
                    chosen_engine = engines[idx - 1]
                    query = base.strip()
            except:
                pass
                
        # Get engine data
        engine_name = chosen_engine.split('. ')[1] if '. ' in chosen_engine else chosen_engine
        idx = engines.index(chosen_engine)
        name, url = engine_data[idx]
        
        # Add to history
        timestamp = datetime.now().strftime("%H:%M")
        history.append((timestamp, name, query))
        
        # Keep only last MAX_HISTORY items
        if len(history) > MAX_HISTORY:
            history.pop(0)
            
        # Save history
        save_history(history)
        
        # Perform search
        if "chat.openai" in url or "gemini.google" in url:
            webbrowser.open(url)
            time.sleep(6)
            pyautogui.click(x=500, y=500)
            pyautogui.write(query)
            pyautogui.press("enter")
        else:
            webbrowser.open(url.format(query))
            
        self.entry.delete(0, tk.END)
        
    def next_engine(self, event=None):
        """Switch to next search engine"""
        current = engines.index(self.engine_var.get())
        self.engine_var.set(engines[(current + 1) % len(engines)])
        
    def prev_engine(self, event=None):
        """Switch to previous search engine"""
        current = engines.index(self.engine_var.get())
        self.engine_var.set(engines[(current - 1) % len(engines)])
        
    def show_history(self):
        """Display search history in a new window with clickable search"""
        if not history:
            messagebox.showinfo("History", "No search history found.")
            return
            
        hist_win = tk.Toplevel(self.root)
        hist_win.title("Search History")
        hist_win.geometry("600x500")
        hist_win.configure(bg=CONFIG['colors']['bg'])
        
        # History header
        header_frame = tk.Frame(hist_win, bg=CONFIG['colors']['bg'])
        header_frame.pack(fill="x", padx=10, pady=10)
        
        header = tk.Label(
            header_frame,
            text="📜 Search History",
            font=CONFIG['fonts']['title'],
            bg=CONFIG['colors']['bg'],
            fg=CONFIG['colors']['success']
        )
        header.pack(side="left")
        
        # Clear history button
        clear_btn = tk.Button(
            header_frame,
            text="🗑️ Clear",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['warning'],
            fg=CONFIG['colors']['fg'],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda: self.clear_history(hist_win)
        )
        clear_btn.pack(side="right")
        
        # History listbox with scrollbar
        hist_frame = tk.Frame(hist_win, bg=CONFIG['colors']['bg'])
        hist_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create listbox and scrollbar
        hist_listbox = tk.Listbox(
            hist_frame,
            font=CONFIG['fonts']['body'],
            bg=CONFIG['colors']['secondary'],
            fg=CONFIG['colors']['fg'],
            selectbackground=CONFIG['colors']['accent'],
            relief="flat",
            bd=0,
            height=20
        )
        hist_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(hist_frame, orient="vertical", command=hist_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        hist_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate history
        for timestamp, engine, query in history[-MAX_HISTORY:]:
            hist_listbox.insert(0, f"[{timestamp}] {engine}: {query}")
            
        # Double-click to search
        hist_listbox.bind("<Double-Button-1>", lambda e: self.search_from_history(hist_listbox, hist_win))
        
        # Instructions
        instructions = tk.Label(
            hist_win,
            text="💡 Double-click any item to search again",
            font=CONFIG['fonts']['small'],
            bg=CONFIG['colors']['bg'],
            fg=CONFIG['colors']['success']
        )
        instructions.pack(pady=(0, 10))
        
    def search_from_history(self, listbox, window):
        """Search from history item"""
        try:
            selection = listbox.get(listbox.curselection())
            # Extract query from history item
            query = selection.split(": ", 1)[1]
            self.entry.delete(0, tk.END)
            self.entry.insert(0, query)
            window.destroy()
            self.search()
        except:
            pass
            
    def clear_history(self, window):
        """Clear all search history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all search history?"):
            global history
            history.clear()
            save_history(history)
            window.destroy()
            messagebox.showinfo("History", "Search history cleared.")
            
    def show_settings(self):
        """Show comprehensive settings window"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("500x600")
        settings_win.configure(bg=CONFIG['colors']['bg'])
        
        # Settings header
        header = tk.Label(
            settings_win,
            text="⚙️ Settings",
            font=CONFIG['fonts']['title'],
            bg=CONFIG['colors']['bg'],
            fg=CONFIG['colors']['success']
        )
        header.pack(pady=10)
        
        # Create scrollable settings frame
        canvas = tk.Canvas(settings_win, bg=CONFIG['colors']['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(settings_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=CONFIG['colors']['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Hotkey settings
        hotkey_frame = tk.LabelFrame(scrollable_frame, text="Hotkey Settings", 
                                   font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                                   fg=CONFIG['colors']['success'])
        hotkey_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(hotkey_frame, text="Toggle Widget:", font=CONFIG['fonts']['body'], 
                bg=CONFIG['colors']['bg'], fg=CONFIG['colors']['fg']).pack(anchor="w", padx=5, pady=2)
        
        hotkey_var = tk.StringVar(value=self.settings['hotkey'])
        hotkey_entry = tk.Entry(hotkey_frame, textvariable=hotkey_var, 
                              font=CONFIG['fonts']['body'], bg=CONFIG['colors']['secondary'], 
                              fg=CONFIG['colors']['fg'])
        hotkey_entry.pack(fill="x", padx=5, pady=2)
        
        # Default engine settings
        engine_frame = tk.LabelFrame(scrollable_frame, text="Default Engine", 
                                   font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                                   fg=CONFIG['colors']['success'])
        engine_frame.pack(fill="x", padx=10, pady=5)
        
        engine_var = tk.StringVar(value=engines[self.settings['default_engine']])
        engine_dropdown = ttk.Combobox(engine_frame, textvariable=engine_var, 
                                     values=engines, font=CONFIG['fonts']['body'], state="readonly")
        engine_dropdown.pack(fill="x", padx=5, pady=2)
        
        # Behavior settings
        behavior_frame = tk.LabelFrame(scrollable_frame, text="Behavior", 
                                     font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                                     fg=CONFIG['colors']['success'])
        behavior_frame.pack(fill="x", padx=10, pady=5)
        
        auto_focus_var = tk.BooleanVar(value=self.settings['auto_focus'])
        tk.Checkbutton(behavior_frame, text="Auto-focus on startup", variable=auto_focus_var,
                      font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                      fg=CONFIG['colors']['fg'], selectcolor=CONFIG['colors']['secondary']).pack(anchor="w", padx=5, pady=2)
        
        start_minimized_var = tk.BooleanVar(value=self.settings['start_minimized'])
        tk.Checkbutton(behavior_frame, text="Start minimized", variable=start_minimized_var,
                      font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                      fg=CONFIG['colors']['fg'], selectcolor=CONFIG['colors']['secondary']).pack(anchor="w", padx=5, pady=2)
        
        # Transparency settings
        transparency_frame = tk.LabelFrame(scrollable_frame, text="Transparency", 
                                         font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                                         fg=CONFIG['colors']['success'])
        transparency_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(transparency_frame, text="Widget Transparency:", font=CONFIG['fonts']['body'], 
                bg=CONFIG['colors']['bg'], fg=CONFIG['colors']['fg']).pack(anchor="w", padx=5, pady=2)
        
        transparency_var = tk.DoubleVar(value=self.settings['transparency'])
        transparency_scale = tk.Scale(transparency_frame, from_=0.1, to=1.0, resolution=0.05,
                                    orient="horizontal", variable=transparency_var,
                                    font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                                    fg=CONFIG['colors']['fg'], highlightthickness=0,
                                    troughcolor=CONFIG['colors']['secondary'],
                                    activebackground=CONFIG['colors']['accent'])
        transparency_scale.pack(fill="x", padx=5, pady=2)
        
        # Live preview of transparency
        def update_transparency_preview(*args):
            self.root.attributes('-alpha', transparency_var.get())
            
        transparency_var.trace('w', update_transparency_preview)
        
        # History settings
        history_frame = tk.LabelFrame(scrollable_frame, text="History Settings", 
                                    font=CONFIG['fonts']['body'], bg=CONFIG['colors']['bg'], 
                                    fg=CONFIG['colors']['success'])
        history_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(history_frame, text="Max History Items:", font=CONFIG['fonts']['body'], 
                bg=CONFIG['colors']['bg'], fg=CONFIG['colors']['fg']).pack(anchor="w", padx=5, pady=2)
        
        max_history_var = tk.StringVar(value=str(self.settings['max_history']))
        max_history_entry = tk.Entry(history_frame, textvariable=max_history_var, 
                                   font=CONFIG['fonts']['body'], bg=CONFIG['colors']['secondary'], 
                                   fg=CONFIG['colors']['fg'])
        max_history_entry.pack(fill="x", padx=5, pady=2)
        
        # Save/Cancel buttons
        button_frame = tk.Frame(scrollable_frame, bg=CONFIG['colors']['bg'])
        button_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(button_frame, text="Save", font=CONFIG['fonts']['body'],
                 bg=CONFIG['colors']['success'], fg=CONFIG['colors']['bg'],
                 relief="flat", bd=0, cursor="hand2",
                 command=lambda: self.save_settings_from_ui(
                     hotkey_var.get(), engine_var.get(), auto_focus_var.get(),
                     start_minimized_var.get(), max_history_var.get(), 
                     transparency_var.get(), settings_win
                 )).pack(side="left", padx=(0, 5))
        
        tk.Button(button_frame, text="Cancel", font=CONFIG['fonts']['body'],
                 bg=CONFIG['colors']['warning'], fg=CONFIG['colors']['fg'],
                 relief="flat", bd=0, cursor="hand2",
                 command=lambda: self.cancel_settings(settings_win)).pack(side="left")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
    def save_settings_from_ui(self, hotkey, engine, auto_focus, start_minimized, max_history, transparency, window):
        """Save settings from UI"""
        try:
            self.settings['hotkey'] = hotkey
            self.settings['default_engine'] = engines.index(engine)
            self.settings['auto_focus'] = auto_focus
            self.settings['start_minimized'] = start_minimized
            self.settings['max_history'] = int(max_history)
            self.settings['transparency'] = transparency
            
            # Apply settings immediately
            self.root.attributes('-alpha', transparency)
            
            self.save_settings()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def cancel_settings(self, window):
        """Cancel settings and restore original values"""
        self.root.attributes('-alpha', self.settings['transparency'])
        window.destroy()
        
    def bring_to_foreground(self):
        """Force the widget window to the foreground using pywin32 (Windows only)"""
        if win32gui and win32con and win32api:
            try:
                hwnd = self.root.winfo_id()
                win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
                # ALT key workaround
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32gui.SetForegroundWindow(hwnd)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception as e:
                pass
        
    def toggle_visibility(self):
        """Toggle widget visibility with debounce"""
        now = time.time()
        if now - getattr(self, 'last_toggle_time', 0) < 0.3:  # 300ms debounce
            return
        self.last_toggle_time = now
        if self.root.state() == "normal":
            self.root.withdraw()
        else:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)  # Force window to be on top
            self.root.focus_force()  # Force window focus
            self.entry.focus_set()  # Always focus the entry
            self.root.after(10, lambda: self.root.attributes('-topmost', False))  # Reset topmost after ensuring focus
            self.bring_to_foreground()  # Use pywin32 to force foreground
            
    def start_hotkey_listener(self):
        """Start hotkey listener in background thread"""
        def listen_toggle():
            keyboard.add_hotkey(self.settings['hotkey'], self.toggle_visibility)
            keyboard.wait()
            
        threading.Thread(target=listen_toggle, daemon=True).start()
        
    def quit_app(self):
        """Use the same toggle behavior as the hotkey"""
        self.toggle_visibility()
        
    def run(self):
        """Start the application"""
        if self.settings['start_minimized']:
            self.root.withdraw()
        self.root.mainloop()

# -- Main execution --
if __name__ == "__main__":
    app = PremiumSearchWidget()
    app.run()

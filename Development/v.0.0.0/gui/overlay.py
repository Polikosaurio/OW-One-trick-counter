"""
In-Game Overlay
"""

import tkinter as tk
import os
from PIL import Image, ImageTk


class Overlay:
    def __init__(self, config, selection):
        self.config = config
        self.selection = selection
        self.window = None
        self.tooltip = None
        self.visible = False
        self._create_window()
    
    def _create_window(self):
        self.window = tk.Tk()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", self.config.get("overlay_opacity", 0.85))
        
        pos = self.config.get("overlay_position", {"x": 100, "y": 100})
        self.window.geometry(f"+{pos['x']}+{pos['y']}")
        self.window.configure(bg="black")
        
        self._setup_ui()
        self.window.withdraw()
    
    def _setup_ui(self):
        hero = self.selection.get("enemy", "tracer")
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_path = os.path.join(project_root, "..", "Assets", "HeroUI", f"{hero}.png")
        
        label = None
        
        if os.path.exists(assets_path):
            try:
                img = Image.open(assets_path)
                img = img.resize((48, 48), Image.LANCZOS)
                self.icon_image = ImageTk.PhotoImage(img)
                label = tk.Label(self.window, image=self.icon_image, bg="black", cursor="hand2")
            except Exception as e:
                print(f"[Overlay] Error loading icon: {e}")
        
        if not label:
            label = tk.Label(
                self.window,
                text=hero[:4].upper(),
                bg="black", fg="white",
                font=("Arial", 14, "bold"),
                cursor="hand2"
            )
        
        label.pack(padx=2, pady=2)
        label.bind("<Button-1>", lambda e: self._toggle_tooltip())
        label.bind("<Enter>", lambda e: self._show_tooltip())
        label.bind("<Leave>", lambda e: self._hide_tooltip())
    
    def _get_advice(self):
        from core.counters import CounterDB
        enemy = self.selection.get("enemy", "")
        your = self.selection.get("your", "")
        
        if not enemy:
            return "Select enemy"
        
        if your:
            c = CounterDB.get_counter(enemy, your)
            if c:
                return f"Counter: {c['hero']}\n\n{c['reason'][:150]}"
        
        counters = CounterDB.get_all_counters(enemy, 3)
        if counters:
            text = f"Best vs {enemy}:\n"
            for c in counters:
                text += f"• {c['hero']}\n"
            return text
        return "No data"
    
    def _toggle_tooltip(self):
        if self.tooltip and self.tooltip.winfo_viewable():
            self.tooltip.withdraw()
        else:
            self._show_tooltip()
    
    def _show_tooltip(self):
        if not self.tooltip:
            self.tooltip = tk.Toplevel(self.window)
            self.tooltip.overrideredirect(True)
            self.tooltip.attributes("-topmost", True)
            self.tooltip.configure(bg="#1a1a2e")
            
            x = self.window.winfo_x() + 60
            y = self.window.winfo_y()
            self.tooltip.geometry(f"+{x}+{y}")
            
            label = tk.Label(
                self.tooltip,
                text=self._get_advice(),
                bg="#1a1a2e", fg="white",
                font=("Arial", 10),
                justify="left", wraplength=200,
                padx=10, pady=10
            )
            label.pack()
        
        self.tooltip.deiconify()
    
    def _hide_tooltip(self):
        if self.tooltip:
            self.tooltip.withdraw()
    
    def show(self):
        if self.window:
            self.window.deiconify()
            self.visible = True
    
    def hide(self):
        if self.window:
            self.window.withdraw()
            if self.tooltip:
                self.tooltip.withdraw()
            self.visible = False
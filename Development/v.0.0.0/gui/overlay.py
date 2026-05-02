"""
In-Game Overlay Window
Small clickable icon with strategy tooltip
"""

import tkinter as tk
import win32con
import win32gui
import win32api
import os


class Overlay:
    def __init__(self, config, selection):
        self.config = config
        self.selection = selection
        self.window = None
        self.visible = False
        
        self._create_window()
    
    def _create_window(self):
        """Create overlay window"""
        self.window = tk.Tk()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", self.config.get("overlay_opacity", 0.85))
        
        pos = self.config.get("overlay_position", {"x": 100, "y": 100})
        self.window.geometry(f"+{pos['x']}+{pos['y']}")
        
        self.window.configure(bg="black")
        
        self._setup_ui()
        
        self.window.withdraw()
        
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
    
    def _setup_ui(self):
        """Setup overlay UI"""
        try:
            from PIL import Image, ImageTk
            
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(base, "Assets", "HeroUI", f"{self.selection['enemy']}.png")
            
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize((64, 64), Image.LANCZOS)
                self.icon_image = ImageTk.PhotoImage(img)
                
                label = tk.Label(
                    self.window,
                    image=self.icon_image,
                    bg="black",
                    cursor="hand2"
                )
            else:
                label = tk.Label(
                    self.window,
                    text=self.selection['enemy'][:3].upper(),
                    bg="black",
                    fg="white",
                    font=("Arial", 24, "bold"),
                    cursor="hand2"
                )
        except Exception as e:
            label = tk.Label(
                self.window,
                text=self.selection['enemy'][:3].upper(),
                bg="black",
                fg="white",
                font=("Arial", 24, "bold")
            )
        
        label.pack(padx=2, pady=2)
        
        label.bind("<Button-1>", self._on_click)
        label.bind("<Enter>", self._show_tooltip)
        label.bind("<Leave>", self._hide_tooltip)
        
        self.label = label
        
        self.tooltip = tk.Toplevel(self.window)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        self.tooltip.attributes("-alpha", 0.95)
        self.tooltip.configure(bg="#1a1a2e")
        self.tooltip.withdraw()
        
        self._setup_tooltip_ui()
    
    def _setup_tooltip_ui(self):
        """Setup tooltip content"""
        info_text = self._get_counter_text()
        
        label = tk.Label(
            self.tooltip,
            text=info_text,
            bg="#1a1a2e",
            fg="white",
            font=("Arial", 10),
            justify="left",
            wraplength=250
        )
        label.pack(padx=10, pady=5)
    
    def _get_counter_text(self):
        """Get counter advice text"""
        from core.counters import CounterDB
        
        enemy = self.selection.get("enemy", "")
        your = self.selection.get("your", "")
        
        if not enemy:
            return "Select enemy hero"
        
        if your:
            counter = CounterDB.get_counter(enemy, your)
            if counter:
                return f"Playing {your}\n\nCounter: {counter['hero']}\n\n{counter['reason'][:150]}"
        
        counters = CounterDB.get_all_counters(enemy, 3)
        if counters:
            text = f"Best counters for {enemy}:\n\n"
            for c in counters:
                text += f"• {c['hero']} ({c['role']})\n"
            return text
        
        return f"No data for {enemy}"
    
    def _on_click(self, event):
        """Handle click - toggle info"""
        if self.tooltip.winfo_viewable():
            self.tooltip.withdraw()
        else:
            self._show_tooltip(None)
    
    def _show_tooltip(self, event):
        """Show tooltip"""
        if self.window.winfo_x() < 100:
            x = self.window.winfo_x() + 80
        else:
            x = self.window.winfo_x() - 280
        
        y = self.window.winfo_y()
        self.tooltip.geometry(f"+{x}+{y}")
        self.tooltip.deiconify()
    
    def _hide_tooltip(self, event):
        """Hide tooltip"""
        self.tooltip.withdraw()
    
    def show(self):
        """Show overlay"""
        if self.window:
            self.window.deiconify()
            self.visible = True
    
    def hide(self):
        """Hide overlay"""
        if self.window:
            self.window.withdraw()
            self.tooltip.withdraw()
            self.visible = False
    
    def toggle(self):
        """Toggle visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def is_visible(self):
        """Check if visible"""
        return self.visible


if __name__ == "__main__":
    from core.config import Config
    cfg = Config.load()
    selection = {"enemy": "widowmaker", "your": "winston"}
    overlay = Overlay(cfg, selection)
    overlay.show()
    print("Overlay running. Press close to exit.")
    overlay.window.mainloop()
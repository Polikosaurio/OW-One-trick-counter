"""
In-Game Overlay
Uses Toplevel so it shares the root Tk instance with MainWindow.
"""

import tkinter as tk
import os
from PIL import Image, ImageTk


class Overlay:
    def __init__(self, root, config, selection):
        """
        root      : the ctk.CTk() root window from MainWindow
        config    : Config singleton
        selection : dict with "enemy" and "your" keys
        """
        self.root = root
        self.config = config
        self.selection = selection
        self.window = None
        self.tooltip = None
        self.visible = False
        self._icon_image = None  # keep reference to avoid GC
        self._create_window()

    def _create_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", self.config.get("overlay_opacity", 0.85))

        pos = self.config.get("overlay_position", {"x": 100, "y": 100})
        self.window.geometry(f"+{pos['x']}+{pos['y']}")
        self.window.configure(bg="black")

        self._setup_ui()
        self.window.withdraw()

    def _assets_path(self, hero):
        gui_dir = os.path.dirname(os.path.abspath(__file__))
        dev_dir = os.path.dirname(gui_dir)          # v.0.0.0/
        project_root = os.path.dirname(dev_dir)     # project root
        return os.path.join(project_root, "Assets", "HeroUI", f"{hero}.png")

    def _setup_ui(self):
        # Remove old widgets
        for widget in self.window.winfo_children():
            widget.destroy()
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None

        hero = self.selection.get("enemy", "tracer")
        assets_path = self._assets_path(hero)

        label = None
        if os.path.exists(assets_path):
            try:
                img = Image.open(assets_path)
                img = img.resize((48, 48), Image.LANCZOS)
                self._icon_image = ImageTk.PhotoImage(img)
                label = tk.Label(
                    self.window,
                    image=self._icon_image,
                    bg="black",
                    cursor="hand2"
                )
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
            return "Select an enemy hero"

        db = CounterDB()

        if your:
            c = db.get_counter(enemy, your)
            if c:
                return f"Playing {your.capitalize()} vs {enemy.capitalize()}:\n\n{c['reason']}"

        counters = db.get_all_counters(enemy, 3)
        if counters:
            text = f"Best vs {enemy.capitalize()}:\n"
            for c in counters:
                text += f"  {c['hero'].capitalize()} ({c['role']})\n"
            return text.strip()

        return "No counter data available"

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

            self._advice_label = tk.Label(
                self.tooltip,
                text=self._get_advice(),
                bg="#1a1a2e", fg="white",
                font=("Arial", 10),
                justify="left", wraplength=220,
                padx=10, pady=10
            )
            self._advice_label.pack()
        else:
            # Refresh advice text each time tooltip is shown
            self._advice_label.config(text=self._get_advice())

        self.tooltip.deiconify()

    def _hide_tooltip(self):
        if self.tooltip:
            self.tooltip.withdraw()

    def update_selection(self, selection):
        """Call this whenever the hero selection changes before showing."""
        self.selection = selection
        if self.window:
            self._setup_ui()

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

    def destroy(self):
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
        self.window = None
        self.tooltip = None

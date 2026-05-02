"""
Main Window - Configuration GUI
"""

import customtkinter as ctk
import os
from gui.hero_selector import HeroSelector
from gui.overlay import Overlay as GameOverlay


class MainWindow:
    def __init__(self, config, game_detector=None):
        self.config = config
        self.game_detector = game_detector
        self.overlay = None
        self.overlay_visible = False
        self.mouse_lock_active = False
        
        self.root = ctk.CTk()
        self.root.title("OW One Trick Counter")
        self.root.geometry("650x600")
        self.root.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
        self._setup_tray()
    
    def _setup_ui(self):
        title = ctk.CTkLabel(
            self.root,
            text="OW One Trick Counter",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=15)
        
        subtitle = ctk.CTkLabel(
            self.root,
            text="Select enemy hero & your hero for counter advice",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        )
        subtitle.pack(pady=(0, 10))
        
        self.hero_selector = HeroSelector(self.root)
        self.hero_selector.pack(pady=5, padx=20, fill="both", expand=True)
        
        controls_frame = ctk.CTkFrame(self.root)
        controls_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(
            controls_frame,
            text="Toggle Overlay (O)",
            command=self.toggle_overlay,
            width=120
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            controls_frame,
            text="Mouse Lock (M)",
            command=self.toggle_mouse_lock,
            width=120
        ).pack(side="left", padx=5, pady=10)
        
        settings_frame = ctk.CTkFrame(self.root)
        settings_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(settings_frame, text="Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.start_with_game_var = ctk.BooleanVar(value=self.config.get("start_with_game", True))
        ctk.CTkCheckBox(
            settings_frame,
            text="Auto-start with OW",
            variable=self.start_with_game_var,
            command=self._toggle_start_with_game
        ).pack(anchor="w", padx=20)
        
        opacity_frame = ctk.CTkFrame(settings_frame)
        opacity_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(opacity_frame, text="Overlay opacity:").pack(side="left", padx=5)
        self.opacity_slider = ctk.CTkSlider(
            opacity_frame,
            from_=30,
            to=100,
            command=self._on_opacity_change
        )
        self.opacity_slider.set(int(self.config.get("overlay_opacity", 0.85) * 100))
        self.opacity_slider.pack(side="left", padx=5, fill="x", expand=True)
        
        pos_frame = ctk.CTkFrame(settings_frame)
        pos_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(pos_frame, text="Overlay position:").pack(side="left", padx=5)
        
        self.pos_x_entry = ctk.CTkEntry(pos_frame, width=60, placeholder_text="X")
        self.pos_x_entry.insert(0, str(self.config.get("overlay_position", {}).get("x", 100)))
        self.pos_x_entry.pack(side="left", padx=2)
        
        self.pos_y_entry = ctk.CTkEntry(pos_frame, width=60, placeholder_text="Y")
        self.pos_y_entry.insert(0, str(self.config.get("overlay_position", {}).get("y", 100)))
        self.pos_y_entry.pack(side="left", padx=2)
        
        ctk.CTkButton(
            pos_frame,
            text="Save",
            command=self._save_position,
            width=50
        ).pack(side="left", padx=5)
        
        hotkey_info = ctk.CTkLabel(
            self.root,
            text=f"Overlay: {self.config.get('hotkey_toggle')} | Mouse Lock: {self.config.get('hotkey_mouse_lock')}",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        hotkey_info.pack(pady=5)
    
    def _setup_tray(self):
        try:
            from pystray import MenuItem as TrayMenuItem
            import pystray
            from PIL import Image
            
            icon_path = self._get_icon_path()
            if icon_path and os.path.exists(icon_path):
                icon = Image.open(icon_path)
                icon = icon.resize((64, 64), Image.LANCZOS)
            else:
                icon = Image.new('RGB', (64, 64), color='#2196F3')
            
            def toggle_overlay_action():
                self.toggle_overlay()
            
            def toggle_lock_action():
                self.toggle_mouse_lock()
            
            menu = (
                TrayMenuItem("Overlay: OFF", toggle_overlay_action),
                TrayMenuItem("Mouse Lock: OFF", toggle_lock_action),
                TrayMenuItem("---", lambda: None),
                TrayMenuItem(f"Hotkey: {self.config.get('hotkey_toggle')}", lambda: None),
                TrayMenuItem(f"Lock: {self.config.get('hotkey_mouse_lock')}", lambda: None),
                TrayMenuItem("---", lambda: None),
                TrayMenuItem("Exit", self.quit)
            )
            
            self.tray = pystray.Icon("OWCounter", icon, "OW Counter", menu)
        except Exception as e:
            print(f"[Tray] Warning: {e}")
            self.tray = None
    
    def _get_icon_path(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "Assets", "HeroUI", "tracer.png")
    
    def _toggle_start_with_game(self):
        self.config.set("start_with_game", self.start_with_game_var.get())
    
    def _on_opacity_change(self, value):
        opacity = value / 100.0
        self.config.set("overlay_opacity", opacity)
        if self.overlay and self.overlay.window:
            self.overlay.window.attributes("-alpha", opacity)
    
    def _save_position(self):
        try:
            x = int(self.pos_x_entry.get())
            y = int(self.pos_y_entry.get())
            self.config.set("overlay_position", {"x": x, "y": y})
            if self.overlay and self.overlay.window:
                self.overlay.window.geometry(f"+{x}+{y}")
        except:
            pass
    
    def toggle_overlay(self):
        if self.overlay_visible:
            if self.overlay:
                self.overlay.hide()
            self.overlay_visible = False
            print("[OW Counter] Overlay hidden")
        else:
            if not self.overlay:
                sel = self.hero_selector.get_selection()
                self.overlay = GameOverlay(self.config, sel)
            self.overlay.show()
            self.overlay_visible = True
            print("[OW Counter] Overlay shown")
    
    def toggle_mouse_lock(self):
        from core.mouse_lock import MouseLock, get_primary_monitor_rect
        
        if self.mouse_lock_active:
            MouseLock.release()
            self.mouse_lock_active = False
            print("[OW Counter] Mouse lock released")
        else:
            rect = get_primary_monitor_rect()
            MouseLock.clip(rect)
            self.mouse_lock_active = True
            print("[OW Counter] Mouse locked")
    
    def run(self):
        print("[OW Counter] Starting...")
        
        if self.tray:
            import threading
            threading.Thread(target=self.tray.run, daemon=True).start()
        
        self.root.mainloop()
    
    def quit(self):
        from core.mouse_lock import MouseLock
        from gui.overlay import Overlay as OL
        
        if self.mouse_lock_active:
            MouseLock.release()
        
        if self.overlay:
            self.overlay.hide()
        
        if self.game_detector:
            self.game_detector.stop()
        
        if self.tray:
            try:
                self.tray.stop()
            except:
                pass
        
        self.root.quit()


if __name__ == "__main__":
    from core.config import Config
    cfg = Config.get_instance()
    app = MainWindow(cfg)
    app.run()
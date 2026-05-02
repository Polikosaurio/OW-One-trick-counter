"""
Main Window - Complete GUI
"""

import customtkinter as ctk
import os
import threading
from gui.hero_selector import HeroSelector
from gui.overlay import Overlay as GameOverlay


class MainWindow:
    def __init__(self, config, game_detector=None):
        self.config = config
        self.game_detector = game_detector
        self.overlay = None
        self.overlay_visible = False
        self.mouse_lock_active = False
        self.tray = None
        
        self.root = ctk.CTk()
        self.root.title("OW One Trick Counter")
        self.root.geometry("650x620")
        self.root.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
        self._setup_tray()
    
    def _setup_ui(self):
        ctk.CTkLabel(
            self.root,
            text="OW One Trick Counter",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=15)
        
        ctk.CTkLabel(
            self.root,
            text="Select enemy hero & your hero",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(0, 10))
        
        self.hero_selector = HeroSelector(self.root)
        self.hero_selector.pack(pady=5, padx=20, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(self.root)
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="Toggle Overlay",
            command=self.toggle_overlay,
            width=140
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Mouse Lock",
            command=self.toggle_mouse_lock,
            width=140
        ).pack(side="left", padx=5, pady=10)
        
        settings_frame = ctk.CTkFrame(self.root)
        settings_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.start_var = ctk.BooleanVar(value=self.config.get("start_with_game", True))
        ctk.CTkCheckBox(
            settings_frame,
            text="Auto-start with Overwatch",
            variable=self.start_var,
            command=self._save_settings
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
        
        ctk.CTkLabel(pos_frame, text="Position X/Y:").pack(side="left", padx=5)
        
        self.x_entry = ctk.CTkEntry(pos_frame, width=60)
        self.x_entry.insert(0, str(self.config.get("overlay_position", {}).get("x", 100)))
        self.x_entry.pack(side="left", padx=2)
        
        self.y_entry = ctk.CTkEntry(pos_frame, width=60)
        self.y_entry.insert(0, str(self.config.get("overlay_position", {}).get("y", 100)))
        self.y_entry.pack(side="left", padx=2)
        
        ctk.CTkButton(
            pos_frame,
            text="Save",
            command=self._save_position,
            width=60
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            self.root,
            text=f"Overlay: {self.config.get('hotkey_toggle')} | Lock: {self.config.get('hotkey_mouse_lock')}",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        ).pack(pady=5)
    
    def _setup_tray(self):
        try:
            from pystray import MenuItem as TrayMenuItem
            import pystray
            from PIL import Image
            
            assets_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "..", "Assets", "HeroUI", "tracer.png"
            )
            
            if os.path.exists(assets_path):
                icon = Image.open(assets_path).resize((64, 64), Image.LANCZOS)
            else:
                icon = Image.new('RGB', (64, 64), color='#2196F3')
            
            self._tray_icon = icon
            
            menu = (
                TrayMenuItem("Show Overlay", lambda: self.toggle_overlay()),
                TrayMenuItem("Toggle Mouse Lock", lambda: self.toggle_mouse_lock()),
                TrayMenuItem("---", lambda: None),
                TrayMenuItem("Exit", lambda: self.quit())
            )
            
            self.tray = pystray.Icon("OWCounter", icon, "OW Counter", menu)
            
        except Exception as e:
            print(f"[Tray] Warning: {e}")
            self.tray = None
    
    def _save_settings(self):
        self.config.set("start_with_game", self.start_var.get())
    
    def _on_opacity_change(self, value):
        opacity = value / 100.0
        self.config.set("overlay_opacity", opacity)
        if self.overlay and self.overlay.window:
            self.overlay.window.attributes("-alpha", opacity)
    
    def _save_position(self):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
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
        else:
            sel = self.hero_selector.get_selection()
            if not self.overlay:
                self.overlay = GameOverlay(self.config, sel)
            self.overlay.show()
            self.overlay_visible = True
    
    def toggle_mouse_lock(self):
        from core.mouse_lock import MouseLock, get_primary_monitor_rect
        
        if self.mouse_lock_active:
            MouseLock.release()
            self.mouse_lock_active = False
        else:
            rect = get_primary_monitor_rect()
            MouseLock.clip(rect)
            self.mouse_lock_active = True
    
    def run(self):
        print("[OW Counter] Ready")
        
        if self.tray:
            threading.Thread(target=self.tray.run, daemon=True).start()
        
        self.root.mainloop()
    
    def quit(self):
        from core.mouse_lock import MouseLock
        
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
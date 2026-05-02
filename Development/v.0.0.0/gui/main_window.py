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
        self.root.title("OW2 One Trick Counter")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
        self._setup_tray()
    
    def _setup_ui(self):
        """Setup main UI"""
        title = ctk.CTkLabel(
            self.root,
            text="OW2 One Trick Counter",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        info = ctk.CTkLabel(
            self.root,
            text="Select enemy hero and your hero to see counters",
            font=ctk.CTkFont(size=14)
        )
        info.pack(pady=(0, 20))
        
        self.hero_selector = HeroSelector(self.root)
        self.hero_selector.pack(pady=10, padx=20, fill="both", expand=True)
        
        controls_frame = ctk.CTkFrame(self.root)
        controls_frame.pack(pady=10, padx=20, fill="x")
        
        self.btn_toggle_overlay = ctk.CTkButton(
            controls_frame,
            text="Toggle Overlay",
            command=self.toggle_overlay
        )
        self.btn_toggle_overlay.pack(side="left", padx=5, pady=10)
        
        self.btn_mouse_lock = ctk.CTkButton(
            controls_frame,
            text="Mouse Lock",
            command=self.toggle_mouse_lock
        )
        self.btn_mouse_lock.pack(side="left", padx=5, pady=10)
        
        hotkey_label = ctk.CTkLabel(
            self.root,
            text=f"Hotkeys: {self.config.get('hotkey_toggle')} | {self.config.get('hotkey_mouse_lock')}",
            font=ctk.CTkFont(size=12)
        )
        hotkey_label.pack(pady=10)
    
    def _setup_tray(self):
        """Setup system tray icon"""
        try:
            from pystray import MenuItem as TrayMenuItem
            import pystray
            from PIL import Image
            
            icon_path = self._get_icon_path()
            if icon_path and os.path.exists(icon_path):
                icon = Image.open(icon_path)
            else:
                icon = Image.new('RGB', (64, 64), color='#2196F3')
            
            menu = (
                TrayMenuItem("Overlay: OFF", self.toggle_overlay),
                TrayMenuItem("Mouse Lock: OFF", self.toggle_mouse_lock),
                TrayMenuItem("---", lambda: None),
                TrayMenuItem(f"Hotkey: {self.config.get('hotkey_toggle')}", lambda: None),
                TrayMenuItem(f"Lock: {self.config.get('hotkey_mouse_lock')}", lambda: None),
                TrayMenuItem("---", lambda: None),
                TrayMenuItem("Exit", self.quit)
            )
            
            self.tray = pystray.Icon("OW2Counter", icon, "OW2 Counter", menu)
        except Exception as e:
            print(f"[Tray] Warning: {e}")
            self.tray = None
    
    def _get_icon_path(self):
        """Get tray icon path"""
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "Assets", "HeroUI", "tracer.png")
    
    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.overlay_visible:
            if self.overlay:
                self.overlay.hide()
            self.overlay_visible = False
            print("[OW2 Counter] Overlay hidden")
        else:
            if not self.overlay:
                self.overlay = GameOverlay(
                    self.config,
                    self.hero_selector.get_selection()
                )
            self.overlay.show()
            self.overlay_visible = True
            print("[OW2 Counter] Overlay shown")
    
    def toggle_mouse_lock(self):
        """Toggle mouse lock"""
        from core.mouse_lock import MouseLock
        
        if self.mouse_lock_active:
            MouseLock.release()
            self.mouse_lock_active = False
            print("[OW2 Counter] Mouse lock released")
        else:
            from core.mouse_lock import get_primary_monitor_rect
            rect = get_primary_monitor_rect()
            MouseLock.clip(rect)
            self.mouse_lock_active = True
            print("[OW2 Counter] Mouse locked")
    
    def run(self):
        """Start main loop"""
        print("[OW2 Counter] Starting...")
        
        if self.tray:
            import threading
            threading.Thread(target=self.tray.run, daemon=True).start()
        
        self.root.mainloop()
    
    def quit(self):
        """Exit application"""
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
    cfg = Config.load()
    app = MainWindow(cfg)
    app.run()
"""
Main Window
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
        self.root.geometry("1050x650")
        self.root.resizable(True, True)
        
        ctk.set_appearance_mode("dark")
        
        self._setup_ui()
        self._setup_tray()
    
    def _setup_ui(self):
        # Compact title area
        top_bar = ctk.CTkFrame(self.root, fg_color="transparent", height=30)
        top_bar.pack(fill="x", padx=10, pady=(5, 0))
        
        ctk.CTkLabel(
            top_bar,
            text="OW ONE TRICK COUNTER",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8888AA"
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            top_bar,
            text=f"Hotkeys: {self.config.get('hotkey_toggle').upper()} (Overlay) | {self.config.get('hotkey_mouse_lock').upper()} (Mouse Lock)",
            font=ctk.CTkFont(size=10),
            text_color="#555555"
        ).pack(side="right", padx=10)
        
        self.hero_selector = HeroSelector(self.root)
        self.hero_selector.pack(pady=0, padx=10, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(self.root)
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="Toggle Overlay (O)",
            command=self.toggle_overlay,
            width=140
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Mouse Lock (M)",
            command=self.toggle_mouse_lock,
            width=140
        ).pack(side="left", padx=5, pady=10)
        
        settings = ctk.CTkFrame(self.root)
        settings.pack(pady=10, padx=20, fill="x")
        
        self.start_var = ctk.BooleanVar(value=self.config.get("start_with_game", True))
        ctk.CTkCheckBox(
            settings,
            text="Auto-start with OW",
            variable=self.start_var,
            command=lambda: self.config.set("start_with_game", self.start_var.get())
        ).pack(anchor="w", padx=20)
        
        op_frame = ctk.CTkFrame(settings)
        op_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(op_frame, text="Opacity:").pack(side="left", padx=5)
        
        self.opacity_slider = ctk.CTkSlider(
            op_frame, from_=30, to=100,
            command=self._on_opacity
        )
        self.opacity_slider.set(int(self.config.get("overlay_opacity", 0.85) * 100))
        self.opacity_slider.pack(side="left", padx=5, fill="x", expand=True)
        
        pos_frame = ctk.CTkFrame(settings)
        pos_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(pos_frame, text="Pos X/Y:").pack(side="left", padx=5)
        
        self.x_entry = ctk.CTkEntry(pos_frame, width=50)
        self.x_entry.insert(0, str(self.config.get("overlay_position", {}).get("x", 100)))
        self.x_entry.pack(side="left", padx=2)
        
        self.y_entry = ctk.CTkEntry(pos_frame, width=50)
        self.y_entry.insert(0, str(self.config.get("overlay_position", {}).get("y", 100)))
        self.y_entry.pack(side="left", padx=2)
        
        ctk.CTkButton(
            pos_frame, text="Save", command=self._save_pos, width=50
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            self.root,
            text=f"Hotkeys: {self.config.get('hotkey_toggle')} / {self.config.get('hotkey_mouse_lock')}",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        ).pack(pady=5)
    
    def _setup_tray(self):
        try:
            from pystray import MenuItem as MI
            import pystray
            from PIL import Image
            
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(project_root, "..", "Assets", "HeroUI", "tracer.png")
            
            if os.path.exists(icon_path):
                icon = Image.open(icon_path).resize((64, 64), Image.LANCZOS)
            else:
                icon = Image.new('RGB', (64, 64), color='#2196F3')
            
            menu = (
                MI("Toggle Overlay", lambda: self.toggle_overlay()),
                MI("Toggle Mouse Lock", lambda: self.toggle_mouse_lock()),
                MI("Exit", lambda: self.quit())
            )
            
            self.tray = pystray.Icon("OWCounter", icon, "OW Counter", menu)
        except Exception as e:
            print(f"[Tray] Error: {e}")
            self.tray = None
    
    def _on_opacity(self, val):
        op = val / 100.0
        self.config.set("overlay_opacity", op)
        if self.overlay and self.overlay.window:
            self.overlay.window.attributes("-alpha", op)
    
    def _save_pos(self):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            self.config.set("overlay_position", {"x": x, "y": y})
            if self.overlay and self.overlay.window:
                self.overlay.window.geometry(f"+{x}+{y}")
        except ValueError:
            print("[Settings] Invalid X/Y position values — must be integers")
    
    def toggle_overlay(self):
        if self.overlay_visible:
            if self.overlay:
                self.overlay.hide()
            self.overlay_visible = False
        else:
            sel = self.hero_selector.get_selection()
            if not self.overlay:
                self.overlay = GameOverlay(self.root, self.config, sel)
            else:
                self.overlay.update_selection(sel)
            self.overlay.show()
            self.overlay_visible = True
    
    def toggle_mouse_lock(self):
        from core.mouse_lock import MouseLock, get_primary_monitor_rect
        
        if self.mouse_lock_active:
            MouseLock.release()
            self.mouse_lock_active = False
        else:
            rect = get_primary_monitor_rect()
            print(f"[MouseLock] Locking to {rect}")
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
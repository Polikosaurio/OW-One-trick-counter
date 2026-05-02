"""
OW2 One Trick Counter - Entry Point
v.0.0.0
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from core.config import Config
from core.game_detector import GameDetector
import keyboard
import threading


def main():
    config = Config.load()
    
    game_detector = GameDetector(config)
    
    if config.get("start_with_game", True):
        game_detector.start()
    
    app = MainWindow(config, game_detector)
    
    setup_hotkeys(app, config)
    
    app.run()


def setup_hotkeys(app, config):
    toggle_hotkey = config.get("hotkey_toggle", "ctrl+shift+o")
    mouse_lock_hotkey = config.get("hotkey_mouse_lock", "ctrl+shift+m")
    
    keyboard.add_hotkey(toggle_hotkey, app.toggle_overlay)
    print(f"[OW2 Counter] Hotkey registered: {toggle_hotkey} -> Toggle overlay")
    
    keyboard.add_hotkey(mouse_lock_hotkey, app.toggle_mouse_lock)
    print(f"[OW2 Counter] Hotkey registered: {mouse_lock_hotkey} -> Mouse lock")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[OW2 Counter] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[OW2 Counter] Error: {e}")
        sys.exit(1)
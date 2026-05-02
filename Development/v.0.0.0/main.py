"""
OW One Trick Counter - Entry Point
v.0.0.0
"""

import sys
import os
import threading
import traceback

sys.setrecursionlimit(10000)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def main():
    from gui.main_window import MainWindow
    from core.config import Config
    from core.game_detector import GameDetector
    import keyboard
    
    config = Config.get_instance()
    
    game_detector = GameDetector(config)
    
    if config.get("start_with_game", True):
        game_detector.start()
    
    app = MainWindow(config, game_detector)
    
    toggle_hotkey = config.get("hotkey_toggle", "ctrl+shift+o")
    mouse_lock_hotkey = config.get("hotkey_mouse_lock", "ctrl+shift+m")
    
    keyboard.add_hotkey(toggle_hotkey, app.toggle_overlay)
    print(f"[OW Counter] Hotkey registered: {toggle_hotkey} -> Toggle overlay")
    
    keyboard.add_hotkey(mouse_lock_hotkey, app.toggle_mouse_lock)
    print(f"[OW Counter] Hotkey registered: {mouse_lock_hotkey} -> Mouse lock")
    
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[OW Counter] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[OW Counter] Error: {e}")
        traceback.print_exc()
        sys.exit(1)
"""
Configuration Manager
"""

import json
import os


class Config:
    DEFAULT_SETTINGS = {
        "hotkey_toggle": "ctrl+shift+o",
        "hotkey_mouse_lock": "ctrl+shift+m",
        "start_with_game": True,
        "overlay_opacity": 0.85,
        "overlay_position": {"x": 100, "y": 100},
        "hero_last_selected": None,
        "cv_hero_detection": False,
        "cv_scoreboard_ocr": False,
    }
    
    def __init__(self):
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.config_path = self._get_config_path()
        self.load()
    
    def _get_config_path(self):
        app_data = os.getenv("APPDATA")
        if app_data:
            config_dir = os.path.join(app_data, "OW2Counter")
            os.makedirs(config_dir, exist_ok=True)
            return os.path.join(config_dir, "config.json")
        return "config.json"
    
    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"[Config] Warning: Failed to load config: {e}")
    
    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            print(f"[Config] Saved to {self.config_path}")
        except Exception as e:
            print(f"[Config] Error saving config: {e}")
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save()
    
    @classmethod
    def load(cls):
        config = cls()
        return config


if __name__ == "__main__":
    cfg = Config.load()
    print(f"Config loaded: {cfg.settings}")
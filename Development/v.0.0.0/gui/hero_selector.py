"""
Hero Selector - Visual Grid with Icons
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys


HERO_ROLES = {
    "Tank": ["dva", "orisa", "ramattra", "reinhardt", "roadhog", "sigma", "winston", "zarya", "wreckingball"],
    "DPS": ["ashe", "bastion", "cassidy", "echo", "genji", "hanzo", "junkrat", "mauga", "pharah", "reaper", "sojourn", "sombra", "symmetra", "torbjorn", "tracer", "venture", "widowmaker", "soldier76"],
    "Support": ["ana", "baptiste", "brigitte", "kiriko", "lifeweaver", "lucio", "mercy", "moira", "zenyatta", "illari", "juno"]
}


def get_assets_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(project_root, "..", "Assets", "HeroUI")


class HeroSelector(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.selected_enemy = None
        self.selected_your = None
        self.hero_images = {}
        self.current_icon_size = (36, 36)
        
        self._load_icons()
        self._setup_ui()
    
    def _load_icons(self):
        assets_path = get_assets_path()
        
        if not os.path.exists(assets_path):
            print(f"[HeroSelector] Assets not found: {assets_path}")
            return
        
        for hero in self._get_all_heroes():
            icon_path = os.path.join(assets_path, f"{hero}.png")
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize(self.current_icon_size, Image.LANCZOS)
                    self.hero_images[hero] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"[HeroSelector] Error loading {hero}: {e}")
        
        print(f"[HeroSelector] Loaded {len(self.hero_images)} icons from {assets_path}")
    
    def _setup_ui(self):
        ctk.CTkLabel(
            self,
            text="Select Enemy Hero (problematic):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=12, pady=5)
        
        col = 0
        row = 1
        for hero in self._get_all_heroes():
            btn = ctk.CTkButton(
                self,
                text="",
                image=self.hero_images.get(hero),
                width=36,
                height=36,
                fg_color="#2b2b2b",
                hover_color="#4b4b4b",
                command=lambda h=hero: self._on_enemy_select(h)
            )
            if hero not in self.hero_images:
                btn.configure(text=hero[:3].upper(), font=ctk.CTkFont(size=8))
            
            btn.grid(row=row, column=col, padx=1, pady=1)
            col += 1
            if col >= 12:
                col = 0
                row += 1
        
        row += 1
        
        ctk.CTkLabel(
            self,
            text="Your Hero:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=0, columnspan=12, pady=(10, 5))
        row += 1
        
        col = 0
        for hero in self._get_all_heroes():
            btn = ctk.CTkButton(
                self,
                text="",
                image=self.hero_images.get(hero),
                width=36,
                height=36,
                fg_color="#1a3a1a",
                hover_color="#2a5a2a",
                command=lambda h=hero: self._on_your_select(h)
            )
            if hero not in self.hero_images:
                btn.configure(text=hero[:3].upper(), font=ctk.CTkFont(size=8))
            
            btn.grid(row=row, column=col, padx=1, pady=1)
            col += 1
            if col >= 12:
                col = 0
                row += 1
        
        row += 1
        
        self.info_label = ctk.CTkLabel(
            self,
            text="Select enemy hero for counter advice",
            font=ctk.CTkFont(size=11),
            wraplength=380,
            justify="left"
        )
        self.info_label.grid(row=row, column=0, columnspan=12, pady=10)
    
    def _on_enemy_select(self, hero):
        self.selected_enemy = hero
        self._update_info()
    
    def _on_your_select(self, hero):
        self.selected_your = hero
        self._update_info()
    
    def _get_all_heroes(self):
        heroes = []
        for role, hero_list in HERO_ROLES.items():
            heroes.extend(hero_list)
        return sorted(heroes, key=str.lower)
    
    def _update_info(self):
        from core.counters import CounterDB
        
        if not self.selected_enemy:
            self.info_label.configure(text="Select enemy hero first")
            return
        
        info = f"Enemy: {self.selected_enemy}\n"
        
        if self.selected_your:
            counter = CounterDB.get_counter(self.selected_enemy, self.selected_your)
            if counter:
                info += f"Counter: {counter['hero']}\n\n{counter['reason'][:180]}"
            else:
                info += "No counter data"
        else:
            counters = CounterDB.get_all_counters(self.selected_enemy, limit=5)
            if counters:
                info += "Best counters:\n"
                for c in counters[:5]:
                    info += f"  • {c['hero']} ({c.get('role', '')})\n"
            else:
                info += "No data"
        
        self.info_label.configure(text=info)
    
    def get_selection(self):
        return {"enemy": self.selected_enemy, "your": self.selected_your}


def get_hero_role(hero):
    for role, heroes in HERO_ROLES.items():
        if hero in heroes:
            return role
    return None


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Hero Selector")
    selector = HeroSelector(root)
    selector.pack(fill="both", expand=True, padx=10, pady=10)
    root.mainloop()
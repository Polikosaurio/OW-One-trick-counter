"""
Hero Selector - Visual Grid with Icons
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import os


HERO_ROLES = {
    "Tank": ["dva", "orisa", "ramattra", "reinhardt", "roadhog", "sigma", "winston", "zarya", "wreckingball"],
    "DPS": ["ashe", "bastion", "cassidy", "echo", "genji", "hanzo", "junkrat", "mauga", "pharah", "reaper", "sojourn", "sombra", "symmetra", "torbjorn", "tracer", "venture", "widowmaker", "soldier76"],
    "Support": ["ana", "baptiste", "brigitte", "kiriko", "lifeweaver", "lucio", "mercy", "moira", "zenyatta", "illari", "juno"]
}


def get_assets_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "Assets", "HeroUI")


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
            return
        
        for hero in self._get_all_heroes():
            icon_path = os.path.join(assets_path, f"{hero}.png")
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize(self.current_icon_size, Image.LANCZOS)
                    self.hero_images[hero] = ImageTk.PhotoImage(img)
                except:
                    pass
    
    def _setup_ui(self):
        title = ctk.CTkLabel(self, text="Select Heroes", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=5)
        
        enemy_label = ctk.CTkLabel(self, text="Enemy (problematic):", font=ctk.CTkFont(size=12))
        enemy_label.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        self._create_hero_grid("enemy", row_start=2)
        
        your_label = ctk.CTkLabel(self, text="Your Hero:", font=ctk.CTkFont(size=12))
        your_label.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        self._create_hero_grid("your", row_start=7)
        
        self.info_label = ctk.CTkLabel(
            self,
            text="Select heroes to see counter advice",
            font=ctk.CTkFont(size=11),
            wraplength=380,
            justify="left"
        )
        self.info_label.grid(row=13, column=0, columnspan=2, pady=10)
    
    def _create_hero_grid(self, select_type, row_start):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row_start, column=0, columnspan=2, pady=2)
        
        col = 0
        for hero in self._get_all_heroes():
            btn = ctk.CTkButton(
                frame,
                text="",
                image=self.hero_images.get(hero),
                width=36,
                height=36,
                fg_color="#2b2b2b",
                hover_color="#4b4b4b",
                command=lambda h=hero, t=select_type: self._on_hero_click(h, t)
            )
            if hero not in self.hero_images:
                btn.configure(text=hero[:3].upper()[:3], font=ctk.CTkFont(size=8))
            
            btn.grid(row=0, column=col, padx=1, pady=1)
            col += 1
            if col >= 12:
                col = 0
    
    def _on_hero_click(self, hero, select_type):
        if select_type == "enemy":
            self.selected_enemy = hero
        else:
            self.selected_your = hero
        
        self._update_counter_info()
    
    def _get_all_heroes(self):
        heroes = []
        for role, hero_list in HERO_ROLES.items():
            heroes.extend(hero_list)
        return heroes
    
    def _update_counter_info(self):
        from core.counters import CounterDB
        
        if not self.selected_enemy:
            self.info_label.configure(text="Select enemy hero first")
            return
        
        info = f"Enemy: {self.selected_enemy}\n\n"
        
        if self.selected_your:
            counter = CounterDB.get_counter(self.selected_enemy, self.selected_your)
            if counter:
                info += f"Counter: {counter['hero']}\n\n{counter['reason'][:180]}"
            else:
                info += "No specific counter data"
        else:
            counters = CounterDB.get_all_counters(self.selected_enemy, limit=5)
            if counters:
                info += "Best counters:\n"
                for c in counters[:5]:
                    role = c.get('role', '')
                    info += f"  {c['hero']} ({role})\n"
            else:
                info += "No counter data"
        
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
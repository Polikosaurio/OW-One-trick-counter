"""
Hero Selector - Dynamic Grid
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import os
import json


class HeroSelector(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.selected_enemy = None
        self.selected_your = None
        self.hero_images = {}
        self.roles_data = {}
        
        self._load_data()
        self._load_icons()
        self._setup_ui()
    
    def _load_data(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        idx_path = os.path.join(base_dir, "data", "heroes_index.json")
        
        if os.path.exists(idx_path):
            with open(idx_path, "r") as f:
                self.roles_data = json.load(f)["roles"]
        else:
            print(f"[HeroSelector] Not found: {idx_path}")
            self.roles_data = {"Tank": [], "DPS": [], "Support": []}
    
    def _load_icons(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(base_dir)
        assets_path = os.path.join(project_root, "Assets", "HeroUI")
        
        print(f"[HeroSelector] Looking in: {assets_path}")
        
        if not os.path.exists(assets_path):
            print(f"[HeroSelector] NOT FOUND: {assets_path}")
            assets_path = "D:\\PROYECTOS\\000001-A MEDIAS\\2026-05-03-One Trick Counter\\Assets\\HeroUI"
        
        all_heroes = []
        for role, heroes in self.roles_data.items():
            all_heroes.extend(heroes)
        
        loaded = 0
        for hero in all_heroes:
            icon_path = os.path.join(assets_path, f"{hero}.png")
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize((32, 32), Image.LANCZOS)
                    self.hero_images[hero] = ImageTk.PhotoImage(img)
                    loaded += 1
                except Exception as e:
                    print(f"[HeroSelector] Error {hero}: {e}")
        
        print(f"[HeroSelector] Loaded {loaded}/{len(all_heroes)} icons")
    
    def _setup_ui(self):
        ctk.CTkLabel(
            self,
            text="Select ENEMY Hero:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, columnspan=10, pady=3)
        
        row = 1
        col = 0
        for role, heroes in self.roles_data.items():
            for hero in heroes:
                btn = ctk.CTkButton(
                    self, text="", image=self.hero_images.get(hero),
                    width=30, height=30, fg_color="#3B2B2B", hover_color="#5B4B4B",
                    command=lambda h=hero: self._on_enemy_click(h)
                )
                if hero not in self.hero_images:
                    btn.configure(text=hero[:3].upper(), font=ctk.CTkFont(size=8))
                btn.grid(row=row, column=col, padx=1, pady=1)
                col += 1
                if col >= 10:
                    col = 0
                    row += 1
            col = 0
            row += 1
        
        row += 1
        ctk.CTkLabel(
            self, text="YOUR Hero:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=0, columnspan=10, pady=3)
        row += 1
        col = 0
        for role, heroes in self.roles_data.items():
            for hero in heroes:
                btn = ctk.CTkButton(
                    self, text="", image=self.hero_images.get(hero),
                    width=30, height=30, fg_color="#2B3B2B", hover_color="#4B5B4B",
                    command=lambda h=hero: self._on_your_click(h)
                )
                if hero not in self.hero_images:
                    btn.configure(text=hero[:3].upper(), font=ctk.CTkFont(size=8))
                btn.grid(row=row, column=col, padx=1, pady=1)
                col += 1
                if col >= 10:
                    col = 0
                    row += 1
        
        row += 1
        self.info = ctk.CTkLabel(
            self, text="Select enemy hero for advice",
            font=ctk.CTkFont(size=10), wraplength=350, justify="left"
        )
        self.info.grid(row=row, column=0, columnspan=10, pady=5)
    
    def _on_enemy_click(self, hero):
        self.selected_enemy = hero
        self._update()
    
    def _on_your_click(self, hero):
        self.selected_your = hero
        self._update()
    
    def _update(self):
        from core.counters import CounterDB
        db = CounterDB()
        
        if not self.selected_enemy:
            self.info.configure(text="Select ENEMY hero first")
            return
        
        enemy_data = db.get_hero_data(self.selected_enemy)
        enemy_name = enemy_data.get("name", self.selected_enemy)
        
        info = f"Enemy: {enemy_name}"
        
        if self.selected_your:
            counter = db.get_counter(self.selected_enemy, self.selected_your)
            info = f"{self.selected_your} vs {enemy_name}\n\n{counter.get('reason', 'No data')}"
            
            rec = db.get_recommended_switch(self.selected_enemy, self.selected_your)
            if rec and rec.get("to") != self.selected_your:
                info += f"\n→ Switch to {rec['to']}"
        else:
            info += "\n\nNow select your hero"
        
        self.info.configure(text=info)
    
    def get_selection(self):
        return {"enemy": self.selected_enemy, "your": self.selected_your}


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Test")
    HeroSelector(root).pack(padx=10, pady=10)
    root.mainloop()
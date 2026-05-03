"""
Hero Selector - Clean Layout
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
    
    def _load_icons(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(base_dir)
        assets_path = os.path.join(project_root, "Assets", "HeroUI")
        
        all_heroes = []
        for role, heroes in self.roles_data.items():
            all_heroes.extend(heroes)
        
        for hero in all_heroes:
            icon_path = os.path.join(assets_path, f"{hero}.png")
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize((36, 36), Image.LANCZOS)
                    self.hero_images[hero] = ImageTk.PhotoImage(img)
                except:
                    pass
    
    def _get_role(self, hero):
        for role, heroes in self.roles_data.items():
            if hero in heroes:
                return role
        return "?"
    
    def _setup_ui(self):
        ctk.CTkLabel(
            self, text="ENEMY (problematic)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B6B"
        ).pack(anchor="w", padx=10, pady=(5,3))
        
        hero_list = []
        for heroes in self.roles_data.values():
            hero_list.extend(heroes)
        
        cols = 8
        enemy_grid = ctk.CTkFrame(self, fg_color="transparent")
        enemy_grid.pack(fill="x", padx=5)
        
        for i, hero in enumerate(hero_list):
            row = i // cols
            col = i % cols
            
            btn = ctk.CTkButton(
                enemy_grid, text="", image=self.hero_images.get(hero),
                width=34, height=34,
                fg_color="#3D2525", hover_color="#5D3535",
                border_width=0,
                command=lambda h=hero: self._on_enemy_click(h)
            )
            if hero not in self.hero_images:
                btn.configure(text=hero[:4].upper()[:4], font=ctk.CTkFont(size=8))
            
            btn.grid(row=row, column=col, padx=1, pady=1)
        
        ctk.CTkLabel(
            self, text="YOUR HERO",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4CAF50"
        ).pack(anchor="w", padx=10, pady=(8,3))
        
        your_grid = ctk.CTkFrame(self, fg_color="transparent")
        your_grid.pack(fill="x", padx=5)
        
        for i, hero in enumerate(hero_list):
            row = i // cols
            col = i % cols
            
            btn = ctk.CTkButton(
                your_grid, text="", image=self.hero_images.get(hero),
                width=34, height=34,
                fg_color="#253D25", hover_color="#355D35",
                border_width=0,
                command=lambda h=hero: self._on_your_click(h)
            )
            if hero not in self.hero_images:
                btn.configure(text=hero[:4].upper()[:4], font=ctk.CTkFont(size=8))
            
            btn.grid(row=row, column=col, padx=1, pady=1)
        
        self.info = ctk.CTkLabel(
            self, text="Select enemy hero for advice",
            font=ctk.CTkFont(size=11),
            text_color="#AAAAAA",
            wraplength=360, justify="left"
        )
        self.info.pack(fill="x", padx=10, pady=8)
    
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
            self.info.configure(text="Select ENEMY hero", text_color="#FF6B6B")
            return
        
        enemy_data = db.get_hero_data(self.selected_enemy)
        enemy_name = enemy_data.get("name", self.selected_enemy)
        
        if self.selected_your:
            counter = db.get_counter(self.selected_enemy, self.selected_your)
            role = db.get_role(self.selected_your)
            
            self.info.configure(
                text=f"▶ {self.selected_your} ({role}) vs {enemy_name}\n\n{counter.get('reason', 'No data')}"
            )
            
            rec = db.get_recommended_switch(self.selected_enemy, self.selected_your)
            if rec and rec.get("to") != self.selected_your:
                self.info.configure(text=self.info.cget("text") + f"\n\n💡 Switch: {rec['to']}")
        else:
            self.info.configure(text=f"Enemy: {enemy_name} | Now pick YOUR hero")
    
    def get_selection(self):
        return {"enemy": self.selected_enemy, "your": self.selected_your}
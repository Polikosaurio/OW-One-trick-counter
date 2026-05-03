"""
Hero Selector with Dynamic Roles
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
        
        with open(os.path.join(base_dir, "data", "heroes_index.json"), "r") as f:
            index = json.load(f)
            self.roles_data = index["roles"]
    
    def _load_icons(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_path = os.path.join(project_root, "..", "Assets", "HeroUI")
        
        if not os.path.exists(assets_path):
            print(f"[HeroSelector] Not found: {assets_path}")
            return
        
        all_heroes = []
        for role, heroes in self.roles_data.items():
            all_heroes.extend(heroes)
        
        for hero in all_heroes:
            icon_path = os.path.join(assets_path, f"{hero}.png")
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize((32, 32), Image.LANCZOS)
                    self.hero_images[hero] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"[HeroSelector] {hero}: {e}")
    
    def _setup_ui(self):
        ctk.CTkLabel(
            self,
            text="Select ENEMY Hero (problematic):",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, columnspan=12, pady=(2, 5))
        
        row = 1
        for role, heroes in self.roles_data.items():
            for hero in heroes:
                btn = ctk.CTkButton(
                    self,
                    text="",
                    image=self.hero_images.get(hero),
                    width=32, height=32,
                    fg_color="#2b2b2b",
                    hover_color="#4b4b4b",
                    command=lambda h=hero: self._on_enemy_click(h)
                )
                if hero not in self.hero_images:
                    btn.configure(text=hero[:3].upper(), font=ctk.CTkFont(size=7))
                
                btn.grid(row=row, column=0, padx=1, pady=1)
                break
            
            row += 1
            col = 0
            for hero in heroes:
                btn = ctk.CTkButton(
                    self,
                    text="",
                    image=self.hero_images.get(hero),
                    width=32, height=32,
                    fg_color="#2b2b2b",
                    hover_color="#4b4b4b",
                    command=lambda h=hero: self._on_enemy_click(h)
                )
                if hero not in self.hero_images:
                    btn.configure(text=hero[:3].upper(), font=ctk.CTkFont(size=7))
                
                btn.grid(row=row, column=col, padx=1, pady=1)
                col += 1
                if col >= 12:
                    col = 0
                    row += 1
        
        row += 1
        ctk.CTkLabel(
            self,
            text="Select YOUR Hero:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=row, column=0, columnspan=12, pady=(10, 5))
        row += 1
        
        col = 0
        for role, heroes in self.roles_data.items():
            for hero in heroes:
                btn = ctk.CTkButton(
                    self,
                    text="",
                    image=self.hero_images.get(hero),
                    width=32, height=32,
                    fg_color="#1a3a1a",
                    hover_color="#2a5a2a",
                    command=lambda h=hero: self._on_your_click(h)
                )
                if hero not in self.hero_images:
                    btn.configure(text=hero[:3].upper(), font=ctk.CTkFont(size=7))
                
                btn.grid(row=row, column=col, padx=1, pady=1)
                col += 1
                if col >= 12:
                    col = 0
                    row += 1
        
        row += 1
        self.info_label = ctk.CTkLabel(
            self,
            text="Select enemy hero for advice",
            font=ctk.CTkFont(size=10),
            wraplength=380,
            justify="left"
        )
        self.info_label.grid(row=row, column=0, columnspan=12, pady=10)
    
    def _on_enemy_click(self, hero):
        self.selected_enemy = hero
        self._update_info()
    
    def _on_your_click(self, hero):
        self.selected_your = hero
        self._update_info()
    
    def _update_info(self):
        from core.counters import CounterDB
        db = CounterDB()
        
        if not self.selected_enemy:
            self.info_label.configure(text="Select enemy hero first")
            return
        
        e_data = db.get_hero_data(self.selected_enemy)
        e_name = e_data.get("name", self.selected_enemy)
        
        info = f"Enemy: {e_name}"
        
        if self.selected_your:
            counter = db.get_counter(self.selected_enemy, self.selected_your)
            reason = counter.get("reason", "No data")
            
            my_role = db.get_role(self.selected_your)
            
            info = f"{self.selected_your} ({my_role}) vs {e_name}\n\n{reason}"
            
            rec = db.get_recommended_switch(self.selected_enemy, self.selected_your)
            if rec and rec["hero"] != self.selected_your:
                info += f"\n\n→ Consider switching to {rec['hero']}: {rec['reason'][:60]}..."
        else:
            role_counters = db.get_role_counters(self.selected_enemy, "DPS")
            if role_counters:
                info += "\n\nDPS counters:"
                for c in role_counters[:3]:
                    info += f"\n• {c['hero']}: {c['reason'][:50]}..."
        
        self.info_label.configure(text=info)
    
    def get_selection(self):
        return {"enemy": self.selected_enemy, "your": self.selected_your}


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Hero Selector")
    selector = HeroSelector(root)
    selector.pack(fill="both", expand=True, padx=10, pady=10)
    root.mainloop()
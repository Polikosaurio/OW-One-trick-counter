"""
Hero Selector - Visual Grid
"""

import customtkinter as ctk
import os
import json


HERO_ROLES = {
    "Tank": ["dva", "orisa", "ramattra", "reinhardt", "roadhog", "sigma", "winston", "zarya", "wreckingball"],
    "DPS": ["ashe", "bastion", "cassidy", "echo", "genji", "hanzo", "junkrat", "mauga", "pharah", "reaper", "sojourn", "sombra", "symmetra", "torbjorn", "tracer", "venture", "widowmaker", "soldier76"],
    "Support": ["ana", "baptiste", "brigitte", "kiriko", "lifeweaver", "lucio", "mercy", "moira", "zenyatta", "illari", "juno"]
}


class HeroSelector(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.selected_enemy = None
        self.selected_your = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        title = ctk.CTkLabel(self, text="Select Heroes", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=5)
        
        enemy_label = ctk.CTkLabel(self, text="Enemy Hero:", font=ctk.CTkFont(size=14))
        enemy_label.grid(row=1, column=0, padx=5, sticky="e")
        
        self.enemy_var = ctk.StringVar(value="Select enemy...")
        self.enemy_combo = ctk.CTkComboBox(
            self,
            values=self._get_all_heroes(),
            variable=self.enemy_var,
            command=self._on_enemy_select,
            width=200
        )
        self.enemy_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        your_label = ctk.CTkLabel(self, text="Your Hero:", font=ctk.CTkFont(size=14))
        your_label.grid(row=2, column=0, padx=5, sticky="e")
        
        self.your_var = ctk.StringVar(value="Select hero...")
        self.your_combo = ctk.CTkComboBox(
            self,
            values=self._get_all_heroes(),
            variable=self.your_var,
            command=self._on_your_select,
            width=200
        )
        self.your_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=350,
            justify="left"
        )
        self.info_label.grid(row=3, column=0, columnspan=2, pady=20)
    
    def _get_all_heroes(self):
        heroes = []
        for role, hero_list in HERO_ROLES.items():
            heroes.extend(hero_list)
        return sorted(heroes, key=str.lower)
    
    def _on_enemy_select(self, value):
        self.selected_enemy = value
        self._update_counter_info()
    
    def _on_your_select(self, value):
        self.selected_your = value
        self._update_counter_info()
    
    def _update_counter_info(self):
        from core.counters import CounterDB
        
        if not self.selected_enemy:
            self.info_label.configure(text="Select an enemy hero to see counters")
            return
        
        info = f"Enemy: {self.selected_enemy}\n"
        
        if self.selected_your:
            counter = CounterDB.get_counter(self.selected_enemy, self.selected_your)
            if counter:
                info += f"Your counter: {counter['hero']}\n"
                info += f"Reason: {counter['reason']}"
            else:
                info += "No specific counter found"
        else:
            counters = CounterDB.get_all_counters(self.selected_enemy)
            if counters:
                info += "Recommended counters:\n"
                for c in counters[:5]:
                    info += f"  - {c['hero']}: {c['reason'][:50]}...\n"
            else:
                info += "No counters available"
        
        self.info_label.configure(text=info)
    
    def get_selection(self):
        return {
            "enemy": self.selected_enemy,
            "your": self.selected_your
        }


def get_hero_role(hero):
    """Get role for a hero"""
    for role, heroes in HERO_ROLES.items():
        if hero in heroes:
            return role
    return None


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Hero Selector Test")
    selector = HeroSelector(root)
    selector.pack(fill="both", expand=True, padx=20, pady=20)
    root.mainloop()
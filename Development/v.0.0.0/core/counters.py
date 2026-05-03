"""
Counter Database v2.0 - Tag-based System
Provides strategic advice based on hero tag matching
"""

import json
import os


TAG_OPPOSITES = {
    "weak_to_flank": "anti_flank",
    "weak_to_mobility": "dive_capability", 
    "weak_to_cc": "crowd_control",
    "weak_to_sniper": "mobile",
    "weak_to_poke": "poke"
}


class CounterDB:
    _instance = None
    _heroes = None
    _roles = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        with open(os.path.join(base_dir, "data", "heroes_index.json"), "r") as f:
            index = json.load(f)
            self._roles = index["roles"]
        
        with open(os.path.join(base_dir, "data", "heroes_db.json"), "r") as f:
            self._heroes = json.load(f)
    
    def get_hero_data(self, hero):
        return self._heroes.get(hero, {})
    
    def get_role(self, hero):
        for role, heroes in self._roles.items():
            if hero in heroes:
                return role
        return "DPS"
    
    def get_counter(self, enemy_hero, my_hero):
        enemy = self.get_hero_data(enemy_hero)
        my_data = self.get_hero_data(my_hero)
        
        if not enemy or not my_data:
            return {"hero": my_hero, "reason": "No data available"}
        
        my_role = self.get_role(my_hero)
        
        advice = self._generate_advice(enemy_hero, enemy, my_data, my_role)
        
        return {
            "hero": my_hero,
            "role": my_role,
            "reason": advice
        }
    
    def _generate_advice(self, enemy_hero, enemy, my_data, my_role):
        enemy_tags = enemy.get("tags", {})
        my_tags = my_data.get("tags", {})
        
        points = []
        
        for tag, weight in enemy_tags.items():
            if tag in TAG_OPPOSITES:
                opposite = TAG_OPPOSITES[tag]
                if my_tags.get(opposite, 0) > 0.5:
                    points.append(f"You have {opposite} to exploit their {tag.replace('weak_to_', '')}")
        
        for my_tag, weight in my_tags.items():
            if weight > 0.7 and my_tag in ["healing", "peel", "anti_flank"]:
                points.append(f"Your {my_tag.replace('_', ' ')} helps in this matchup")
        
        if my_role == "Support" and my_tags.get("peel", 0) > 0.6:
            points.append("Focus on peeling for teammates")
        
        if my_role == "DPS":
            if enemy.get("counters_me"):
                c = enemy.get("counters_me", [])[:2]
                if c:
                    e_name = enemy.get("name", enemy_hero)
                    points.append(f"Beware: these counter {e_name}: {', '.join(c)}")
        
        e_best = enemy.get("best_against", [])
        if e_best:
            e_name = enemy.get("name", enemy_hero)
            points.append(f"{e_name} targets: {', '.join(e_best[:2])}")
        
        if not points:
            advice = {
                "Tank": "Peel for supports, disrupt positioning",
                "DPS": "Use high ground, don't overcommit",
                "Support": "Play safe, prioritize survival"
            }
            points.append(advice.get(my_role, "Play your life"))
        
        return " | ".join(points[:3])
    
    def get_all_counters(self, enemy_hero, limit=5):
        enemy = self.get_hero_data(enemy_hero)
        if not enemy:
            return []
        
        results = []
        
        for hero, data in self._heroes.items():
            if hero == enemy_hero:
                continue
            
            role = self.get_role(hero)
            counter = self.get_counter(enemy_hero, hero)
            
            results.append({
                "hero": hero,
                "role": role,
                "reason": counter.get("reason", "")[:100]
            })
        
        return results[:limit]
    
    def get_role_counters(self, enemy_hero, my_role):
        enemy = self.get_hero_data(enemy_hero)
        if not enemy:
            return []
        
        results = []
        
        for hero in self._roles.get(my_role, []):
            if hero == enemy_hero:
                continue
            
            counter = self.get_counter(enemy_hero, hero)
            results.append({
                "hero": hero,
                "reason": counter.get("reason", "")
            })
        
        return results
    
    def get_recommended_switch(self, enemy_hero, current_hero):
        my_role = self.get_role(current_hero)
        role_counters = self.get_role_counters(enemy_hero, my_role)
        
        if role_counters:
            best = role_counters[0]
            return {
                "from": current_hero,
                "to": best["hero"],
                "reason": best["reason"],
                "role": my_role
            }
        
        return None


def get_counter(enemy_hero, my_hero):
    db = CounterDB()
    return db.get_counter(enemy_hero, my_hero)


def get_role_counters(enemy_hero, my_role):
    db = CounterDB()
    return db.get_role_counters(enemy_hero, my_role)


def get_recommended_switch(enemy_hero, current_hero):
    db = CounterDB()
    return db.get_recommended_switch(enemy_hero, current_hero)


if __name__ == "__main__":
    print("Testing CounterDB...")
    db = CounterDB()
    
    print("\n--- Widowmaker vs Ana ---")
    print(get_counter("widowmaker", "ana"))
    
    print("\n--- Recommend switch from Ana vs Widow ---")
    print(get_recommended_switch("widowmaker", "ana"))
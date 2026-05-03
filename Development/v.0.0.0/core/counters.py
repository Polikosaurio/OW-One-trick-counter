"""
Counter Database v2.1 - Tag-based System
Provides strategic advice based on hero tag matching.
Counters are scored and sorted so the best ones come first.
"""

import json
import os


# Maps an enemy weakness tag → the player tag that exploits it.
# Covers all weakness tags actually used in heroes_db.json.
TAG_OPPOSITES = {
    # Mobility / positioning weaknesses
    "weak_to_flank":    "flank",
    "weak_to_mobility": "dive_capability",
    "weak_to_dive":     "dive_capability",
    # CC weaknesses
    "weak_to_cc":       "crowd_control",
    # Range / aim weaknesses
    "weak_to_sniper":   "sniper",
    "weak_to_poke":     "poke",
    "weak_to_ranged":   "poke",
    "weak_to_hitscan":  "hitscan",
    # Damage-type weaknesses
    "weak_to_burst":    "burst_damage",
    "weak_to_anti_air": "hitscan",
}

# Tags that are inherently good for a hero to have regardless of matchup
GENERIC_GOOD_TAGS = {"healing", "peel", "anti_flank", "utility", "versatile"}


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

        with open(os.path.join(base_dir, "data", "heroes_index.json"), "r", encoding="utf-8") as f:
            index = json.load(f)
            self._roles = index["roles"]

        self._heroes = {}
        heroes_dir = os.path.join(base_dir, "data", "heroes")
        if os.path.exists(heroes_dir):
            for file_name in os.listdir(heroes_dir):
                if file_name.endswith(".json"):
                    hero_key = file_name.replace(".json", "")
                    with open(os.path.join(heroes_dir, file_name), "r", encoding="utf-8") as f:
                        self._heroes[hero_key] = json.load(f)

    def get_hero_data(self, hero):
        return self._heroes.get(hero, {})

    def get_role(self, hero):
        for role, heroes in self._roles.items():
            if hero in heroes:
                return role
        return "DPS"

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score_counter(self, enemy_hero, my_hero):
        """
        Returns a numeric score (higher = better counter).
        Based on how many of the enemy's weaknesses the player hero covers.
        """
        enemy = self.get_hero_data(enemy_hero)
        my_data = self.get_hero_data(my_hero)
        if not enemy or not my_data:
            return 0.0

        enemy_tags = enemy.get("tags", {})
        my_tags = my_data.get("tags", {})

        score = 0.0
        for tag, weight in enemy_tags.items():
            if tag in TAG_OPPOSITES:
                opposite = TAG_OPPOSITES[tag]
                my_val = my_tags.get(opposite, 0.0)
                score += weight * my_val  # both sides contribute

        # Bonus if the enemy explicitly lists my_hero in their counters_me
        if my_hero in [c.strip().lower() for c in enemy.get("counters_me", [])]:
            score += 1.0

        return score

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_counter(self, enemy_hero, my_hero):
        """Advice for playing my_hero against enemy_hero."""
        enemy = self.get_hero_data(enemy_hero)
        my_data = self.get_hero_data(my_hero)

        if not enemy or not my_data:
            return {"hero": my_hero, "reason": "No data available"}

        my_role = self.get_role(my_hero)
        advice = self._generate_advice(enemy_hero, enemy, my_data, my_role)

        return {
            "hero": my_hero,
            "role": my_role,
            "score": self._score_counter(enemy_hero, my_hero),
            "reason": advice,
        }

    def _generate_advice(self, enemy_hero, enemy, my_data, my_role):
        enemy_tags = enemy.get("tags", {})
        my_tags = my_data.get("tags", {})
        enemy_name = enemy.get("name", enemy_hero.capitalize())

        adv_yours = []
        adv_theirs = []
        tactics = []

        # 1. Tu héroe explota debilidades del enemigo
        for tag, weight in sorted(enemy_tags.items(), key=lambda kv: -kv[1]):
            if tag in TAG_OPPOSITES and weight >= 0.5:
                opposite = TAG_OPPOSITES[tag]
                if my_tags.get(opposite, 0) >= 0.5:
                    weakness = tag.replace("weak_to_", "").replace("_", " ").upper()
                    ability = opposite.replace("_", " ").upper()
                    adv_yours.append(f"✓ You have {ability} against their weak {weakness}")

        # 2. El enemigo explota tus debilidades
        for tag, weight in sorted(my_tags.items(), key=lambda kv: -kv[1]):
            if tag in TAG_OPPOSITES and weight >= 0.5:
                opposite = TAG_OPPOSITES[tag]
                if enemy_tags.get(opposite, 0) >= 0.5:
                    weakness = tag.replace("weak_to_", "").replace("_", " ").upper()
                    ability = opposite.replace("_", " ").upper()
                    adv_theirs.append(f"⚠ They have {ability} against your weak {weakness}")

        # 3. Role-specific generic tips based on my own strong tags
        for my_tag, val in my_tags.items():
            if val >= 0.7 and my_tag in GENERIC_GOOD_TAGS:
                tactics.append(f"• Prioritize your {my_tag.replace('_', ' ').upper()} in this matchup.")

        # 4. What the enemy preys on
        e_best = [b.strip().capitalize() for b in enemy.get("best_against", []) if b.strip()]
        if e_best:
            tactics.append(f"• {enemy_name} usually targets: {', '.join(e_best[:3])}.")

        # Formatear el breakdown
        breakdown = []
        if adv_yours:
            breakdown.append("YOUR ADVANTAGES:\n" + "\n".join(adv_yours))
        if adv_theirs:
            breakdown.append("ENEMY THREATS:\n" + "\n".join(adv_theirs))
        if tactics:
            breakdown.append("TACTICS:\n" + "\n".join(tactics))

        if not breakdown:
            fallback = {
                "Tank": "Peel for supports, disrupt their positioning.",
                "DPS": "Use high ground, don't overcommit.",
                "Support": "Play safe, prioritise survival and your allies.",
            }
            breakdown.append("TACTICS:\n• " + fallback.get(my_role, "Play your life — no specific data"))

        return "\n\n".join(breakdown)

    def get_all_counters(self, enemy_hero, limit=5):
        """Returns the top `limit` counter-picks for enemy_hero, sorted by score."""
        enemy = self.get_hero_data(enemy_hero)
        if not enemy:
            return []

        results = []
        for hero in self._heroes:
            if hero == enemy_hero:
                continue
            score = self._score_counter(enemy_hero, hero)
            counter = self.get_counter(enemy_hero, hero)
            results.append({
                "hero": hero,
                "role": self.get_role(hero),
                "score": score,
                "reason": counter.get("reason", "")[:120],
            })

        results.sort(key=lambda x: -x["score"])
        return results[:limit]

    def get_role_counters(self, enemy_hero, my_role):
        """
        Returns all heroes of my_role sorted by counter score vs enemy_hero.
        """
        enemy = self.get_hero_data(enemy_hero)
        if not enemy:
            return []

        results = []
        for hero in self._roles.get(my_role, []):
            if hero == enemy_hero:
                continue
            score = self._score_counter(enemy_hero, hero)
            counter = self.get_counter(enemy_hero, hero)
            results.append({
                "hero": hero,
                "score": score,
                "reason": counter.get("reason", ""),
            })

        results.sort(key=lambda x: -x["score"])
        return results

    def get_recommended_switch(self, enemy_hero, current_hero):
        """
        Suggests the best hero of the same role to switch to.
        Excludes the hero you're already on.
        """
        my_role = self.get_role(current_hero)
        role_counters = self.get_role_counters(enemy_hero, my_role)

        # Filter out current hero (already excluded in get_role_counters, but be safe)
        candidates = [r for r in role_counters if r["hero"] != current_hero]

        if candidates:
            best = candidates[0]
            return {
                "from": current_hero,
                "to": best["hero"],
                "score": best["score"],
                "reason": best["reason"],
                "role": my_role,
            }

        return None


# ---------------------------------------------------------------------------
# Module-level convenience wrappers
# ---------------------------------------------------------------------------

def get_counter(enemy_hero, my_hero):
    return CounterDB().get_counter(enemy_hero, my_hero)


def get_role_counters(enemy_hero, my_role):
    return CounterDB().get_role_counters(enemy_hero, my_role)


def get_recommended_switch(enemy_hero, current_hero):
    return CounterDB().get_recommended_switch(enemy_hero, current_hero)


if __name__ == "__main__":
    print("Testing CounterDB...")
    db = CounterDB()

    print("\n--- Widowmaker vs Ana ---")
    print(get_counter("widowmaker", "ana"))

    print("\n--- Top 5 counters vs Widowmaker ---")
    for c in db.get_all_counters("widowmaker", 5):
        print(f"  {c['hero']} (score={c['score']:.2f}) — {c['reason'][:60]}")

    print("\n--- Recommend switch from Ana vs Widow ---")
    print(get_recommended_switch("widowmaker", "ana"))

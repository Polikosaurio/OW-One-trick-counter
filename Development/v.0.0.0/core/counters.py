"""
Counter Database v2.3 - Tag-based System with Skill Scaling & Smurf Detection
Provides strategic advice based on hero tag matching, adjusted by player skill rank.
Counters are scored and sorted so the best ones come first.
"""

import json
import os

# Overwatch 2 Competitive Ranks with emojis
RANK_INFO = {
    "bronze":     {"tier": 0, "label": "Bronze",     "emoji": "\u2B50"},
    "silver":     {"tier": 1, "label": "Silver",     "emoji": "\U0001F948"},
    "gold":       {"tier": 2, "label": "Gold",       "emoji": "\U0001F947"},
    "platinum":   {"tier": 3, "label": "Platinum",   "emoji": "\U0001F48E"},
    "diamond":    {"tier": 4, "label": "Diamond",    "emoji": "\U0001F48E"},
    "master":     {"tier": 5, "label": "Master",     "emoji": "\U0001F31F"},
    "grandmaster":{"tier": 6, "label": "Grandmaster","emoji": "\U0001F451"},
    "champion":   {"tier": 7, "label": "Champion",   "emoji": "\U0001F3C6"},
}

RANK_ORDER = list(RANK_INFO.keys())
DEFAULT_RANK = "platinum"

# Smurf: enemy plays as if 3 tiers above current lobby rank
SMURF_TIER_BOOST = 3
SMURF_EMOJI = "\U0001F535"
SMURF_WARNING = "\u26A0\uFE0F"

# Tags whose effectiveness scales with player skill rank.
# direction="positive" = stronger at high ranks (aim-dependent, mechanical heroes)
# direction="negative" = stronger at low ranks (mobility, unpredictable play)
SKILL_DEPENDENT_TAGS = {
    # Aim-dependent: benefit from good mechanics at high rank
    "aim_intensive":    {"direction": "positive", "weight": 0.3},
    "high_skill_ceiling": {"direction": "positive", "weight": 0.25},
    "sniper":           {"direction": "positive", "weight": 0.2},
    "hitscan":          {"direction": "positive", "weight": 0.15},
    # Mobility-based: benefit from enemy tracking weakness at low rank
    "mobile":           {"direction": "negative", "weight": 0.25},
    "dive_capability":  {"direction": "negative", "weight": 0.2},
    "flank":            {"direction": "negative", "weight": 0.15},
    "escape_ability":   {"direction": "negative", "weight": 0.15},
    # Game sense: benefit from macro understanding at high rank
    "game_sense_intensive": {"direction": "positive", "weight": 0.2},
    # Cooldown dependent: benefit from enemies not playing around CDs at low rank
    "cooldown_dependent":   {"direction": "negative", "weight": 0.15},
}


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
    # Additional weakness tags from subrole system
    "weak_to_kiting":       "mobile",
    "weak_to_grounding":    "anti_air",
    "weak_to_close_combat": "close_combat",
    "weak_to_aoe":          "area_denial",
    "weak_to_sustained_damage": "sustained_damage",
    "weak_to_anti_flank":   "anti_flank",
    "weak_to_long_range":   "long_range",
    "weak_to_anti_heal":    "anti_healer",
    # Subrole-specific counter tags
    "weak_against_bruiser":       "bruiser",
    "weak_against_initiator":     "initiator",
    "weak_against_stalwart":      "stalwart",
    "weak_against_sharpshooter":  "sharpshooter",
    "weak_against_flanker":       "flanker",
    "weak_against_specialist":    "specialist",
    "weak_against_recon":         "recon",
    "weak_against_tactician":     "tactician",
    "weak_against_medic":         "medic",
    "weak_against_survivor":      "survivor",
    # --- Matchup-specific tags (contextual weaknesses) ---
    # Los pierde en duelos del mismo tipo (ej: poke vs poke)
    "loses_poke_duels":       "sniper",
    # Depende de cobertura para ser efectivo
    "cover_dependent":        "angle_denial",
    # Muy débil cuando está expuesto/sin cobertura
    "exposed_vulnerable":     "poke",
    # Le cuesta contra enemigos a distancia
    "struggles_vs_ranged":    "long_range",
    # Vulnerable a que lo kiteen
    "vulnerable_to_kiting":   "mobile",
    # Depende de escudos para sobrevivir
    "shield_reliant":         "shield_break",
    # Solo puede pelear en melee
    "melee_only":             "long_range",
    # Le cuesta contra composiciones dive
    "struggles_vs_dive":      "dive_capability",
    # Pierde contra poke sostenido (no burst)
    "weak_vs_sustained_poke": "sustained_damage",
    # Le cuesta en combate cerrado
    "struggles_vs_close_combat": "close_combat",
}

# Tags that are inherently good for a hero to have regardless of matchup
GENERIC_GOOD_TAGS = {"healing", "peel", "anti_flank", "utility", "versatile",
    "close_quarters_dominant", "strong_cover_utilization", "high_burst_combo",
    "ally_transport", "projectile_absorption", "pick_potential_from_range",
    "dive_synergy", "zone_lockdown", "shield_break", "angle_denial"}

# Subrole descriptions for advice generation
SUBROLE_INFO = {
    "bruiser":       {"role": "Tank", "passive": "Reduces critical damage. At low HP, gain movement speed."},
    "initiator":     {"role": "Tank", "passive": "Staying airborne lightly heals you."},
    "stalwart":      {"role": "Tank", "passive": "Reduces knockbacks and slows received."},
    "sharpshooter":  {"role": "DPS", "passive": "Critical hits reduce movement ability cooldowns."},
    "flanker":       {"role": "DPS", "passive": "Health packs restore more health."},
    "specialist":    {"role": "DPS", "passive": "Eliminations briefly increase reload speed."},
    "recon":         {"role": "DPS", "passive": "Detect enemies below half health through walls after damaging them."},
    "tactician":     {"role": "Support", "passive": "Excess ultimate charge carries over after using your ultimate."},
    "medic":         {"role": "Support", "passive": "Healing allies with your weapon also heals you."},
    "survivor":      {"role": "Support", "passive": "Using a movement ability activates passive health regeneration."},
}

# Human-readable labels for matchup tags
MATCHUP_LABELS = {
    # Matchup-specific tags (contextual weaknesses)
    "loses_poke_duels":       "poke duels",
    "cover_dependent":        "cover denial",
    "exposed_vulnerable":     "exposure to poke",
    "struggles_vs_ranged":    "ranged opponents",
    "vulnerable_to_kiting":   "kiting",
    "shield_reliant":         "shield pressure",
    "melee_only":             "range advantage",
    "struggles_vs_dive":      "dive compositions",
    "weak_vs_sustained_poke": "sustained poke",
    "struggles_vs_close_combat": "close combat",
    # Kit strength tags
    "poke_from_cover":        "poke from cover",
    "strong_cover_utilization": "cover fights",
    "close_quarters_dominant": "close quarters",
    "high_burst_combo":       "burst combos",
    "ally_transport":         "ally mobility",
    "projectile_absorption":  "projectile-heavy comps",
    "pick_potential_from_range": "pick potential at range",
    "dive_synergy":           "dive compositions",
    "zone_lockdown":          "zone control",
    "shield_break":           "shields",
    "angle_denial":           "angle control",
    # Legacy weakness tags
    "weak_to_flank":          "flank pressure",
    "weak_to_mobility":       "mobile enemies",
    "weak_to_dive":           "dive compositions",
    "weak_to_cc":             "crowd control",
    "weak_to_sniper":         "snipers",
    "weak_to_poke":           "poke damage",
    "weak_to_ranged":         "ranged pressure",
    "weak_to_hitscan":        "hitscan accuracy",
    "weak_to_burst":          "burst damage",
    "weak_to_anti_air":       "anti-air",
    "weak_to_kiting":         "kiting",
    "weak_to_grounding":      "grounding effects",
    "weak_to_close_combat":   "close combat",
    "weak_to_aoe":            "AoE damage",
    "weak_to_sustained_damage": "sustained damage",
    "weak_to_anti_flank":     "anti-flank",
    "weak_to_long_range":     "long range",
    "weak_to_anti_heal":      "anti-heal",
    # Legacy strength tags
    "sniper":                 "sniper damage",
    "poke":                   "poke damage",
    "hitscan":                "hitscan pressure",
    "burst_damage":           "burst damage",
    "flank":                  "flank access",
    "dive_capability":        "dive potential",
    "crowd_control":          "crowd control",
    "mobile":                 "mobility",
    "long_range":             "long range",
    "sustained_damage":       "sustained damage",
    "close_combat":           "close combat",
    "area_denial":            "area denial",
    "anti_flank":             "anti-flank",
    "anti_air":               "anti-air",
    # Subrole weakness tags
    "weak_against_bruiser":       "bruiser pressure",
    "weak_against_initiator":     "initiator dive",
    "weak_against_stalwart":      "stalwart defense",
    "weak_against_sharpshooter":  "sharpshooter picks",
    "weak_against_flanker":       "flank pressure",
    "weak_against_specialist":    "specialist sustained fire",
    "weak_against_recon":         "recon tracking",
    "weak_against_tactician":     "tactician ult economy",
    "weak_against_medic":         "medic sustain",
    "weak_against_survivor":      "survivor sustain",
    # Subrole strength tags
    "strong_against_bruiser":       "bruiser counter",
    "strong_against_initiator":     "initiator counter",
    "strong_against_stalwart":      "stalwart counter",
    "strong_against_sharpshooter":  "sharpshooter counter",
    "strong_against_flanker":       "flanker counter",
    "strong_against_specialist":    "specialist counter",
    "strong_against_recon":         "recon counter",
    "strong_against_tactician":     "tactician counter",
    "strong_against_medic":         "medic counter",
    "strong_against_survivor":      "survivor counter",
}


class CounterDB:
    _instance = None
    _heroes = None
    _roles = None
    _rank = DEFAULT_RANK
    _smurf_suspected = False

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

    def set_rank(self, rank):
        """Set the current skill rank for matchup scaling."""
        if rank in RANK_INFO:
            self._rank = rank

    def get_rank(self):
        return self._rank

    def set_smurf(self, suspected):
        """Toggle smurf suspicion mode - enemy plays above their rank."""
        self._smurf_suspected = suspected

    def get_smurf(self):
        return self._smurf_suspected

    def _get_skill_modifier(self, hero, rank_override=None):
        """
        Returns a multiplier based on hero's skill-dependent tags and current rank.
        > 1.0 means hero benefits at current rank level
        < 1.0 means hero is disadvantaged at current rank level
        rank_override: use a specific rank key instead of self._rank (for smurf detection)
        """
        hero_data = self.get_hero_data(hero)
        tags = hero_data.get("tags", {})
        effective_rank = rank_override if rank_override else self._rank
        rank_tier = RANK_INFO[effective_rank]["tier"]
        max_tier = len(RANK_ORDER) - 1  # 7 for Champion

        modifier = 1.0

        for tag, info in SKILL_DEPENDENT_TAGS.items():
            if tag not in tags:
                continue
            tag_weight = tags[tag]
            direction = info["direction"]
            strength = info["weight"]

            if direction == "positive":
                # Aim/mechanical heroes: stronger at high rank
                # Bronze (tier 0) → 0.7, Champion (tier 7) → 1.3
                rank_factor = 0.7 + (0.6 * rank_tier / max_tier)
            else:
                # Mobility heroes: stronger at low rank
                # Bronze (tier 0) → 1.3, Champion (tier 7) → 0.7
                rank_factor = 1.3 - (0.6 * rank_tier / max_tier)

            modifier += tag_weight * strength * (rank_factor - 1.0)

        return modifier

    def _get_enemy_rank(self):
        """Returns the effective rank of the enemy (boosted if smurf is suspected)."""
        lobby_rank = self._rank
        if self._smurf_suspected:
            boosted_tier = min(RANK_INFO[lobby_rank]["tier"] + SMURF_TIER_BOOST, len(RANK_ORDER) - 1)
            return RANK_ORDER[boosted_tier]
        return lobby_rank

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score_counter(self, enemy_hero, my_hero):
        """
        Returns a numeric score (higher = better counter).
        Based on how many of the enemy's weaknesses the player hero covers.
        Skill rank modifiers are applied to both heroes.
        If smurf is suspected, enemy weaknesses are harder to exploit
        (better positioning, mechanics, game sense).
        """
        enemy = self.get_hero_data(enemy_hero)
        my_data = self.get_hero_data(my_hero)
        if not enemy or not my_data:
            return 0.0

        enemy_tags = enemy.get("tags", {})
        my_tags = my_data.get("tags", {})

        # Enemy skill: determines how well they mitigate their weaknesses
        enemy_rank = self._get_enemy_rank()
        # For the enemy, higher rank = less exploitable weaknesses
        # We use an INVERSE modifier: high skill reduces weakness weight
        enemy_skill = self._get_skill_modifier(enemy_hero, rank_override=enemy_rank)
        # Invert: 1.3 skill → 0.77 weakness mitigation
        enemy_weakness_mod = 2.0 - enemy_skill

        # My skill: determines how well I exploit enemy weaknesses
        my_mod = self._get_skill_modifier(my_hero)

        score = 0.0
        for tag, weight in enemy_tags.items():
            if tag in TAG_OPPOSITES:
                opposite = TAG_OPPOSITES[tag]
                my_val = my_tags.get(opposite, 0.0)
                # Enemy weakness scaled down by their skill (smurf = harder to exploit)
                # My counter strength scaled by my skill
                effective_weakness = weight * enemy_weakness_mod
                score += effective_weakness * (my_val * my_mod)

        # Bonus if the enemy explicitly lists my_hero in their counters_me
        # Smurf enemies play around their counters better
        if my_hero in [c.strip().lower() for c in enemy.get("counters_me", [])]:
            score += 1.0 * my_mod * enemy_weakness_mod

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

    def _format_tag_label(self, tag):
        """Return a human-readable label for any tag."""
        if tag in MATCHUP_LABELS:
            return MATCHUP_LABELS[tag]
        return tag.replace("weak_to_", "").replace("weak_against_", "").replace("_", " ")

    def _generate_advice(self, enemy_hero, enemy, my_data, my_role):
        enemy_tags = enemy.get("tags", {})
        my_tags = my_data.get("tags", {})
        enemy_name = enemy.get("name", enemy_hero.capitalize())
        my_name = my_data.get("name", "Your hero")

        adv_yours = []
        adv_theirs = []
        tactics = []

        # 1. Tu héroe explota debilidades del enemigo
        for tag, weight in sorted(enemy_tags.items(), key=lambda kv: -kv[1]):
            if tag in TAG_OPPOSITES and weight >= 0.5:
                opposite = TAG_OPPOSITES[tag]
                if my_tags.get(opposite, 0) >= 0.5:
                    weakness = self._format_tag_label(tag)
                    ability = self._format_tag_label(opposite)
                    adv_yours.append(f"[+] You have {ability} against their {weakness}")

        # 2. El enemigo explota tus debilidades
        for tag, weight in sorted(my_tags.items(), key=lambda kv: -kv[1]):
            if tag in TAG_OPPOSITES and weight >= 0.5:
                opposite = TAG_OPPOSITES[tag]
                if enemy_tags.get(opposite, 0) >= 0.5:
                    weakness = self._format_tag_label(tag)
                    ability = self._format_tag_label(opposite)
                    adv_theirs.append(f"[!] They have {ability} against your {weakness}")

        # 3. Role-specific generic tips based on my own strong tags
        for my_tag, val in my_tags.items():
            if val >= 0.7 and my_tag in GENERIC_GOOD_TAGS:
                tactics.append(f"- Prioritize your {my_tag.replace('_', ' ').upper()} in this matchup.")

        # 4. What the enemy preys on
        e_best = [b.strip().capitalize() for b in enemy.get("best_against", []) if b.strip()]
        if e_best:
            tactics.append(f"- {enemy_name} usually targets: {', '.join(e_best[:3])}.")

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
            breakdown.append("TACTICS:\n- " + fallback.get(my_role, "Play your life - no specific data"))

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

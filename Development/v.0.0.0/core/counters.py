"""
Counter Database v3.0 - Fully Dynamic Tag-based System
All matchups computed from tag weights + skill rank + map phase context.
No hardcoded hero lists (best_against / counters_me removed).
"""

import json
import os

# ---------------------------------------------------------------------------
# Competitive Ranks
# ---------------------------------------------------------------------------

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

SMURF_TIER_BOOST = 3
SMURF_EMOJI = "\U0001F535"
SMURF_WARNING = "\u26A0\uFE0F"

# ---------------------------------------------------------------------------
# Skill-dependent tags
# direction="positive" = stronger at high rank
# direction="negative" = stronger at low rank
# ---------------------------------------------------------------------------

SKILL_DEPENDENT_TAGS = {
    "aim_intensive":        {"direction": "positive", "weight": 0.3},
    "high_skill_ceiling":   {"direction": "positive", "weight": 0.25},
    "sniper":               {"direction": "positive", "weight": 0.2},
    "hitscan":              {"direction": "positive", "weight": 0.15},
    "mobile":               {"direction": "negative", "weight": 0.25},
    "dive_capability":      {"direction": "negative", "weight": 0.2},
    "flank":                {"direction": "negative", "weight": 0.15},
    "escape_ability":       {"direction": "negative", "weight": 0.15},
    "game_sense_intensive": {"direction": "positive", "weight": 0.2},
    "cooldown_dependent":   {"direction": "negative", "weight": 0.15},
}

# ---------------------------------------------------------------------------
# Tag opposites: weakness → exploit ability
# ---------------------------------------------------------------------------

TAG_OPPOSITES = {
    # Mobility / positioning
    "weak_to_flank":            "flank",
    "weak_to_mobility":         "dive_capability",
    "weak_to_dive":             "dive_capability",
    # CC
    "weak_to_cc":               "crowd_control",
    # Range / aim
    "weak_to_sniper":           "sniper",
    "weak_to_poke":             "poke",
    "weak_to_ranged":           "poke",
    "weak_to_hitscan":          "hitscan",
    # Damage types
    "weak_to_burst":            "burst_damage",
    "weak_to_anti_air":         "hitscan",
    # Extended weaknesses
    "weak_to_kiting":           "mobile",
    "weak_to_grounding":        "anti_air",
    "weak_to_close_combat":     "close_combat",
    "weak_to_aoe":              "area_denial",
    "weak_to_sustained_damage": "sustained_damage",
    "weak_to_anti_flank":       "anti_flank",
    "weak_to_long_range":       "long_range",
    "weak_to_anti_heal":        "anti_healer",
    # Subrole weaknesses
    "weak_against_bruiser":      "bruiser",
    "weak_against_initiator":    "initiator",
    "weak_against_stalwart":     "stalwart",
    "weak_against_sharpshooter": "sharpshooter",
    "weak_against_flanker":      "flanker",
    "weak_against_specialist":   "specialist",
    "weak_against_recon":        "recon",
    "weak_against_tactician":    "tactician",
    "weak_against_medic":        "medic",
    "weak_against_survivor":     "survivor",
    # Contextual
    "loses_poke_duels":          "sniper",
    "cover_dependent":           "angle_denial",
    "exposed_vulnerable":        "poke",
    "struggles_vs_ranged":       "long_range",
    "vulnerable_to_kiting":      "mobile",
    "shield_reliant":            "shield_break",
    "melee_only":                "long_range",
    "struggles_vs_dive":         "dive_capability",
    "weak_vs_sustained_poke":    "sustained_damage",
    "struggles_vs_close_combat": "close_combat",
    "weak_to_hack":              "anti_flank",
    "weak_to_cleanse":           "dot_damage",
    "weak_to_projectile_absorption": "projectile",
    "weak_to_barrier":           "shield_break",
}

# Tags that are inherently advantageous regardless of matchup
GENERIC_GOOD_TAGS = {
    "healing", "peel", "anti_flank", "utility", "versatile",
    "close_quarters_dominant", "strong_cover_utilization", "high_burst_combo",
    "ally_transport", "projectile_absorption", "pick_potential_from_range",
    "dive_synergy", "zone_lockdown", "shield_break", "angle_denial",
    "tracking_ability", "invulnerability_frames", "dot_damage",
    "damage_reduction", "deflect_melee", "block_ability",
    "burst_healing", "sustained_healing",
}

# ---------------------------------------------------------------------------
# Tag-to-behavior mapping for advice generation
# Maps strong hero tags → what they naturally prey on
# ---------------------------------------------------------------------------

TAG_PREYS_ON = {
    "sniper":              "exposed / low-mobility heroes",
    "poke":                "heroes who must step into the open",
    "hitscan":             "aerial / fast-moving targets",
    "dive_capability":     "backline supports and squishy DPS",
    "flank":               "isolated supports and positional heroes",
    "burst_damage":        "low-sustain heroes caught off-guard",
    "sustained_damage":    "shield-reliant and kiting heroes",
    "close_combat":        "immobile heroes without escape tools",
    "crowd_control":       "dive heroes and ability-reliant comps",
    "area_denial":         "grouped heroes and zone-dependent setups",
    "long_range":          "short-range heroes that must close distance",
    "mobile":              "static / anchor-type heroes",
    "aim_intensive":       "heroes with predictable movement patterns",
    "high_skill_ceiling":  "heroes with exploitable cooldown windows",
    "anti_healer":         "sustain-dependent compositions",
    "dot_damage":          "heroes without cleanse options",
    "tracking_ability":    "erratic movement heroes (dive / flank)",
    "projectile_absorption":"projectile-heavy teams",
    "shield_break":        "barrier-reliant tanks and setups",
    "aerial":              "ground-bound heroes without anti-air",
    "brawl":               "poke-dependent compositions",
    "shield":              "poke and sustain heroes",
}

# Subrole descriptions
SUBROLE_INFO = {
    "bruiser":      {"role": "Tank",    "passive": "Reduces critical damage. At low HP, gain movement speed."},
    "initiator":    {"role": "Tank",    "passive": "Staying airborne lightly heals you."},
    "stalwart":     {"role": "Tank",    "passive": "Reduces knockbacks and slows received."},
    "sharpshooter": {"role": "DPS",     "passive": "Critical hits reduce movement ability cooldowns."},
    "flanker":      {"role": "DPS",     "passive": "Health packs restore more health."},
    "specialist":   {"role": "DPS",     "passive": "Eliminations briefly increase reload speed."},
    "recon":        {"role": "DPS",     "passive": "Detect enemies below half health through walls after damaging them."},
    "tactician":    {"role": "Support", "passive": "Excess ultimate charge carries over after using your ultimate."},
    "medic":        {"role": "Support", "passive": "Healing allies with your weapon also heals you."},
    "survivor":     {"role": "Support", "passive": "Using a movement ability activates passive health regeneration."},
}

MATCHUP_LABELS = {
    # Contextual weaknesses
    "loses_poke_duels":          "poke duels",
    "cover_dependent":           "cover denial",
    "exposed_vulnerable":        "exposure to poke",
    "struggles_vs_ranged":       "ranged opponents",
    "vulnerable_to_kiting":      "kiting",
    "shield_reliant":            "shield pressure",
    "melee_only":                "range advantage",
    "struggles_vs_dive":         "dive compositions",
    "weak_vs_sustained_poke":    "sustained poke",
    "struggles_vs_close_combat": "close combat",
    "weak_to_hack":              "hack vulnerability",
    "weak_to_cleanse":           "cleanse/sustain",
    "weak_to_projectile_absorption": "projectile absorption",
    "weak_to_barrier":           "barrier pressure",
    # Kit strengths
    "tracking_ability":          "tracking shots",
    "invulnerability_frames":    "invulnerability",
    "dot_damage":                "burn/dot damage",
    "damage_reduction":          "damage mitigation",
    "deflect_melee":             "melee deflection",
    "block_ability":             "block/parry",
    "burst_healing":             "burst healing",
    "sustained_healing":         "sustained healing",
    "poke_from_cover":           "poke from cover",
    "strong_cover_utilization":  "cover fights",
    "close_quarters_dominant":   "close quarters",
    "high_burst_combo":          "burst combos",
    "ally_transport":            "ally mobility",
    "projectile_absorption":     "projectile-heavy comps",
    "pick_potential_from_range": "pick potential at range",
    "dive_synergy":              "dive compositions",
    "zone_lockdown":             "zone control",
    "shield_break":              "shields",
    "angle_denial":              "angle control",
    # Weaknesses
    "weak_to_flank":             "flank pressure",
    "weak_to_mobility":          "mobile enemies",
    "weak_to_dive":              "dive compositions",
    "weak_to_cc":                "crowd control",
    "weak_to_sniper":            "snipers",
    "weak_to_poke":              "poke damage",
    "weak_to_ranged":            "ranged pressure",
    "weak_to_hitscan":           "hitscan accuracy",
    "weak_to_burst":             "burst damage",
    "weak_to_anti_air":          "anti-air",
    "weak_to_kiting":            "kiting",
    "weak_to_grounding":         "grounding effects",
    "weak_to_close_combat":      "close combat",
    "weak_to_aoe":               "AoE damage",
    "weak_to_sustained_damage":  "sustained damage",
    "weak_to_anti_flank":        "anti-flank",
    "weak_to_long_range":        "long range",
    "weak_to_anti_heal":         "anti-heal",
    # Strengths
    "sniper":              "sniper damage",
    "poke":                "poke damage",
    "hitscan":             "hitscan pressure",
    "burst_damage":        "burst damage",
    "flank":               "flank access",
    "dive_capability":     "dive potential",
    "crowd_control":       "crowd control",
    "mobile":              "mobility",
    "long_range":          "long range",
    "sustained_damage":    "sustained damage",
    "close_combat":        "close combat",
    "area_denial":         "area denial",
    "anti_flank":          "anti-flank",
    "anti_air":            "anti-air",
    # Subrole tags
    "weak_against_bruiser":      "bruiser pressure",
    "weak_against_initiator":    "initiator dive",
    "weak_against_stalwart":     "stalwart defense",
    "weak_against_sharpshooter": "sharpshooter picks",
    "weak_against_flanker":      "flank pressure",
    "weak_against_specialist":   "specialist sustained fire",
    "weak_against_recon":        "recon tracking",
    "weak_against_tactician":    "tactician ult economy",
    "weak_against_medic":        "medic sustain",
    "weak_against_survivor":     "survivor sustain",
    "strong_against_bruiser":    "bruiser counter",
    "strong_against_initiator":  "initiator counter",
    "strong_against_stalwart":   "stalwart counter",
    "strong_against_sharpshooter":"sharpshooter counter",
    "strong_against_flanker":    "flanker counter",
    "strong_against_specialist": "specialist counter",
    "strong_against_recon":      "recon counter",
    "strong_against_tactician":  "tactician counter",
    "strong_against_medic":      "medic counter",
    "strong_against_survivor":   "survivor counter",
}

# ---------------------------------------------------------------------------
# Map phase modifiers (extensible - add maps as data becomes available)
# Each phase modifies tag weights multiplicatively.
# weight > 1.0 buffs that tag, < 1.0 nerfs it.
# ---------------------------------------------------------------------------

MAP_PHASE_MODIFIERS = {
    "circuit_royale": {
        "phase_1": {
            "name": "Outside Push to First Checkpoint",
            "tags": {
                "long_range":         1.25,
                "poke":               1.20,
                "sniper":             1.20,
                "hitscan":            1.15,
                "shield_break":       1.10,
                "pick_potential_from_range": 1.15,
            },
        },
        "phase_2": {
            "name": "Checkpoint to Bank Interior",
            "tags": {
                "dive_capability":    1.25,
                "mobile":             1.20,
                "flank":              1.20,
                "burst_damage":       1.15,
                "escape_ability":     1.15,
            },
        },
        "phase_3": {
            "name": "Final Stand to Vault Door",
            "tags": {
                "close_combat":       1.30,
                "brawl":              1.25,
                "area_denial":        1.20,
                "crowd_control":      1.15,
                "close_quarters_dominant": 1.20,
                "sustained_damage":   1.15,
            },
        },
    },
}

# Map aliases (so UI can reference maps by different keys)
MAP_ALIASES = {
    "circuitroyal": "circuit_royale",
    "circuit_royale": "circuit_royale",
    "cr": "circuit_royale",
}


class CounterDB:
    _instance = None
    _heroes = None
    _roles = None
    _rank = DEFAULT_RANK
    _smurf_suspected = False
    _current_map = None
    _current_phase = None

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

    def get_subrole(self, hero):
        data = self.get_hero_data(hero)
        return data.get("subrole", "unknown")

    def set_rank(self, rank):
        if rank in RANK_INFO:
            self._rank = rank

    def get_rank(self):
        return self._rank

    def set_smurf(self, suspected):
        self._smurf_suspected = suspected

    def get_smurf(self):
        return self._smurf_suspected

    def set_map(self, map_key=None, phase=None):
        """Set current map and optional phase for context-aware scoring."""
        if not map_key:
            self._current_map = None
            self._current_phase = None
            return
        normalized = MAP_ALIASES.get(map_key.lower(), map_key.lower())
        if normalized in MAP_PHASE_MODIFIERS:
            self._current_map = normalized
            if phase and phase in MAP_PHASE_MODIFIERS[normalized]:
                self._current_phase = phase
            else:
                self._current_phase = None
        else:
            self._current_map = None
            self._current_phase = None

    def get_map_info(self):
        """Return current map/phase display info."""
        if not self._current_map:
            return None
        info = {"map": self._current_map.replace("_", " ").title()}
        if self._current_phase:
            phase_data = MAP_PHASE_MODIFIERS[self._current_map][self._current_phase]
            info["phase"] = phase_data["name"]
            info["phase_key"] = self._current_phase
        return info

    def _get_skill_modifier(self, hero, rank_override=None):
        """
        Multiplier based on skill-dependent tags and rank.
        > 1.0 = hero benefits at this rank
        < 1.0 = hero is disadvantaged
        """
        hero_data = self.get_hero_data(hero)
        tags = hero_data.get("tags", {})
        effective_rank = rank_override if rank_override else self._rank
        rank_tier = RANK_INFO[effective_rank]["tier"]
        max_tier = len(RANK_ORDER) - 1

        modifier = 1.0
        for tag, info in SKILL_DEPENDENT_TAGS.items():
            if tag not in tags:
                continue
            tag_weight = tags[tag]
            direction = info["direction"]
            strength = info["weight"]

            if direction == "positive":
                rank_factor = 0.7 + (0.6 * rank_tier / max_tier)
            else:
                rank_factor = 1.3 - (0.6 * rank_tier / max_tier)

            modifier += tag_weight * strength * (rank_factor - 1.0)

        return modifier

    def _get_enemy_rank(self):
        lobby_rank = self._rank
        if self._smurf_suspected:
            boosted_tier = min(RANK_INFO[lobby_rank]["tier"] + SMURF_TIER_BOOST, len(RANK_ORDER) - 1)
            return RANK_ORDER[boosted_tier]
        return lobby_rank

    def _get_tag_modifiers(self):
        """Return tag weight multipliers from current map phase, if any."""
        if not self._current_map or not self._current_phase:
            return {}
        try:
            return MAP_PHASE_MODIFIERS[self._current_map][self._current_phase].get("tags", {})
        except KeyError:
            return {}

    # ------------------------------------------------------------------
    # Core scoring - purely tag-driven
    # ------------------------------------------------------------------

    def _score_counter(self, enemy_hero, my_hero):
        """
        Numeric score (higher = better counter).
        Computed entirely from enemy weakness tags matched against
        player hero's exploitation tags, scaled by skill rank and map.
        """
        enemy = self.get_hero_data(enemy_hero)
        my_data = self.get_hero_data(my_hero)
        if not enemy or not my_data:
            return 0.0

        enemy_tags = enemy.get("tags", {})
        my_tags = my_data.get("tags", {})
        tag_mods = self._get_tag_modifiers()

        # Enemy skill → how well they mitigate weaknesses
        enemy_rank = self._get_enemy_rank()
        enemy_skill = self._get_skill_modifier(enemy_hero, rank_override=enemy_rank)
        enemy_weakness_mod = 2.0 - enemy_skill

        if self._smurf_suspected:
            enemy_weakness_mod *= 0.75

        # My skill → how well I exploit weaknesses
        my_mod = self._get_skill_modifier(my_hero)

        score = 0.0
        for tag, weight in enemy_tags.items():
            if tag not in TAG_OPPOSITES:
                continue
            opposite = TAG_OPPOSITES[tag]
            my_val = my_tags.get(opposite, 0.0)
            if my_val <= 0:
                continue

            effective_weakness = weight * enemy_weakness_mod

            # Apply map phase modifier if this tag is affected
            map_mult = tag_mods.get(opposite, 1.0)

            score += effective_weakness * (my_val * my_mod) * map_mult

        return score

    # ------------------------------------------------------------------
    # Dynamic matchup computation (replaces hardcoded lists)
    # ------------------------------------------------------------------

    def compute_matchups(self, hero, limit=5):
        """
        Compute both best counters (heroes that beat `hero`)
        and best targets (heroes that `hero` beats) dynamically.

        Returns:
            {
                "counters_me": [{"hero": "x", "score": 3.2}, ...],
                "best_against": [{"hero": "y", "score": 2.8}, ...],
            }
        """
        all_heroes = list(self._heroes.keys())

        # Counters: heroes that beat `hero` (high counter score when playing THEM vs hero)
        counters = []
        for candidate in all_heroes:
            if candidate == hero:
                continue
            score = self._score_counter(hero, candidate)
            if score > 0:
                counters.append({"hero": candidate, "score": round(score, 2)})
        counters.sort(key=lambda x: -x["score"])

        # Best against: heroes that `hero` beats
        # (high counter score when playing `hero` vs THEM)
        best_against = []
        for candidate in all_heroes:
            if candidate == hero:
                continue
            score = self._score_counter(candidate, hero)
            if score > 0:
                best_against.append({"hero": candidate, "score": round(score, 2)})
        best_against.sort(key=lambda x: -x["score"])

        return {
            "counters_me": counters[:limit],
            "best_against": best_against[:limit],
        }

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
        if tag in MATCHUP_LABELS:
            return MATCHUP_LABELS[tag]
        return tag.replace("weak_to_", "").replace("weak_against_", "").replace("_", " ")

    def _infer_enemy_targets(self, enemy_hero, enemy):
        """
        Derive what type of heroes this enemy preys on from their tags.
        Replaces the old hardcoded best_against list.
        """
        tags = enemy.get("tags", {})
        targets = []
        for tag, val in sorted(tags.items(), key=lambda kv: -kv[1]):
            if tag in TAG_PREYS_ON and val >= 0.6:
                targets.append(TAG_PREYS_ON[tag])
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for t in targets:
            if t not in seen:
                seen.add(t)
                unique.append(t)
        return unique[:3]

    def _generate_advice(self, enemy_hero, enemy, my_data, my_role):
        enemy_tags = enemy.get("tags", {})
        my_tags = my_data.get("tags", {})
        enemy_name = enemy.get("name", enemy_hero.capitalize())

        adv_yours = []
        adv_theirs = []
        tactics = []

        # 1. Your hero exploits enemy weaknesses
        seen_advantages = set()
        for tag, weight in sorted(enemy_tags.items(), key=lambda kv: -kv[1]):
            if tag in TAG_OPPOSITES and weight >= 0.5:
                opposite = TAG_OPPOSITES[tag]
                if my_tags.get(opposite, 0) >= 0.5:
                    weakness = self._format_tag_label(tag)
                    ability = self._format_tag_label(opposite)
                    label = f"_{ability}__{weakness}"
                    if label not in seen_advantages:
                        seen_advantages.add(label)
                        adv_yours.append(f"[+] You have {ability} against their {weakness}")

        # 2. Enemy exploits your weaknesses
        seen_threats = set()
        for tag, weight in sorted(my_tags.items(), key=lambda kv: -kv[1]):
            if tag in TAG_OPPOSITES and weight >= 0.5:
                opposite = TAG_OPPOSITES[tag]
                if enemy_tags.get(opposite, 0) >= 0.5:
                    weakness = self._format_tag_label(tag)
                    ability = self._format_tag_label(opposite)
                    label = f"_{ability}__{weakness}"
                    if label not in seen_threats:
                        seen_threats.add(label)
                        adv_theirs.append(f"[!] They have {ability} against your {weakness}")

        # 3. Role-specific tips from strong generic tags
        for my_tag, val in my_tags.items():
            if val >= 0.7 and my_tag in GENERIC_GOOD_TAGS:
                tactics.append(f"- Prioritize your {my_tag.replace('_', ' ').upper()} in this matchup.")

        # 4. Dynamic: what this enemy type preys on (derived from tags)
        prey_types = self._infer_enemy_targets(enemy_hero, enemy)
        if prey_types:
            tactics.append(f"- {enemy_name} typically preys on: {'; '.join(prey_types)}.")

        # 5. Map phase context (if active)
        map_info = self.get_map_info()
        if map_info:
            tactics.append(f"- Map: {map_info['map']}")
            if "phase" in map_info:
                tactics.append(f"  Phase: {map_info['phase']}")

        # Format
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
        """Top counter-picks for enemy_hero, sorted by score."""
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
        """All heroes of my_role sorted by counter score vs enemy_hero."""
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
        """Best hero of same role to switch to."""
        my_role = self.get_role(current_hero)
        role_counters = self.get_role_counters(enemy_hero, my_role)
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
# Module-level wrappers
# ---------------------------------------------------------------------------

def get_counter(enemy_hero, my_hero):
    return CounterDB().get_counter(enemy_hero, my_hero)


def get_role_counters(enemy_hero, my_role):
    return CounterDB().get_role_counters(enemy_hero, my_role)


def get_recommended_switch(enemy_hero, current_hero):
    return CounterDB().get_recommended_switch(enemy_hero, current_hero)


if __name__ == "__main__":
    print("Testing CounterDB v3.0...")
    db = CounterDB()

    print(f"\nTotal heroes: {len(db._heroes)}")

    print("\n--- Dynamic matchups: Widowmaker ---")
    matchups = db.compute_matchups("widowmaker", 5)
    print("Counters me (who beats Widow):")
    for c in matchups["counters_me"]:
        print(f"  {c['hero']} (score={c['score']:.2f})")
    print("Best against (who Widow beats):")
    for c in matchups["best_against"]:
        print(f"  {c['hero']} (score={c['score']:.2f})")

    print("\n--- Dynamic matchups: Hazard ---")
    matchups = db.compute_matchups("hazard", 5)
    print("Counters me:")
    for c in matchups["counters_me"]:
        print(f"  {c['hero']} (score={c['score']:.2f})")
    print("Best against:")
    for c in matchups["best_against"]:
        print(f"  {c['hero']} (score={c['score']:.2f})")

    print("\n--- Advice: Tracer vs Domina ---")
    r = db.get_counter("domina", "tracer")
    print(f"Score: {r['score']:.2f}")
    print(r["reason"])

    print("\n--- Map context: Circuit Royale Phase 3 vs Widowmaker ---")
    db.set_map("circuit_royale", "phase_3")
    for c in db.get_all_counters("widowmaker", 5):
        print(f"  {c['hero']} (score={c['score']:.2f})")
    db.set_map(None)

    print("\n--- Top counters vs Vendetta ---")
    for c in db.get_all_counters("vendetta", 5):
        print(f"  {c['hero']} (score={c['score']:.2f})")

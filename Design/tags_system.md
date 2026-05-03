# OW One Trick Counter - Global Tags System
# Version: 1.0
# Purpose: Universal tag framework for hero profiling

================================================================================
TAG CATEGORIES
================================================================================

## 1. MOBILITY (how hero moves)
─────────────────────────────────────────────
mobile           : High mobility, many movement abilities
dive_capability   : Can dive enemy backline
escape_ability   : Has escape/blink abilities
fast_movement    : Moves faster than average
aerial          : Can fly/be airborne
vertical        : Uses vertical space well
wall_climb      : Can climb walls

## 2. DAMAGE TYPE
─────────────────────────────────────────────
burst_damage     : High burst potential
sustained_damage: Continuous damage output
poke           : Long range poking
close_combat    : Close range combat
one_shot       : Can one-shot enemies
spam           : Area denial/spam damage
hitscan        : Hitscan weapons
projectile     : Projectile weapons
hybrid_damage  : Both hitscan and projectile

## 3. UTILITY
─────────────────────────────────────────────
crowd_control   : CC abilities (stun, freeze, root, slow)
shield        : Provides shields to allies
healing       : Can heal allies
damage_boost  : Increases ally damage
utility      : General utility
debuff        : Applies debuffs to enemies
reveal        : Can reveal invisible/hidden enemies
mobility_boost : Speed boost to allies

## 4. DEFENSE
─────────────────────────────────────────────
tanky          : High HP/armor
fortify        : Damage mitigation
invulnerability: Invulnerability frames
peel          : Can protect teammates
intercept     : Can counter dives
self_heal      : Self healing capability

## 5. ROLE CATEGORIES
─────────────────────────────────────────────
main_support   : Primary healer
off_support   : Off healer/secondary support
main_tank    : Main tank (anchor)
off_tank     : Off tank
hitscan_dps   : Hitscan DPS
projectile_dps: Projectile DPS
flank_dps    : Flanker DPS
sniper_dps   : Sniper DPS
brawl_dps    : Brawl/dive DPS

## 6. PLAYSTYLE
─────────────────────────────────────────────
poke_playstyle     : Poke comp style
brawl_playstyle   : Brawl comp style
dive_playstyle   : Dive comp style
sniper_playstyle  : Sniper comp style
pocket_playstyle : Can pocket ally
teamfight_playstyle: Teamfight focused
sniper          : Long range engagements

## 7. COUNTER TAGS (what they counter)
─────────────────────────────────────────────
anti_dive        : Counters dive heroes
anti_flank      : Counters flankers
anti_sniper    : Counters snipers
anti_mobility  : Counters mobile heroes
anti_healer   : Pressure healers
anti_dive      : Counters dive
anti_trap      : Counters traps

## 8. SKILL REQUIREMENTS (rank weighting)
─────────────────────────────────────────────
aim_intensive    : Requires good aim
game_sense_intensive: Requires game sense
mechanic_intensive: Requires mechanics
beginner_friendly: Good for beginners
low_effort     : Easy to play effectively
high_skill_ceiling: High skill cap

## 9. WEAKNESSES (what they struggle against)
─────────────────────────────────────────────
weak_to_sniper    : Vulnerable to snipers
weak_to_mobility : Vulnerable to mobile
weak_to_cc      : Vulnerable to CC
weak_to_burst   : Vulnerable to burst
no_self_defense : No self defense

## 10. SPECIAL TAGS
─────────────────────────────────────────────
ultimate_stomp   : High team fight ultimate
game_changer  : Ultimate swings fights
comp_specific : Comp specific viability
low_rank_strong: Performs well in low ranks
high_rank_strong: Performs well in high ranks
all_rank_viable: Viable in all ranks

================================================================================
TAG WEIGHT VALUE REFERENCE
================================================================================

Values: 0.0 to 1.0
- 0.0 = None (hero doesn't have this trait)
- 0.3 = Low amount
- 0.5 = Medium amount
- 0.7 = High amount
- 1.0 = Core identity (fundamental to hero)

Example hero tag entry:
{
  "hero": "widowmaker",
  "tags": {
    "sniper": 1.0,
    "one_shot": 0.8,
    "aim_intensive": 0.9,
    "mobile": 0.2,
    "poke": 0.8,
    ...
  },
  "hard_counters": ["winston", "genji"],
  "soft_counters": ["tracer", "sombra"],
  "counters_me": ["ashe", "cassidy"]
}

================================================================================
COUNTER LOGIC
================================================================================

Matching Algorithm:

1. Calculate DIFFERENCE SCORE between enemy_tag and my_tag:
   score = 0
   if enemy.tag == "mobile" and my.tag == "anti_mobile": score += 0.5
   if enemy.tag == "dive" and my.tag == "anti_dive": score += 0.5
   etc.

2. WEIGHT BY ROLE:
   - If I'm Support and enemy is flanker: prioritize peel/anti_flank
   - If I'm Tank and enemy is sniper: prioritize anti_sniper/cover
   - If I'm DPS and enemy is one_trick: prioritize counterpick

3. RECOMMENDATION OUTPUT:
   - Primary counter: highest difference score
   - Role-specific: filter by my role's counters
   - Fallback: use hard/soft counter list

================================================================================
NEW HERO PROCESS
================================================================================

To add new hero:
1. Create hero_hero.json in data/heroes/
2. Fill tag weights (0.0-1.0)
3. List hard/soft counters
4. Update global list in heroes_index.json
5. Auto-added to system

Recommended tag minimums per hero:
- At least 3 tags with weight >= 0.5
- At least 1 weakness
- At least 2 hard_counters
- At least 2 heroes that counter you
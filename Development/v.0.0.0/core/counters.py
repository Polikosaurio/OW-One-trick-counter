"""
Counter Database
Hero-to-hero counter relationships
"""

COUNTERS = {
    "widowmaker": {
        "reason": "Best flankers to avoid her sight lines",
        "best": ["winston", "tracer", "genji", "sombra"],
        "dps": {
            "tracer": "Flank and secure 1-tap after blinks",
            "genji": "Dash reflect + deflect to close gap",
            "reaper": "Corner PEEL to approach unseen",
            "soldier76": "Sustained damage forces reposition"
        },
        "tank": {
            "winston": "Jump from cover, bubble blocks aim",
            "dva": "Rocket boost to close, matrix absorbs"
        },
        "support": {
            "lucio": "Speed to reposition safely",
            "kiriko": "Suzu escapes dive"
        }
    },
    "tracer": {
        "reason": "Squishy with low HP - focus fire wins",
        "best": ["torbjorn", "symmetra", "sombra", "cassidy"],
        "dps": {
            "cassidy": "Magnetic grenade guarantees kill",
            "torbjorn": "Turret deters recall path",
            "symmetra": "Teleporter blocks exits",
            "widowmaker": "Prefire corners"
        },
        "tank": {
            "zarya": "Beam outdamages recall"
        },
        "support": {
            "moira": "Fade escapes + consistent damage",
            "kiriko": "Headshot timing"
        }
    },
    "genji": {
        "reason": "Deflect punishes poor aim, dash escapes",
        "best": ["moira", " symmetra", "zarya", "mei"],
        "dps": {
            "mei": "Freeze negates deflect",
            "symmetra": "Wall blocks blade paths",
            "hanzo": "Storm arrows punish dash"
        },
        "tank": {
            "zarya": "Beam damage outpaces deflect",
            "dva": "Matrix absorbs dragonblade"
        },
        "support": {
            "moira": "Sustained damage beats deflect"
        }
    },
    "hanzo": {
        "reason": "Storm bow punishes positioning",
        "best": ["winston", "sombra", "tracer"],
        "dps": {
            "tracer": "Fast blink to close during storm",
            "sombra": "Hack prevents storm",
            "genji": "Deflect reflects storm"
        },
        "tank": {
            "winston": "Jump avoids storm, melee kills",
            "dva": "Matrix absorbs scatter"
        },
        "support": {
            "lucio": "Speed beats scatter"
        }
    },
    "junkrat": {
        "reason": "Spam damage punishes static targets",
        "best": ["pharah", "dva", "zarya", "sombra"],
        "dps": {
            "pharah": "Aerial approach avoids spam",
            "cassidy": "Quick 1-tap from range"
        },
        "tank": {
            "dva": "Matrix absorbs riptire",
            "zarya": "Bubble blocks spam"
        },
        "support": {
            "kiriko": "Suzu blocks explode",
            "baptiste": "Window outranges"
        }
    },
    "reaper": {
        "reason": "Shotgun close-range melt",
        "best": ["mcree", "cassidy", "sombra", "tracer", " Ashe"],
        "dps": {
            "cassidy": "Flashbang into 1-tap",
            "ashe": "Coach gun knockback",
            "sombra": "Hack prevents wraith"
        },
        "tank": {
            "zarya": "Bubble blocks wraith exit",
            "dva": "Matrix absorbs shotgun"
        },
        "support": {
            "moira": "Fade escapes shadow step",
            "kiriko": "Protection Suzu"
        }
    },
    "mcree": {
        "reason": "High accuracy punishes positioning",
        "best": ["sombra", "tracer", "genji", "winston"],
        "dps": {
            "sombra": "Hack prevents roll",
            "tracer": "Fast flank avoids aim",
            "genji": "Deflect punishes missed"
        },
        "tank": {
            "winston": "Jump from cover",
            "dva": "Boost to close gap"
        },
        "support": {
            "kiriko": "Suzu for burst save",
            "lucio": "Speed beats roll"
        }
    },
    "ashe": {
        "reason": "Scoped headshot potential",
        "best": ["sombra", "winston", "tracer", "genji"],
        "dps": {
            "sombra": "Hack prevents coach gun",
            "tracer": "Fast blink to close",
            "genji": "Deflect reflects shots"
        },
        "tank": {
            "winston": "Jump in without scope",
            "dva": "Boost closes range"
        },
        "support": {
            "lucio": "Speed to reposition",
            "kiriko": "Suzu saves from snipe"
        }
    },
    "pharah": {
        "reason": "Aerial spam without regard",
        "best": ["hitscan", "Widowmaker", "bastion", "ashe", "soldier76"],
        "dps": {
            "soldier76": "Consistent hitscan",
            "bastion": "Turret shreds rockets",
            "ashe": "Scope punishes flight"
        },
        "tank": {
            "zarya": "Graviton ends flight"
        },
        "support": {
            "ana": "Anti-air scoped shots"
        }
    },
    "soldier76": {
        "reason": "Consistent mid-range damage",
        "best": ["genji", "tracer", "sombra", "winston"],
        "dps": {
            "genji": "Deflect reflects visor",
            "tracer": "Blink past visor",
            "sombra": "Hack during visor"
        },
        "tank": {
            "winston": "Jump close to cancel visor",
            "dva": "Boost to close gap"
        },
        "support": {
            "moira": "Fade escapes visor",
            "kiriko": "Suzu saves from visor"
        }
    },
    "sombra": {
        "reason": "Hack disruption and health pack control",
        "best": ["symmetra", "torbjorn", "sombra", "cassidy"],
        "dps": {
            "cassidy": "EMP beats stealth",
            "sombra": "Counter-hack war",
            "symmetra": "Hacked turrets help"
        },
        "tank": {
            "zarya": "Bubble blocks hack",
            "dva": "Matrix absorbs EMP"
        },
        "support": {
            "kiriko": "Protection from hack",
            "lifeweaver": "Off-angle healing"
        }
    },
    "symmetra": {
        "reason": "Area denial with portal/turret",
        "best": ["dva", "winston", "pharah", "tracer"],
        "dps": {
            "dva": "Boost to destroy TP",
            "winston": "Jump to reach portal",
            "pharah": "Fly over turret field"
        },
        "tank": {
            "winston": "Barrier blocks turret damage",
            "dva": "Boost and matrix"
        },
        "support": {
            "kiriko": "Swift step teleports"
        }
    },
    "torbjorn": {
        "reason": "Turret adds unexpected damage",
        "best": ["dva", "winston", "genji", "sombra"],
        "dps": {
            "dva": "Boost to destroy turret",
            "winston": "Jump in to smash turret",
            "genji": "Reflect turret shots"
        },
        "tank": {
            "dva": "Matrix absorbs turret",
            "winston": "Zap turret and enemy"
        },
        "support": {
            "kiriko": "Protection from overload"
        }
    },
    "bastion": {
        "reason": "Turret mode melt potential",
        "best": ["sombra", "winston", "dva", "zarya", "pharah"],
        "dps": {
            "sombra": "Hack prevents turret",
            "pharah": "Fly over and spam",
            "genji": "Reflect in sentry"
        },
        "tank": {
            "winston": "Zap before turret kills",
            "zarya": "Graviton shuts down"
        },
        "support": {
            "ana": "Antiheal punishes config"
        }
    },
    "mei": {
        "reason": "Freeze and wall isolation",
        "best": ["genji", "tracer", "sombra", "pharah"],
        "dps": {
            "genji": "Deflect blocks freeze",
            "pharah": "Fly over wall",
            "tracer": "Fast blink escapes"
        },
        "tank": {
            "zarya": "Bubble blocks freeze",
            "winston": "Zap to keep warm"
        },
        "support": {
            "baptiste": "Window to escape",
            "moira": "Fade escapes wall"
        }
    },
    "dt": {
        "reason": "Apex predator - mobility + damage",
        "best": ["zarya", "roadhog", "dva", "winston", "symmetra"],
        "dps": {
            "zarya": "Bubble blocks matrix exit",
            "roadhog": "Hook punishes boost"
        },
        "tank": {
            "zarya": "Graviton catches boosters",
            "roadhog": "Hook punishes overcommit",
            "dva": "Boost to escape"
        },
        "support": {
            "lucio": "Speed boost to outrun"
        }
    },
    "orisa": {
        "reason": "Static anchor with fortify",
        "best": ["sombra", "tracer", "genji", "winston"],
        "dps": {
            "sombra": "Hack disables fortify",
            "tracer": "Blink to avoid fortify",
            "genji": "Deflect javelin"
        },
        "tank": {
            "zarya": "Grav ends anchor",
            "sigma": "Shield blocks javelin"
        },
        "support": {
            "kiriko": "Suzu for burst"
        }
    },
    "reinhardt": {
        "reason": "Aggressive swing and charge",
        "best": ["sombra", "reaper", "moira", "pharah"],
        "dps": {
            "sombra": "Hack prevents charge",
            "reaper": "Shotgun melt",
            "pharah": "Fly over swing"
        },
        "tank": {
            "zarya": "Graviton after firestrike",
            "sigma": "Accretion knock down"
        },
        "support": {
            "moira": "Fade escapes charge",
            "ana": "Antiheal after pin"
        }
    },
    "zarya": {
        "reason": "Graviton team wipe potential",
        "best": ["dva", "winston", "sombra", "genji"],
        "dps": {
            "dva": "Matrix saves team from grav",
            "winston": "Jump to escape grav",
            "genji": "Deflect reflects grav"
        },
        "tank": {
            "dva": "Matrix blocks grav",
            "winston": "Jump out of grav"
        },
        "support": {
            "zenyatta": "Transcendence outheals"
        }
    },
    "roadhog": {
        "reason": "1-tap hook combo",
        "best": ["zarya", "dva", "winston", "ashe"],
        "dps": {
            "zarya": "Bubble blocks hook",
            "dva": "Matrix prevents kill",
            "ashe": "Quick 2-tap"
        },
        "tank": {
            "dva": "Matrix saves from combo",
            "zarya": "Bubble blocks hook"
        },
        "support": {
            "baptiste": "Immortality Field saves"
        }
    },
    "winston": {
        "reason": "Dive isolations and primal",
        "best": ["mcree", "cassidy", "reaper", "mei"],
        "dps": {
            "reaper": "Shotgun melt",
            "mei": "Freeze during primal",
            "cassidy": "Flashbang punishes dive"
        },
        "tank": {
            "zarya": "Particle beam melts",
            "sigma": "Barrier to block leap"
        },
        "support": {
            "ana": "Antiheal punishes Primal Rage"
        }
    },
    "wreckingball": {
        "reason": "Mobile pile driver dives",
        "best": ["zarya", "sigma", "mcree", "cassidy"],
        "dps": {
            "zarya": "Particle beam builds charge",
            "cassidy": "Flashbang before piledriver",
            "mcree": "Rolled stun stops piledriver"
        },
        "tank": {
            "zarya": "Graviton ends mobility",
            "sigma": "Shield blocks piledriver"
        },
        "support": {
            "kiriko": "Suzu saves from piledriver"
        }
    },
    "sigma": {
        "reason": "Singularity and shield manipulation",
        "best": ["winston", "dva", "genji", "tracer"],
        "dps": {
            "winston": "Jump over accretion",
            "dva": "Boost to destroy shield",
            "genji": "Deflect singularity"
        },
        "tank": {
            "dva": "Matrix absorbs accretion",
            "winston": "Jump to escape"
        },
        "support": {
            "kiriko": "Suzu for recovery"
        }
    },
    "ramattra": {
        "reason": "Pummel rush and vortex",
        "best": ["dva", "zarya", "genji", "tracer"],
        "dps": {
            "dva": "Matrix blocks pummel",
            "zarya": "Graviton after vortex",
            "genji": "Deflect pummel"
        },
        "tank": {
            "dva": "Matrix stops rush",
            "zarya": "Grav ends vortex"
        },
        "support": {
            "kiriko": "Suzu blocks vortex"
        }
    },
    "ana": {
        "reason": "Antiheal and snipe impact",
        "best": ["genji", "tracer", "dva", "winston"],
        "dps": {
            "genji": "Deflect returns anti",
            "tracer": "Blink to avoid snipe",
            "dva": "Matrix blocks shots"
        },
        "tank": {
            "winston": "Jump to avoid snipe",
            "dva": "Matrix saves team"
        },
        "support": {
            "kiriko": "Protection from anti"
        }
    },
    "moira": {
        "reason": "Sustained healing and escape",
        "best": ["cassidy", "sombra", "genji", "zarya"],
        "dps": {
            "cassidy": "Flashbang interrupts heal",
            "sombra": "Hack prevents fade",
            "genji": "Deflect for surprise"
        },
        "tank": {
            "zarya": "Beam damage outpaces heal",
            "sigma": "Accretion interrupts"
        },
        "support": {
            "ana": "Anti-heal stops healing"
        }
    },
    "mercy": {
        "reason": "pocket healing and rez",
        "best": ["sombra", "pharah", "dva", "widowmaker"],
        "dps": {
            "sombra": "Hack disables GA",
            "pharah": "Pocket snipe",
            "dva": "Sniper deny rez"
        },
        "tank": {
            "zarya": "Graviton counters rez",
            "sigma": "Shield to block"
        },
        "support": {
            "ana": "Antiheal punishes heal"
        }
    },
    "lucio": {
        "reason": "Speed boost and boop",
        "best": ["winston", "dva", "zarya", "ashe"],
        "dps": {
            "zarya": "Graviton counts speed",
            "ashe": "Quick damage"
        },
        "tank": {
            "zarya": "Particle outranges boop",
            "dva": "Matrix blocks boop"
        },
        "support": {
            "ana": "Anti-heal from range"
        }
    },
    "zenyatta": {
        "reason": "Discord global focus target",
        "best": ["sombra", "tracer", "genji", "winston"],
        "dps": {
            "sombra": "Hack disables orb",
            "tracer": "Fast target priority",
            "genji": "Deflect returns orb"
        },
        "tank": {
            "winston": "Jump to close gap",
            "dva": "Matrix to block orb"
        },
        "support": {
            "baptiste": "Immortality negates orb"
        }
    },
    "baptiste": {
        "reason": "Strong AOE healing and immortality",
        "best": ["sombra", "pharah", "zarya", "widowmaker"],
        "dps": {
            "sombra": "Hack disables field",
            "pharah": "Aerial pressure",
            "widowmaker": "Quick snipe"
        },
        "tank": {
            "zarya": "Graviton ends field",
            "sigma": "Accretion knocks"
        },
        "support": {
            "ana": "Anti-heal punishes immortality"
        }
    },
    "brigitte": {
        "reason": "Rally armor and shield bash",
        "best": ["tracer", "pharah", "sombra", "widowmaker"],
        "dps": {
            "tracer": "Fast dive escapes",
            "pharah": "Fly over armor",
            "widowmaker": "Quick snipe"
        },
        "tank": {
            "zarya": "Beam over shield",
            "sigma": "Shield blocks bash"
        },
        "support": {
            "ana": "Anti-heal beats rally"
        }
    },
    "kiriko": {
        "reason": "Mobility and protection",
        "best": ["sombra", "widowmaker", "genji", "tracer"],
        "dps": {
            "sombra": "Hack prevents dash",
            "widowmaker": "Quick snipe",
            "genji": "Deflect timing"
        },
        "tank": {
            "zarya": "Graviton punishes dash",
            "dva": "Matrix to block kitsune"
        },
        "support": {
            "ana": "Anti-heal punishes suzu"
        }
    },
    "lifeweaver": {
        "reason": "Tree healing and pull",
        "best": ["sombra", "widowmaker", "genji", "tracer"],
        "dps": {
            "sombra": "Hack disables pull",
            "widowmaker": "Quick snipe",
            "tracer": "Fast dive target"
        },
        "tank": {
            "zarya": "Graviton ends tree",
            "roadhog": "Hook to cancel"
        },
        "support": {
            "ana": "Anti-heal punishes tree"
        }
    },
    "illari": {
        "reason": "Sniper healer with pylon",
        "best": ["sombra", "genji", "tracer", "widowmaker"],
        "dps": {
            "sombra": "Hack disables pylon",
            "widowmaker": "Outsnipe",
            "genji": "Deflect timing"
        },
        "tank": {
            "zarya": "Beam over shield",
            "dva": "Matrix to block pylon"
        },
        "support": {
            "ana": "Anti-heal beats ultimate"
        }
    },
    "juno": {
        "reason": "Mobility orb and ring accelerator",
        "best": ["sombra", "widowmaker", "genji", "tracer"],
        "dps": {
            "sombra": "Hack disables dash",
            "widowmaker": "Quick snipe",
            "genji": "Deflect returns"
        },
        "tank": {
            "zarya": "Graviton after dash",
            "dva": "Matrix to block orbital"
        },
        "support": {
            "ana": "Anti-heal from range"
        }
    },
    "venture": {
        "reason": "Mobility and unyielding",
        "best": ["sombra", "dva", "roadhog", "zarya"],
        "dps": {
            "sombra": "Hack disables dash",
            "roadhog": "Hook punishes overextend"
        },
        "tank": {
            "zarya": "Graviton counters dash",
            "dva": "Matrix to survive"
        },
        "support": {
            "kiriko": "Suzu blocks unyielding"
        }
    },
    "cassidy": {
        "reason": "Magnetic grenade 1-tap",
        "best": ["sombra", "genji", "tracer", "winston"],
        "dps": {
            "sombra": "Hack prevents roll",
            "genji": "Deflect punishes miss",
            "tracer": "Fast blink away"
        },
        "tank": {
            "winston": "Jump from cover",
            "dva": "Matrix blocks rolls"
        },
        "support": {
            "kiriko": "Suzu for protection"
        }
    },
    "sojourn": {
        "reason": "Railgun charge spam",
        "best": ["sombra", "genji", "dva", "winston"],
        "dps": {
            "sombra": "Hack slows charge",
            "genji": "Deflect returns",
            "dva": "Matrix to block rail"
        },
        "tank": {
            "winston": "Jump to close gap",
            "dva": "Boost to escape rail"
        },
        "support": {
            "kiriko": "Suzu blocks one-shot"
        }
    },
    "echo": {
        "reason": "Duplicate and beam focus",
        "best": ["sombra", "widowmaker", "zarya", "winston"],
        "dps": {
            "sombra": "Hack disables duplicate",
            "widowmaker": "Quick snipe duplicate",
            "zarya": "Graviton after duplicate"
        },
        "tank": {
            "zarya": "Graviton ends flight",
            "dva": "Matrix blocks flight"
        },
        "support": {
            "baptiste": "Immortality Field counters"
        }
    },
    "mauga": {
        "reason": "Melt potential and OVERDRIVE",
        "best": ["sombra", "zarya", "roadhog", "dva"],
        "dps": {
            "sombra": "Hack disables overdrive",
            "roadhog": "Hook punishes overdrive",
            "zarya": "Graviton after overdrive"
        },
        "tank": {
            "zarya": "Bubble blocks overdrive",
            "dva": "Matrix to block"
        },
        "support": {
            "kiriko": "Suzu for recovery"
        }
    },
    "junkerqueen": {
        "reason": "Sustain and commandqueue",
        "best": ["sombra", "zarya", "roadhog", "dva"],
        "dps": {
            "sombra": "Hack prevents shout",
            "roadhog": "Hook punishes command",
            "zarya": "Graviton after shout"
        },
        "tank": {
            "zarya": "Bubble blocks command",
            "dva": "Matrix to block"
        },
        "support": {
            "baptiste": "Window counters shout"
        }
    },
    " widowmaker": { "_note": "Uses same data as widowmaker" },
    "windowmaker": { "_note": "Uses same data as widowmaker" },
    "freja": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "mizuki": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "emre": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "anran": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "sierra": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "jetpackcat": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "wuyang": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "domina": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "vendetta": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    },
    "hazard": {
        "reason": "New hero - requires testing",
        "best": ["dva", "winston", "zarya", "genji"]
    }
}


class CounterDB:
    @staticmethod
    def get_counter(enemy_hero, your_hero):
        """Get counter for specific matchup"""
        from gui.hero_selector import get_hero_role
        
        if enemy_hero not in COUNTERS:
            return None
        
        enemy_data = COUNTERS[enemy_hero]
        your_role = get_hero_role(your_hero)
        
        if not your_role:
            return None
        
        if your_role in enemy_data and your_hero in enemy_data[your_role]:
            return {
                "hero": your_hero,
                "reason": enemy_data[your_role][your_hero]
            }
        
        best = enemy_data.get("best", [])
        if your_hero in best:
            return {
                "hero": your_hero,
                "reason": enemy_data.get("reason", "")
            }
        
        return None
    
    @staticmethod
    def get_all_counters(enemy_hero, limit=5):
        """Get all counters for enemy hero"""
        if enemy_hero not in COUNTERS:
            return []
        
        enemy_data = COUNTERS[enemy_hero]
        counters = []
        reason = enemy_data.get("reason", "")
        
        for role, role_counters in enemy_data.items():
            if role in ["dps", "tank", "support"]:
                for hero, advice in role_counters.items():
                    counters.append({
                        "hero": hero,
                        "role": role,
                        "reason": advice
                    })
        
        return counters[:limit]
    
    @staticmethod
    def get_counter_by_role(enemy_hero, role, limit=3):
        """Get counters by role"""
        if enemy_hero not in COUNTERS:
            return []
        
        enemy_data = COUNTERS[enemy_hero]
        counters = []
        
        if role in enemy_data:
            for hero, advice in enemy_data[role].items():
                counters.append({
                    "hero": hero,
                    "reason": advice
                })
        
        return counters[:limit]


if __name__ == "__main__":
    print("Testing counter DB:")
    print(CounterDB.get_counter("widowmaker", "winston"))
    print(CounterDB.get_all_counters("widowmaker"))
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
        self.enemy_btns = {}
        self.your_btns = {}
        self._update_debounce_id = None
        self._last_update_state = None
        self._db = None
        
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
        # base_dir ends at v.0.0.0/ - go up TWO levels to project root for Assets
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_path = os.path.join(base_dir, "..", "..", "Assets", "HeroUI")
        assets_path = os.path.normpath(assets_path)
        
        all_heroes = []
        for role, heroes in self.roles_data.items():
            all_heroes.extend(heroes)
        
        for hero in all_heroes:
            icon_path = os.path.join(assets_path, f"{hero}.png")
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    # Use native CTkImage to prevent invisible image bugs
                    self.hero_images[hero] = ctk.CTkImage(light_image=img, dark_image=img, size=(34, 34))
                except:
                    pass
    
    def _get_role(self, hero):
        for role, heroes in self.roles_data.items():
            if hero in heroes:
                return role
        return "?"
    
    def _setup_ui(self):
        # 0. Global Split Layout (Left Content vs Right Sidebar)
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True)
        
        content_left = ctk.CTkFrame(main_layout, fg_color="transparent")
        content_left.pack(side="left", fill="both", expand=True)
        
        sidebar_right = ctk.CTkFrame(main_layout, fg_color="#1A1A24", corner_radius=8, width=320)
        sidebar_right.pack(side="right", fill="y", padx=(5, 5), pady=(5, 5))
        sidebar_right.pack_propagate(False) # Forzar ancho fijo
        
        # 1. TOP BAND: Enemy Card (Left) | Roster (Center) | Your Card (Right)
        top_band = ctk.CTkFrame(content_left, fg_color="transparent")
        top_band.pack(fill="x", padx=5, pady=(5, 5))
        
        # --- LEFT: Enemy Profile ---
        self.enemy_profile = ctk.CTkFrame(top_band, fg_color="#22222B", corner_radius=8, width=180)
        self.enemy_profile.pack(side="left", fill="y", padx=(0, 10))
        self.enemy_profile.pack_propagate(False)
        
        self.enemy_title_lbl = ctk.CTkLabel(self.enemy_profile, text="ENEMY HERO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FF4444")
        self.enemy_title_lbl.pack(pady=(10,5))
        
        self.enemy_pic = ctk.CTkLabel(self.enemy_profile, text="[Left Click]")
        self.enemy_pic.pack(pady=(0, 5))
        
        self.enemy_subrole_lbl = ctk.CTkLabel(self.enemy_profile, text="", font=ctk.CTkFont(size=9), text_color="#888")
        self.enemy_subrole_lbl.pack(pady=(0, 5))
        
        self.enemy_tags_frame = ctk.CTkScrollableFrame(self.enemy_profile, fg_color="transparent")
        self.enemy_tags_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # --- CENTER: Single Roster Grid ---
        roster_container = ctk.CTkFrame(top_band, fg_color="transparent")
        roster_container.pack(side="left", expand=True)
        
        header_frame = ctk.CTkFrame(roster_container, fg_color="transparent")
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(header_frame, text="ROSTER (L-Click: Enemy | R-Click: You)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#888").pack(side="left", padx=10)
        
        # Intensity Slider
        slider_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        slider_frame.pack(side="right", padx=10)
        ctk.CTkLabel(slider_frame, text="Intensity", font=ctk.CTkFont(size=9)).pack(side="top", pady=(0, 0))
        
        self.intensity_var = ctk.DoubleVar(value=0.5)
        ctk.CTkSlider(
            slider_frame, from_=0.0, to=1.0, 
            variable=self.intensity_var, command=lambda v: self._schedule_update(), 
            width=70, height=12
        ).pack(side="bottom", pady=(0, 2))
        
        self.value_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            header_frame, text="Value (0-1)", 
            variable=self.value_var, command=self._schedule_update, 
            font=ctk.CTkFont(size=10), switch_width=30, switch_height=15
        ).pack(side="right", padx=10)
        
        self.colorblind_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            header_frame, text="Colorblind", 
            variable=self.colorblind_var, command=self._schedule_update, 
            font=ctk.CTkFont(size=10), switch_width=30, switch_height=15
        ).pack(side="right", padx=5)
        
        # Skill Rank Selector
        from core.counters import RANK_INFO, DEFAULT_RANK
        rank_labels = [RANK_INFO[r]["label"] for r in RANK_INFO]
        self.skill_rank_var = ctk.StringVar(value=RANK_INFO[DEFAULT_RANK]["label"])
        self.skill_rank_combo = ctk.CTkComboBox(
            header_frame,
            values=rank_labels,
            variable=self.skill_rank_var,
            command=self._on_rank_change,
            width=110, height=22,
            font=ctk.CTkFont(size=9),
            dropdown_font=ctk.CTkFont(size=9)
        )
        self.skill_rank_combo.pack(side="right", padx=5)
        ctk.CTkLabel(header_frame, text="Rank", font=ctk.CTkFont(size=9)).pack(side="right", padx=(0, 2))
        
        # Smurf Alert - clickable cube, blue only when active
        from core.counters import SMURF_EMOJI
        self.smurf_active = False
        self.smurf_btn = ctk.CTkButton(
            header_frame, text=f"{SMURF_EMOJI}", 
            font=ctk.CTkFont(size=14), width=28, height=28,
            fg_color="transparent", hover_color="#3355FF",
            border_color="#555", border_width=2, corner_radius=4,
            command=self._toggle_smurf
        )
        self.smurf_btn.pack(side="right", padx=5)
        
        self.roster_frame = ctk.CTkFrame(roster_container, fg_color="transparent")
        self.roster_frame.pack()
        self.roster_btns = {}
        self._build_single_grid()
        
        # --- RIGHT: Your Profile ---
        self.your_profile = ctk.CTkFrame(top_band, fg_color="#222B22", corner_radius=8, width=180)
        self.your_profile.pack(side="right", fill="y", padx=(10, 0))
        self.your_profile.pack_propagate(False)
        
        self.your_title_lbl = ctk.CTkLabel(self.your_profile, text="YOUR HERO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E5FF")
        self.your_title_lbl.pack(pady=(10,5))
        
        self.your_pic = ctk.CTkLabel(self.your_profile, text="[Right Click]")
        self.your_pic.pack(pady=(0, 5))
        
        self.your_subrole_lbl = ctk.CTkLabel(self.your_profile, text="", font=ctk.CTkFont(size=9), text_color="#888")
        self.your_subrole_lbl.pack(pady=(0, 5))
        
        self.your_tags_frame = ctk.CTkScrollableFrame(self.your_profile, fg_color="transparent")
        self.your_tags_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # 2. BOTTOM BAND: Alternatives
        bottom_band = ctk.CTkFrame(content_left, fg_color="#1A1A24", corner_radius=8)
        bottom_band.pack(fill="x", padx=5, pady=(5, 5))
        
        # Sub-band for alternatives
        self.alts_frame = ctk.CTkFrame(bottom_band, fg_color="transparent", height=70)
        self.alts_frame.pack(fill="x", padx=10, pady=(10, 10))
        self.alts_frame.pack_propagate(False)
        
        # Left panel for label and filter toggle
        alts_left_panel = ctk.CTkFrame(self.alts_frame, fg_color="transparent", width=140)
        alts_left_panel.pack(side="left", fill="y", padx=(0, 5))
        alts_left_panel.pack_propagate(False)
        
        self.alts_title_lbl = ctk.CTkLabel(alts_left_panel, text="BEST ALTERNATIVES", font=ctk.CTkFont(size=11, weight="bold"), text_color="#AAAAAA")
        self.alts_title_lbl.pack(anchor="w")
        
        self.alts_filter_var = ctk.StringVar(value="Your Role")
        self.alts_filter_seg = ctk.CTkSegmentedButton(
            alts_left_panel, 
            values=["Your Role", "All Roles"], 
            variable=self.alts_filter_var,
            command=lambda v: self._schedule_update(),
            height=20,
            font=ctk.CTkFont(size=10)
        )
        self.alts_filter_seg.pack(anchor="w", pady=(2, 0), fill="x")
        
        self.alts_icons_frame = ctk.CTkScrollableFrame(self.alts_frame, orientation="horizontal", fg_color="transparent")
        self.alts_icons_frame.pack(side="left", fill="both", expand=True)
        
        # 3. SIDEBAR: Matchup Analysis (Right Column)
        ctk.CTkLabel(sidebar_right, text="MATCHUP ANALYSIS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF").pack(pady=(20, 10))
        
        # Switch/Intercambiar button
        self.switch_btn = ctk.CTkButton(
            sidebar_right,
            text="⇄ SWITCH",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#3A3A4A",
            hover_color="#555566",
            border_color="#666",
            border_width=1,
            corner_radius=6,
            height=30,
            command=self._switch_selections
        )
        self.switch_btn.pack(fill="x", padx=15, pady=(0, 10))
        
        self.info = ctk.CTkTextbox(
            sidebar_right,
            font=ctk.CTkFont(size=14),
            text_color="#DDDDDD",
            fg_color="transparent",
            wrap="word",
            activate_scrollbars=True
        )
        self.info.pack(fill="both", expand=True, padx=15, pady=(0, 20))
        self.info.insert("1.0", "Select heroes to see matchup analysis...")
        self.info.configure(state="disabled")
        
        self.hi_res_images = {}

    def _build_single_grid(self):
        cols = 10
        current_row = 0
        
        for role_name in ["Tank", "DPS", "Support"]:
            heroes_in_role = self.roles_data.get(role_name, [])
            if not heroes_in_role: continue
                
            role_lbl = ctk.CTkLabel(
                self.roster_frame, text=role_name.upper(), 
                font=ctk.CTkFont(size=10, weight="bold"), 
                text_color="#666"
            )
            role_lbl.grid(row=current_row, column=0, columnspan=cols, pady=(6, 1), sticky="w", padx=2)
            current_row += 1
            
            for i, hero in enumerate(sorted(heroes_in_role)):
                r = current_row + (i // cols)
                c = i % cols
                
                # Contenedor principal de la casilla
                container = ctk.CTkFrame(self.roster_frame, width=38, height=38, fg_color="transparent")
                container.grid(row=r, column=c, padx=2, pady=2)
                container.pack_propagate(False)
                
                # Botón de héroe (ahora ocupa todo el contenedor)
                btn = ctk.CTkButton(
                    container, text="", image=self.hero_images.get(hero),
                    fg_color="#2B2B36", hover_color="#444455",
                    border_color="#2B2B36", border_width=2, corner_radius=4,
                    command=lambda h=hero: self._on_enemy_click(h)
                )
                if hero not in self.hero_images:
                    btn.configure(text=hero[:4].upper(), font=ctk.CTkFont(size=9))
                
                btn.bind("<Button-3>", lambda e, h=hero: self._on_your_click(h))
                btn.pack(fill="both", expand=True)
                
                # Indicador numérico central inferior (Oculto por defecto)
                val_badge = ctk.CTkLabel(
                    container, text="", font=ctk.CTkFont(size=9, weight="bold"), 
                    text_color="#FFFFFF", fg_color="#111111", corner_radius=4, height=12
                )
                
                self.roster_btns[hero] = {
                    "btn": btn,
                    "val_badge": val_badge
                }
                    
            current_row += (len(heroes_in_role) - 1) // cols + 1

    def _switch_selections(self):
        self.selected_enemy, self.selected_your = self.selected_your, self.selected_enemy
        self._schedule_update()

    def _on_rank_change(self, value):
        # Always schedule update; rank is applied in _update
        from core.counters import RANK_INFO
        if self._db:
            for key, info in RANK_INFO.items():
                if info["label"] == value:
                    self._db.set_rank(key)
                    break
        self._schedule_update()

    def _toggle_smurf(self):
        """Toggle smurf alert: blue cube when active, transparent when not."""
        self.smurf_active = not self.smurf_active
        if self.smurf_active:
            self.smurf_btn.configure(fg_color="#3355FF", border_color="#3355FF")
        else:
            self.smurf_btn.configure(fg_color="transparent", border_color="#555")
        if self._db:
            self._db.set_smurf(self.smurf_active)
        self._schedule_update()

    def _schedule_update(self):
        if self._update_debounce_id is not None:
            self.after_cancel(self._update_debounce_id)
        self._update_debounce_id = self.after(80, self._update)
    def _on_enemy_click(self, hero):
        # Deselect if clicking the same hero, otherwise select
        if self.selected_enemy == hero:
            self.selected_enemy = None
        else:
            self.selected_enemy = hero
        self._schedule_update()
        
    def _on_your_click(self, hero):
        # Deselect if clicking the same hero, otherwise select
        if self.selected_your == hero:
            self.selected_your = None
        else:
            self.selected_your = hero
        self._schedule_update()

    def _get_hi_res_image(self, hero):
        if hero in self.hi_res_images:
            return self.hi_res_images[hero]
            
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_path = os.path.normpath(os.path.join(base_dir, "..", "..", "Assets", "HeroUI"))
        icon_path = os.path.join(assets_path, f"{hero}.png")
        
        if os.path.exists(icon_path):
            try:
                from PIL import Image
                img = Image.open(icon_path)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                self.hi_res_images[hero] = photo
                return photo
            except Exception as e:
                print(f"Error loading hi-res image for {hero}: {e}")
                pass
        return None

    def _short_tag(self, tag):
        """Return a short, readable label for any tag."""
        short = {
            # Subrole matchup tags
            "weak_against_bruiser": "vs Bruiser",
            "weak_against_initiator": "vs Initiator",
            "weak_against_stalwart": "vs Stalwart",
            "weak_against_sharpshooter": "vs Sharpshooter",
            "weak_against_flanker": "vs Flanker",
            "weak_against_specialist": "vs Specialist",
            "weak_against_recon": "vs Recon",
            "weak_against_tactician": "vs Tactician",
            "weak_against_medic": "vs Medic",
            "weak_against_survivor": "vs Survivor",
            "strong_against_bruiser": "Neglects Bruiser",
            "strong_against_initiator": "Neglects Initiator",
            "strong_against_stalwart": "Neglects Stalwart",
            "strong_against_sharpshooter": "Neglects Sharpshooter",
            "strong_against_flanker": "Neglects Flanker",
            "strong_against_specialist": "Neglects Specialist",
            "strong_against_recon": "Neglects Recon",
            "strong_against_tactician": "Neglects Tactician",
            "strong_against_medic": "Neglects Medic",
            "strong_against_survivor": "Neglects Survivor",
            # Contextual weakness tags
            "loses_poke_duels": "Loses poke duels",
            "cover_dependent": "Cover dependent",
            "exposed_vulnerable": "Exposed = vulnerable",
            "struggles_vs_ranged": "Struggles vs ranged",
            "vulnerable_to_kiting": "Vulnerable to kiting",
            "shield_reliant": "Shield reliant",
            "melee_only": "Melee only",
            "struggles_vs_dive": "Struggles vs dive",
            "weak_vs_sustained_poke": "Weak vs sustained poke",
            "struggles_vs_close_combat": "Struggles in CQC",
            # Kit strength tags
            "poke_from_cover": "Poke from cover",
            "strong_cover_utilization": "Cover fights",
            "close_quarters_dominant": "CQC dominant",
            "high_burst_combo": "High burst combos",
            "ally_transport": "Ally transport",
            "projectile_absorption": "Projectile absorption",
            "pick_potential_from_range": "Pick from range",
            "dive_synergy": "Dive synergy",
            # Legacy tags
            "weak_to_flank": "Weak to flank",
            "weak_to_mobility": "Weak to mobility",
            "weak_to_dive": "Weak to dive",
            "weak_to_cc": "Weak to CC",
            "weak_to_sniper": "Weak to snipers",
            "weak_to_poke": "Weak to poke",
            "weak_to_ranged": "Weak to ranged",
            "weak_to_hitscan": "Weak to hitscan",
            "weak_to_burst": "Weak to burst",
            "weak_to_anti_air": "Weak to AA",
            "weak_to_kiting": "Weak to kiting",
            "weak_to_grounding": "Weak to grounding",
            "weak_to_close_combat": "Weak to CQC",
            "weak_to_aoe": "Weak to AoE",
            "weak_to_sustained_damage": "Weak to sustained dmg",
            "weak_to_anti_flank": "Weak to anti-flank",
            "weak_to_long_range": "Weak to long range",
            "weak_to_anti_heal": "Weak to anti-heal",
            "vulnerable_to_cc": "Vulnerable to CC",
            "crowd_control": "Crowd control",
            "burst_damage": "Burst damage",
            "area_denial": "Area denial",
            "zone_control": "Zone control",
            "sustained_damage": "Sustained damage",
            "close_combat": "Close combat",
            "dive_capability": "Dive capability",
            "escape_ability": "Escape ability",
            "self_sustain": "Self sustain",
            "info_gathering": "Info gathering",
            "game_sense_intensive": "Game sense int.",
            "aim_intensive": "Aim intensive",
            "high_skill_ceiling": "High skill ceiling",
            "critical_damage": "Critical damage",
            "pick_potential": "Pick potential",
            "ultimate_economy": "Ult economy",
            "resistant_to_cc": "Resistant to CC",
            "resistant_to_knockback": "Resist knockback",
            "no_self_defense": "No self defense",
            "low_mobility": "Low mobility",
            "static": "Static",
            "anti_flank": "Anti-flank",
            "anti_air": "Anti-air",
            "off_support": "Off support",
            "main_tank": "Main tank",
            "frontline": "Frontline",
            "brawl": "Brawl",
            "aerial": "Aerial",
            "anchor": "Anchor",
            "engage": "Engage",
            "healing": "Healing",
            "peel": "Peel",
            "flank": "Flank",
            "sniper": "Sniper",
            "hitscan": "Hitscan",
            "projectile": "Projectile",
            "poke": "Poke",
            "mobile": "Mobile",
            "tanky": "Tanky",
            "shield": "Shield",
            "utility": "Utility",
            "versatile": "Versatile",
            "assassination": "Assassination",
            "one_shot": "One-shot",
            "self_heal": "Self heal",
        }
        return short.get(tag, tag.replace("_", " ").title())

    def _populate_tags_scroll(self, scroll_frame, tags_dict, cb_mode=False):
        # Limpiar frame
        for widget in scroll_frame.winfo_children():
            widget.destroy()
            
        if not tags_dict:
            ctk.CTkLabel(scroll_frame, text="No data", font=ctk.CTkFont(size=11)).pack(anchor="w")
            return
            
        # Ordenamos las tags de mayor a menor
        sorted_tags = sorted(tags_dict.items(), key=lambda kv: -kv[1])
        
        for tag, weight in sorted_tags:
            tag_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            tag_frame.pack(fill="x", pady=1)
            
            # Color coding según el modo
            if cb_mode:
                # Daltónico: Naranja intenso (>0.8), Naranja claro (>0.5), Gris (<0.5)
                val_color = "#F46D43" if weight >= 0.8 else "#FDAE61" if weight >= 0.5 else "#AAAAAA"
            else:
                # Estándar: Verde brillante (>0.8), Amarillo (>0.5), Gris (<0.5)
                val_color = "#44FF44" if weight >= 0.8 else "#FFCC00" if weight >= 0.5 else "#AAAAAA"
            
            ctk.CTkLabel(tag_frame, text=self._short_tag(tag), font=ctk.CTkFont(size=10)).pack(side="left")
            ctk.CTkLabel(tag_frame, text=f"{weight:.1f}", font=ctk.CTkFont(size=10, weight="bold"), text_color=val_color).pack(side="right", padx=5)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def _interpolate_color(self, c1, c2, factor):
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        r = r1 + (r2 - r1) * factor
        g = g1 + (g2 - g1) * factor
        b = b1 + (b2 - b1) * factor
        return self._rgb_to_hex((r, g, b))

    def _get_color_for_score(self, score, cb=False):
        # Determinamos el indice basado en el score
        if score < 0.2: idx = 0     # Terrible
        elif score < 0.6: idx = 1   # Bad
        elif score < 1.0: idx = 2   # Neutral
        elif score < 1.5: idx = 3   # Good
        else: idx = 4               # Excellent
        
        # Paletas de color maestras
        palettes = {
            "standard": {
                "muted": ["#5C2B2B", "#5C402B", "#5C5C00", "#405C2B", "#2B5C2B"],
                "vibrant": ["#FF0000", "#FF6600", "#FFFF00", "#88FF00", "#00FF00"],
                "contrast": ["#000000", "#444444", "#888888", "#BBBBBB", "#FFFFFF"]
            },
            "colorblind": {
                "muted": ["#20235B", "#4A6E85", "#444444", "#A36D3A", "#9C4226"],
                "vibrant": ["#313695", "#74ADD1", "#CCCCCC", "#FDAE61", "#F46D43"],
                "contrast": ["#000000", "#444444", "#888888", "#BBBBBB", "#FFFFFF"]
            }
        }
        
        mode = "colorblind" if cb else "standard"
        intensity = self.intensity_var.get()
        
        # Lógica de interpolación matemática según la posición del slider
        if intensity <= 0.5:
            # Transición entre Muted y Vibrant
            c1 = palettes[mode]["muted"][idx]
            c2 = palettes[mode]["vibrant"][idx]
            factor = intensity * 2.0
        else:
            # Transición entre Vibrant y High Contrast (B/W)
            c1 = palettes[mode]["vibrant"][idx]
            c2 = palettes[mode]["contrast"][idx]
            factor = (intensity - 0.5) * 2.0
            
        return self._interpolate_color(c1, c2, factor)

    def _normalize_score(self, score):
        # Convertimos las puntuaciones relativas (normalmente 0.0 - 2.0) a un cap estricto 0.0 - 1.0
        norm = score / 1.5
        return min(max(norm, 0.0), 1.0)

    def _update(self):
        self._update_debounce_id = None
        
        if self._db is None:
            from core.counters import CounterDB
            self._db = CounterDB()
            # Set initial rank
            from core.counters import RANK_INFO
            for key, info in RANK_INFO.items():
                if info["label"] == self.skill_rank_var.get():
                    self._db.set_rank(key)
                    break
        db = self._db
        
        # Early exit: skip if state hasn't changed since last render
        cb_mode = self.colorblind_var.get()
        show_value = self.value_var.get()
        intensity = self.intensity_var.get()
        alts_filter = self.alts_filter_var.get()
        skill_rank = self.skill_rank_var.get()
        smurf_active = self.smurf_active
        current_state = (self.selected_enemy, self.selected_your, cb_mode, show_value, intensity, alts_filter, skill_rank, smurf_active)
        if current_state == self._last_update_state:
            return
        self._last_update_state = current_state
        
        # Apply smurf state to DB
        if self._db:
            self._db.set_smurf(self.smurf_active)
        
        # Paleta de selecciones principales
        enemy_c = "#FF9900" if cb_mode else "#FF4444"  # Orange vs Red
        ally_c = "#3366FF" if cb_mode else "#00E5FF"   # Blue vs Cyan
        
        # Actualizamos los títulos principales
        self.enemy_title_lbl.configure(text_color=enemy_c)
        self.your_title_lbl.configure(text_color=ally_c)
        
        # Update switch button state (disabled when no selections)
        if self.selected_enemy is None and self.selected_your is None:
            self.switch_btn.configure(state="disabled", fg_color="#2A2A34", text="⇄ SWITCH")
        else:
            self.switch_btn.configure(state="normal", fg_color="#3A3A4A", text="⇄ SWITCH")
        
        # 1. Update Grid Colors (Heatmap & Borders)
        for h, data in self.roster_btns.items():
            btn = data["btn"]
            val_badge = data["val_badge"]
            
            # Logic for borders
            btn_border_color = "#2B2B36"
            btn_border_width = 2
            
            if h == self.selected_enemy and h == self.selected_your:
                btn_border_color = "#FFFFFF" # Mirror Match
                btn_border_width = 3
            elif h == self.selected_enemy:
                btn_border_color = enemy_c
                btn_border_width = 3
            elif h == self.selected_your:
                btn_border_color = ally_c
                btn_border_width = 3
                
            btn.configure(border_color=btn_border_color, border_width=btn_border_width)
            
            has_heatmap = False
            raw_score = 0.0
            
            # Heatmap background logic
            if self.selected_enemy:
                raw_score = db._score_counter(self.selected_enemy, h)
                color = self._get_color_for_score(raw_score, cb_mode)
                btn.configure(fg_color=color, hover_color=color)
                has_heatmap = True
            elif self.selected_your:
                raw_score = db._score_counter(h, self.selected_your)
                color = self._get_color_for_score(raw_score, cb_mode)
                btn.configure(fg_color=color, hover_color=color)
                has_heatmap = True
            else:
                btn.configure(fg_color="#2B2B36", hover_color="#444455")
                
            # Logica del Value Badge (Totalmente oculto si no se necesita)
            if show_value and has_heatmap:
                norm_score = self._normalize_score(raw_score)
                val_badge.configure(text=f"{norm_score:.1f}")
                val_badge.place(relx=0.5, rely=0.95, anchor="s")
                val_badge.tkraise() # Bring to front
            else:
                val_badge.place_forget() # Oculta la etiqueta por completo
                
        # 2. Update Alternatives List (Clear first)
        for widget in self.alts_icons_frame.winfo_children():
            widget.destroy()
        
        filter_mode = self.alts_filter_var.get()  # "Your Role" or "All Roles"
        
        if self.selected_enemy:
            all_alts = db.get_all_counters(self.selected_enemy, limit=60)
            
            # Determine which role to filter by
            if self.selected_your:
                filter_role = db.get_role(self.selected_your)
            else:
                filter_role = db.get_role(self.selected_enemy)
            
            if filter_mode == "Your Role" and filter_role:
                all_alts = [a for a in all_alts if a['role'] == filter_role]
                if self.selected_your:
                    self.alts_title_lbl.configure(text=f"BEST {filter_role.upper()} ALTS")
                else:
                    self.alts_title_lbl.configure(text=f"WEAK TO ({filter_role.upper()})")
            else:
                if self.selected_your:
                    self.alts_title_lbl.configure(text="BEST ALTERNATIVES")
                else:
                    self.alts_title_lbl.configure(text="WEAK TO")
            
            # Filter out selected heroes
            all_alts = [a for a in all_alts if a['hero'] not in (self.selected_enemy, self.selected_your)]
            
            for alt in all_alts:
                alt_img = self.hero_images.get(alt['hero'])
                btn = ctk.CTkButton(
                    self.alts_icons_frame, text="", image=alt_img, width=34, height=34,
                    fg_color=self._get_color_for_score(alt['score'], cb_mode), 
                    border_width=0,
                    command=lambda h=alt['hero']: self._on_your_click(h)
                )
                btn.pack(side="left", padx=2)
                
        elif self.selected_your:
            strong_against = []
            for h in db._heroes.keys():
                if h == self.selected_your: continue
                score = db._score_counter(h, self.selected_your)
                strong_against.append({'hero': h, 'score': score, 'role': db.get_role(h)})
            
            strong_against.sort(key=lambda x: -x['score'])
            
            filter_role = db.get_role(self.selected_your)
            if filter_mode == "Your Role" and filter_role:
                strong_against = [a for a in strong_against if a['role'] == filter_role]
            
            self.alts_title_lbl.configure(text="STRONG AGAINST")
                
            for alt in strong_against:
                alt_img = self.hero_images.get(alt['hero'])
                btn = ctk.CTkButton(
                    self.alts_icons_frame, text="", image=alt_img, width=34, height=34,
                    fg_color=self._get_color_for_score(alt['score'], cb_mode), 
                    border_width=0,
                    command=lambda h=alt['hero']: self._on_enemy_click(h)
                )
                btn.pack(side="left", padx=2)
                
        else:
            self.alts_title_lbl.configure(text="BEST ALTERNATIVES")

        # 3. Update Profiles
        enemy_name = ""
        your_name = ""
        
        # Subrole lookup
        from core.counters import SUBROLE_INFO
        
        if self.selected_enemy:
            enemy_data = db.get_hero_data(self.selected_enemy)
            enemy_name = enemy_data.get("name", self.selected_enemy.capitalize())
            e_img = self._get_hi_res_image(self.selected_enemy)
            if e_img:
                self.enemy_pic.configure(image=e_img, text="")
            else:
                self.enemy_pic.configure(image="", text=enemy_name)
            
            # Subrole label
            e_sr = enemy_data.get("subrole", "")
            if e_sr and e_sr in SUBROLE_INFO:
                sr = SUBROLE_INFO[e_sr]
                self.enemy_subrole_lbl.configure(text=f"{sr['role']} · {e_sr.title()}")
                self.enemy_subrole_lbl.configure(text_color="#AAAACC")
            else:
                self.enemy_subrole_lbl.configure(text="")
                
            self._populate_tags_scroll(self.enemy_tags_frame, enemy_data.get("tags", {}), cb_mode)
        else:
            self.enemy_pic.configure(image="", text="[Left Click]")
            self.enemy_subrole_lbl.configure(text="")
            self._populate_tags_scroll(self.enemy_tags_frame, {}, cb_mode)
            
        if self.selected_your:
            your_data = db.get_hero_data(self.selected_your)
            your_name = your_data.get("name", self.selected_your.capitalize())
            y_img = self._get_hi_res_image(self.selected_your)
            if y_img:
                self.your_pic.configure(image=y_img, text="")
            else:
                self.your_pic.configure(image="", text=your_name)
            
            # Subrole label
            y_sr = your_data.get("subrole", "")
            if y_sr and y_sr in SUBROLE_INFO:
                sr = SUBROLE_INFO[y_sr]
                self.your_subrole_lbl.configure(text=f"{sr['role']} · {y_sr.title()}")
                self.your_subrole_lbl.configure(text_color="#AACCAA")
            else:
                self.your_subrole_lbl.configure(text="")
                
            self._populate_tags_scroll(self.your_tags_frame, your_data.get("tags", {}), cb_mode)
        else:
            self.your_pic.configure(image="", text="[Right Click]")
            self.your_subrole_lbl.configure(text="")
            self._populate_tags_scroll(self.your_tags_frame, {}, cb_mode)

        # 4. Update Matchup Info Textbox
        self.info.configure(state="normal")
        self.info.delete("1.0", "end")
        
        if self.selected_enemy and self.selected_your:
            if self.selected_enemy == self.selected_your:
                advice_text = f"[MIRROR MATCH] {your_name} vs {enemy_name}\n\nThis is a pure skill matchup. Both heroes share the exact same strengths and weaknesses.\n\nTACTICS:\n- Victory depends heavily on superior mechanical execution and better cooldown management.\n- Focus on out-positioning your counterpart.\n- Wait for them to use their defensive/escape cooldowns before you commit yours."
            else:
                counter = db.get_counter(self.selected_enemy, self.selected_your)
                advice_text = f"MATCHUP: {your_name} vs {enemy_name}\n\n{counter.get('reason', 'No data')}"
            self.info.insert("1.0", advice_text)
        elif self.selected_enemy:
            self.info.insert("1.0", f"Enemy: {enemy_name} selected.\nRight Click a hero in the roster to see the matchup analysis, or pick one of the alternatives above.")
        elif self.selected_your:
            self.info.insert("1.0", f"Ally: {your_name} selected.\nLeft Click an enemy hero in the roster to see the matchup analysis.")
        else:
            self.info.insert("1.0", "Select heroes to see matchup analysis (Left Click for Enemy, Right Click for You).")
            
        self.info.configure(state="disabled")
    
    def get_selection(self):
        return {"enemy": self.selected_enemy, "your": self.selected_your}
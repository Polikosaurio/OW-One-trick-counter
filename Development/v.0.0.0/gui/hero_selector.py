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
        # 1. TOP BAND: Enemy Card (Left) | Roster (Center) | Your Card (Right)
        top_band = ctk.CTkFrame(self, fg_color="transparent")
        top_band.pack(fill="x", padx=5, pady=(5, 5))
        
        # --- LEFT: Enemy Profile ---
        self.enemy_profile = ctk.CTkFrame(top_band, fg_color="#22222B", corner_radius=8, width=180)
        self.enemy_profile.pack(side="left", fill="y", padx=(0, 10))
        self.enemy_profile.pack_propagate(False)
        
        ctk.CTkLabel(self.enemy_profile, text="ENEMY HERO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FF4444").pack(pady=(10,5))
        self.enemy_pic = ctk.CTkLabel(self.enemy_profile, text="[Left Click]")
        self.enemy_pic.pack(pady=(0, 10))
        self.enemy_tags_frame = ctk.CTkScrollableFrame(self.enemy_profile, fg_color="transparent")
        self.enemy_tags_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # --- CENTER: Single Roster Grid ---
        roster_container = ctk.CTkFrame(top_band, fg_color="transparent")
        roster_container.pack(side="left", expand=True)
        
        header_frame = ctk.CTkFrame(roster_container, fg_color="transparent")
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(header_frame, text="ROSTER (L-Click: Enemy | R-Click: You)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#888").pack(side="left", padx=10)
        
        self.colorblind_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            header_frame, text="Colorblind", 
            variable=self.colorblind_var, command=self._update, 
            font=ctk.CTkFont(size=10), switch_width=30, switch_height=15
        ).pack(side="right", padx=5)
        
        self.value_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            header_frame, text="Value (0-1)", 
            variable=self.value_var, command=self._update, 
            font=ctk.CTkFont(size=10), switch_width=30, switch_height=15
        ).pack(side="right", padx=10)
        
        # Intensity Slider
        slider_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        slider_frame.pack(side="right", padx=10)
        ctk.CTkLabel(slider_frame, text="Intensity", font=ctk.CTkFont(size=9)).pack(side="top", pady=(0, 0))
        
        self.intensity_var = ctk.DoubleVar(value=0.5)
        ctk.CTkSlider(
            slider_frame, from_=0.0, to=1.0, 
            variable=self.intensity_var, command=lambda v: self._update(), 
            width=70, height=12
        ).pack(side="bottom", pady=(0, 2))
        
        self.roster_frame = ctk.CTkFrame(roster_container, fg_color="transparent")
        self.roster_frame.pack()
        self.roster_btns = {}
        self._build_single_grid()
        
        # --- RIGHT: Your Profile ---
        self.your_profile = ctk.CTkFrame(top_band, fg_color="#222B22", corner_radius=8, width=180)
        self.your_profile.pack(side="right", fill="y", padx=(10, 0))
        self.your_profile.pack_propagate(False)
        
        ctk.CTkLabel(self.your_profile, text="YOUR HERO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E5FF").pack(pady=(10,5))
        self.your_pic = ctk.CTkLabel(self.your_profile, text="[Right Click]")
        self.your_pic.pack(pady=(0, 10))
        self.your_tags_frame = ctk.CTkScrollableFrame(self.your_profile, fg_color="transparent")
        self.your_tags_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # 2. BOTTOM BAND: Matchup Analysis & Alternatives
        bottom_band = ctk.CTkFrame(self, fg_color="#1A1A24", corner_radius=8)
        bottom_band.pack(fill="both", expand=True, padx=5, pady=(5, 5))
        
        # Sub-band for alternatives (top of bottom band)
        self.alts_frame = ctk.CTkFrame(bottom_band, fg_color="transparent", height=70)
        self.alts_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.alts_frame.pack_propagate(False)
        
        # Left panel for label and filter toggle
        alts_left_panel = ctk.CTkFrame(self.alts_frame, fg_color="transparent", width=140)
        alts_left_panel.pack(side="left", fill="y", padx=(0, 5))
        alts_left_panel.pack_propagate(False)
        
        ctk.CTkLabel(alts_left_panel, text="BEST ALTERNATIVES", font=ctk.CTkFont(size=11, weight="bold"), text_color="#AAAAAA").pack(anchor="w")
        
        self.alts_filter_var = ctk.StringVar(value="Your Role")
        self.alts_filter_seg = ctk.CTkSegmentedButton(
            alts_left_panel, 
            values=["Your Role", "All Roles"], 
            variable=self.alts_filter_var,
            command=lambda v: self._update(),
            height=20,
            font=ctk.CTkFont(size=10)
        )
        self.alts_filter_seg.pack(anchor="w", pady=(2, 0), fill="x")
        
        self.alts_icons_frame = ctk.CTkScrollableFrame(self.alts_frame, orientation="horizontal", fg_color="transparent")
        self.alts_icons_frame.pack(side="left", fill="both", expand=True)
        
        # Matchup Textbox
        self.info = ctk.CTkTextbox(
            bottom_band,
            font=ctk.CTkFont(size=13),
            text_color="#FFFFFF",
            fg_color="transparent",
            wrap="word",
            activate_scrollbars=True
        )
        self.info.pack(fill="both", expand=True, padx=10, pady=10)
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

    def _on_enemy_click(self, hero):
        # Deselect if clicking the same hero, otherwise select
        if self.selected_enemy == hero:
            self.selected_enemy = None
        else:
            self.selected_enemy = hero
        self._update()
        
    def _on_your_click(self, hero):
        # Deselect if clicking the same hero, otherwise select
        if self.selected_your == hero:
            self.selected_your = None
        else:
            self.selected_your = hero
        self._update()

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

    def _populate_tags_scroll(self, scroll_frame, tags_dict):
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
            
            val_color = "#44FF44" if weight >= 0.8 else "#FFCC00" if weight >= 0.5 else "#AAAAAA"
            
            ctk.CTkLabel(tag_frame, text=tag.replace('_', ' ').title(), font=ctk.CTkFont(size=10)).pack(side="left")
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
                "muted": ["#5C2B2B", "#5C402B", "#5C5C2B", "#405C2B", "#2B5C2B"],
                "vibrant": ["#FF0000", "#FF6600", "#666644", "#88FF00", "#00FF00"],
                "contrast": ["#000000", "#444444", "#888888", "#BBBBBB", "#FFFFFF"]
            },
            "colorblind": {
                "muted": ["#20235B", "#4A6E85", "#5C5C2B", "#A36D3A", "#9C4226"],
                "vibrant": ["#313695", "#74ADD1", "#5C5C2B", "#FDAE61", "#F46D43"],
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
        from core.counters import CounterDB
        db = CounterDB()
        
        # Obtenemos el estado del modo daltónico y valor numérico
        cb_mode = self.colorblind_var.get()
        show_value = self.value_var.get()
        
        # Paleta de selecciones principales
        enemy_c = "#FF9900" if cb_mode else "#FF4444"  # Orange vs Red
        ally_c = "#3366FF" if cb_mode else "#00E5FF"   # Blue vs Cyan
        
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
        
        if self.selected_enemy:
            # Get absolutely all counters sorted by score
            all_alts = db.get_all_counters(self.selected_enemy, limit=60)
            
            # Apply "Your Role" filter if toggle is set AND we have a selected hero
            if self.alts_filter_var.get() == "Your Role" and self.selected_your:
                my_role = db.get_role(self.selected_your)
                all_alts = [a for a in all_alts if a['role'] == my_role]
            
            # Filter out the currently selected enemy and your currently selected hero
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

        # 3. Update Profiles
        enemy_name = ""
        your_name = ""
        
        if self.selected_enemy:
            enemy_data = db.get_hero_data(self.selected_enemy)
            enemy_name = enemy_data.get("name", self.selected_enemy.capitalize())
            e_img = self._get_hi_res_image(self.selected_enemy)
            if e_img:
                self.enemy_pic.configure(image=e_img, text="")
            else:
                self.enemy_pic.configure(image="", text=enemy_name)
                
            self._populate_tags_scroll(self.enemy_tags_frame, enemy_data.get("tags", {}))
        else:
            self.enemy_pic.configure(image="", text="[Left Click]")
            self._populate_tags_scroll(self.enemy_tags_frame, {})
            
        if self.selected_your:
            your_data = db.get_hero_data(self.selected_your)
            your_name = your_data.get("name", self.selected_your.capitalize())
            y_img = self._get_hi_res_image(self.selected_your)
            if y_img:
                self.your_pic.configure(image=y_img, text="")
            else:
                self.your_pic.configure(image="", text=your_name)
                
            self._populate_tags_scroll(self.your_tags_frame, your_data.get("tags", {}))
        else:
            self.your_pic.configure(image="", text="[Right Click]")
            self._populate_tags_scroll(self.your_tags_frame, {})

        # 4. Update Matchup Info Textbox
        self.info.configure(state="normal")
        self.info.delete("1.0", "end")
        
        if self.selected_enemy and self.selected_your:
            if self.selected_enemy == self.selected_your:
                advice_text = f"⚔️ MIRROR MATCH: {your_name} vs {enemy_name} ⚔️\n\nThis is a pure skill matchup. Both heroes share the exact same strengths and weaknesses.\n\nTACTICS:\n• Victory depends heavily on superior mechanical execution and better cooldown management.\n• Focus on out-positioning your counterpart.\n• Wait for them to use their defensive/escape cooldowns before you commit yours."
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
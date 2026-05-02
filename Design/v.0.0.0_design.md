# OW One Trick Counter - Design Document
# Version: v.0.0.0
# Date: 2026-05-03

================================================================================
PROJECT OVERVIEW
================================================================================

Name: OW One Trick Counter
Type: Lightweight Windows game overlay tool
Purpose: Help OW players identify and counter "one trick" enemies with strategic advice
Target Users: Overwatch players who struggle against dominant enemy players

================================================================================
TECH STACK
================================================================================

Core Libraries:
- customtkinter          # GUI (modern, dark mode, lightweight)
- keyboard             # Global hotkeys
- win32api / pywin32    # Mouse lock (ClipCursor), window control
- pystray             # System tray icon + menu
- pyscreeze            # Screenshot capture
- opencv-python        # Template matching (hero detection)
- pytesseract + Tesseract # OCR (scoreboard stats)

================================================================================
FILE STRUCTURE
================================================================================

Development/
└── v.0.0.0/
    ├── main.py                 # Entry point
    ├── gui/
    │   ├── main_window.py     # Main config window
    │   ├── hero_selector.py  # Visual hero grid
    │   └── overlay.py      # In-game overlay
    ├── core/
    │   ├── counters.py     # Counter logic + data
    │   ├── hotkeys.py    # Global hotkey manager
    │   ├── mouse_lock.py  # ClipCursor implementation
    │   ├── config.py     # Settings JSON
    │   └── game_detector.py # OW process detection
    ├── cv/
    │   ├── hero_detector.py  # Template matching
    │   └── scoreboard_reader.py # OCR stats extraction
    ├── data/
    │   └── heroes.json   # Counter relationships
    ├── assets/
    │   └── icons/       # Link to ../../Assets/HeroUI/
    └── run.bat          # Quick launcher

================================================================================
FEATURES
================================================================================

CORE FEATURES:
[1] Visual Hero Selector
    - Grid of all hero icons (clickable, updated with latest heroes aditions)
    - Select: problem hero + your hero (your role)
    - Output: counter recommendation per role

[2] Counter Recommendations
    - Focus: "what can I do individually"
    - By role: Tank/DPS/Support
    - Show best counter for each role

[3] In-Game Overlay
    - Small clickable icon
    - Shows tooltips with strategy
    - Opacity adjustable (default: 0.85)
    - Position configurable

[4] Global Hotkeys
    - Toggle overlay: Ctrl+Shift+O (configurable)
    - Mouse lock: Ctrl+Shift+M (independent)

[5] Mouse Lock
    - Win32 ClipCursor API
    - Confine cursor to monitor
    - Independent of game mode
    - Toggle with Ctrl+Shift+M

[6] Auto-Detect OW
    - Detect when OW process runs
    - Option: launch with game
    - Option: manual only (configurable)

[7] System Tray
    - Status indicator
    - Menu items:
        * Overlay ON/OFF
        * Mouse Lock ON/OFF
        * Show hotkey info
        * Open settings
        * Exit

[8] Computer Vision (Investigation)
    [8a] Hero Detection
        - Template matching with hero icons
        - Auto-detect heroes on screen
        
    [8b] Scoreboard OCR
        - Capture scoreboard (Tab)
        - Parse: E, A, D, DMG, H, MIT
        - Calculate threat score (K/D ratio)
        - Identify "one trick" enemy

================================================================================
CONFIGURATION
================================================================================

Settings stored in: config.json

{
    "hotkey_toggle": "ctrl+shift+o",
    "hotkey_mouse_lock": "ctrl+shift+m",
    "start_with_game": true,
    "overlay_opacity": 0.85,
    "overlay_position": {"x": 100, "y": 100},
    "cv_hero_detection": false,
    "cv_scoreboard_ocr": false,
    "hero_last_selected": null
}

================================================================================
LIMITATIONS
================================================================================

1. OVERLAY ON FULLSCREEN
   - Standard Windows overlay (topmost) does NOT work on fullscreen DirectX/OpenGL games
   - SOLUTION: Run OW in borderless window mode
   
2. SCREENSHOT CAPTURE
   - DirectX rendered games may return black screenshots
   - Alternative: desktopmagic, OBS virtual camera
   
3. OCR ACCURACY
   - Depends on Tesseract installation
   - May need image preprocessing per OW version

================================================================================
DEPENDENCIES
================================================================================

Python Packages:
- customtkinter
- keyboard
- pywin32
- pystray
- pyscreeze
- opencv-python
- pytesseract

External:
- Tesseract OCR (Windows): https://github.com/UB-Mannheim/tesseract/wiki

================================================================================
DESIGN DECISIONS
================================================================================

1. Hotkeys: Independent (not combined)
   - Toggle overlay: Ctrl+Shift+O
   - Mouse lock: Ctrl+Shift+M

2. Start Mode: Configurable
   - True: Launch with OW
   - False: Manual only

3. CV Features: OFF by default
   - Must be enabled in config

4. Mouse Lock: Toggle with Ctrl+Shift+M
   - Works regardless of game mode

5. System Tray: Always visible
   - Quick access to controls
   - Show current hotkeys

6. Feedback: Individual focus
   - "What can I do"
   - Not team-focused

================================================================================
GITHUB
================================================================================

Repo: Polikosaurio/OW2-One-trick-counter
[Token removed for security]

================================================================================
NOTES
================================================================================

- OW = Overwatch (formerly Overwatch 2)
- Focus: Individual player feedback
- Tool designed for quick use -> hide with hotkey
- Mouse lock is system-wide, works in any mode
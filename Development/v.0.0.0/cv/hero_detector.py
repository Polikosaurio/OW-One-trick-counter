"""
Computer Vision - Hero Detection Module
Template matching to detect heroes on screen
"""

import os
import cv2
import numpy as np
from PIL import ImageGrab


class HeroDetector:
    def __init__(self, icons_folder):
        self.icons_folder = icons_folder
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load hero icon templates"""
        if not os.path.exists(self.icons_folder):
            print(f"[HeroDetector] Icons folder not found: {self.icons_folder}")
            return
        
        for filename in os.listdir(self.icons_folder):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                hero_name = os.path.splitext(filename)[0]
                path = os.path.join(self.icons_folder, filename)
                
                try:
                    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        self.templates[hero_name] = img
                except Exception as e:
                    print(f"[HeroDetector] Failed to load {filename}: {e}")
        
        print(f"[HeroDetector] Loaded {len(self.templates)} hero templates")
    
    def detect_on_screen(self, region=None, threshold=0.8):
        """
        Detect heroes on screen
        region: (left, top, right, bottom) or None for full screen
        threshold: match confidence (0.0-1.0)
        
        Returns: list of (hero_name, confidence, position)
        """
        if not self.templates:
            print("[HeroDetector] No templates loaded")
            return []
        
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(f"[HeroDetector] Screenshot failed: {e}")
            return []
        
        matches = []
        
        for hero_name, template in self.templates.items():
            try:
                template_h, template_w = template.shape
                
                if template_h > screen_gray.shape[0] or template_w > screen_gray.shape[1]:
                    continue
                
                result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= threshold:
                    matches.append({
                        'hero': hero_name,
                        'confidence': max_val,
                        'position': max_loc,
                        'size': (template_w, template_h)
                    })
            except Exception as e:
                continue
        
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches[:10]
    
    def detect_in_region(self, region, threshold=0.8):
        """Detect heroes in specific region"""
        return self.detect_on_screen(region, threshold)


def get_hero_detector():
    """Create hero detector with default icons"""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    icons_folder = os.path.join(base, "Assets", "HeroUI")
    return HeroDetector(icons_folder)


if __name__ == "__main__":
    print("[HeroDetector] Testing...")
    detector = get_hero_detector()
    
    print("[HeroDetector] Scanning screen...")
    matches = detector.detect_on_screen(threshold=0.7)
    
    for match in matches:
        print(f"  {match['hero']}: {match['confidence']:.2f} at {match['position']}")
"""
Computer Vision - Scoreboard OCR
Extract stats from OW scoreboard using OCR
"""

import os
import re
import cv2
import numpy as np
import pytesseract
from PIL import ImageGrab


class ScoreboardReader:
    def __init__(self):
        self.stats_patterns = {
            'eliminations': r'(\d+)\s*E',
            'assists': r'(\d+)\s*A',
            'deaths': r'(\d+)\s*D',
            'damage': r'(\d+)',
            'healing': r'(\d+)',
            'mitigated': r'(\d+)'
        }
    
    def capture_scoreboard(self, region=None):
        """Capture screenshot of scoreboard area"""
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[ScoreboardOCR] Capture failed: {e}")
            return None
    
    def preprocess_image(self, image):
        """Preprocess image for OCR"""
        if image is None:
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return denoised
    
    def extract_text(self, image):
        """Extract text from image using Tesseract"""
        if image is None:
            return ""
        
        try:
            text = pytesseract.image_to_string(
                image,
                config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789EWADMH'
            )
            return text
        except Exception as e:
            print(f"[ScoreboardOCR] OCR failed: {e}")
            return ""
    
    def parse_stats(self, text):
        """Parse stats from extracted text"""
        stats = {}
        
        lines = text.split('\n')
        
        elimination_pattern = r'(\d+)'
        
        for i, line in enumerate(lines):
            numbers = elimination_pattern.findall(line)
            
            if len(numbers) >= 3:
                stats['eliminations'] = int(numbers[0])
                stats['assists'] = int(numbers[1])
                stats['deaths'] = int(numbers[2])
            
            if len(numbers) >= 4:
                stats['damage'] = int(numbers[3])
            
            if len(numbers) >= 5:
                stats['healing'] = int(numbers[4])
            
            if len(numbers) >= 6:
                stats['mitigated'] = int(numbers[5])
        
        return stats
    
    def calculate_threat_score(self, stats):
        """Calculate threat score from stats"""
        if not stats or stats.get('deaths', 0) == 0:
            return 0
        
        elims = stats.get('eliminations', 0)
        deaths = stats.get('deaths', 1)
        
        damage = stats.get('damage', 0)
        
        kd_ratio = elims / max(deaths, 1)
        
        threat_score = (kd_ratio * 0.6) + (damage / 10000 * 0.4)
        
        return round(threat_score, 2)
    
    def read_scoreboard(self, region=None):
        """Main method: capture and parse scoreboard"""
        image = self.capture_scoreboard(region)
        
        if image is None:
            return {'error': 'Capture failed'}
        
        processed = self.preprocess_image(image)
        
        text = self.extract_text(processed)
        
        stats = self.parse_stats(text)
        
        if stats:
            stats['threat_score'] = self.calculate_threat_score(stats)
        
        return stats
    
    def detect_threat_players(self, region=None):
        """Detect players with highest threat score"""
        stats_list = []
        
        text = self.extract_text(self.preprocess_image(self.capture_scoreboard(region)))
        
        stats = self.parse_stats(text)
        
        if stats:
            stats['threat_score'] = self.calculate_threat_score(stats)
            stats_list.append(stats)
        
        return stats_list


def get_scoreboard_reader():
    """Create scoreboard reader"""
    return ScoreboardReader()


if __name__ == "__main__":
    print("[ScoreboardOCR] Testing...")
    reader = get_scoreboard_reader()
    
    print("[ScoreboardOCR] Press Tab to open scoreboard, then run this script")
    
    stats = reader.read_scoreboard()
    
    print(f"Detected stats: {stats}")
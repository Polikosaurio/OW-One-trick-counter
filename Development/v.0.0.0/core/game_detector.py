"""
Game Process Detector
Detects when OW process is running and triggers actions
"""

import subprocess
import threading
import time
import psutil


class GameDetector:
    OW_PROCESS_NAMES = [
        "Overwatch.exe",
        "Overwatch2.exe",
    ]
    
    def __init__(self, config, on_game_launch=None, on_game_close=None):
        self.config = config
        self.on_game_launch = on_game_launch
        self.on_game_close = on_game_close
        self.running = False
        self.game_detected = False
        self._thread = None
    
    def start(self):
        """Start monitoring for OW process"""
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print("[GameDetector] Monitoring for Overwatch...")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            is_running = self._is_ow_running()
            
            if is_running and not self.game_detected:
                self.game_detected = True
                print("[GameDetector] Overwatch detected!")
                if self.on_game_launch:
                    self.on_game_launch()
            
            elif not is_running and self.game_detected:
                self.game_detected = False
                print("[GameDetector] Overwatch closed")
                if self.on_game_close:
                    self.on_game_close()
            
            time.sleep(2)
    
    def _is_ow_running(self):
        """Check if OW process is running"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.OW_PROCESS_NAMES:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def is_game_running(self):
        """Return current game status"""
        return self.game_detected


if __name__ == "__main__":
    detector = GameDetector(None)
    if detector._is_ow_running():
        print("Overwatch is running")
    else:
        print("Overwatch not detected")
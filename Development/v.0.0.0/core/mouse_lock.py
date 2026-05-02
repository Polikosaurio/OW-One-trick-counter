"""
Mouse Lock Module
Uses Win32 ClipCursor to confine cursor to monitor
"""

import win32api
import win32con


class MouseLock:
    @staticmethod
    def clip(rect):
        """
        Confine cursor to rectangle
        rect: (left, top, right, bottom)
        """
        left, top, right, bottom = rect
        win32api.ClipCursor((left, top, right, bottom))
        print(f"[MouseLock] Cursor clipped to {rect}")
    
    @staticmethod
    def release():
        """Release cursor confinement"""
        win32api.ClipCursor(None)
        print("[MouseLock] Cursor released")
    
    @staticmethod
    def is_clipped():
        """Check if cursor is currently clipped"""
        try:
            rect = win32api.GetClipCursor()
            return rect != (0, 0, 0, 0)
        except:
            return False


def get_primary_monitor_rect():
    """Get primary monitor bounds"""
    import ctypes
    from ctypes import wintypes
    
    user32 = ctypes.windll.user32
    
    user32.SetProcessDPIAware()
    
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    
    return (0, 0, width, height)


def get_all_monitors():
    """Get all monitor rectangles"""
    import ctypes
    from ctypes import wintypes
    
    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int
    )
    
    monitors = []
    
    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        r = ctypes.wintypes.RECT()
        ctypes.memmove(ctypes.addressof(r), lprcMonitor, ctypes.sizeof(r))
        monitors.append((r.left, r.top, r.right, r.bottom))
        return 1
    
    user32 = ctypes.windll.user32
    user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
    
    return monitors


if __name__ == "__main__":
    rect = get_primary_monitor_rect()
    print(f"Primary monitor: {rect}")
    
    print(f"All monitors: {get_all_monitors()}")
    
    print(f"Clipped: {MouseLock.is_clipped()}")
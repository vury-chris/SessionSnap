import sys
from PyQt5.QtWidgets import QApplication
from app_selector import AppSelectorPage
from timer_page import TimerPage
from app_state import AppState

def main():
    # Create application instance 
    app = QApplication(sys.argv)
    
    # Fix for Windows taskbar icon
    import os
    import ctypes
    from PyQt5.QtWinExtras import QtWin  # Import Windows-specific module
    from PyQt5.QtGui import QIcon
    
    # Set app ID for Windows taskbar
    if os.name == 'nt':  # Windows
        # Create a unique app ID
        app_id = 'company.productivitytimer.app.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        
        # Enable icon handling in taskbar
        if os.path.exists("appicon.ico"):
            # Force refresh icon cache using QtWin
            QtWin.setCurrentProcessExplicitAppUserModelID(app_id)
            app_icon = QIcon("appicon.ico")
            app.setWindowIcon(app_icon)
    
    # Create shared app state
    state = AppState()
    
    # Create both pages
    selector_page = AppSelectorPage(state)
    timer_page = TimerPage(state)
    
    # Connect navigation signals
    selector_page.navigate_to_timer.connect(timer_page.show)
    selector_page.navigate_to_timer.connect(selector_page.hide)
    timer_page.navigate_to_selector.connect(selector_page.show)
    timer_page.navigate_to_selector.connect(timer_page.hide)
    
    # Show initial page
    selector_page.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
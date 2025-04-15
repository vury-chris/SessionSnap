import os
import time
import psutil
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

class TimerPage(QMainWindow):
    # Signal to navigate back to app selector
    navigate_to_selector = pyqtSignal()
    
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        
        self.setWindowTitle("Productivity Timer")
        self.setFixedSize(160, 80)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparency
        
        # Set window icon
        if os.path.exists("appicon.ico"):
            from PyQt5.QtGui import QIcon
            self.setWindowIcon(QIcon("appicon.ico"))
        
        self.init_ui()
        self.setup_window_drag()
        
        # Setup timers
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_time)
        self.update_timer.setInterval(100)  # Update every 100ms for smoother display
        
        self.check_app_timer = QTimer(self)
        self.check_app_timer.timeout.connect(self.check_target_app_running)
        self.check_app_timer.setInterval(1000)  # Check every second
        
        # Position window to top right corner
        self.position_window()
    
    def init_ui(self):
        # Main container with proper object name for styling
        self.main_widget = QWidget()
        self.main_widget.setObjectName("container")
        self.setCentralWidget(self.main_widget)
        
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(6, 4, 6, 4)
        main_layout.setSpacing(2)
        
        # Window title bar
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)
        
        back_button = QPushButton("←")
        back_button.setObjectName("back_button")
        back_button.setFixedSize(16, 16)
        back_button.setToolTip("Back")
        back_button.clicked.connect(self.on_back_clicked)
        
        window_title = QLabel(f"{self.app_state.target_app_name}")
        window_title.setObjectName("window_title")
        window_title.setMaximumWidth(80)
        
        close_button = QPushButton("×")
        close_button.setObjectName("close_button")
        close_button.setFixedSize(16, 16)
        close_button.setToolTip("Close")
        close_button.clicked.connect(self.close)
        
        title_bar.addWidget(back_button)
        title_bar.addWidget(window_title)
        title_bar.addStretch()
        title_bar.addWidget(close_button)
        
        # Content layout for timer and control
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(5)
        
        # Timer display
        self.time_label = QLabel("00:00:00")
        self.time_label.setObjectName("time_label")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Roboto", 18))
        
        # Pause button container
        button_container = QVBoxLayout()
        button_container.setContentsMargins(0, 0, 0, 0)
        button_container.addStretch()
        
        self.pause_button = QPushButton("")
        self.pause_button.setObjectName("pause_button")
        self.pause_button.setFixedSize(16, 16)
        self.pause_button.setToolTip("Pause/Resume")
        self.pause_button.clicked.connect(self.toggle_timer)
        self.pause_button.setVisible(False)  # Initially hidden
        
        button_container.addWidget(self.pause_button)
        button_container.addStretch()
        
        # Add elements to content layout
        content.addLayout(button_container)
        content.addWidget(self.time_label)
        
        # Add layouts to main layout
        main_layout.addLayout(title_bar)
        main_layout.addLayout(content)
        
        # Apply theming
        self.apply_theme()
    
    def setup_window_drag(self):
        # For dragging the window
        self.old_pos = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
    
    def apply_theme(self):
        # Style with transparency for main container, solid buttons and text
        self.setStyleSheet("""
            #container {
                background-color: rgba(177, 156, 217, 180);
                border: 1px solid rgba(154, 134, 196, 200);
                border-radius: 8px;
            }
            
            QPushButton {
                background-color: #FFEB99;
                border: 1px solid #EED982;
                border-radius: 4px;
                padding: 0px;
                color: #4A4A4A;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #FFF3BA;
            }
            
            QPushButton:pressed {
                background-color: #E6D47E;
            }
            
            #time_label {
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                background-color: transparent;
            }
            
            #window_title {
                color: #000000;
                font-weight: bold;
                font-size: 10px;
                text-overflow: ellipsis;
                background-color: transparent;
            }
            
            #back_button, #close_button {
                background-color: #FFEB99;
                border: 1px solid #EED982;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            
            #close_button:hover {
                background-color: #FFB6C1;
            }
            
            #pause_button {
                background-color: #FFEB99;
                border-radius: 8px;
                border: none;
            }
        """)
    
    def position_window(self):
        # Position to top right of the screen
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width() - self.width() - 20, 50)
    
    def show(self):
        super().show()
        
        # Start checking for app
        self.check_app_timer.start()
        
        # Update window title
        self.findChild(QLabel, "window_title").setText(self.app_state.target_app_name)
    
    def on_back_clicked(self):
        # Save session if running
        if self.app_state.is_running:
            self.app_state.save_session_stats()
        
        # Stop timers
        self.update_timer.stop()
        self.check_app_timer.stop()
        
        # Reset state
        self.app_state.is_running = False
        
        # Navigate back
        self.navigate_to_selector.emit()
    
    def closeEvent(self, event):
        # Save session if running
        if self.app_state.is_running:
            self.app_state.save_session_stats()
            
        # Stop timers
        self.update_timer.stop()
        self.check_app_timer.stop()
        
        super().closeEvent(event)
    
    def toggle_timer(self):
        if not self.app_state.is_running:
            self.start_timer()
        else:
            self.pause_timer()
    
    def start_timer(self):
        self.app_state.is_running = True
        
        if self.app_state.start_time == 0:
            self.app_state.start_time = time.time()
        else:
            # Resume from pause: adjust start_time to account for elapsed time
            self.app_state.start_time = time.time() - self.app_state.elapsed_time
        
        self.update_timer.start()
        
        # Change button color to orange when running
        self.pause_button.setStyleSheet("background-color: #FFD699; border-radius: 8px; border: none;")
        self.pause_button.setVisible(True)
    
    def pause_timer(self):
        # Save current elapsed time before pausing
        if self.app_state.is_running:
            self.app_state.elapsed_time = time.time() - self.app_state.start_time
        
        self.app_state.is_running = False
        self.update_timer.stop()
        
        # Change button color back to yellow when paused
        self.pause_button.setStyleSheet("background-color: #FFEB99; border-radius: 8px; border: none;")
    
    def update_time(self):
        if self.app_state.is_running:
            self.app_state.elapsed_time = time.time() - self.app_state.start_time
            self.update_display()
    
    def update_display(self):
        hours, remainder = divmod(int(self.app_state.elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.time_label.setText(time_str)
    
    def check_target_app_running(self):
        if not self.app_state.target_app:
            return
            
        target_basename = os.path.basename(self.app_state.target_app).lower()
        app_running = False
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_exe = proc.info['exe']
                if process_exe and os.path.basename(process_exe).lower() == target_basename:
                    app_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Auto-start/stop timer based on app state
        if app_running and not self.app_state.is_running and self.app_state.start_time == 0:
            # App just started, auto-start timer
            self.start_timer()
        elif not app_running and self.app_state.is_running:
            # App was closed, auto-pause timer
            self.pause_timer()
            # Save session stats
            self.app_state.save_session_stats()
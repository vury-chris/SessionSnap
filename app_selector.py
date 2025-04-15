import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont

class AppSelectorPage(QMainWindow):
    # Signal to navigate to timer page
    navigate_to_timer = pyqtSignal()
    
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        
        self.setWindowTitle("App Selector")
        self.setFixedSize(180, 140)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Set window icon
        if os.path.exists("appicon.ico"):
            from PyQt5.QtGui import QIcon
            self.setWindowIcon(QIcon("appicon.ico"))
        
        self.init_ui()
        self.apply_theme()
        self.setup_window_drag()
        
        # Position window to center of screen
        self.center_window()
    
    def init_ui(self):
        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 6, 8, 8)
        main_layout.setSpacing(6)
        
        # Window title bar
        title_bar = QHBoxLayout()
        
        window_title = QLabel("Select App")
        window_title.setObjectName("window_title")
        
        close_button = QPushButton("×")
        close_button.setObjectName("close_button")
        close_button.setFixedSize(16, 16)
        close_button.setToolTip("Close")
        close_button.clicked.connect(self.close)
        
        title_bar.addWidget(window_title)
        title_bar.addStretch()
        title_bar.addWidget(close_button)
        
        # App selection
        self.app_selector = QComboBox()
        self.app_selector.setObjectName("app_selector")
        self.app_selector.setMinimumHeight(24)
        self.populate_recent_apps()
        
        # Browse button
        browse_layout = QHBoxLayout()
        
        browse_button = QPushButton("Browse...")
        browse_button.setObjectName("browse_button")
        browse_button.setFixedHeight(24)
        browse_button.clicked.connect(self.browse_for_app)
        
        browse_layout.addStretch()
        browse_layout.addWidget(browse_button)
        browse_layout.addStretch()
        
        # Begin button
        self.begin_button = QPushButton("Begin")
        self.begin_button.setObjectName("begin_button")
        self.begin_button.setFixedHeight(28)
        self.begin_button.clicked.connect(self.on_begin_clicked)
        self.begin_button.setEnabled(False)
        
        # Add all elements to main layout
        main_layout.addLayout(title_bar)
        main_layout.addWidget(QLabel("Select an application to track:"))
        main_layout.addWidget(self.app_selector)
        main_layout.addLayout(browse_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.begin_button)
        
        # Connect signals
        self.app_selector.currentIndexChanged.connect(self.on_app_selected)
    
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
        # Set pastel purple and yellow theme
        self.setStyleSheet("""
            QWidget {
                background-color: #B19CD9; /* Pastel purple */
                color: #4A4A4A;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 10px;
            }
            QMainWindow {
                border-radius: 8px;
                background-color: #B19CD9;
                border: 1px solid #9A86C4;
            }
            QComboBox {
                background-color: #D3BCE4;
                border: 1px solid #9A86C4;
                border-radius: 4px;
                padding: 3px;
                color: #4A4A4A;
                font-size: 9px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 16px;
                border-left: 1px solid #9A86C4;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: #D3BCE4;
                border: 1px solid #9A86C4;
                selection-background-color: #FFEB99; /* Pastel yellow */
            }
            QPushButton {
                background-color: #FFEB99; /* Pastel yellow */
                border: 1px solid #EED982;
                border-radius: 4px;
                padding: 3px;
                color: #4A4A4A;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #FFF3BA;
            }
            QPushButton:pressed {
                background-color: #E6D47E;
            }
            QPushButton:disabled {
                background-color: #E6DCB5;
                color: #8A8A8A;
            }
            QLabel {
                color: #4A4A4A;
                font-size: 10px;
            }
            #window_title {
                font-weight: bold;
                font-size: 10px;
            }
            #close_button {
                background-color: #FFEB99;
                border: 1px solid #EED982;
                border-radius: 3px;
                padding: 0px;
                font-size: 10px;
                font-weight: bold;
            }
            #close_button:hover {
                background-color: #FFB6C1;
            }
            #begin_button {
                font-size: 11px;
            }
        """)
    
    def center_window(self):
        # Center the window on screen
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def populate_recent_apps(self):
        self.app_selector.clear()
        self.app_selector.addItem("Select an application...")
        
        # Add recent apps from saved data
        for app in self.app_state.app_data.get("recent_apps", []):
            if os.path.exists(app["path"]):
                self.app_selector.addItem(app["name"], app["path"])
    
    def browse_for_app(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "Select Application", 
            "",
            "Applications (*.exe);;All Files (*)"
        )
        
        if file_path:
            app_name = os.path.basename(file_path)
            self.app_state.add_to_recent_apps(app_name, file_path)
            self.populate_recent_apps()
            # Select the newly added app
            self.app_selector.setCurrentIndex(self.app_selector.findData(file_path))
    
    def on_app_selected(self, index):
        if index > 0:  # Skip "Select an application..." item
            self.app_state.target_app = self.app_selector.currentData()
            self.app_state.target_app_name = self.app_selector.currentText()
            self.begin_button.setEnabled(True)
        else:
            self.app_state.target_app = ""
            self.app_state.target_app_name = ""
            self.begin_button.setEnabled(False)
    
    def on_begin_clicked(self):
        if self.app_state.target_app:
            self.navigate_to_timer.emit()
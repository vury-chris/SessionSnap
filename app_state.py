import os
import json
import time
from PyQt5.QtCore import QObject, pyqtSignal

class AppState(QObject):
    """Shared state between pages"""
    
    
    app_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        
        self.target_app = ""
        self.target_app_name = ""
        
        
        self.is_running = False
        self.elapsed_time = 0
        self.start_time = 0
        
        
        self.app_data = self.load_app_data()
    
    def load_app_data(self):
        """Load saved application data"""
        data_path = os.path.join(os.path.expanduser("~"), ".productivity_timer_data.json")
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading app data: {e}")
                
        return {"recent_apps": [], "statistics": {}}
    
    def save_app_data(self):
        """Save application data"""
        data_path = os.path.join(os.path.expanduser("~"), ".productivity_timer_data.json")
        try:
            with open(data_path, 'w') as f:
                json.dump(self.app_data, f)
        except Exception as e:
            print(f"Error saving app data: {e}")
    
    def add_to_recent_apps(self, name, path):
        """Add app to recent apps list"""
        
        self.app_data["recent_apps"] = [app for app in self.app_data.get("recent_apps", []) 
                                       if app["path"] != path]
        
        
        self.app_data["recent_apps"].insert(0, {"name": name, "path": path})
        
        
        self.app_data["recent_apps"] = self.app_data["recent_apps"][:5]
        
        
        self.save_app_data()
    
    def save_session_stats(self):
        """Save session statistics"""
        if self.elapsed_time <= 0 or not self.target_app_name:
            return
            
        
        if self.target_app_name not in self.app_data.get("statistics", {}):
            self.app_data["statistics"][self.target_app_name] = {
                "total_time": 0,
                "sessions": []
            }
            
        
        from datetime import datetime
        session = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "duration": int(self.elapsed_time),
            "start_time": datetime.fromtimestamp(int(self.start_time)).strftime("%H:%M:%S")
        }
        
        self.app_data["statistics"][self.target_app_name]["sessions"].append(session)
        self.app_data["statistics"][self.target_app_name]["total_time"] += int(self.elapsed_time)
        
        
        self.save_app_data()
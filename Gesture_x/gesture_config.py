import json
import os
import numpy as np
import cv2
from datetime import datetime

class GestureConfig:
    def __init__(self, config_file="custom_gestures.json"):
        self.config_file = config_file
        self.gestures = self.load_gestures()
        
    def load_gestures(self):
        """Load custom gestures from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_gestures()
        else:
            return self.get_default_gestures()
    
    def save_gestures(self):
        """Save gestures to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.gestures, f, indent=4)
        print(f"✅ Gestures saved to {self.config_file}")
    
    def get_default_gestures(self):
        """Return default gesture configuration"""
        return {
            "mouse_mode": {
                "move": {
                    "name": "Move Cursor",
                    "fingers": [0, 1, 0, 0, 0],  # Index finger up
                    "description": "Index finger up only"
                },
                "left_click": {
                    "name": "Left Click",
                    "type": "pinch",
                    "fingers": [1, 2],  # Thumb and index
                    "threshold": 30,
                    "description": "Pinch thumb and index finger"
                },
                "right_click": {
                    "name": "Right Click",
                    "type": "pinch",
                    "fingers": [2, 3],  # Index and middle
                    "threshold": 30,
                    "description": "Pinch index and middle fingers"
                },
                "scroll": {
                    "name": "Scroll",
                    "fingers": [0, 0, 0, 0, 0],  # Fist
                    "description": "Make a fist and move up/down"
                }
            },
            "presentation_mode": {
                "next_slide": {
                    "name": "Next Slide",
                    "type": "swipe",
                    "direction": "right",
                    "threshold": 100,
                    "description": "Swipe hand right"
                },
                "prev_slide": {
                    "name": "Previous Slide",
                    "type": "swipe",
                    "direction": "left",
                    "threshold": 100,
                    "description": "Swipe hand left"
                }
            },
            "global": {
                "switch_mode": {
                    "name": "Switch Mode",
                    "fingers": [1, 1, 1, 1, 1],  # All fingers up
                    "description": "Show all five fingers"
                }
            }
        }
    
    def add_custom_gesture(self, mode, gesture_id, gesture_data):
        """Add a new custom gesture"""
        if mode not in self.gestures:
            self.gestures[mode] = {}
        
        self.gestures[mode][gesture_id] = gesture_data
        self.save_gestures()
        print(f"✅ Custom gesture '{gesture_data['name']}' added!")
    
    def update_gesture(self, mode, gesture_id, gesture_data):
        """Update existing gesture"""
        if mode in self.gestures and gesture_id in self.gestures[mode]:
            self.gestures[mode][gesture_id].update(gesture_data)
            self.save_gestures()
            print(f"✅ Gesture '{gesture_data['name']}' updated!")
    
    def delete_gesture(self, mode, gesture_id):
        """Delete a gesture"""
        if mode in self.gestures and gesture_id in self.gestures[mode]:
            del self.gestures[mode][gesture_id]
            self.save_gestures()
            print(f"✅ Gesture deleted!")
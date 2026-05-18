import numpy as np
import time
from collections import deque

class GestureRecognizerEnhanced:
    def __init__(self, config):
        self.config = config
        self.prev_hand_x = None
        self.prev_hand_y = None
        self.gesture_start_time = {}
        self.gesture_active = {}
        self.gesture_history = deque(maxlen=10)
        self.double_click_timer = 0
        
    def recognize_gesture(self, lm_list, fingers, mode):
        """Enhanced gesture recognition with hold time and cooldown"""
        if len(lm_list) == 0:
            return 'idle'
        
        current_time = time.time()
        
        # Get all possible gestures based on mode
        possible_gestures = []
        
        # Check each gesture in config
        for gesture_key, gesture_data in self.config.GESTURES.items():
            # Skip if not string (for backward compatibility)
            if not isinstance(gesture_data, dict):
                continue
                
            gesture_name = gesture_data['name']
            
            # Check if gesture belongs to current mode
            if mode == 'mouse_mode':
                if gesture_name in ['move', 'left_click', 'right_click', 'double_click', 
                                  'scroll', 'scroll_up', 'scroll_down']:
                    possible_gestures.append((gesture_key, gesture_data))
            elif mode == 'presentation_mode':
                if gesture_name in ['next_slide', 'prev_slide', 'start_presentation', 
                                  'end_presentation']:
                    possible_gestures.append((gesture_key, gesture_data))
            
            # Global gestures always checked
            if gesture_name in ['switch_mode']:
                possible_gestures.append((gesture_key, gesture_data))
        
        # Check each possible gesture
        for gesture_key, gesture_data in possible_gestures:
            if self.match_gesture(lm_list, fingers, gesture_data):
                # Check if gesture is being held
                if gesture_key not in self.gesture_start_time:
                    self.gesture_start_time[gesture_key] = current_time
                    self.gesture_active[gesture_key] = False
                
                hold_time = current_time - self.gesture_start_time[gesture_key]
                min_hold = gesture_data.get('min_hold', 0.1)
                
                # Check cooldown
                if gesture_key in self.gesture_active and self.gesture_active[gesture_key]:
                    cooldown = gesture_data.get('cooldown', 0.3)
                    if current_time - self.gesture_active[gesture_key] < cooldown:
                        continue
                
                # If held long enough, activate gesture
                if hold_time >= min_hold and not self.gesture_active.get(gesture_key, False):
                    self.gesture_active[gesture_key] = current_time
                    self.gesture_history.append((gesture_name, current_time))
                    
                    # Special handling for double click
                    if gesture_name == 'pinch' and self.check_double_click():
                        return 'double_click'
                    
                    return gesture_name
            else:
                # Reset if gesture not maintained
                if gesture_key in self.gesture_start_time:
                    del self.gesture_start_time[gesture_key]
        
        return 'idle'
    
    def match_gesture(self, lm_list, fingers, gesture_data):
        """Enhanced gesture matching"""
        gesture_type = gesture_data.get('type', 'finger_pattern')
        
        try:
            if gesture_type == 'finger_pattern':
                # Match exact finger pattern
                expected_fingers = gesture_data.get('fingers', [])
                if len(expected_fingers) == 5 and len(fingers) == 5:
                    return all(f == e for f, e in zip(fingers, expected_fingers))
            
            elif gesture_type == 'pinch':
                # Pinch detection with dynamic threshold
                finger1, finger2 = gesture_data.get('fingers', [4, 8])
                base_threshold = gesture_data.get('threshold', 30)
                
                if len(lm_list) > max(finger1, finger2):
                    x1, y1 = lm_list[finger1][1], lm_list[finger1][2]
                    x2, y2 = lm_list[finger2][1], lm_list[finger2][2]
                    
                    # Calculate distance
                    distance = np.hypot(x2 - x1, y2 - y1)
                    
                    # Dynamic threshold based on hand distance from camera
                    hand_size = self.get_hand_size(lm_list)
                    dynamic_threshold = base_threshold * (hand_size / 100)
                    
                    return distance < dynamic_threshold
            
            elif gesture_type == 'double_pinch':
                # Double pinch detection
                return self.check_double_pinch(lm_list, gesture_data)
            
            elif gesture_type == 'swipe':
                # Swipe detection with direction
                direction = gesture_data.get('direction', 'right')
                threshold = gesture_data.get('threshold', 100)
                
                if len(lm_list) > 0:
                    current_x = lm_list[0][1]
                    current_y = lm_list[0][2]
                    
                    if self.prev_hand_x is None:
                        self.prev_hand_x = current_x
                        self.prev_hand_y = current_y
                        return False
                    
                    movement_x = current_x - self.prev_hand_x
                    movement_y = current_y - self.prev_hand_y
                    
                    self.prev_hand_x = current_x
                    self.prev_hand_y = current_y
                    
                    if direction == 'right' and movement_x > threshold:
                        return True
                    elif direction == 'left' and movement_x < -threshold:
                        return True
                    elif direction == 'up' and movement_y < -threshold:
                        return True
                    elif direction == 'down' and movement_y > threshold:
                        return True
            
            elif 'fingers' in gesture_data:
                # Legacy support
                expected_fingers = gesture_data.get('fingers', [])
                if len(expected_fingers) == 5 and len(fingers) == 5:
                    return all(f == e for f, e in zip(fingers, expected_fingers))
        
        except Exception as e:
            print(f"Error matching gesture: {e}")
        
        return False
    
    def get_hand_size(self, lm_list):
        """Calculate hand size for dynamic thresholds"""
        if len(lm_list) < 21:
            return 100
        
        wrist = lm_list[0]
        middle_tip = lm_list[12]
        
        # Distance from wrist to middle finger tip as hand size
        size = np.hypot(middle_tip[1] - wrist[1], middle_tip[2] - wrist[2])
        return max(size, 1)  # Avoid division by zero
    
    def check_double_pinch(self, lm_list, gesture_data):
        """Check for double pinch gesture"""
        # Implement double pinch logic
        return False
    
    def check_double_click(self):
        """Check if current pinch should be a double click"""
        current_time = time.time()
        
        # Count pinches in last 0.3 seconds
        recent_pinches = [g for g, t in self.gesture_history 
                         if g == 'pinch' and current_time - t < 0.3]
        
        return len(recent_pinches) >= 2
    
    def get_gesture_hold_progress(self, gesture_name):
        """Get hold progress for UI feedback"""
        if gesture_name in self.gesture_start_time:
            hold_time = time.time() - self.gesture_start_time[gesture_name]
            gesture_data = self.get_gesture_data(gesture_name)
            min_hold = gesture_data.get('min_hold', 0.1) if gesture_data else 0.1
            return min(hold_time / min_hold, 1.0)
        return 0
    
    def get_gesture_data(self, gesture_name):
        """Get gesture data by name"""
        for gesture_data in self.config.GESTURES.values():
            if isinstance(gesture_data, dict) and gesture_data.get('name') == gesture_name:
                return gesture_data
        return None
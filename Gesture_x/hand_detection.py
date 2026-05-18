import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import time

class HandDetectorEnhanced:
    def __init__(self, mode=False, max_hands=1, detection_con=0.8, track_con=0.8):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con,
            model_complexity=1  # 0 = Lite, 1 = Full (more accurate)
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.tip_ids = [4, 8, 12, 16, 20]
        
        # Smoothing filters
        self.position_history = deque(maxlen=5)  # For moving average
        self.kalman_filters = {}  # Kalman filters for each landmark
        
        # Handedness tracking
        self.hand_type = None
        
    def init_kalman(self, landmark_id):
        """Initialize Kalman filter for a landmark"""
        kalman = cv2.KalmanFilter(4, 2)
        kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                            [0, 1, 0, 0]], np.float32)
        kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                           [0, 1, 0, 1],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]], np.float32)
        kalman.processNoiseCov = np.array([[1, 0, 0, 0],
                                          [0, 1, 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]], np.float32) * 1e-4
        return kalman
        
    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False
        self.results = self.hands.process(img_rgb)
        img_rgb.flags.writeable = True
        
        if self.results.multi_hand_landmarks:
            for idx, hand_lms in enumerate(self.results.multi_hand_landmarks):
                # Get hand type (left/right)
                if self.results.multi_handedness:
                    self.hand_type = self.results.multi_handedness[idx].classification[0].label
                
                if draw:
                    # Draw with custom styles
                    self.mp_draw.draw_landmarks(
                        img,
                        hand_lms,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_styles.get_default_hand_landmarks_style(),
                        self.mp_styles.get_default_hand_connections_style()
                    )
                    
                    # Draw hand type
                    if self.hand_type:
                        h, w, _ = img.shape
                        x = int(hand_lms.landmark[0].x * w)
                        y = int(hand_lms.landmark[0].y * h)
                        cv2.putText(img, f"{self.hand_type} Hand", (x, y-20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        return img
    
    def find_position(self, img, hand_no=0, draw=True, smooth=True):
        x_list = []
        y_list = []
        bbox = []
        self.lm_list = []
        
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            h, w, c = img.shape
            
            for id, lm in enumerate(my_hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                
                # Apply Kalman filter if enabled
                if smooth and id in self.kalman_filters:
                    kalman = self.kalman_filters[id]
                    measurement = np.array([[np.float32(cx)], [np.float32(cy)]])
                    kalman.correct(measurement)
                    prediction = kalman.predict()
                    cx, cy = int(prediction[0]), int(prediction[1])
                else:
                    self.kalman_filters[id] = self.init_kalman(id)
                
                x_list.append(cx)
                y_list.append(cy)
                self.lm_list.append([id, cx, cy])
                
                if draw:
                    # Different colors for fingertips
                    color = (0, 255, 0) if id in self.tip_ids else (255, 0, 255)
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)
                    
                    # Draw landmark numbers (for debugging)
                    if id in self.tip_ids:
                        cv2.putText(img, str(id), (cx+10, cy-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Get bounding box
            if x_list and y_list:
                x_min, x_max = max(0, min(x_list)), min(w, max(x_list))
                y_min, y_max = max(0, min(y_list)), min(h, max(y_list))
                bbox = x_min, y_min, x_max - x_min, y_max - y_min
                
                if draw:
                    # Draw bounding box with hand type
                    cv2.rectangle(img, (int(x_min)-20, int(y_min)-20),
                                (int(x_max)+20, int(y_max)+20), (0, 255, 0), 2)
                    
                    # Draw hand type in bounding box
                    if self.hand_type:
                        cv2.putText(img, self.hand_type, (int(x_min), int(y_min)-30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return self.lm_list, bbox
    
    def fingers_up(self):
        """Enhanced finger detection with angle checks"""
        fingers = []
        
        if len(self.lm_list) < 21:
            return fingers
        
        # Thumb - check both x and y coordinates for better accuracy
        thumb_tip = self.lm_list[4]
        thumb_ip = self.lm_list[3]
        thumb_mcp = self.lm_list[2]
        
        # For right hand, thumb is up if tip.x > ip.x
        # For left hand, thumb is up if tip.x < ip.x
        if self.hand_type == "Right":
            if thumb_tip[1] < thumb_ip[1] and thumb_tip[1] < thumb_mcp[1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:  # Left hand
            if thumb_tip[1] < thumb_ip[1] and thumb_tip[1] < thumb_mcp[1]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        # Other fingers - check angle for more accurate detection
        for id in range(1, 5):
            tip_id = self.tip_ids[id]
            pip_id = tip_id - 2
            mcp_id = tip_id - 3
            
            tip = self.lm_list[tip_id]
            pip = self.lm_list[pip_id]
            mcp = self.lm_list[mcp_id]
            
            # Calculate angle
            v1 = np.array([pip[1] - mcp[1], pip[2] - mcp[2]])
            v2 = np.array([tip[1] - pip[1], tip[2] - pip[2]])
            
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                angle = np.arccos(np.clip(cos_angle, -1, 1)) * 180 / np.pi
                
                # Finger is considered up if angle > 160 degrees (almost straight)
                if angle > 160:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                # Fallback to simple y-coordinate comparison
                if tip[2] < pip[2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        
        return fingers
    
    def find_distance(self, p1, p2, img=None):
        """Enhanced distance calculation with error checking"""
        if len(self.lm_list) <= max(p1, p2):
            return 0, img, [0, 0, 0, 0, 0, 0]
        
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Calculate Euclidean distance
        length = np.hypot(x2 - x1, y2 - y1)
        
        # Calculate angle between points
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        
        if img is not None:
            # Draw line with color based on distance
            color = (0, 255, 0) if length < 30 else (0, 0, 255)
            cv2.line(img, (x1, y1), (x2, y2), color, 3)
            cv2.circle(img, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 8, (0, 255, 0), cv2.FILLED)
            
            # Show distance value
            cv2.putText(img, f"{int(length)}px", (cx-30, cy-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return length, img, [x1, y1, x2, y2, cx, cy]
    
    def get_hand_orientation(self):
        """Determine hand orientation (palm facing towards/away from camera)"""
        if len(self.lm_list) < 21:
            return "unknown"
        
        # Use wrist and MCP points to determine orientation
        wrist = self.lm_list[0]
        index_mcp = self.lm_list[5]
        pinky_mcp = self.lm_list[17]
        
        # Calculate palm center
        palm_center_x = (index_mcp[1] + pinky_mcp[1]) // 2
        palm_center_y = (index_mcp[2] + pinky_mcp[2]) // 2
        
        # Compare with wrist position
        if palm_center_y < wrist[2]:
            return "facing_up"
        else:
            return "facing_down"
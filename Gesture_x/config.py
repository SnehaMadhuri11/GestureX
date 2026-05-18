# ============================================
# GESTUREX - ADVANCED CONFIGURATION
# Optimized for Maximum Accuracy
# ============================================

# ----------------------
# CAMERA SETTINGS
# ----------------------
CAMERA_ID = 0
CAMERA_WIDTH = 1280  # Increased from 640 - Higher resolution for better detection
CAMERA_HEIGHT = 720  # Increased from 480
FPS = 60  # Increased from 30 - Smoother tracking

# ----------------------
# HAND DETECTION SETTINGS
# ----------------------
# MediaPipe confidence thresholds
DETECTION_CONFIDENCE = 0.8  # Increased from 0.7 - More strict detection
TRACKING_CONFIDENCE = 0.8   # Increased from 0.5 - Better tracking stability

# Maximum number of hands to detect
MAX_HANDS = 1  # Keep at 1 for focus, change to 2 for multi-hand support

# ----------------------
# GESTURE THRESHOLDS
# ----------------------
# Pinch detection (pixels)
PINCH_THRESHOLD = 25  # Reduced from 30 - More precise pinch detection
PINCH_COOLDOWN = 0.3  # Seconds between pinch detections

# Two-finger pinch for right click
TWO_FINGER_PINCH_THRESHOLD = 30

# Scroll settings
SCROLL_SPEED = 30  # Reduced for smoother scrolling
SCROLL_SENSITIVITY = 1.5  # New: Adjust scroll sensitivity

# Cursor smoothing (lower = more responsive, higher = smoother)
SMOOTHENING = 3  # Reduced from 5 - More responsive while still smooth

# Swipe detection
SWIPE_THRESHOLD = 80  # Reduced from 100 - More sensitive swipe detection
SWIPE_COOLDOWN = 0.5  # Seconds between swipes

# ----------------------
# SCREEN RESOLUTION
# ----------------------
# Auto-detect screen resolution instead of hardcoding
import pyautogui
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Mouse movement boundaries (percentage of screen)
MOUSE_BOUNDARY_PERCENT = 10  # Ignore edges of frame for mouse control

# ----------------------
# ADVANCED FILTERING
# ----------------------
# Kalman filter parameters for cursor smoothing
USE_KALMAN_FILTER = True  # New: Enable Kalman filtering
KALMAN_PROCESS_NOISE = 1e-4
KALMAN_MEASUREMENT_NOISE = 1e-2

# Moving average filter
USE_MOVING_AVERAGE = True  # New: Smooth cursor movement
MOVING_AVERAGE_WINDOW = 5  # Number of frames to average

# ----------------------
# GESTURE RECOGNITION
# ----------------------
# Minimum finger movement to register gesture (pixels)
MIN_FINGER_MOVEMENT = 10

# Gesture hold time (seconds)
GESTURE_HOLD_TIME = 0.2  # How long a gesture must be held to register

# Cooldown times for different actions (seconds)
COOLDOWNS = {
    'left_click': 0.3,
    'right_click': 0.3,
    'scroll': 0.1,
    'next_slide': 0.5,
    'prev_slide': 0.5,
    'switch_mode': 1.0
}

# ----------------------
# GESTURE DEFINITIONS
# ----------------------
GESTURES = {
    # Mouse Control
    'MOVE': {
        'name': 'move',
        'fingers': [0, 1, 0, 0, 0],  # Index finger up
        'min_hold': 0.1,
        'cooldown': 0.05
    },
    'LEFT_CLICK': {
        'name': 'left_click',
        'type': 'pinch',
        'fingers': [4, 8],  # Thumb and index
        'threshold': PINCH_THRESHOLD,
        'min_hold': 0.15,
        'cooldown': COOLDOWNS['left_click']
    },
    'RIGHT_CLICK': {
        'name': 'right_click',
        'type': 'pinch',
        'fingers': [8, 12],  # Index and middle
        'threshold': TWO_FINGER_PINCH_THRESHOLD,
        'min_hold': 0.15,
        'cooldown': COOLDOWNS['right_click']
    },
    'DOUBLE_CLICK': {  # New gesture
        'name': 'double_click',
        'type': 'double_pinch',
        'fingers': [4, 8],
        'threshold': PINCH_THRESHOLD,
        'time_window': 0.3,  # Double click within 0.3 seconds
        'cooldown': 0.5
    },
    'SCROLL': {
        'name': 'scroll',
        'fingers': [0, 0, 0, 0, 0],  # Fist
        'min_hold': 0.2,
        'cooldown': COOLDOWNS['scroll']
    },
    'SCROLL_UP': {  # New: Specific scroll up
        'name': 'scroll_up',
        'fingers': [0, 1, 1, 0, 0],  # Index and middle up
        'direction': 'up',
        'min_hold': 0.2,
        'cooldown': 0.1
    },
    'SCROLL_DOWN': {  # New: Specific scroll down
        'name': 'scroll_down',
        'fingers': [0, 1, 1, 0, 0],  # Index and middle up
        'direction': 'down',
        'min_hold': 0.2,
        'cooldown': 0.1
    },
    
    # Presentation Control
    'NEXT_SLIDE': {
        'name': 'next_slide',
        'type': 'swipe',
        'direction': 'right',
        'threshold': SWIPE_THRESHOLD,
        'min_hold': 0.1,
        'cooldown': COOLDOWNS['next_slide']
    },
    'PREV_SLIDE': {
        'name': 'prev_slide',
        'type': 'swipe',
        'direction': 'left',
        'threshold': SWIPE_THRESHOLD,
        'min_hold': 0.1,
        'cooldown': COOLDOWNS['prev_slide']
    },
    'START_PRESENTATION': {  # New gesture
        'name': 'start_presentation',
        'fingers': [1, 1, 1, 0, 0],  # Three fingers up
        'min_hold': 0.3,
        'cooldown': 1.0
    },
    'END_PRESENTATION': {  # New gesture
        'name': 'end_presentation',
        'fingers': [0, 1, 1, 1, 0],  # Three middle fingers up
        'min_hold': 0.3,
        'cooldown': 1.0
    },
    
    # Global Controls
    'SWITCH_MODE': {
        'name': 'switch_mode',
        'fingers': [1, 1, 1, 1, 1],  # All fingers up
        'min_hold': 0.5,  # Longer hold to prevent accidental switching
        'cooldown': COOLDOWNS['switch_mode']
    },
    'IDLE': {
        'name': 'idle',
        'cooldown': 0
    }
}

# Modes
MODES = {
    'MOUSE': 'mouse_mode',
    'PRESENTATION': 'presentation_mode'
}

# ----------------------
# ADVANCED HAND TRACKING
# ----------------------
# Hand landmark indices for reference
HAND_LANDMARKS = {
    'WRIST': 0,
    'THUMB_CMC': 1,
    'THUMB_MCP': 2,
    'THUMB_IP': 3,
    'THUMB_TIP': 4,
    'INDEX_MCP': 5,
    'INDEX_PIP': 6,
    'INDEX_DIP': 7,
    'INDEX_TIP': 8,
    'MIDDLE_MCP': 9,
    'MIDDLE_PIP': 10,
    'MIDDLE_DIP': 11,
    'MIDDLE_TIP': 12,
    'RING_MCP': 13,
    'RING_PIP': 14,
    'RING_DIP': 15,
    'RING_TIP': 16,
    'PINKY_MCP': 17,
    'PINKY_PIP': 18,
    'PINKY_DIP': 19,
    'PINKY_TIP': 20
}

# ----------------------
# VISUALIZATION SETTINGS
# ----------------------
SHOW_LANDMARKS = True
SHOW_BOUNDING_BOX = True
SHOW_FPS = True
SHOW_GESTURE_HOLD = True  # Show gesture hold progress

# Colors (BGR format)
COLORS = {
    'LANDMARK': (255, 0, 255),  # Pink
    'CONNECTION': (0, 255, 0),   # Green
    'BOUNDING_BOX': (0, 255, 0), # Green
    'TEXT': (255, 255, 255),     # White
    'GESTURE_ACTIVE': (0, 255, 0), # Green
    'GESTURE_IDLE': (0, 0, 255),   # Red
    'MODE_MOUSE': (255, 255, 0),   # Cyan
    'MODE_PRESENTATION': (255, 0, 255) # Magenta
}

# ----------------------
# PERFORMANCE OPTIMIZATION
# ----------------------
# Frame skipping for better performance on slower systems
FRAME_SKIP = 0  # 0 = process every frame, 1 = process every other frame, etc.

# Region of Interest (ROI) - only process this portion of frame for hand detection
USE_ROI = False  # Set to True to enable ROI
ROI_SIZE = 300  # Size of ROI square
ROI_POSITION = 'center'  # 'center', 'top_right', 'bottom_left', etc.

# ----------------------
# DEBUGGING
# ----------------------
DEBUG_MODE = False  # Set to True for debug output
LOG_GESTURES = False  # Log recognized gestures to file
GESTURE_LOG_FILE = 'gesture_log.txt'
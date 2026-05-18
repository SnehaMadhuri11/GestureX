import cv2
import numpy as np
from hand_detector import HandDetector
from gesture_recognition import GestureRecognizer
from action_executor import ActionExecutor

# Define constants directly to avoid import issues
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.5
MODES = {
    'MOUSE': 'mouse_mode',
    'PRESENTATION': 'presentation_mode'
}
GESTURES = {
    'MOVE': 'move',
    'LEFT_CLICK': 'left_click',
    'RIGHT_CLICK': 'right_click',
    'SCROLL': 'scroll',
    'NEXT_SLIDE': 'next_slide',
    'PREV_SLIDE': 'prev_slide',
    'SWITCH_MODE': 'switch_mode',
    'IDLE': 'idle'
}

class GestureController:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(CAMERA_ID)
        self.cap.set(3, CAMERA_WIDTH)
        self.cap.set(4, CAMERA_HEIGHT)
        
        # Check if camera opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Initialize modules
        self.detector = HandDetector(
            detection_con=DETECTION_CONFIDENCE,
            track_con=TRACKING_CONFIDENCE
        )
        self.recognizer = GestureRecognizer()
        self.executor = ActionExecutor()
        
        self.current_mode = MODES['MOUSE']
        self.last_mode_switch = 0
        
    def run(self):
        print("Gesture Control Started. Press 'q' to quit.")
        
        while True:
            success, img = self.cap.read()
            if not success:
                print("Failed to grab frame")
                break
            
            # Flip image horizontally for mirror effect
            img = cv2.flip(img, 1)
            
            # Find hands and landmarks
            img = self.detector.find_hands(img)
            lm_list, bbox = self.detector.find_position(img)
            
            if len(lm_list) != 0:
                # Get fingers up/down status
                fingers = self.detector.fingers_up()
                
                if len(fingers) == 5:  # Make sure we have all fingers
                    # Recognize gesture
                    gesture = self.recognizer.recognize_gesture(lm_list, fingers, self.current_mode)
                    
                    # Handle mode switching
                    if gesture == GESTURES['SWITCH_MODE']:
                        import time
                        current_time = time.time()
                        if current_time - self.last_mode_switch > 1.0:
                            if self.current_mode == MODES['MOUSE']:
                                self.current_mode = MODES['PRESENTATION']
                            else:
                                self.current_mode = MODES['MOUSE']
                            self.last_mode_switch = current_time
                            print(f"Switched to {self.current_mode}")
                    
                    # Execute actions
                    self.execute_action(gesture, lm_list, img)
                    
                    # Draw info
                    self.draw_info(img, gesture, fingers)
            
            # Show the frame
            cv2.imshow("GestureX - AI Touchless Control", img)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
    
    def execute_action(self, gesture, lm_list, img):
        h, w, _ = img.shape
        
        if self.current_mode == MODES['MOUSE']:
            if gesture == GESTURES['MOVE'] and len(lm_list) > 8:
                # Move cursor with index finger
                x, y = lm_list[8][1], lm_list[8][2]
                self.executor.move_mouse(x, y, w, h)
                
            elif gesture == GESTURES['LEFT_CLICK']:
                if self.executor.left_click():
                    cv2.putText(img, "LEFT CLICK", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
            elif gesture == GESTURES['RIGHT_CLICK']:
                if self.executor.right_click():
                    cv2.putText(img, "RIGHT CLICK", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
            elif gesture == GESTURES['SCROLL'] and len(lm_list) > 9:
                # Scroll with hand position
                y = lm_list[9][2]
                self.executor.scroll(y, h)
                
        elif self.current_mode == MODES['PRESENTATION']:
            if gesture == GESTURES['NEXT_SLIDE']:
                self.executor.next_slide()
                cv2.putText(img, "NEXT SLIDE", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
            elif gesture == GESTURES['PREV_SLIDE']:
                self.executor.prev_slide()
                cv2.putText(img, "PREVIOUS SLIDE", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    def draw_info(self, img, gesture, fingers):
        # Draw mode
        mode_text = f"Mode: {self.current_mode.replace('_', ' ').title()}"
        cv2.putText(img, mode_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw gesture
        gesture_text = f"Gesture: {gesture.replace('_', ' ').title()}"
        cv2.putText(img, gesture_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw finger states
        if len(fingers) == 5:
            finger_state = "".join(["⬆️" if f else "⬇️" for f in fingers])
            cv2.putText(img, f"Fingers: {finger_state}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Draw instructions
        instructions = [
            "Move: Index finger up",
            "Left Click: Thumb+Index pinch",
            "Right Click: Index+Middle pinch",
            "Scroll: Fist",
            "Switch Mode: All fingers up",
            "Press 'q' to quit"
        ]
        
        y_offset = 150
        for inst in instructions:
            cv2.putText(img, inst, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y_offset += 25
import pyautogui
import time
import numpy as np

class ActionExecutor:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothening = 5
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        self.click_active = False
        self.last_click_time = 0
        self.click_cooldown = 0.3  # seconds
        
    def move_mouse(self, hand_x, hand_y, frame_width, frame_height):
        # Map hand coordinates to screen coordinates
        screen_x = np.interp(hand_x, [100, frame_width - 100], [0, self.screen_width])
        screen_y = np.interp(hand_y, [100, frame_height - 100], [0, self.screen_height])
        
        # Smoothen the movement
        self.curr_x = self.prev_x + (screen_x - self.prev_x) / self.smoothening
        self.curr_y = self.prev_y + (screen_y - self.prev_y) / self.smoothening
        
        # Move mouse
        pyautogui.moveTo(int(self.curr_x), int(self.curr_y))
        
        self.prev_x, self.prev_y = self.curr_x, self.curr_y
    
    def left_click(self):
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.click()
            self.last_click_time = current_time
            return True
        return False
    
    def right_click(self):
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.rightClick()
            self.last_click_time = current_time
            return True
        return False
    
    def scroll(self, hand_y, frame_height):
        # Map hand position to scroll amount
        scroll_amount = np.interp(hand_y, [0, frame_height], [10, -10])
        pyautogui.scroll(int(scroll_amount))
    
    def next_slide(self):
        pyautogui.press('right')
        time.sleep(0.5)
    
    def prev_slide(self):
        pyautogui.press('left')
        time.sleep(0.5)
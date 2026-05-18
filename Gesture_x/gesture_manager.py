import cv2
import numpy as np
from gesture_config import GestureConfig
from gesture_controller import GestureTrainer
from gesture_controller import HandDetector
from gesture_controller import GestureRecognitionWithCustom

class GestureManager:
    def __init__(self):
        self.config = GestureConfig()
        self.trainer = GestureTrainer()
        
    def show_menu(self):
        """Display gesture management menu"""
        while True:
            print("\n" + "="*50)
            print("🎮 GESTURE MANAGER")
            print("="*50)
            print("1. View all gestures")
            print("2. Add new custom gesture")
            print("3. Edit existing gesture")
            print("4. Delete gesture")
            print("5. Reset to default gestures")
            print("6. Export gestures")
            print("7. Import gestures")
            print("8. Test gesture recognition")
            print("9. Back to main application")
            
            choice = input("\nEnter your choice (1-9): ")
            
            if choice == '1':
                self.view_gestures()
            elif choice == '2':
                self.trainer.train_new_gesture()
            elif choice == '3':
                self.edit_gesture()
            elif choice == '4':
                self.delete_gesture()
            elif choice == '5':
                self.reset_to_default()
            elif choice == '6':
                self.export_gestures()
            elif choice == '7':
                self.import_gestures()
            elif choice == '8':
                self.test_recognition()
            elif choice == '9':
                break
    
    def view_gestures(self):
        """Display all configured gestures"""
        print("\n📋 CURRENT GESTURES")
        print("="*50)
        
        for mode, gestures in self.config.gestures.items():
            print(f"\n🔹 {mode.upper()} MODE:")
            for gesture_id, data in gestures.items():
                print(f"  • {data['name']} ({gesture_id})")
                print(f"    Description: {data.get('description', 'No description')}")
                if 'fingers' in data:
                    print(f"    Finger pattern: {data['fingers']}")
                if 'threshold' in data:
                    print(f"    Threshold: {data['threshold']}")
    
    def edit_gesture(self):
        """Edit an existing gesture"""
        self.view_gestures()
        
        mode = input("\nEnter mode (mouse/presentation/global): ").lower()
        gesture_id = input("Enter gesture ID to edit: ")
        
        if mode in self.config.gestures and gesture_id in self.config.gestures[mode]:
            print("\nLeave blank to keep current value")
            
            current = self.config.gestures[mode][gesture_id]
            new_data = {}
            
            name = input(f"Name [{current['name']}]: ")
            if name:
                new_data['name'] = name
            
            desc = input(f"Description [{current.get('description', '')}]: ")
            if desc:
                new_data['description'] = desc
            
            if 'threshold' in current:
                thresh = input(f"Threshold [{current['threshold']}]: ")
                if thresh:
                    new_data['threshold'] = int(thresh)
            
            self.config.update_gesture(mode, gesture_id, new_data)
        else:
            print("❌ Gesture not found!")
    
    def delete_gesture(self):
        """Delete a gesture"""
        self.view_gestures()
        
        mode = input("\nEnter mode: ").lower()
        gesture_id = input("Enter gesture ID to delete: ")
        
        confirm = input(f"Are you sure you want to delete {gesture_id}? (y/n): ")
        if confirm.lower() == 'y':
            self.config.delete_gesture(mode, gesture_id)
    
    def reset_to_default(self):
        """Reset to default gestures"""
        confirm = input("⚠️ This will delete all custom gestures. Continue? (y/n): ")
        if confirm.lower() == 'y':
            self.config.gestures = self.config.get_default_gestures()
            self.config.save_gestures()
            print("✅ Reset to default gestures!")
    
    def export_gestures(self):
        """Export gestures to a file"""
        filename = input("Enter export filename (default: gestures_export.json): ")
        if not filename:
            filename = "gestures_export.json"
        
        import shutil
        shutil.copy(self.config.config_file, filename)
        print(f"✅ Gestures exported to {filename}")
    
    def import_gestures(self):
        """Import gestures from a file"""
        filename = input("Enter filename to import: ")
        
        try:
            import json
            with open(filename, 'r') as f:
                imported = json.load(f)
            
            self.config.gestures.update(imported)
            self.config.save_gestures()
            print(f"✅ Gestures imported from {filename}")
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    def test_recognition(self):
        """Test gesture recognition in real-time"""
        from gesture_controller import GestureController
        from gesture_recognition import GestureRecognizer
        
        print("\n🎥 Testing gesture recognition...")
        print("Press 'q' to quit")
        
        cap = cv2.VideoCapture(0)
        detector = HandDetector()
        recognizer = GestureRecognitionWithCustom()
        
        while True:
            success, img = cap.read()
            if not success:
                break
            
            img = cv2.flip(img, 1)
            img = detector.find_hands(img)
            lm_list, bbox = detector.find_position(img)
            
            if len(lm_list) != 0:
                fingers = detector.fingers_up()
                gesture = recognizer.recognize_gesture(lm_list, fingers, 'mouse')
                
                # Display recognized gesture
                cv2.putText(img, f"Gesture: {gesture}", (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Display finger states
                finger_text = "".join(["⬆️" if f else "⬇️" for f in fingers])
                cv2.putText(img, finger_text, (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow("Gesture Test", img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
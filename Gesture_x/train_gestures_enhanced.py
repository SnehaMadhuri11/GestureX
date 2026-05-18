#!/usr/bin/env python3
"""
Enhanced Gesture Training System
Let users train gestures exactly how they want
"""

import cv2
import numpy as np
import os
import time
import pickle
import json
from hand_detection import HandDetector
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class EnhancedGestureTrainer:
    def __init__(self):
        self.detector = HandDetector()
        self.user_name = self.get_user_name()
        self.gesture_map = {}  # Maps user gestures to actions
        
    def get_user_name(self):
        """Get or create user profile"""
        users_dir = "gesture_models/users"
        os.makedirs(users_dir, exist_ok=True)
        
        users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
        
        print("\n👤 User Profile")
        print("=" * 50)
        if users:
            print("Existing users:")
            for i, user in enumerate(users):
                print(f"  {i+1}. {user}")
            print("  n. Create new user")
            
            choice = input("\nSelect user: ")
            if choice.isdigit() and 1 <= int(choice) <= len(users):
                return users[int(choice)-1]
        
        return input("Enter your name: ").lower().replace(" ", "_")
    
    def show_menu(self):
        """Main training menu"""
        while True:
            print("\n" + "="*60)
            print(f"🎯 GESTURE TRAINING - User: {self.user_name}")
            print("="*60)
            print("1. Train New Gesture")
            print("2. List Trained Gestures")
            print("3. Map Gestures to Actions")
            print("4. Test Recognition")
            print("5. Save Model")
            print("6. Load Existing Model")
            print("7. Delete Gesture")
            print("8. Advanced Settings")
            print("9. Back")
            
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                self.train_gesture()
            elif choice == '2':
                self.list_gestures()
            elif choice == '3':
                self.map_gestures()
            elif choice == '4':
                self.test_recognition()
            elif choice == '5':
                self.save_model()
            elif choice == '6':
                self.load_model()
            elif choice == '7':
                self.delete_gesture()
            elif choice == '8':
                self.advanced_settings()
            elif choice == '9':
                break
    
    def train_gesture(self):
        """Train a new gesture with user preferences"""
        print("\n🎯 Train New Gesture")
        print("=" * 50)
        
        # Get gesture name
        gesture_name = input("Gesture name (e.g., 'thumbs_up'): ").lower()
        
        # Ask what action this gesture should perform
        print("\nWhat action should this gesture perform?")
        actions = [
            "1. Mouse Movement",
            "2. Left Click",
            "3. Right Click",
            "4. Scroll Up",
            "5. Scroll Down",
            "6. Next Slide",
            "7. Previous Slide",
            "8. Switch Mode",
            "9. Custom Action (type name)"
        ]
        
        for action in actions:
            print(action)
        
        action_choice = input("\nSelect action (1-9): ")
        
        action_map = {
            '1': 'move',
            '2': 'left_click',
            '3': 'right_click',
            '4': 'scroll_up',
            '5': 'scroll_down',
            '6': 'next_slide',
            '7': 'prev_slide',
            '8': 'switch_mode',
            '9': input("Enter custom action name: ").lower()
        }
        
        action = action_map.get(action_choice, 'custom')
        
        # Get number of samples
        num_samples = int(input("Number of samples to collect (50-200): ") or "100")
        
        # Create user directory
        user_dir = f"gesture_models/users/{self.user_name}"
        os.makedirs(user_dir, exist_ok=True)
        
        # Create gesture directory
        gesture_dir = os.path.join(user_dir, gesture_name)
        os.makedirs(gesture_dir, exist_ok=True)
        
        print(f"\n🖐️ Show the '{gesture_name}' gesture to camera")
        print(f"📸 Need {num_samples} samples")
        print("Press SPACE to capture, 'q' to quit")
        
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)
        
        collected = 0
        while collected < num_samples:
            success, img = cap.read()
            if not success:
                break
            
            img = cv2.flip(img, 1)
            img = self.detector.find_hands(img)
            lm_list, bbox = self.detector.find_position(img)
            
            # Extract and save features
            if len(lm_list) > 0:
                features = self.extract_features(lm_list)
                
                # Display info
                cv2.putText(img, f"Gesture: {gesture_name}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"Collected: {collected}/{num_samples}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Progress bar
                progress = int((collected / num_samples) * 30)
                bar = '█' * progress + '░' * (30 - progress)
                cv2.putText(img, f"[{bar}]", (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("Gesture Training", img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and len(lm_list) > 0:
                # Save features
                if features is not None:
                    filename = os.path.join(gesture_dir, f"{gesture_name}_{collected:04d}.npy")
                    np.save(filename, features)
                    collected += 1
                    print(f"✅ Captured {collected}/{num_samples}")
                    time.sleep(0.1)  # Debounce
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Save gesture-action mapping
        self.gesture_map[gesture_name] = {
            'action': action,
            'samples': collected,
            'timestamp': time.time()
        }
        
        print(f"\n✅ Trained '{gesture_name}' -> '{action}' with {collected} samples")
    
    def map_gestures(self):
        """Map gestures to actions"""
        print("\n🔄 Map Gestures to Actions")
        print("=" * 50)
        
        # Load existing gestures
        user_dir = f"gesture_models/users/{self.user_name}"
        if not os.path.exists(user_dir):
            print("❌ No gestures found. Train some first!")
            return
        
        gestures = [d for d in os.listdir(user_dir) 
                   if os.path.isdir(os.path.join(user_dir, d))]
        
        if not gestures:
            print("❌ No gestures found")
            return
        
        print("Available gestures:")
        for i, gesture in enumerate(gestures):
            print(f"  {i+1}. {gesture}")
        
        print("\nAvailable actions:")
        actions = [
            'move', 'left_click', 'right_click', 'double_click',
            'scroll_up', 'scroll_down', 'next_slide', 'prev_slide',
            'switch_mode', 'volume_up', 'volume_down', 'play_pause',
            'custom'
        ]
        
        for i, action in enumerate(actions):
            print(f"  {i+1}. {action}")
        
        # Map each gesture
        for gesture in gestures:
            print(f"\n🎯 Gesture: {gesture}")
            action_idx = input(f"  Select action (1-{len(actions)}): ")
            
            if action_idx.isdigit() and 1 <= int(action_idx) <= len(actions):
                action = actions[int(action_idx)-1]
                self.gesture_map[gesture] = {
                    'action': action,
                    'timestamp': time.time()
                }
                print(f"  ✅ Mapped {gesture} -> {action}")
        
        # Save mapping
        mapping_file = f"gesture_models/users/{self.user_name}/gesture_map.json"
        with open(mapping_file, 'w') as f:
            json.dump(self.gesture_map, f, indent=4)
        
        print(f"\n✅ Mapping saved to {mapping_file}")
    
    def extract_features(self, lm_list):
        """Extract features from landmarks"""
        if len(lm_list) < 21:
            return None
        
        features = []
        
        # Normalized positions
        wrist_x, wrist_y = lm_list[0][1], lm_list[0][2]
        for lm in lm_list:
            features.append(lm[1] - wrist_x)
            features.append(lm[2] - wrist_y)
        
        # Distances between fingertips
        tip_ids = [4, 8, 12, 16, 20]
        for i in range(len(tip_ids)):
            for j in range(i+1, len(tip_ids)):
                x1, y1 = lm_list[tip_ids[i]][1], lm_list[tip_ids[i]][2]
                x2, y2 = lm_list[tip_ids[j]][1], lm_list[tip_ids[j]][2]
                dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                features.append(dist)
        
        return np.array(features)
    
    def load_dataset(self):
        """Load all training data"""
        X = []
        y = []
        gesture_names = []
        
        user_dir = f"gesture_models/users/{self.user_name}"
        if not os.path.exists(user_dir):
            return X, y, gesture_names
        
        gestures = [d for d in os.listdir(user_dir) 
                   if os.path.isdir(os.path.join(user_dir, d)) and d != 'models']
        
        for label, gesture in enumerate(gestures):
            gesture_dir = os.path.join(user_dir, gesture)
            npy_files = [f for f in os.listdir(gesture_dir) if f.endswith('.npy')]
            
            for npy_file in npy_files:
                features = np.load(os.path.join(gesture_dir, npy_file))
                X.append(features)
                y.append(label)
            
            gesture_names.append(gesture)
            print(f"✅ Loaded {len(npy_files)} samples for '{gesture}'")
        
        return np.array(X), np.array(y), gesture_names
    
    def save_model(self):
        """Save trained model"""
        print("\n💾 Saving Model")
        print("=" * 50)
        
        # Load dataset
        X, y, gesture_names = self.load_dataset()
        
        if len(X) == 0:
            print("❌ No training data found")
            return
        
        # Train model
        print("🧠 Training model...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42
        )
        model.fit(X_scaled, y)
        
        # Create label map
        label_map = {i: name for i, name in enumerate(gesture_names)}
        
        # Save model
        model_dir = f"gesture_models/users/{self.user_name}/models"
        os.makedirs(model_dir, exist_ok=True)
        
        timestamp = int(time.time())
        model_path = f"{model_dir}/model_{timestamp}.pkl"
        
        model_data = {
            'model': model,
            'scaler': scaler,
            'label_map': label_map,
            'gesture_map': self.gesture_map,
            'user': self.user_name,
            'timestamp': timestamp
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        # Also save as default
        default_path = f"gesture_models/{self.user_name}_model.pkl"
        with open(default_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {model_path}")
        print(f"✅ Default model saved to {default_path}")
        print(f"📊 Gestures: {gesture_names}")
    
    def load_model(self):
        """Load existing model"""
        print("\n📂 Load Model")
        print("=" * 50)
        
        model_dir = f"gesture_models/users/{self.user_name}/models"
        if not os.path.exists(model_dir):
            print("❌ No models found")
            return
        
        models = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
        
        if not models:
            print("❌ No models found")
            return
        
        print("Available models:")
        for i, model in enumerate(models):
            print(f"  {i+1}. {model}")
        
        choice = input("\nSelect model number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            model_path = os.path.join(model_dir, models[int(choice)-1])
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Save as default for this user
            default_path = f"gesture_models/{self.user_name}_model.pkl"
            with open(default_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✅ Loaded model with gestures: {list(model_data['label_map'].values())}")
            print(f"✅ Set as default for user {self.user_name}")
    
    def test_recognition(self):
        """Test trained model"""
        print("\n🎥 Testing Recognition")
        print("Press 'q' to quit")
        
        # Try to load default model
        model_path = f"gesture_models/{self.user_name}_model.pkl"
        if not os.path.exists(model_path):
            print(f"❌ No model found for {self.user_name}")
            return
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        scaler = model_data['scaler']
        label_map = model_data['label_map']
        gesture_map = model_data.get('gesture_map', {})
        
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)
        
        prediction_buffer = []
        
        while True:
            success, img = cap.read()
            if not success:
                break
            
            img = cv2.flip(img, 1)
            img = self.detector.find_hands(img)
            lm_list, bbox = self.detector.find_position(img)
            
            if len(lm_list) > 0:
                features = self.extract_features(lm_list)
                
                if features is not None:
                    # Predict
                    features_scaled = scaler.transform([features])
                    pred_idx = model.predict(features_scaled)[0]
                    probs = model.predict_proba(features_scaled)[0]
                    confidence = np.max(probs)
                    
                    gesture_name = label_map[pred_idx]
                    
                    # Smooth predictions
                    prediction_buffer.append(gesture_name)
                    if len(prediction_buffer) > 5:
                        prediction_buffer.pop(0)
                    
                    from collections import Counter
                    if prediction_buffer:
                        most_common = Counter(prediction_buffer).most_common(1)[0][0]
                        gesture_name = most_common
                    
                    # Get mapped action if available
                    action = gesture_map.get(gesture_name, {}).get('action', gesture_name)
                    
                    # Display
                    color = (0, 255, 0) if confidence > 0.8 else (0, 255, 255)
                    cv2.putText(img, f"Gesture: {gesture_name}", (10, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    cv2.putText(img, f"Action: {action}", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    cv2.putText(img, f"Confidence: {confidence*100:.1f}%", (10, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("Gesture Test", img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    def list_gestures(self):
        """List all trained gestures"""
        print("\n📋 Trained Gestures")
        print("=" * 50)
        
        user_dir = f"gesture_models/users/{self.user_name}"
        if not os.path.exists(user_dir):
            print("No gestures found")
            return
        
        gestures = [d for d in os.listdir(user_dir) 
                   if os.path.isdir(os.path.join(user_dir, d)) and d != 'models']
        
        if not gestures:
            print("No gestures found")
            return
        
        # Load mapping if exists
        mapping_file = os.path.join(user_dir, "gesture_map.json")
        gesture_map = {}
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                gesture_map = json.load(f)
        
        for gesture in gestures:
            gesture_dir = os.path.join(user_dir, gesture)
            samples = len([f for f in os.listdir(gesture_dir) if f.endswith('.npy')])
            action = gesture_map.get(gesture, {}).get('action', 'not mapped')
            print(f"  • {gesture}: {samples} samples -> {action}")
    
    def delete_gesture(self):
        """Delete a gesture"""
        print("\n🗑️ Delete Gesture")
        print("=" * 50)
        
        user_dir = f"gesture_models/users/{self.user_name}"
        if not os.path.exists(user_dir):
            print("No gestures found")
            return
        
        gestures = [d for d in os.listdir(user_dir) 
                   if os.path.isdir(os.path.join(user_dir, d)) and d != 'models']
        
        if not gestures:
            print("No gestures found")
            return
        
        for i, gesture in enumerate(gestures):
            print(f"  {i+1}. {gesture}")
        
        choice = input("\nSelect gesture to delete (number): ")
        if choice.isdigit() and 1 <= int(choice) <= len(gestures):
            gesture = gestures[int(choice)-1]
            
            import shutil
            gesture_dir = os.path.join(user_dir, gesture)
            shutil.rmtree(gesture_dir)
            print(f"✅ Deleted {gesture}")
    
    def advanced_settings(self):
        """Advanced training settings"""
        print("\n⚙️ Advanced Settings")
        print("=" * 50)
        
        settings = {
            'samples_per_gesture': 100,
            'confidence_threshold': 0.7,
            'smoothing_frames': 5,
            'model_type': 'Random Forest'
        }
        
        print("Current settings:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
        
        print("\n1. Change samples per gesture")
        print("2. Change confidence threshold")
        print("3. Change smoothing frames")
        print("4. Change model type")
        print("5. Back")
        
        choice = input("\nSelect setting to change: ")
        # Implement settings changes here

def main():
    trainer = EnhancedGestureTrainer()
    trainer.show_menu()

if __name__ == "__main__":
    main()
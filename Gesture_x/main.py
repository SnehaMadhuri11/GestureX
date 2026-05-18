#!/usr/bin/env python3
"""
GestureX - AI-Powered Touchless Interaction System
"""

import sys

try:
    from gesture_controller import GestureController
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nPlease make sure all required files are in the same directory:")
    print("- gesture_controller.py")
    print("- hand_detector.py")
    print("- gesture_recognition.py")
    print("- action_executor.py")
    print("- gesture_manager.py")
    print("- gesture_config.py")
    sys.exit(1)

def main():
    print("\n" + "="*50)
    print("GestureX - AI Touchless Interaction System")
    print("="*50)
    print("\nInitializing camera and hand detector...")
    
    try:
        controller = GestureController()
        print("\n✅ System ready! Starting gesture control...")
        print("\n📋 Instructions:")
        print("- Show your hand to the camera")
        print("- Use gestures to control mouse/slides")
        print("- Press 'q' to quit")
        print("="*50 + "\n")
        
        controller.run()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your camera is connected")
        print("2. Check if all dependencies are installed")
        print("3. Ensure adequate lighting")
        sys.exit(1)
    
    print("\n👋 GestureX stopped. Goodbye!")

if __name__ == "__main__":
    main()
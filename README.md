# GestureX — AI Touchless Interaction System

GestureX is an advanced computer-vision framework that bridges human body language and operating system mechanics. Leveraging state-of-the-art hand tracking algorithms via MediaPipe, dynamic tracking logic, and reliable OS pipeline triggers via PyAutoGUI, GestureX allows you to control your desktop computer entirely with touchless hand gestures. 

The software utilizes a dual-mode system architecture to seamlessly transition between precise mouse manipulation (**Mouse Mode**) and interactive slideshow presentation controls (**Presentation Mode**). Additionally, it features an interactive training dashboard (`GestureManager`) that manages customizable user-defined finger triggers serialized dynamically through JSON storage.

---

## ✨ Core Features

* **Dual-Mode Operation Pipeline**:
    * **Mouse Mode**: Enables full desktop navigation including smooth pointer movement, single left-clicks, right-clicks, scroll dynamics, and double-click routines.
    * **Presentation Mode**: Optimizes dynamic coordinate mapping to capture broad spatial hand movements for instant slide transitions (Next / Previous slide controls).
* **Proportional Signal Filtering & Smoothing**: Employs mathematical interpolation mappings (`np.interp`) bounded inside tailored screen margins to map raw webcam inputs cleanly into screen pixels, using an adjustable step-size smoothing divisor (`smoothening = 5`) to eliminate micro-tremor hand jitters.
* **Precision Geometric Tracking**: Uses real-time Euclidean distance thresholds calculated across specified 3D landmark coordinate arrays to evaluate complex gestures such as thumb-to-index pinches (`PINCH_THRESHOLD = 25`).
* **Dynamic Command Gating**: Features continuous coordinate history logging using double-ended queues (`deque`), dynamic activation hold intervals (`min_hold`), and localized temporal cool-down mechanisms to avoid accidental mouse clicking or multiple page skips.
* **Extensible Gesture Manager & Trainer**: Includes an interactive Command Line Interface (CLI) application (`GestureManager`) to register, review, edit, calibrate, and export customized finger-state maps dynamically to persistent storage.

---

## 📁 Repository Structure & Code Modules

The codebase is organized modularly, separating global variables, spatial analytics pipelines, peripheral action mapping, and persistent state management:

```text
📂 GestureX/
├── 📄 config.py               # Global device definitions, camera constraints, and UI colors
├── 📄 action_executor.py       # Maps virtual inputs to system-level OS actions (PyAutoGUI)
├── 📄 gesture_config.py       # Persistent state container tracking JSON-based custom gesture arrays
├── 📄 gesture_recognition.py  # Algorithmic tracking engine filtering hand coordinate distances and histories
├── 📄 gesture_controller.py   # Core runtime engine tying together camera capture, loops, and detectors
├── 📄 gesture_manager.py      # Terminal developer hub for custom action calibration and testing
└── 📄 custom_gestures.json     # Generated persistent ledger mapping bespoke serialized gestures

```

### Module Breakdown:

* **`config.py`**: Optimizes the system canvas layout ($1280 \times 720$ resolution running at $60\text{ FPS}$) and enforces a high tracking/detection confidence limit (`0.8`) to guarantee tracking stability in variable lighting conditions.
* **`action_executor.py`**: Interacts directly with core desktop dimensions. Features decoupled click loops gated by specific temporal safety blocks (`click_cooldown = 0.3s`).
* **`gesture_recognition.py`**: Tracks multi-finger indexing configurations (`UP` vs `DOWN`) while monitoring hand sizes relative to the wrist to adjust coordinate calculations based on your distance from the camera.
* **`gesture_controller.py`**: The primary execution pipeline that orchestrates the camera canvas loop, processes spatial image transforms, and displays real-time performance text and tracking diagnostics onto the feed window.
* **`gesture_manager.py`** & **`gesture_config.py`**: Provides the developer management dashboard to add, update, reset, or troubleshoot custom tracking triggers seamlessly.

---

## 🎮 Default Gesture Configuration

| Operation Mode | Mapped OS Trigger | Finger State Sequence / Visual Action |
| --- | --- | --- |
| **Global Context** | `Switch Mode` | All five fingers fully upright simultaneously `[1, 1, 1, 1, 1]` |
| **Mouse Mode** | `Move Cursor` | Index finger pointing up exclusively `[0, 1, 0, 0, 0]` |
| **Mouse Mode** | `Left Click` | Index finger and thumb pinching close together (Distance < `PINCH_THRESHOLD`) |
| **Mouse Mode** | `Right Click` | Middle finger, index finger, and thumb pinching simultaneously |
| **Mouse Mode** | `Scroll Window` | Discrete coordinate variation mappings configured for vertical web scrolling |
| **Presentation** | `Next Slide` | Dynamic horizontal swipe motion toward the right |
| **Presentation** | `Previous Slide` | Dynamic horizontal swipe motion toward the left |

---

## 🛠️ System Requirements & Installation

Ensure you have a system environment configured with **Python 3.8+** along with a functioning integrated or external USB webcam device.

### 1. Download Project Components

```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/GestureX.git](https://github.com/YOUR_GITHUB_USERNAME/GestureX.git)
cd GestureX

```

### 2. Install Dependencies

Install the required tracking and automation dependencies using `pip`:

```bash
pip install opencv-python mediapipe pyautogui numpy

```

> ⚠️ **Linux Platform Note**: If you are deploying this on a Linux workspace environment, install the underlying X11 development tools required by `PyAutoGUI` before running the software:
> ```bash
> sudo apt-get install python3-tk python3-dev
> 
> ```
> 
> 

---

## 🚀 How to Run GestureX

### Start Main Interaction Pipeline

To spin up the real-time webcam frame loops and initialize mouse control, run:

```bash
python gesture_controller.py

```

### Open the Developer Management Dashboard

To view, recalibrate, clear, or test customized tracking patterns inside an isolated terminal loop, invoke:

```bash
python gesture_manager.py

```

---

## ⚙️ Custom Calibration & Fine-Tuning

You can adapt performance parameters to match your ambient room lighting or hardware capabilities by modifying values inside `config.py`:

```python
# System Performance Constants inside config.py
CAMERA_WIDTH = 1280          # Downscale to 640 if processing on low-spec edge hardware
CAMERA_HEIGHT = 720          # Downscale to 480 alongside lower dimensions
DETECTION_CONFIDENCE = 0.8   # Increase limits to drastically cut down on noise triggers
PINCH_THRESHOLD = 25         # Lower to require tighter finger pinches for clicking

```

---

## 🤝 Contributing

Contributions are welcome to help optimize mathematical coordinate arrays, expand multi-hand detection layers, or implement an interactive Graphical User Interface (GUI)!

1. Fork the project repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---



```

# Specquity

Specquity is a real-time Texas Hold'em equity calculator designed for the Raspberry Pi. It uses computer vision (YOLO) to identify physical cards and physical GPIO buttons to progress through the stages of a poker hand (Pre-flop, Flop, Turn, and River), providing immediate win probability feedback.

## Features

- **Computer Vision Integration:** Uses an optimized YOLO model to detect cards via a camera module.
- **Hardware Controls:** Integrated with Raspberry Pi GPIO for physical "Capture" and "Reset" buttons.
- **Real-time Equity Calculation:** Leverages `holdem_calc` to simulate win probabilities against random opponents.
- **Stage-based Logic:** Tracks the state of the game from hole cards through the river.

## Hardware Requirements

- Raspberry Pi (tested on RPi 4/5)
- Raspberry Pi Camera or USB Webcam
- 2x Momentary Push Buttons
- (Optional) I2C OLED Display (128x64)

### GPIO Pinout
- **Capture Button:** GPIO 17
- **Reset Button:** GPIO 22

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/specquity.git
   cd specquity
   ```

2. **Install Dependencies:**
   ```bash
   pip install opencv-python ultralytics holdem_calc RPi.GPIO
   ```

3. **Model Setup:**
   Ensure your trained YOLO model is placed in the `models/` directory:
   ```bash
   mkdir models
   # Place poker_best.ncnn inside models/
   ```

## Usage

Run the main orchestrator:
```bash
python main.py
```

### Controls
1. **Reset:** Press the Reset button (GPIO 22) to start a new hand.
2. **Capture (Pre-flop):** Place your hole cards in view and press Capture (GPIO 17).
3. **Capture (Flop/Turn/River):** Add community cards to the table and press Capture at each stage.
4. **View Equity:** The terminal (and optional OLED) will display your current win probability and strategic advice.

## Project Structure

- `main.py`: The main application loop and state machine.
- `src/vision.py`: Camera interface and YOLO card detection logic.
- `src/poker_math.py`: Equity calculations using Monte Carlo simulations.
- `src/buttons.py`: GPIO button interrupt handling.
- `src/ui_driver.py`: (Optional) OLED HUD display driver.


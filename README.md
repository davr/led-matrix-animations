# LED Matrix Animations

This project is designed to prototype visual animations for an LED matrix. It provides a framework for creating various animations and a graphical user interface (GUI) for previewing them.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd led-matrix-animations
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage Guidelines

- To create a new animation, add a new method `def update_frame_XYZ(self):` in preview_canvas.py. Increse MAX_MODE by 1. Add an extra elif statement to update_frame() to call your new method with the new mode number

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
import sys
from PyQt5.QtCore import QTimer
from gui.preview_canvas import PreviewCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Logic to start the animation
        self.preview_canvas = PreviewCanvas(parent=self)  # Pass 'self' as the parent

        self.setWindowTitle("LED Matrix Animation Preview")
        self.setGeometry(100, 100, 400, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("Animation Preview Area")
        self.layout.addWidget(self.label)

        self.bar = QWidget()
        self.bar.setLayout(QHBoxLayout())
        self.layout.addWidget(self.bar)
        self.start_button = QPushButton("Start Animation")
        self.start_button.clicked.connect(self.start_animation)
        self.bar.layout().addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Animation")
        self.stop_button.clicked.connect(self.stop_animation)
        self.bar.layout().addWidget(self.stop_button)

        self.grid = QPushButton("Toggle Grid")
        self.grid.clicked.connect(self.preview_canvas.toggle_grid)
        self.bar.layout().addWidget(self.grid)

        self.mode = QPushButton("Toggle Mode")
        self.mode.clicked.connect(self.preview_canvas.toggle_mode)
        self.bar.layout().addWidget(self.mode)

        self.layout.addWidget(self.preview_canvas)

        self.start_animation()

    def start_animation(self):

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.preview_canvas.update_frame)
        self.timer.start(50)  # Update every 100 ms

        self.label.setText("Animation Started")

    def stop_animation(self):
        # Logic to stop the animation
        self.timer.stop()
        self.label.setText("Animation Stopped")


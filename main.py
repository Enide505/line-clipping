import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class LineClipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Clipping with Rectangle Window")

        self.rect_x_min = 2
        self.rect_y_min = 2
        self.rect_x_max = 8
        self.rect_y_max = 8
        self.num_segments = 10

        self.setup_ui()
        self.generate_segments()
        self.plot_segments()

    def setup_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        refresh_button = ttk.Button(frame, text="Refresh", command=self.refresh)
        refresh_button.pack(pady=5)

    def generate_segments(self):
        self.segments = [
            ((random.uniform(0, 10), random.uniform(0, 10)),
             (random.uniform(0, 10), random.uniform(0, 10)))
            for _ in range(self.num_segments)
        ]

    def plot_segments(self):
        self.ax.clear()

        self.ax.plot(
            [self.rect_x_min, self.rect_x_max, self.rect_x_max, self.rect_x_min, self.rect_x_min],
            [self.rect_y_min, self.rect_y_min, self.rect_y_max, self.rect_y_max, self.rect_y_min],
            color='blue', linestyle='--', label="Clipping window"
        )

        for (x1, y1), (x2, y2) in self.segments:
            self.ax.plot([x1, x2], [y1, y2], color='black')

        for (x1, y1), (x2, y2) in self.segments:
            if self.is_segment_in_window(x1, y1, x2, y2):
                self.ax.plot([x1, x2], [y1, y2], color='red', linewidth=2)

        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()

    def is_segment_in_window(self, x1, y1, x2, y2):
        if (self.rect_x_min <= x1 <= self.rect_x_max and self.rect_y_min <= y1 <= self.rect_y_max) or \
                (self.rect_x_min <= x2 <= self.rect_x_max and self.rect_y_min <= y2 <= self.rect_y_max):
            return True
        return False

    def refresh(self):
        self.generate_segments()
        self.plot_segments()


root = tk.Tk()
app = LineClipperApp(root)
root.mainloop()

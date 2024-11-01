import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

INSIDE = 0  # 0000
LEFT = 1  # 0001
RIGHT = 2  # 0010
BOTTOM = 4  # 0100
TOP = 8  # 1000


class LineClipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Clipping with Cohen-Sutherland Algorithm")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.rect_x_min = 2
        self.rect_y_min = 2
        self.rect_x_max = 8
        self.rect_y_max = 6
        self.default_num_segments = 10

        self.dragging_edge = None
        self.dragging_rectangle = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.setup_ui()
        self.generate_segments()
        self.plot_segments()

    def setup_ui(self):
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=5)

        ttk.Label(input_frame, text="Количество отрезков:").pack(side=tk.LEFT)
        self.num_segments_entry = ttk.Entry(input_frame, width=5)
        self.num_segments_entry.pack(side=tk.LEFT)
        self.num_segments_entry.insert(0, str(self.default_num_segments))

        refresh_button = ttk.Button(input_frame, text="Сгенерировать", command=self.refresh)
        refresh_button.pack(side=tk.LEFT, padx=5)

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)

    def generate_segments(self):
        try:
            num_segments = int(self.num_segments_entry.get())
        except ValueError:
            num_segments = self.default_num_segments
        self.segments = [
            ((random.uniform(0, 10), random.uniform(0, 10)),
             (random.uniform(0, 10), random.uniform(0, 10)))
            for _ in range(num_segments)
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
            clipped_line = self.cohen_sutherland_clip(x1, y1, x2, y2)
            if clipped_line:
                cx1, cy1, cx2, cy2 = clipped_line
                self.ax.plot([cx1, cx2], [cy1, cy2], color='red', linewidth=2)

        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()

    def cohen_sutherland_clip(self, x1, y1, x2, y2):
        code1 = self.compute_code(x1, y1)
        code2 = self.compute_code(x2, y2)
        while True:
            if code1 == 0 and code2 == 0:
                return x1, y1, x2, y2
            elif code1 & code2 != 0:
                return None
            else:
                x, y = 0.0, 0.0
                out_code = code1 if code1 != 0 else code2
                if out_code & TOP:
                    x = x1 + (x2 - x1) * (self.rect_y_max - y1) / (y2 - y1)
                    y = self.rect_y_max
                elif out_code & BOTTOM:
                    x = x1 + (x2 - x1) * (self.rect_y_min - y1) / (y2 - y1)
                    y = self.rect_y_min
                elif out_code & RIGHT:
                    y = y1 + (y2 - y1) * (self.rect_x_max - x1) / (x2 - x1)
                    x = self.rect_x_max
                elif out_code & LEFT:
                    y = y1 + (y2 - y1) * (self.rect_x_min - x1) / (x2 - x1)
                    x = self.rect_x_min

                if out_code == code1:
                    x1, y1 = x, y
                    code1 = self.compute_code(x1, y1)
                else:
                    x2, y2 = x, y
                    code2 = self.compute_code(x2, y2)

    def compute_code(self, x, y):
        code = INSIDE
        if x < self.rect_x_min:
            code |= LEFT
        elif x > self.rect_x_max:
            code |= RIGHT
        if y < self.rect_y_min:
            code |= BOTTOM
        elif y > self.rect_y_max:
            code |= TOP
        return code

    def on_mouse_press(self, event):
        if event.xdata is None or event.ydata is None:
            return

        margin = 0.2
        if abs(event.xdata - self.rect_x_min) < margin:
            self.dragging_edge = 'left'
        elif abs(event.xdata - self.rect_x_max) < margin:
            self.dragging_edge = 'right'
        elif abs(event.ydata - self.rect_y_min) < margin:
            self.dragging_edge = 'bottom'
        elif abs(event.ydata - self.rect_y_max) < margin:
            self.dragging_edge = 'top'
        elif self.rect_x_min < event.xdata < self.rect_x_max and self.rect_y_min < event.ydata < self.rect_y_max:
            self.dragging_rectangle = True

        self.drag_start_x, self.drag_start_y = event.xdata, event.ydata

    def on_mouse_move(self, event):
        if event.xdata is None or event.ydata is None:
            return

        dx = event.xdata - self.drag_start_x
        dy = event.ydata - self.drag_start_y

        if self.dragging_edge == 'left':
            self.rect_x_min += dx
        elif self.dragging_edge == 'right':
            self.rect_x_max += dx
        elif self.dragging_edge == 'bottom':
            self.rect_y_min += dy
        elif self.dragging_edge == 'top':
            self.rect_y_max += dy
        elif self.dragging_rectangle:
            self.rect_x_min += dx
            self.rect_x_max += dx
            self.rect_y_min += dy
            self.rect_y_max += dy

        self.drag_start_x, self.drag_start_y = event.xdata, event.ydata
        self.plot_segments()

    def on_mouse_release(self, event):
        self.dragging_edge = None
        self.dragging_rectangle = False

    def refresh(self):
        self.generate_segments()
        self.plot_segments()

    def on_close(self):
        self.root.quit()
        self.root.destroy()


root = tk.Tk()
app = LineClipperApp(root)
root.mainloop()

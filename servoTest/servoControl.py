import tkinter as tk
import serial
import time
import math

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

PORT = "COM4"
BAUD_RATE = 9600

class ArduinoController:
    def __init__(self, port, baud_rate):
        # Open serial connection
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print("Połączono z Arduino")

        # GUI elements to be set later
        self.root = None
        self.distance_label = None
        self.angle_label = None
        self.detection_label = None

        # Radar data
        self.radar_data = []           
        self.current_angle = 0.0       
        self.last_angle_deg = None     

    def send_command(self, command):
        if self.ser.is_open:
            msg = (command + '\n').encode('utf-8')
            self.ser.write(msg)
            print(f"Wysłano: {command}")

    def close(self):
        if self.ser.is_open:
            
            self.ser.write(b'stop\n')
            time.sleep(0.1)
            self.ser.close()
            print("Zamknięto połączenie")

    def update_labels(self):
        detected = False
        detected_info = (0, 0)

        # Read all available serial lines
        while self.ser.in_waiting:
            line = self.ser.readline().decode('utf-8').strip()
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    distance = int(parts[0])
                    angle_deg = int(parts[1])

                    # Update labels
                    self.distance_label.config(text=f"Dystans: {distance} cm")
                    self.angle_label.config(text=f"Kąt: {angle_deg}°")

                    # Compute radar‐plot angle (shift by 90°)
                    rad = math.radians(angle_deg - 90)
                    self.current_angle = rad

                    # Remove any old point at this exact angle,
                    # then append the new one
                    self.radar_data = [
                        (a, d) for (a, d) in self.radar_data
                        if abs(a - rad) > 1e-6
                    ]
                    self.radar_data.append((rad, distance))

                    # Detection threshold
                    if distance <= 100:
                        detected = True
                        detected_info = (distance, angle_deg)

                except ValueError:
                    print("Niepoprawny format danych:", line)
            else:
                print("Nieoczekiwany format (brak przecinka):", line)

        # Show detection message
        if detected:
            d, a = detected_info
            self.detection_label.config(
                text=f"Wykryto obiekt na {d} cm i {a}°", fg='red'
            )
        else:
            self.detection_label.config(text="", fg='black')

        # Redraw radar
        self.update_radar()

        # Schedule next update
        self.root.after(200, self.update_labels)

    def update_radar(self):
        ax = self.radar_ax
        ax.clear()

        # Radar limits: ±90° from top, 0–100 cm
        ax.set_thetalim(-math.pi/2, math.pi/2)
        ax.set_ylim(0, 100)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)

        # Plot scanned points
        if self.radar_data:
            angles, dists = zip(*self.radar_data)
            ax.scatter(angles, dists, c='red')

        # Scanning line
        ax.plot([self.current_angle, self.current_angle], [0, 100], alpha=0.3)

        self.radar_canvas.draw()


def create_gui(controller):
    controller.root = tk.Tk()
    controller.root.title("Kontroler Arduino z Radarem 180°")

    # Info panel
    info_frame = tk.Frame(controller.root, padx=10, pady=10)
    info_frame.pack(side=tk.LEFT, fill=tk.Y)

    controller.distance_label = tk.Label(
        info_frame, text="Dystans: - cm", font=("Arial", 14)
    )
    controller.distance_label.pack(pady=5)

    controller.angle_label = tk.Label(
        info_frame, text="Kąt: -°", font=("Arial", 14)
    )
    controller.angle_label.pack(pady=5)

    controller.detection_label = tk.Label(
        info_frame, text="", font=("Arial", 12)
    )
    controller.detection_label.pack(pady=5)

    # Control buttons
    btn_frame = tk.Frame(info_frame)
    btn_frame.pack(pady=10)
    for text, cmd in [("Start", "start"), ("Stop", "stop"), ("Reset", "reset"), ("Close", None)]:
        action = (lambda c=cmd: controller.send_command(c)) if cmd else (lambda: on_close(controller))
        tk.Button(btn_frame, text=text, width=8, command=action).pack(side=tk.LEFT, padx=3)

    controller.root.protocol("WM_DELETE_WINDOW", lambda: on_close(controller))

    # Radar plot
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection='polar')
    controller.radar_ax = ax

    canvas = FigureCanvasTkAgg(fig, master=controller.root)
    controller.radar_canvas = canvas
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Start updating
    controller.update_labels()
    controller.root.mainloop()


def on_close(controller):
    controller.close()
    if controller.root:
        controller.root.destroy()


if __name__ == "__main__":
    try:
        ctrl = ArduinoController(PORT, BAUD_RATE)
        create_gui(ctrl)
    except serial.SerialException as e:
        print("Błąd połączenia z Arduino:", e)

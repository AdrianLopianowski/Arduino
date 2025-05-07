import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial
import time
import math
import json
import csv

# Use reportlab for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Serial port settings
PORT = "COM4"
BAUD_RATE = 9600

class ArduinoController:
    def __init__(self, port, baud_rate):
        # Open serial connection
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print("Połączono z Arduino")

        # GUI elements set later
        self.root = None
        self.distance_label = None
        self.angle_label = None
        self.detection_label = None
        self.indicator_label = None
        self.start_listen_btn = None
        self.stop_listen_btn = None

        # Radar plotting
        self.radar_data = []
        self.current_angle = 0.0

        # Recording
        self.listening = False
        self.records = []  # dicts: timestamp, angle, distance

    def send_command(self, command):
        if self.ser.is_open:
            self.ser.write((command + '\n').encode('utf-8'))
            print(f"Wysłano: {command}")

    def close(self):
        if self.ser.is_open:
            self.send_command('stop')
            time.sleep(0.1)
            self.ser.close()
            print("Zamknięto połączenie")

    def start_listening(self):
        self.records.clear()
        self.listening = True
        self.detection_label.config(text="Recording...", foreground='yellow')
        self.indicator_label.config(text='●')
        self.start_listen_btn.config(state='disabled')
        self.stop_listen_btn.config(state='normal')
        print("Start listening to radar data.")

    def stop_listening(self):
        if not self.listening:
            return
        # Stop servo
        self.send_command('stop')
        self.listening = False
        self.detection_label.config(text="Recording stopped.")
        self.indicator_label.config(text='')
        self.start_listen_btn.config(state='normal')
        self.stop_listen_btn.config(state='disabled')
        print("Stop listening. Prompting to save data.")

        filetypes = [
            ("CSV File", "*.csv"),
            ("JSON File", "*.json"),
            ("PDF File", "*.pdf"),
            ("All files", "*.*")
        ]
        filepath = filedialog.asksaveasfilename(title="Zapisz dane", filetypes=filetypes,
                                                defaultextension=filetypes)
        if not filepath:
            print("Save cancelled.")
            return

        ext = filepath.split('.')[-1].lower()
        try:
            if ext == 'csv':
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['timestamp', 'angle', 'distance'])
                    writer.writeheader()
                    writer.writerows(self.records)

            elif ext == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.records, f, ensure_ascii=False, indent=2)

            elif ext == 'pdf':
                # Generate simple PDF with list of detections
                c = pdf_canvas.Canvas(filepath, pagesize=letter)
                width, height = letter
                c.setFont("Helvetica", 12)
                y = height - 40
                c.drawString(40, y, "Radar Detections:")
                y -= 20
                for rec in self.records:
                    line = f"[{rec['timestamp']}] Angle: {rec['angle']}°, Distance: {rec['distance']} cm"
                    if y < 40:
                        c.showPage()
                        y = height - 40
                        c.setFont("Helvetica", 12)
                    c.drawString(40, y, line)
                    y -= 15
                c.save()

            else:
                messagebox.showerror("Błąd", f"Nieobsługiwane rozszerzenie: .{ext}")
                return

            messagebox.showinfo("Success", f"Dane zapisane do {filepath}")
            print(f"Data saved to {filepath}")

        except Exception as e:
            messagebox.showerror("Error saving file", str(e))
            print(f"Error saving data: {e}")

    def reset_all(self):
        self.send_command('reset')
        self.radar_data.clear()
        self.records.clear()
        self.distance_label.config(text="Dystans: - cm")
        self.angle_label.config(text="Kąt: -°")
        self.detection_label.config(text="")
        self.update_radar()
        print("Radar and records reset.")

    def update_labels(self):
        detected = False
        detected_info = (0, 0)
        while self.ser.in_waiting:
            line = self.ser.readline().decode('utf-8').strip()
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    distance = int(parts[0]); angle_deg = int(parts[1])
                    self.distance_label.config(text=f"Dystans: {distance} cm")
                    self.angle_label.config(text=f"Kąt: {angle_deg}°")
                    rad = math.radians(angle_deg - 90)
                    self.current_angle = rad
                    self.radar_data = [(a, d) for (a, d) in self.radar_data if abs(a - rad) > 1e-6]
                    self.radar_data.append((rad, distance))
                    if distance <= 100:
                        detected = True; detected_info = (distance, angle_deg)
                        if self.listening:
                            self.records.append({'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'angle': angle_deg,
                                                 'distance': distance})
                except ValueError:
                    print("Niepoprawny format danych:", line)
            else:
                print("Nieoczekiwany format (brak przecinka):", line)
        if detected:
            d, a = detected_info
            self.detection_label.config(text=f"Wykryto obiekt na {d} cm i {a}°", foreground='red')
        elif self.listening:
            self.detection_label.config(text="Recording...", foreground='yellow')
        self.update_radar()
        self.root.after(200, self.update_labels)

    def update_radar(self):
        ax = self.radar_ax
        ax.clear()
        ax.set_thetalim(-math.pi/2, math.pi/2)
        ax.set_ylim(0, 100)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_facecolor('#000')
        ax.tick_params(colors='lightgrey')
        ax.grid(color='grey', linestyle='--', linewidth=0.5)
        if self.radar_data:
            angles, dists = zip(*self.radar_data)
            ax.scatter(angles, dists, c='lime', s=50)
        ax.plot([self.current_angle, self.current_angle], [0, 100], alpha=0.3, linestyle='--', color='lightgrey')
        self.radar_canvas.draw()


def create_gui(controller):
    root = tk.Tk(); controller.root = root
    root.title("Kontroler Arduino - Radar 180°"); root.geometry('800x500'); root.configure(bg='#1e1e1e')
    style = ttk.Style(root); style.theme_use('clam')
    style.configure('TFrame', background='#1e1e1e'); style.configure('TLabel', background='#1e1e1e', foreground='#ddd', font=('Helvetica', 12))
    style.configure('Header.TLabel', foreground='#fff', font=('Helvetica', 18, 'bold'))
    style.configure('TButton', font=('Helvetica', 11), padding=6, background='#333', foreground='#fff', borderwidth=0)
    style.map('TButton', background=[('pressed', '#555'), ('active', '#444')], relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
    ttk.Label(root, text="Arduino Radar Control Panel", style='Header.TLabel').pack(pady=10)
    content = ttk.Frame(root); content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    info_frame = ttk.Frame(content); info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
    controller.distance_label = ttk.Label(info_frame, text="Dystans: - cm"); controller.distance_label.pack(pady=5)
    controller.angle_label = ttk.Label(info_frame, text="Kąt: -°"); controller.angle_label.pack(pady=5)
    controller.detection_label = ttk.Label(info_frame, text="", foreground='red'); controller.detection_label.pack(pady=5)
    send_frame = ttk.Frame(info_frame); send_frame.pack(pady=15)
    for cmd in ["start","stop"]:
        ttk.Button(send_frame, text=cmd.capitalize(), command=lambda c=cmd: controller.send_command(c)).pack(side=tk.LEFT, padx=5)
    ttk.Button(send_frame, text="Reset", command=controller.reset_all).pack(side=tk.LEFT, padx=5)
    listen_frame = ttk.Frame(info_frame); listen_frame.pack(pady=5)
    controller.start_listen_btn = ttk.Button(listen_frame, text="Start Listening", command=controller.start_listening)
    controller.start_listen_btn.pack(side=tk.LEFT, padx=5)
    controller.stop_listen_btn = ttk.Button(listen_frame, text="Stop Listening", command=controller.stop_listening, state='disabled')
    controller.stop_listen_btn.pack(side=tk.LEFT, padx=5)
    controller.indicator_label = ttk.Label(listen_frame, text='', foreground='red', font=('Helvetica', 16))
    controller.indicator_label.pack(side=tk.LEFT, padx=5)
    ttk.Button(info_frame, text='Close', command=lambda: on_close(controller)).pack(pady=10)
    fig = Figure(figsize=(5,5), facecolor='#000'); ax = fig.add_subplot(111, projection='polar')
    controller.radar_ax = ax; controller.radar_canvas = FigureCanvasTkAgg(fig, master=content)
    controller.radar_canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    controller.update_labels(); root.mainloop()

def on_close(controller):
    controller.close(); controller.root.destroy() if controller.root else None

if __name__ == "__main__":
    try:
        ctrl = ArduinoController(PORT, BAUD_RATE)
        create_gui(ctrl)
    except serial.SerialException as e:
        print("Błąd połączenia z Arduino:", e)

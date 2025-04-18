import tkinter as tk
import serial
import threading
import time

PORT = "COM4"
BAUD_RATE = 9600

class ArduinoController:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Czekamy na inicjalizację portu
        print("Połączono z Arduino")

    def send_command(self, command):
        if self.ser.is_open:
            self.ser.write((command + '\n').encode())
            print(f"Wysłano: {command}")

    def close(self):
        if self.ser.is_open:
            self.ser.close()

# GUI
def create_gui(controller):
    root = tk.Tk()
    root.title("Kontroler Arduino")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    start_button = tk.Button(frame, text="Start", command=lambda: controller.send_command("start"), width=10)
    start_button.pack(pady=5)

    stop_button = tk.Button(frame, text="Stop", command=lambda: controller.send_command("stop"), width=10)
    stop_button.pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, controller))
    root.mainloop()

def on_close(root, controller):
    controller.close()
    root.destroy()

# Start
if __name__ == "__main__":
    try:
        controller = ArduinoController(PORT, BAUD_RATE)
        create_gui(controller)
    except serial.SerialException as e:
        print("Błąd połączenia z Arduino:", e)

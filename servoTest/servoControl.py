import tkinter as tk
import serial
import time

PORT = "COM4"
BAUD_RATE = 9600

class ArduinoController:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print("Połączono z Arduino")
        self.root = None
        self.distance_label = None
        self.angle_label = None

    def send_command(self, command):
        if self.ser.is_open:
            self.ser.write((command + '').encode())
            print(f"Wysłano: {command}")

    def close(self):
        if self.ser.is_open:
            self.ser.close()

    def update_labels(self):
        # Odczytuj wszystkie linie w buforze
        while self.ser.in_waiting:
            data = self.ser.readline().decode('utf-8').strip()
            parts = data.split(',')
            if len(parts) == 2:
                try:
                    distance = int(parts[0])
                    angle = int(parts[1])
                    self.distance_label.config(text=f"Dystans: {distance} cm")
                    self.angle_label.config(text=f"Kąt: {angle}°")
                except ValueError:
                    print("Niepoprawny format danych:", data)
            else:
                print("Nieoczekiwany format (brak przecinka):", data)
        # Zaplanuj kolejną aktualizację
        self.root.after(200, self.update_labels)


def create_gui(controller):
    controller.root = tk.Tk()
    controller.root.title("Kontroler Arduino")

    frame = tk.Frame(controller.root, padx=20, pady=20)
    frame.pack()

    controller.distance_label = tk.Label(controller.root, text="Dystans: - cm", font=("Arial", 16))
    controller.distance_label.pack(pady=5)

    controller.angle_label = tk.Label(controller.root, text="Kąt: -°", font=("Arial", 16))
    controller.angle_label.pack(pady=5)

    controller.update_labels()

    start_button = tk.Button(frame, text="Start", command=lambda: controller.send_command("start"), width=10)
    start_button.pack(side=tk.LEFT, padx=5)

    stop_button = tk.Button(frame, text="Stop", command=lambda: controller.send_command("stop"), width=10)
    stop_button.pack(side=tk.LEFT, padx=5)

    reset_button = tk.Button(frame, text="Reset", command=lambda: controller.send_command("reset"), width=10)
    reset_button.pack(side=tk.LEFT, padx=5)

    close_button = tk.Button(frame, text="Close", command=lambda: on_close(controller), width=10)
    close_button.pack(side=tk.LEFT, padx=5)

    # Gdy użytkownik zamknie okno (X), również wywołaj on_close
    controller.root.protocol("WM_DELETE_WINDOW", lambda: on_close(controller))
    controller.root.mainloop()


def on_close(controller):
    # Zatrzymaj serwo przed zamknięciem
    controller.send_command("stop")
    controller.close()
    controller.root.destroy()

# Start programu
if __name__ == "__main__":
    try:
        controller = ArduinoController(PORT, BAUD_RATE)
        create_gui(controller)
    except serial.SerialException as e:
        print("Błąd połączenia z Arduino:", e)
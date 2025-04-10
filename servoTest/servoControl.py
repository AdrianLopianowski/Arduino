import serial
import time

# input
PORT = "COM4" 
BAUD_RATE = 9600

# Arduino Connection
try:
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
except Exception as e:
    print("Błąd podczas łączenia z Arduino:", e)
    exit()

# Arduino reset
time.sleep(2)
print("Połączono z Arduino. Wpisz kąt (0-180) lub 'q' aby zakończyć.")

while True:
    user_input = input("Wpisz kąt (0-180) lub 'q': ")
    if user_input.lower() == 'q':
        print("Koniec programu.")
        break
    try:
        angle = int(user_input)
        if angle < 0 or angle > 180:
            print("Kąt musi być w zakresie 0-180.")
            continue

       
        message = f"{angle}\n" 
        arduino.write(message.encode('utf-8'))
        print(f"Wysłano kąt: {angle}")

    except ValueError:
        print("Wprowadź poprawną liczbę.")

arduino.close()

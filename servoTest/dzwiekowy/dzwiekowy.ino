#include <Servo.h>

#define TRIG_PIN 12
#define ECHO_PIN 11
#define SERVO_PIN 9

Servo myServo;
bool working = false;
int pozycjaServo = 0;
int kierunek = 1;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  myServo.attach(SERVO_PIN);
  myServo.write(0);
}

void loop() {
  // Odbieranie komend
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "start") {
      working = true;
    } else if (command == "stop") {
      working = false;
    } else if (command == "reset") {
      // Reset pozycji, ale nie przerywa ruchu
      pozycjaServo = 0;
      kierunek = 1;
      myServo.write(pozycjaServo);
    }
  }

  if (working) {
    // Pomiar odległości
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long czas = pulseIn(ECHO_PIN, HIGH);
    int dystans = czas / 58;

    // Ruch serwa (spowolniony)
    myServo.write(pozycjaServo);
    delay(100);  // zwiększ opóźnienie, by zwolnić prędkość ruchu
    
    // Wysyłanie danych: dystans, kąt
    Serial.print(dystans);
    Serial.print(",");
    Serial.println(pozycjaServo);

    // Zmiana kierunku na krańcach
    const int krok = 1;      // krok obrotu w stopniach
    if (pozycjaServo >= 180) kierunek = -1;
    else if (pozycjaServo <= 0) kierunek = 1;
    pozycjaServo += kierunek * krok;
  }
}
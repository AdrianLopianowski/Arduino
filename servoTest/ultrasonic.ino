#include <Servo.h>

#define trigPin 12
#define echoPin 11

Servo myServo;
int servoPin = 9;

bool working = false;
int pozycjaServo = 0;
int kierunek = 1;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  myServo.attach(servoPin);
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
      working = false;
      pozycjaServo = 0;
      kierunek = 1;
      myServo.write(pozycjaServo);
    }
  }

  if (working) {
    // Pomiar odległości
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long czas = pulseIn(echoPin, HIGH);
    int dystans = czas / 58;

    // Ruch serwa
    myServo.write(pozycjaServo);
    delay(50);
    
    // Wysyłanie danych: dystans, kąt
    Serial.print(dystans);
    Serial.print(",");
    Serial.println(pozycjaServo);

    // Zmiana kierunku na krańcach
    if (pozycjaServo >= 180) kierunek = -1;
    else if (pozycjaServo <= 0) kierunek = 1;
    pozycjaServo += kierunek;
  }
}
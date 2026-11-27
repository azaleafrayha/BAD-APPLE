// run in arduino IDE only once to check if the OLED is detected on the I2C bus

#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Serial.println("Searching I2C...");

  byte count = 0;
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("OLED detected at address: 0x");
      Serial.println(addr, HEX);
      count++;
    }
  }

  if (count == 0) {
    Serial.println("No I2C devices detected! Check VCC, GND, SDA (A4), SCL (A5) cables.");
  }
}

void loop() {}
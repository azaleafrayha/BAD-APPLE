// run in arduino IDE to display the frame sent from the PC via USB serial

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const size_t FRAME_BYTES = (SCREEN_WIDTH * SCREEN_HEIGHT) / 8; // 1024 byte

void setup() {
  Serial.begin(500000);
  Serial.setTimeout(500);

  Wire.begin();
  Wire.setClock(800000);

  display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS);

  display.ssd1306_command(0xD5);
  display.ssd1306_command(0xF0);
  
  display.clearDisplay();
  display.display();
  Serial.write('R');
}

void loop() {
  if (Serial.available() > 0) {
    uint8_t cmd = Serial.read();

    if (cmd == '?') {
      Serial.write('R');
    } else if (cmd == 'F') {
      size_t received = Serial.readBytes((char*)display.getBuffer(), FRAME_BYTES);
      if (received == FRAME_BYTES) {
        display.display();
      }
      Serial.write('R');
    }
  }
}
# **RULE 86 OF THE INTERNET: IF IT EXISTS YOU CAN PLAY BAD APPLE ON IT**

<div align="center">

<img src="https://media1.tenor.com/m/omQ5ylUjNokAAAAC/bad-apple.gif" alt="Bad Apple animation" width="700">

</div>

Bad Apple is the final boss of "is this technically possible?" projects. It went from Touhou fan culture to a legendary test video that has somehow appeared on calculators, watches, printers, and now a tiny OLED. This build sends each frame of a Bad Apple video from a computer to an Arduino, which forwards the 1-bit image data to a 128 x 64 SSD1306 OLED.

The result is peak low-resolution chaos: 8,192 pixels, one silhouette at a time, absolutely no right to look this cool.

## What You Need

- Arduino Uno
- 128 x 64 I2C SSD1306 OLED
- USB cable for the Arduino
- 4 male-to-female or male-to-male jumper wires
- A computer with Python 3
- A Bad Apple MP4

## Wiring

The OLED communicates with the Arduino Uno over I2C. Only four connections are needed.

```text
  128 x 64 SSD1306 OLED
+-------------------------+
| VCC   GND   SDA   SCL  |
+---+----+-----+-----+---+
    |    |     |     |
    |    |     |     |
    |    |     |     |
Arduino Uno             |
+------------------------+
| 5V  GND  A4   A5      |
+------------------------+
    |
    +----- USB cable ------> Computer
```

| OLED | Arduino Uno |
|---|---|
| VCC | 5V |
| GND | GND |
| SDA | A4 |
| SCL | A5 |

Do not swap SDA and SCL. If the OLED uses 3.3V rather than 5V, follow the module's voltage rating and power it from the Uno's 3.3V pin instead.

## Project Layout

```text
BAD APPLE OLED/
|-- main.py
|-- sketch_checkOLED/
|   `-- sketch_checkOLED.ino
|-- sketch_OLED/
|   `-- sketch_OLED.ino
`-- README.md
```

- `sketch_checkOLED.ino` scans the I2C bus to confirm that the OLED is connected and to find its address.
- `sketch_OLED.ino` receives complete frames from the computer and sends them to the OLED.
- `main.py` reads the video, converts each frame to monochrome, packs the pixels, and streams the result over serial.

## Set It Up

### 1. Install the Arduino libraries

Open the Arduino IDE and install these libraries through the Library Manager:

- `Adafruit GFX Library`
- `Adafruit SSD1306`

They are dependencies of the OLED display code, and Adafruit GFX supplies the drawing and text support used by the SSD1306 driver.

### 2. Check the OLED

Connect the four OLED wires as shown above. Upload `sketch_checkOLED/sketch_checkOLED.ino` to the Uno. Open the Serial Monitor at 115200 baud.

A working OLED should report an address such as `0x3C`. If the sketch says no I2C devices were detected, check VCC, GND, SDA, and SCL first. The wrong address or a loose wire will leave you staring at a very expensive black rectangle.

The main sketch uses address `0x3C`, so update `SCREEN_ADDRESS` in `sketch_OLED.ino` if the scan reports a different address.

### 3. Install the Python packages

From the project folder, run:

```bash
pip install opencv-python numpy pyserial
```

### 4. Configure the Python script

Open `main.py` and edit these values if needed:

```python
PORT = "COM3"
BAUD = 500000
VIDEO_PATH = r"C:\Users\User\Downloads\BA.mp4"
```

Set `PORT` to the Uno's serial port. In Windows, it will look similar to `COM3`, `COM4`, or `COM5`. You can find it in the Arduino IDE under Tools, then Port.

Set `VIDEO_PATH` to the full path of the Bad Apple video on your computer. In Windows Explorer, hold Shift, right-click the video, and choose "Copy as path", or set the path manually.

The screen settings are:

```python
WIDTH = 128
HEIGHT = 64
THRESHOLD = 128
TARGET_FPS = 25
MAX_DURATION = 56.5
```

The threshold decides whether a pixel is black or white. Gray values at or above 128 become white; darker values become black.

## Upload and Run

1. Close the Arduino Serial Monitor before starting the Python script.
2. Upload `sketch_OLED/sketch_OLED.ino`.
3. Update `PORT` and `VIDEO_PATH` in `main.py`.
4. Run:

```bash
python main.py
```

The Uno sends `R`, which means "ready." The Python script sends `?` until it receives that ready signal, then starts streaming.

## How the Data Pipeline Works

```text
Bad Apple MP4
      |
      v
OpenCV reads and downsizes each frame
      |
      v
Convert to grayscale and apply a threshold
      |
      v
Pack pixels into SSD1306 display format
      |
      v
Send one frame over USB serial
      |
      v
Arduino acknowledges and updates the OLED
```

OpenCV resizes each video frame to the OLED's resolution and converts it to grayscale. The Python script then turns the result into a strictly black-and-white frame and packs eight vertical pixels into each byte, matching the SSD1306's display memory layout.

A complete frame is 1,024 bytes. That is enough for the entire 128 x 64 screen, making the Arduino a very focused middleman between a PC and a tiny OLED.

The Uno and PC use a simple serial protocol:

- `?` asks whether the Uno is ready.
- `R` means ready or frame received.
- `F` starts a frame transfer.

The Uno reads the frame into the SSD1306 display buffer, pushes it to the screen, and sends `R` as an acknowledgment. The Python script waits for that acknowledgment before sending the next frame. This keeps the transfer predictable and prevents a frame from being drawn while the next one is only halfway across the wire.

## Troubleshooting

**No I2C device found**

Check every wire and verify that VCC and GND are not reversed. OLED modules vary, so confirm the address and voltage requirements printed on the board.

**The script cannot open the COM port**

Close the Arduino Serial Monitor and any other serial application, then confirm the Uno's port in the Arduino IDE and update `PORT` in `main.py`.

**The OLED is detected but stays blank**

Make sure `SCREEN_ADDRESS` matches the address reported by the I2C scanner and that the display sketch was uploaded successfully.

**The animation stutters**

Stutter usually means the transfer cannot keep up reliably. Keep the Uno connected through a stable USB cable and review the playback settings in `main.py`.

**The image looks inverted or washed out**

The black-and-white threshold is configurable in `main.py`. Lower it for a brighter image or raise it for stronger black silhouettes.

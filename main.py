import time
import cv2
import numpy as np
import serial

PORT = "COM3"
BAUD = 500000
VIDEO_PATH = r"C:\Users\User\Downloads\BA.mp4" # copy the video file path here from your computer

WIDTH = 128
HEIGHT = 64
THRESHOLD = 128
TARGET_FPS = 25       
MAX_DURATION = 56.5


def frame_to_ssd1306_bytes(gray_frame: np.ndarray) -> bytes:
    resized = cv2.resize(gray_frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)
    bits = (resized >= THRESHOLD).astype(np.uint8)

    pages = bits.reshape(8, 8, WIDTH)
    packed = np.zeros((8, WIDTH), dtype=np.uint8)
    for bit_idx in range(8):
        packed |= (pages[:, bit_idx, :] << bit_idx)

    return packed.tobytes()


def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {VIDEO_PATH}")

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2)

    print("Waiting for 'R' signal from Arduino Uno...")
    while True:
        ser.write(b"?")
        if ser.read(1) == b"R":
            break

    ser.timeout = 1
    ser.reset_input_buffer()

    print(f"Streaming to SSD1306 (target {TARGET_FPS} FPS)...")
    start_time = time.perf_counter()
    current_video_idx = 0
    sent_frames = 0
    frame_interval = 1.0 / TARGET_FPS

    try:
        while True:
            elapsed = time.perf_counter() - start_time
            if elapsed >= MAX_DURATION:
                break

            # Skip frames to match the target FPS
            target_video_idx = int(elapsed * src_fps)
            while current_video_idx < target_video_idx:
                if not cap.grab():
                    break
                current_video_idx += 1

            ret, frame = cap.read()
            if not ret:
                break
            current_video_idx += 1

            loop_start = time.perf_counter()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            payload = frame_to_ssd1306_bytes(gray)

            ser.write(b"F" + payload)

            if ser.read(1) != b"R":
                ser.reset_input_buffer()

            sent_frames += 1

            sleep_time = frame_interval - (time.perf_counter() - loop_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        cap.release()
        ser.close()
        total = time.perf_counter() - start_time
        print(f"Done: {sent_frames} frame in {total:.2f} second ({sent_frames/total:.1f} FPS).")


if __name__ == "__main__":
    main()
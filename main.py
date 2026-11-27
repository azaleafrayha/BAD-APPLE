import time
import cv2
import numpy as np
import serial

PORT = "COM3"
BAUD = 115200
VIDEO_PATH = r"C:\Users\User\Pictures\Bad Apple!! - 43sc - Trim.mp4"

WIDTH = 128
HEIGHT = 64
THRESHOLD = 128       # Bisa digeser (0-255) kalau siluetnya kurang jelas
TARGET_FPS = 12       # 10-15 FPS pas untuk OLED I2C 128x64
START_SEC = 0.0
MAX_DURATION = 43.5   # Menyesuaikan klip 43 detik


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
        raise RuntimeError(f"Gagal membuka video: {VIDEO_PATH}")

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step_frames = max(1, round(src_fps / TARGET_FPS))

    if START_SEC > 0:
        cap.set(cv2.CAP_PROP_POS_MSEC, START_SEC * 1000.0)

    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(2)  # Tunggu Arduino Uno selesai boot

    print("Menunggu sinyal 'R' dari Arduino Uno...")
    while True:
        ser.write(b"?")  # Tanya kesiapan Arduino tanpa menghapus buffer awal
        b = ser.read(1)
        if b == b"R":
            break
        if b == b"E":
            raise RuntimeError("OLED tidak terdeteksi oleh Arduino (cek kabel / 0x3C vs 0x3D).")

    ser.timeout = 2
    ser.reset_input_buffer()  # Bersihkan sisa 'R' ekstra sebelum mulai kirim frame

    print(f"Mulai streaming ke OLED ({TARGET_FPS} FPS, max {MAX_DURATION}s)...")
    start_time = time.perf_counter()
    frame_idx = 0
    sent_frames = 0
    frame_interval = 1.0 / TARGET_FPS

    try:
        while True:
            elapsed = time.perf_counter() - start_time
            if elapsed >= MAX_DURATION:
                break

            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            if (frame_idx - 1) % step_frames != 0:
                continue

            loop_start = time.perf_counter()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            payload = frame_to_ssd1306_bytes(gray)

            ser.write(b"F")
            ser.write(payload)
            ser.flush()

            ack = ser.read(1)
            if ack != b"R":
                print("Peringatan: tidak menerima 'R', mencoba sinkronisasi ulang...")
                ser.reset_input_buffer()

            sent_frames += 1

            work_time = time.perf_counter() - loop_start
            sleep_time = frame_interval - work_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nDihentikan oleh pengguna.")
    finally:
        cap.release()
        ser.close()
        total_time = time.perf_counter() - start_time
        print(f"Selesai: {sent_frames} frame terkirim dalam {total_time:.2f} detik.")


if __name__ == "__main__":
    main()
import json
import signal
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Inicializar lector
reader = SimpleMFRC522()

# Captura Ctrl+C
continue_reading = True

def end_read(signal, frame):
    global continue_reading
    print("\n[INFO] Lectura detenida con Ctrl+C")
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read)

print("[INFO] Escanea una tarjeta RFID...")

while continue_reading:
    try:
        id, text = reader.read()
        print(f"[INFO] UID leído: {id}")

        # Guardar en JSON
        data = {"uid": id}

        with open("rfid_log.json", "w") as f:
            json.dump(data, f, indent=4)

        print("[INFO] UID guardado en rfid_log.json\n")

    except Exception as e:
        print(f"[ERROR] {e}")
        GPIO.cleanup()
        break

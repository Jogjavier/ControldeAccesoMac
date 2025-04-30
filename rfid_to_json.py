import RPi.GPIO as GPIO
import MFRC522
import signal
import json
import os

continue_reading = True
json_file = "rfid_data.json"

# Captura Ctrl+C
def end_read(signal, frame):
    global continue_reading
    print("\nCtrl+C detectado, saliendo.")
    continue_reading = False
    GPIO.cleanup()

# Cargar archivo JSON si existe, sino crear uno vacío
def load_data():
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            return json.load(file)
    else:
        return []

# Guardar nuevo UID si no está en la lista
def save_uid(uid_list, new_uid):
    if new_uid not in uid_list:
        uid_list.append(new_uid)
        with open(json_file, "w") as file:
            json.dump(uid_list, file, indent=4)
        print(f"Nuevo UID guardado: {new_uid}")
    else:
        print(f"UID ya registrado: {new_uid}")

# Hook de señal Ctrl+C
signal.signal(signal.SIGINT, end_read)

# Inicializar lector RFID
MIFAREReader = MFRC522.MFRC522()

print("Listo para leer tarjetas RFID. Presiona Ctrl+C para salir.")

# Cargar datos existentes
uids = load_data()

# Bucle de lectura
while continue_reading:
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    if status == MIFAREReader.MI_OK:
        print("Tarjeta detectada")

        (status, uid) = MIFAREReader.MFRC522_Anticoll()

        if status == MIFAREReader.MI_OK:
            uid_str = "-".join([str(x) for x in uid])  # Ej: "10-98-205-15"
            print(f"UID leído: {uid_str}")
            save_uid(uids, uid_str)
            MIFAREReader.MFRC522_SelectTag(uid)
            MIFAREReader.MFRC522_StopCrypto1()

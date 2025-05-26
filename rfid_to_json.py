from pirc522 import RFID
import signal
import time

rdr = RFID()         # Inicializa lector RFID
util = rdr.util()
util.debug = False   # Opcional: activa debug si necesitas

def end_read(signal, frame):
    print("\nSaliendo...")
    rdr.cleanup()
    exit()

# Captura Ctrl+C para salir con gracia
signal.signal(signal.SIGINT, end_read)

print("Acerque una tarjeta RFID al lector...")

while True:
    rdr.wait_for_tag()
    (error, tag_type) = rdr.request()
    
    if not error:
        print("Tarjeta detectada")
        (error, uid) = rdr.anticoll()

        if not error:
            print("UID de la tarjeta:", uid)
            print("Hex UID:", ''.join([format(x, '02X') for x in uid]))
            time.sleep(2)

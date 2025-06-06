#script para reescribir en una tarjeta rfid (no se borra por completo se queda el id de la terjeta)
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print("Acerca la tarjeta para leer su contenido actual...")
    id, texto_actual = reader.read()
    print(f"\n📇 ID de tarjeta: {id}")
    print(f"📄 Contenido actual: '{texto_actual.strip()}'")

    confirmar_borrado = input("\n¿Deseas borrar este contenido? (s/n): ").lower()

    if confirmar_borrado == 's':
        reader.write("")  # Borra escribiendo cadena vacía
        print("✅ Contenido borrado.")

        escribir_nuevo = input("\n¿Deseas escribir un nuevo texto? (s/n): ").lower()
        if escribir_nuevo == 's':
            nuevo_texto = input("Escribe el nuevo texto para la tarjeta: ")
            print("Acerca la tarjeta nuevamente para escribir...")
            reader.write(nuevo_texto)
            print("✍️ Texto escrito correctamente.")
        else:
            print("ℹ️ No se escribió nuevo texto.")
    else:
        print("❌ Borrado cancelado.")

except Exception as e:
    print("⚠️ Error:", e)
finally:
    reader.cleanup()

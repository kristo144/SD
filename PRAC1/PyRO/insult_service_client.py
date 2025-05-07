#!/usr/bin/env python3
# Cliente para InsultService con PyRO4

import Pyro4
import time
import sys


def main():
    # Conectar con el servidor de nombres de PyRO
    ns = Pyro4.locateNS()

    # Buscar el servicio de insultos
    uri = ns.lookup("insult.service")

    # Conectar con el servicio
    insult_service = Pyro4.Proxy(uri)

    while True:
        print("\nInsult Service Cliente - Menú")
        print("1. Añadir un insulto")
        print("2. Ver todos los insultos")
        print("3. Suscribirse a insultos aleatorios")
        print("4. Salir")

        option = input("Selecciona una opción: ")

        if option == "1":
            insult = input("Introduce un insulto: ")
            result = insult_service.add_insult(insult)
            if result:
                print(f"Insulto '{insult}' añadido correctamente.")
            else:
                print(f"El insulto '{insult}' ya existe en la lista.")

        elif option == "2":
            insults = insult_service.get_insults()
            if insults:
                print("Lista de insultos:")
                for i, insult in enumerate(insults, 1):
                    print(f"{i}. {insult}")
            else:
                print("No hay insultos en la lista.")

        elif option == "3":
            # Crear un objeto callback para recibir notificaciones
            name = input("Introduce un nombre para el suscriptor: ")

            # Crear un daemon para el callback
            daemon = Pyro4.Daemon()

            # Importar y crear un objeto subscriber
            from insult_service import InsultSubscriber
            subscriber = InsultSubscriber(name)

            # Registrar el objeto subscriber
            uri = daemon.register(subscriber)

            # Suscribirse al servicio
            insult_service.subscribe(subscriber)
            print(f"Suscrito como '{name}'. Esperando insultos aleatorios...")

            try:
                # Iniciar un bucle para recibir callbacks
                daemon.requestLoop()
            except KeyboardInterrupt:
                print("Desuscribiendo...")
                insult_service.unsubscribe(subscriber)
                daemon.shutdown()

        elif option == "4":
            print("Saliendo...")
            break

        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCliente terminado por el usuario.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
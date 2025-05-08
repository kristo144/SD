# insult_client_pyro.py
import Pyro4
import sys


# Cliente para interactuar con el servicio de insultos
@Pyro4.expose
class InsultSubscriber:
    def receive_insult(self, insult):
        """Método que será llamado cuando el servicio envíe un insulto"""
        print(f"[RANDOM INSULT]: {insult}")


def main():
    # Conectar con el servicio
    insult_service = Pyro4.Proxy("PYRONAME:insult.service")

    # Crear y registrar un suscriptor para recibir insultos
    daemon = Pyro4.Daemon()
    subscriber = InsultSubscriber()
    uri = daemon.register(subscriber)

    # Menú de opciones
    while True:
        print("\n--- Cliente de InsultService ---")
        print("1. Añadir un insulto")
        print("2. Ver todos los insultos")
        print("3. Suscribirse a notificaciones")
        print("4. Cancelar suscripción")
        print("5. Salir")
        option = input("Selecciona una opción: ")

        if option == "1":
            insult = input("Escribe el insulto a añadir: ")
            if insult_service.add_insult(insult):
                print("Insulto añadido correctamente")
            else:
                print("El insulto ya existía en la lista")

        elif option == "2":
            insults = insult_service.get_insults()
            if insults:
                print("Lista de insultos:")
                for i, insult in enumerate(insults, 1):
                    print(f"{i}. {insult}")
            else:
                print("No hay insultos almacenados")

        elif option == "3":
            if insult_service.subscribe(str(uri)):
                print(f"Suscrito correctamente con URI: {uri}")
                # Iniciar un hilo para recibir notificaciones
                import threading
                thread = threading.Thread(target=daemon.requestLoop)
                thread.daemon = True
                thread.start()
            else:
                print("Ya estabas suscrito")

        elif option == "4":
            if insult_service.unsubscribe(str(uri)):
                print("Suscripción cancelada")
            else:
                print("No estabas suscrito")

        elif option == "5":
            print("Saliendo...")
            break

        else:
            print("Opción no válida")


if __name__ == "__main__":
    main()
import Pyro4
import Pyro4.errors
import sys
import uuid


@Pyro4.expose
class InsultCallback:
    """
    Callback para recibir notificaciones de insultos aleatorios
    """

    def notify(self, insult):
        print(f"\n[RANDOM INSULT]: {insult}")
        return True


def main():
    try:
        # Conectar con el servicio de insultos
        insult_service = Pyro4.Proxy("PYRONAME:insult.service")

        # Crear un callback para recibir notificaciones
        callback = InsultCallback()
        daemon = Pyro4.Daemon()
        callback_uri = daemon.register(callback)

        # Generar un ID único para este cliente
        client_id = str(uuid.uuid4())

        # Flag para mantener la ejecución del programa
        running = True

        # Flag para controlar la suscripción
        subscribed = False

        print("Cliente del Servicio de Insultos (Pyro4)")
        print("---------------------------------------")

        while running:
            print("\nOpciones:")
            print("1. Añadir insulto")
            print("2. Ver todos los insultos")
            print("3. Suscribirse a notificaciones")
            print("4. Cancelar suscripción")
            print("5. Ver suscriptores activos")
            print("6. Salir")

            choice = input("\nSelecciona una opción (1-6): ")

            if choice == "1":
                insult = input("Introduce el insulto a añadir: ")
                if insult_service.add_insult(insult):
                    print(f"Insulto '{insult}' añadido correctamente")
                else:
                    print(f"El insulto '{insult}' ya existe o es inválido")

            elif choice == "2":
                insults = insult_service.get_insults()
                if insults:
                    print("\nLista de insultos:")
                    for idx, insult in enumerate(insults, 1):
                        print(f"{idx}. {insult}")
                else:
                    print("No hay insultos almacenados")

            elif choice == "3":
                if subscribed:
                    print("Ya estás suscrito a las notificaciones")
                else:
                    # Suscribirse para recibir notificaciones
                    if insult_service.subscribe(client_id, callback):
                        subscribed = True
                        print("Te has suscrito a las notificaciones de insultos aleatorios")
                        # Iniciar un hilo para procesar callbacks
                        import threading
                        daemon_thread = threading.Thread(target=daemon.requestLoop)
                        daemon_thread.daemon = True
                        daemon_thread.start()
                    else:
                        print("Error al suscribirse")

            elif choice == "4":
                if not subscribed:
                    print("No estás suscrito a las notificaciones")
                else:
                    # Cancelar la suscripción
                    if insult_service.unsubscribe(client_id):
                        subscribed = False
                        print("Has cancelado tu suscripción")
                    else:
                        print("Error al cancelar la suscripción")

            elif choice == "5":
                # Ver suscriptores activos
                subscribers = insult_service.get_subscribers()
                if subscribers:
                    print("\nSuscriptores activos:")
                    for idx, subscriber_id in enumerate(subscribers, 1):
                        status = "TÚ" if subscriber_id == client_id else ""
                        print(f"{idx}. {subscriber_id} {status}")
                else:
                    print("No hay suscriptores activos")

            elif choice == "6":
                # Cancelar suscripción si existe antes de salir
                if subscribed:
                    insult_service.unsubscribe(client_id)
                running = False
                print("Saliendo...")

            else:
                print("Opción no válida, intenta de nuevo")

    except Pyro4.errors.PyroError as e:
        print(f"Error de Pyro4: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSaliendo...")
        # Cancelar suscripción si existe antes de salir por Ctrl+C
        if 'subscribed' in locals() and subscribed and 'insult_service' in locals():
            try:
                insult_service.unsubscribe(client_id)
            except:
                pass
        sys.exit(0)


if __name__ == "__main__":
    main()
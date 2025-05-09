import Pyro4
import Pyro4.errors
import sys


def main():
    try:
        # Conectar con el servicio de filtrado
        filter_service = Pyro4.Proxy("PYRONAME:filter.service")

        # También conectamos con el servicio de insultos para verificar qué insultos hay disponibles
        insult_service = Pyro4.Proxy("PYRONAME:insult.service")

        # Flag para mantener la ejecución del programa
        running = True

        print("Cliente del Servicio de Filtrado de Insultos (Pyro4)")
        print("--------------------------------------------------")

        while running:
            print("\nOpciones:")
            print("1. Filtrar texto")
            print("2. Ver textos filtrados")
            print("3. Ver insultos disponibles para filtrar")
            print("4. Salir")

            choice = input("\nSelecciona una opción (1-4): ")

            if choice == "1":
                # Obtener el texto a filtrar
                text = input("Introduce el texto a filtrar: ")

                # Enviar el texto para filtrado
                filtered_text = filter_service.filter_text(text)

                print("\nTexto filtrado:")
                print(filtered_text)

            elif choice == "2":
                # Ver textos filtrados
                filtered_texts = filter_service.get_filtered_texts()
                if filtered_texts:
                    print("\nTextos filtrados:")
                    for idx, text in enumerate(filtered_texts, 1):
                        print(f"{idx}. {text}")
                else:
                    print("No hay textos filtrados")

            elif choice == "3":
                # Ver insultos disponibles (obtenidos del InsultService)
                try:
                    insults = insult_service.get_insults()
                    if insults:
                        print("\nInsultos disponibles para filtrar:")
                        for idx, insult in enumerate(insults, 1):
                            print(f"{idx}. {insult}")
                    else:
                        print("No hay insultos disponibles en el sistema")
                except Pyro4.errors.PyroError as e:
                    print(f"Error al conectar con el servicio de insultos: {e}")

            elif choice == "4":
                running = False
                print("Saliendo...")

            else:
                print("Opción no válida, intenta de nuevo")

    except Pyro4.errors.PyroError as e:
        print(f"Error de Pyro4: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSaliendo...")
        sys.exit(0)


if __name__ == "__main__":
    main()
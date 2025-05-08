# insult_filter_client_pyro.py
import Pyro4
import time


def main():
    # Conectar con ambos servicios
    insult_service = Pyro4.Proxy("PYRONAME:insult.service")
    insult_filter = Pyro4.Proxy("PYRONAME:insult.filter")

    # Obtener la lista de insultos del InsultService y configurarla en el InsultFilter
    insults = insult_service.get_insults()
    if not insults:
        print("No hay insultos en el servicio. Añadiendo algunos para pruebas...")
        test_insults = ["tonto", "idiota", "imbécil", "estúpido"]
        for insult in test_insults:
            insult_service.add_insult(insult)
        insults = insult_service.get_insults()

    print(f"Configurando lista de insultos en el filtro: {insults}")
    insult_filter.set_insult_list(insults)

    # Menú de opciones
    while True:
        print("\n--- Cliente de InsultFilter ---")
        print("1. Filtrar un texto")
        print("2. Ver textos filtrados")
        print("3. Salir")
        option = input("Selecciona una opción: ")

        if option == "1":
            text = input("Escribe el texto a filtrar: ")
            if insult_filter.filter_text(text):
                print("Texto enviado para ser filtrado")
            else:
                print("Error al enviar el texto")

            # Esperar un momento para que se procese el texto
            time.sleep(0.5)

        elif option == "2":
            filtered_texts = insult_filter.get_filtered_texts()
            if filtered_texts:
                print("Textos filtrados:")
                for i, text in enumerate(filtered_texts, 1):
                    print(f"{i}. {text}")
            else:
                print("No hay textos filtrados")

        elif option == "3":
            print("Saliendo...")
            break

        else:
            print("Opción no válida")


if __name__ == "__main__":
    main()
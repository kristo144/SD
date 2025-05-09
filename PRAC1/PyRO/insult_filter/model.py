"""
    Servicio para filtrar textos que contienen insultos, reemplazándolos
    por "CENSORED" y almacenando los resultados.
"""

class InsultFilter:
    def __init__(self):
        """
        Inicializa el filtro de insultos con una lista vacía para almacenar resultados.
        """
        self.filtered_texts = []    # Lista para almacenar los textos filtrados

    def filter_text(self, text, insults):
        """
        Filtra un texto reemplazando los insultos por "CENSORED"

        Args:
            text (str): El texto a filtrar
            insults (list): Lista de insultos a censurar

        Returns:
            str: El texto con los insultos censurados
        """
        # Crear una copia para no modificar el original
        filtered = text

        # Aplicar el filtrado para cada insulto
        for insult in insults:
            # Asegurarse de que el insulto no está vacío
            if insult.strip():
                # Reemplazar el insulto por "CENSORED" (case insensitive)
                filtered = filtered.replace(insult, "CENSORED")
                # También considerar mayúsculas/minúsculas
                filtered = filtered.replace(insult.lower(), "CENSORED")
                filtered = filtered.replace(insult.upper(), "CENSORED")
                filtered = filtered.replace(insult.capitalize(), "CENSORED")

        self.filtered_texts.append(filtered)    # Almacenar el resultado en la lista de textos filtrados

        return filtered

    def get_filtered_texts(self):
        """
        Devuelve la lista de textos filtrados

        Returns:
            list: Lista de textos filtrados
        """
        return self.filtered_texts
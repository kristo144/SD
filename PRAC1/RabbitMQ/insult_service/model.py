"""
    Servicio que gestiona una lista de insultos y permite operaciones como
    añadir insultos, consultar la lista y suscribirse a emisiones de insultos aleatorios.
    Implementación para RabbitMQ.
"""
import json


class InsultService:
    def __init__(self):
        # Lista para almacenar los insultos
        self.insults = []
        # Lista para almacenar los IDs de los suscriptores
        self.subscribers = []

    def add_insult(self, insult):
        """
        Añade un insulto a la lista si no existe ya

        Args:
            insult (str): El insulto a añadir

        Returns:
            bool: True si se añadió con éxito, False si ya existía
        """
        if insult.strip() and insult not in self.insults:
            self.insults.append(insult)
            return True
        return False

    def get_insults(self):
        """
        Devuelve la lista completa de insultos

        Returns:
            list: Lista de insultos almacenados
        """
        return self.insults

    def subscribe(self, subscriber_id):
        """
        Registra un suscriptor para recibir insultos aleatorios

        Args:
            subscriber_id (str): Identificador único del suscriptor

        Returns:
            bool: True si la suscripción fue exitosa
        """
        if subscriber_id not in self.subscribers:
            self.subscribers.append(subscriber_id)
            return True
        return False

    def unsubscribe(self, subscriber_id):
        """
        Elimina un suscriptor de la lista de suscriptores

        Args:
            subscriber_id (str): Identificador único del suscriptor

        Returns:
            bool: True si se eliminó, False si no existía
        """
        if subscriber_id in self.subscribers:
            self.subscribers.remove(subscriber_id)
            return True
        return False

    def get_subscribers(self):
        """
        Devuelve la lista de IDs de suscriptores

        Returns:
            list: Lista de IDs de suscriptores
        """
        return self.subscribers

# insult_filter_pyro.py
import Pyro4
import threading
import queue
import time
import multiprocessing


@Pyro4.expose
class InsultFilter:
    def __init__(self):
        self.insult_list = []  # Lista para almacenar los insultos conocidos
        self.filtered_texts = []  # Lista para almacenar los textos filtrados
        self.work_queue = queue.Queue()  # Cola de trabajo
        self.workers = []  # Lista de trabajadores
        self.running = True

        # Crear trabajadores para procesar textos
        for _ in range(multiprocessing.cpu_count()):
            worker = threading.Thread(target=self._process_queue)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def set_insult_list(self, insults):
        """Establece la lista de insultos a filtrar"""
        self.insult_list = insults

    def filter_text(self, text):
        """Añade un texto a la cola para ser filtrado"""
        # Añadir el texto a la cola de trabajo
        self.work_queue.put(text)
        return True

    def get_filtered_texts(self):
        """Devuelve la lista de textos filtrados"""
        return self.filtered_texts

    def _process_queue(self):
        """Procesa los textos en la cola de trabajo"""
        while self.running:
            try:
                # Obtener un texto de la cola con un timeout
                text = self.work_queue.get(timeout=1)
                filtered_text = self._filter_insults(text)
                self.filtered_texts.append(filtered_text)
                self.work_queue.task_done()
            except queue.Empty:
                # Si la cola está vacía, esperar un poco
                time.sleep(0.1)

    def _filter_insults(self, text):
        """Reemplaza los insultos en el texto con 'CENSORED'"""
        words = text.split()
        for i, word in enumerate(words):
            # Eliminar puntuación para la comparación
            clean_word = ''.join(c for c in word.lower() if c.isalnum())
            if clean_word in [insult.lower() for insult in self.insult_list]:
                words[i] = "CENSORED"
        return ' '.join(words)

    def stop(self):
        """Detiene todos los trabajadores"""
        self.running = False
        for worker in self.workers:
            worker.join()


# Iniciar el servidor Pyro4
def start_server():
    # Crear y registrar el servicio
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(InsultFilter)
    ns.register("insult.filter", uri)

    print(f"El servidor InsultFilter está ejecutándose en: {uri}")
    daemon.requestLoop()


if __name__ == "__main__":
    start_server()
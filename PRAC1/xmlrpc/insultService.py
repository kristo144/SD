#!/usr/bin/env python3

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy

from threading import Thread
from time import sleep
from random import choice
from sys import argv

class InsultRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class insultService:
    def add_insult(self, new_insult: str):
        self.insults.add(new_insult)
        return "Accepted"

    def get_insults(self):
        return list(self.insults)

    def insult_me(self):
        return choice(list(self.insults))

    def subscribe(self, url: str):
        observer = ServerProxy(url)
        self.observers.add(observer)
        return True

    def publish(self):
        while True:
            _ins = list(self.insults)
            removed = set()
            for observer in self.observers:
                insult = choice(_ins)
                try:
                    observer.notify(insult)
                except:
                    removed.add(observer)
            self.observers.difference_update(removed)
            sleep(5)

    def serve(self, port=8080):
        server = SimpleXMLRPCServer(('localhost', port), requestHandler=InsultRequestHandler, logRequests=False)
        server.register_introspection_functions()
        for func in [
                self.add_insult,
                self.get_insults,
                self.insult_me,
                self.subscribe
                ]:
            server.register_function(func)

        self.insults = { "tonto", "lerdo", "desagradable" }
        self.observers = set()

        thread = Thread(target=self.publish)
        thread.daemon = True
        thread.start()
        server.serve_forever()

if __name__ == "__main__":
    if len(argv) > 1:
        insultService().serve(argv[1])
    else:
        insultService().serve()

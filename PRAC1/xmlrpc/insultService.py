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

port = 8080
if len(argv)>1:
    port = int(argv[1])

with SimpleXMLRPCServer(
     ('localhost', port),
     requestHandler=InsultRequestHandler) as server:
    server.register_introspection_functions()

    insults = { "tonto", "lerdo", "desagradable" }
    observers = set()

    def add_insult(new_insult: str):
        insults.add(new_insult)
        return "Accepted"

    def get_insults():
        return list(insults)

    def insult_me():
        return choice(list(insults))

    def serve():
        server.serve_forever()

    def subscribe(url: str):
        observer = ServerProxy(url)
        observers.add(observer)
        return True

    def publish():
        global observers
        _ins = list(insults)
        removed = set()
        for observer in observers:
            insult = choice(_ins)
            try:
                observer.notify(insult)
            except:
                removed.add(observer)
        observers = observers - removed

    for func in [add_insult, get_insults, insult_me, subscribe]:
        server.register_function(func)

    thread = Thread(target = serve)
    thread.start()

    i = 0
    while True:
        publish()
        sleep(5)

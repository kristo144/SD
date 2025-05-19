#!/usr/bin/env python3

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy

from time import sleep

class InsultRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

server = SimpleXMLRPCServer(('localhost', 8081), requestHandler=InsultRequestHandler)
server.register_introspection_functions()
proxy = ServerProxy("http://localhost:8080")

texts = set()

def add_text(new_text: str):
    insults = proxy.get_insults()
    for insult in insults:
        new_text = new_text.replace(insult, "CENSORED")
    texts.add(new_text)
    return "Accepted"

def get_texts():
    return list(texts)

for func in [add_text, get_texts]:
    server.register_function(func)

server.serve_forever()

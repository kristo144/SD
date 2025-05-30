#!/usr/bin/env python3

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy

from time import sleep
from sys import argv

class InsultRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class filterService:
    def add_text(self, new_text: str):
        insults = self.proxy.get_insults()
        for insult in insults:
            new_text = new_text.replace(insult, "CENSORED")
        self.texts.add(new_text)
        return new_text

    def get_texts(self):
        return list(self.texts)

    def serve(self, port=8090, insult_port=8080):
        server = SimpleXMLRPCServer(('localhost', port), requestHandler=InsultRequestHandler)
        server.register_introspection_functions()
        self.proxy = ServerProxy(f"http://localhost:{insult_port}")
        self.texts = set()
        for func in [self.add_text, self.get_texts]:
            server.register_function(func)
        server.serve_forever()

if __name__ == "__main__":
    if len(argv) > 1:
        filterService().serve(argv[1])
    else:
        filterService().serve()

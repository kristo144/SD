#!/usr/bin/env python3

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy

from sys import argv

server = ServerProxy('http://localhost:8080')


class Observer(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2')

def notify(msg: str):
    print(msg)
    return True

if len(argv) == 1:
    client = SimpleXMLRPCServer(('localhost', 0), requestHandler = Observer)
    client.register_introspection_functions()
    client.register_function(notify)
    addr = client.server_address
    url = 'http://' + addr[0] + ':' + str(addr[1])
    server.subscribe(url)
    client.serve_forever()
else:
    for insult in argv[1:]:
        server.add_insult(insult)
    print(server.get_insults())

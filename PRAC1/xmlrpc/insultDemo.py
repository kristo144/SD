#!/usr/bin/env python3

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy

from sys import argv, exit
from time import sleep
from insultService import insultService
from threading import Thread

server = ServerProxy('http://localhost:8080')

print("Demo script for insultService")
print("Starting insultService...")
service_thread = Thread(target=insultService().serve)
service_thread.daemon = True
service_thread.start()
sleep(2)

print("\n----\n")
print("Get list of insults:")
print(server.get_insults())

print("\n----\n")
newInsult = "poopyhead"
print(f"Add insult '{newInsult}':")
server.add_insult(newInsult)
print("Get list of insults:")
print(server.get_insults())

print("\n----\n")
numInsults = 3
print(f"Get {numInsults} insults:")
for i in range(numInsults):
    print(server.insult_me())

print("\n----\n")
print("Subscribing to insultService. ^C to close.")

class Observer(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2')

def notify(msg: str):
    print(msg)
    return True

client = SimpleXMLRPCServer(('localhost', 0), requestHandler = Observer)
client.register_introspection_functions()
client.register_function(notify)
addr = client.server_address
url = 'http://' + addr[0] + ':' + str(addr[1])
server.subscribe(url)
client.serve_forever()

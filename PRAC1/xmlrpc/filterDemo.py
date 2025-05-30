#!/usr/bin/env python3

from xmlrpc.client import ServerProxy

from time import sleep
from threading import Thread

from insultService import insultService
from filterService import filterService

server = ServerProxy('http://localhost:8090')

print("Demo script for filterService")

print("Starting insultService...")
insult_thread = Thread(target = insultService().serve)
insult_thread.daemon = True
insult_thread.start()
sleep(2)

print("Starting filterService...")
filter_thread = Thread(target = filterService().serve)
filter_thread.daemon = True
filter_thread.start()
sleep(2)

print("\n----\n")
texts = [ "eres muy tonto", "eres un lerdo" ]
for text in texts:
    print(f"Submit insult '{text}':")
    print(server.add_text(text))

print("\n----\n")
print("Get list of texts:")
print(server.get_texts())

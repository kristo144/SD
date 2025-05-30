#!/usr/bin/env python3

from xmlrpc.client import ServerProxy

from subprocess import Popen
from time import sleep

server = ServerProxy('http://localhost:8081')

print("Demo script for filterService")
print("Starting insultService...")
process = Popen("./insultService.py")
sleep(2)
print("Starting filterService...")
process2 = Popen("./filterService.py")
sleep(2)

print("\n----\n")
texts = [ "eres muy tonto", "eres un lerdo" ]
for text in texts:
    print(f"Submit insult '{text}':")
    print(server.add_text(text))

print("\n----\n")
print("Get list of texts:")
print(server.get_texts())


print("Closing servers:")
process2.kill()
process.kill()

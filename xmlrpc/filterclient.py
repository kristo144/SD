#!/usr/bin/env python3

from xmlrpc.client import ServerProxy

from sys import argv

server = ServerProxy('http://localhost:8081')

def notify(msg: str):
    print(msg)
    return True

if len(argv) == 1:
    print(server.get_texts())
else:
    server.add_text(" ".join(argv[1:]))

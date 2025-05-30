#!/usr/bin/env python3

from os import _exit as exit
from redis import Redis
from threading import Thread
from insultService import insultService

print("Demo script for insultService")

server = Redis(decode_responses=True)

insult_set = "INSULTS"

print("\n----\n")
print("Clear insults:")
server.delete(insult_set)
print("Get list of insults:")
print(server.smembers(insult_set))

print("\n----\n")
for newInsult in [ "tonto", "lerdo", "desagradable" ]:
    print(f"Add insult '{newInsult}':")
    server.sadd(insult_set, newInsult)
    print("Get list of insults:")
    print(server.smembers(insult_set))

print("\n----\n")
print("Starting insultService...")
service = insultService()
thread = Thread(target = service.serve)
thread.start()

try:
    print("Subscribing to insultService. ^C to close.")
    pubsub = server.pubsub()
    pubsub.subscribe("insult_channel")
    for msg in pubsub.listen():
        if msg["type"] == "message":
            print(f"Received: {msg['data']}")
except KeyboardInterrupt:
    exit(0)

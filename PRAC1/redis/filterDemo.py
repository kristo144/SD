#!/usr/bin/env python3

from os import _exit as exit
from redis import Redis
from threading import Thread
from filterService import filterService
from time import sleep

print("Demo script for filterService")

server = Redis(decode_responses=True)
server.delete("result_list")
for newInsult in [ "tonto", "lerdo", "desagradable" ]:
    server.sadd("insult_set", newInsult)

service = filterService()
thread = Thread(target=service.serve)
thread.start()

print("\n----\n")
texts = [ "eres muy tonto", "eres un lerdo" ]
for text in texts:
    print(f"Submit insult '{text}':")
    print(server.lpush("text_queue", text))

print("Waiting 2 seconds...")
sleep(2)

print("\n----\n")
print("Get list of texts:")
print(server.smembers("result_list"))

exit(0)

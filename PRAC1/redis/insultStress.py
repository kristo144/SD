#!/usr/bin/env python3

from os import _exit as exit
from time import time, sleep
from sys import argv
from os import process_cpu_count
from multiprocessing import Pool
from itertools import repeat

from redis import Redis

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

num_reqs = 100_000
if len(argv) > 1:
    num_reqs = int(argv[1])
num_workers = process_cpu_count()
total_reqs = num_reqs * num_workers

def worker(none):
    for j in range(num_reqs):
        insult = server.srandmember(insult_set)

print(f'Testing {total_reqs} requests across {num_workers} workers.')
pool = Pool(num_workers)
start_time = time()
pool.map(worker, repeat(None, num_workers))
end_time = time()
total_time = end_time - start_time
average = total_reqs/total_time
print(f'Done in {total_time} seconds, throughput {average} requests/second')

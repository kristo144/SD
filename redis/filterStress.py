#!/usr/bin/env python3

from redis import Redis
from filterService import filterService
from multiprocessing import Process
from time import sleep

total_reqs = 1_000_000
work_time = 30

server = Redis(decode_responses=True)
server.delete("text_queue")
server.delete("total_queue")

print(f"Adding {total_reqs} texts to queue");
for i in range(total_reqs):
    server.lpush("total_queue", "eres tonto")

for num_nodes in [1, 2, 3]:
    print(f"Testing for {num_nodes} nodes")
    server.copy("total_queue", "text_queue", replace=True)
    active = [ filterService() for i in range(num_nodes) ]
    procs = [ Process(target=service.serve) for service in active ]

    print("Processing insults");
    [ proc.start() for proc in procs ]
    sleep(work_time)
    [ proc.terminate() for proc in procs ]

    remaining = server.llen("text_queue")
    processed = total_reqs - remaining
    rate = processed/work_time
    print(f"Processed {rate} requests per second.")

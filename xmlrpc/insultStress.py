#!/usr/bin/env python3

from xmlrpc.client import ServerProxy
from subprocess import Popen, DEVNULL
from multiprocessing import Pool
from itertools import cycle, repeat
from functools import partial
from time import time, sleep
from sys import argv
from os import process_cpu_count

procs = []
procs.append(Popen(["nice", "--10", "./insultService.py", "8080"], stderr=DEVNULL))
procs.append(Popen(["nice", "--10", "./insultService.py", "8081"], stderr=DEVNULL))
procs.append(Popen(["nice", "--10", "./insultService.py", "8082"], stderr=DEVNULL))

sleep(2)

servers = [
    ServerProxy('http://localhost:8080'),
    ServerProxy('http://localhost:8081'),
    ServerProxy('http://localhost:8082'),
]

num_reqs = 10_000
if len(argv) > 1:
    num_reqs = int(argv[1])
num_workers = process_cpu_count()
total_reqs = num_reqs * num_workers
average_time = dict()

def worker(nodes):
    nodes = cycle(servers[:nodes])
    for j in range(num_reqs):
        next(nodes).insult_me()

pool = Pool(num_workers)
for num_nodes in [1, 2, 3]:
    print(f"Testing for {num_nodes} nodes")
    start_time = time()
    pool.map(worker, repeat(num_nodes, num_workers))
    end_time = time()

    total = end_time - start_time
    average_time[num_nodes] = total_reqs/total
    print(f'Processed {total_reqs} requests across {num_workers} workers in {total}s')
    print(f'Average: {average_time[num_nodes]} requests/second')

[ proc.kill() for proc in procs ]

#!/usr/bin/env python3

from xmlrpc.client import ServerProxy
#from subprocess import Popen, DEVNULL
from multiprocessing import Pool, Process
from itertools import cycle, repeat
from functools import partial
from time import time, sleep
from sys import argv
from os import process_cpu_count

from insultService import insultService

procs = []
servers = []
for i in range(3):
    p = Process(target=insultService().serve, args=(8080 + i,))
    procs.append(p)
    p.start()
    servers.append(ServerProxy(f"http://localhost:{8080+i}"))

sleep(2)

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

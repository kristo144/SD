#!/usr/bin/env python3

from redis import Redis
from time import sleep

class insultService:
    def serve(self):
        self.server = Redis()
        while True:
            insult = self.server.srandmember("INSULTS")
            self.server.publish("insult_channel", insult)
            sleep(5)

if __name__ == "__main__":
    insultService().serve()

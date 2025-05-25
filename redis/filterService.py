#!/usr/bin/env python3

from redis import Redis

class filterService:
    def serve(self):
        self.server = Redis(decode_responses=True)
        while True:
            new_text = self.server.blpop("text_queue")[1]
            insults = list(self.server.smembers("INSULTS"))
            for insult in insults:
                new_text = new_text.replace(insult, "CENSORED")
            self.server.sadd("result_list",new_text)

if __name__ == "__main__":
    filterService().serve()

from utils.states import Event
from src.atc_agent import Agent
from utils.logger import Logger


class ARTSSClock():
    def __init__(self, start_time):
        self.time = start_time

    def tick(self):
        self.time += 1

    def get_time(self):
        return "00:00"


class ARTSS():
    def __init__(self):
        self.clock = ARTSSClock(0)
        self.logger = Logger(self.clock) 
        self.atc_agent = Agent()

    def tick(self):
        self.clock.tick()
        return Event.NONE

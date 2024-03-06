from utils.states import Event
from atc_agent import Agent

class ARTSS():
    def __init__(self):
        self.atc_agent = Agent()
        pass

    def tick(self):
        return Event.NONE

from utils.states import Event
from .atc_agent import Agent
from utils.logger import Logger
from utils.map_handler import load_map
from .plane_agent import Plane
from utils.flight_data_handler import FlightStatus
from utils.coms import CommunicationType


def init_plane_queue(num_planes):
    queue = []
    for _ in range(num_planes):
        queue.append(Plane((0, 255, 0), 50, 50))
    pass


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
        self.plane_queue = init_plane_queue() 
        self.map = load_map()

    def tick(self):
        self.clock.tick()
        self.address_queue()
        return Event.NONE

    def address_queue(self):
        plane = self.plane_queue.pop(0)
        self.plane_queue.append(plane)

        status = plane.get_status()
        if status == FlightStatus.HOLDING_SHORT:
            com = self.atc_agent.check_request(("", CommunicationType.HOLDING_SHORT), plane)
            plane.receieve_com(self.atc_agent, com)
            return
        elif status == FlightStatus.WAITING_FOR_TAKEOFF_CLEARANCE:
            com = self.atc_agent.check_request(("", CommunicationType.TAKEOFF_CLEARANCE))
            plane.receieve_com(self.atc_agent, com)
            return
        elif int(status) > 0:
            return

        plane.send_com(self.atc_agent, status)

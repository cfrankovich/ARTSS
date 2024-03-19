from utils.states import Event
from .atc_agent import Agent
from utils.logger import ARTSSClock 
from .plane_agent import Plane
from utils.flight_data_handler import FlightStatus
from utils.coms import CommunicationType

def init_plane_queue(num_planes):
    queue = []
    for _ in range(num_planes):
        queue.append(Plane())
    return queue


class ARTSS():
    # static for user interface - werks so not fixing  
    plane_queue = None 

    def __init__(self):
        self.atc_agent = Agent()
        ARTSS.plane_queue = init_plane_queue(1)

    def tick(self):
        ARTSSClock.tick()
        self.address_queue()
        return Event.NONE
    
    def address_queue(self):
        plane = ARTSS.plane_queue.pop(0)
        ARTSS.plane_queue.append(plane)

        status = plane.get_status()
        if status == FlightStatus.HOLDING_SHORT:
            self.atc_agent.receive_com(("", CommunicationType.HOLDING_SHORT), plane)
            return
        elif status == FlightStatus.WAITING_FOR_TAKEOFF_CLEARANCE:
            self.atc_agent.receive_com(("", CommunicationType.TAKEOFF_CLEARANCE), plane)
            return
        elif int(status.value) > 0:
            plane.update(self.atc_agent)
            return

        plane.send_com(self.atc_agent)

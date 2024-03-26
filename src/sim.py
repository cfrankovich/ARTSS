from utils.states import Event
from .atc_agent import Agent
from utils.logger import ARTSSClock 
from .plane_agent import init_plane_queue, plane_queue 
from utils.flight_data_handler import FlightStatus
from utils.coms import CommunicationType
from utils.map_handler import init_winds, adjust_wind, debug_init_winds

STARTING_PLANE_COUNT = 6


class ARTSS():
    def __init__(self):
        self.atc_agent = Agent()
        init_plane_queue(STARTING_PLANE_COUNT)
        init_winds(300)
        #debug_init_winds(300)

    def tick(self):
        ARTSSClock.tick()
        adjust_wind()
        self.address_queue()
        return Event.NONE
    
    def address_queue(self):
        for plane in plane_queue:
            status = plane.get_status()

            if status == FlightStatus.HOLDING_SHORT: # reminder for atc to check on the plane w/o sending com
                self.atc_agent.receive_com(("", CommunicationType.HOLDING_SHORT), plane)
                continue
            elif status == FlightStatus.WAITING_FOR_TAKEOFF_CLEARANCE: # another reminder 
                self.atc_agent.receive_com(("", CommunicationType.TAKEOFF_CLEARANCE), plane)
                continue
            elif int(status.value) > 0: # positive enum values are not dependent on the atc
                plane.update()
                continue

            plane.send_com(self.atc_agent)

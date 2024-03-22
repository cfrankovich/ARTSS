from utils.states import Event
from .atc_agent import Agent
from utils.logger import ARTSSClock 
from .plane_agent import init_plane_queue, plane_queue 
from utils.flight_data_handler import FlightStatus
from utils.coms import CommunicationType
import random
import numpy as np

STARTING_PLANE_COUNT = 3
MAX_WIND_SPEED = 25
MIN_WIND_SPEED = 5

winds = []
wind_direction = random.randrange(0, 360) # deg 
wind_speed = random.randrange(MIN_WIND_SPEED, MAX_WIND_SPEED + 1) # knots 
winds.append((wind_direction, wind_speed))


def adjust_wind():
    global winds
    global wind_direction
    global wind_speed 

    new_wind = winds.pop(0)
    wind_direction = new_wind[0]
    wind_speed = new_wind[1]

    dir = int(np.random.normal(winds[-1][0], 8)) % 360 
    speed = int(np.random.normal(winds[-1][1], 4))
    speed = max(MIN_WIND_SPEED, min(MAX_WIND_SPEED, speed))
    winds.append((dir, speed))


def init_winds(samples):
    global winds
    for i in range(1, samples):
        dir = int(np.random.normal(winds[i-1][0], 8)) % 360 
        speed = int(np.random.normal(winds[i-1][1], 4))
        speed = max(MIN_WIND_SPEED, min(MAX_WIND_SPEED, speed))
        winds.append((dir, speed))


def get_wind_info():
    return (wind_direction, wind_speed)


def get_winds():
    return winds


class ARTSS():
    def __init__(self):
        self.atc_agent = Agent(get_wind_info)
        init_plane_queue(STARTING_PLANE_COUNT)
        init_winds(100)

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

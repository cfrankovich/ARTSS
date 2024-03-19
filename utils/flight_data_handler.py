from enum import Enum
from .map_handler import get_random_gate
import random


# values < 0 mean its "actionable" 
class FlightStatus(Enum):
    AT_GATE = 0 
    READY_FOR_PUSHBACK = -1 # request to pushback via "PUSHBACK CLEARANCE" com 
    PUSHBACK_IN_PROGRESS = 2
    WAITING_FOR_TAXI_CLEARANCE = -3 # request to taxi via "TAXI CLEARANCE" com
    TAXIING_TO_RUNWAY = 4
    HOLDING_SHORT = -6 # plane sends "HOLDING SHORT" com - now ready for "LINE UP" com 
    LINING_UP = 7 # recieved "LINE UP" com from atc, now awaiting "TAKEOFF CLEARANCE" com 
    WAITING_FOR_TAKEOFF_CLEARANCE = 8
    TAKING_OFF = 9
    AIRBORNE = -10 # pilot sends "DEPARTURE" com 
    CLIMBING = 11 
    DEPARTED = 12 # marks success of departure 
    CRUISING = 13 # plane is cruising in airspace 
    REQUEST_TO_APPROACH = -14 # "INTIAL CONTACT WITH APPROACH CONTROL" com 
    HOLDING = 15 # pilot recieved "HOLD" com - hold before landing - fly in circular pattern 
    APPROACHING = -16 # pilot receieved "APPROACH CLEARANCE" com and pilot sends "INITIAL CONTACT WITH TOWER" com 
    DESCENDING = 17 # pilot receieved "LANDING CLEARANCE" com
    VACATING_RUNWAY = -18 # pilot sends "AFTER LANDING" com 
    TAXIING_TO_GATE = 19  
    SHUTTING_DOWN = 20 # pilot sends "AT THE GATE" com - marks success of landing 


def generate_flight_number():
    number_range = (100, 999)
    flight_number = random.randint(*number_range)
    airline_codes = ["DL", "AA", "ERU"]
    airline_code = random.choice(airline_codes) 
    return f"{airline_code}{flight_number}"


used_flight_nums = []
def generate_flight_data(status=FlightStatus.AT_GATE):
    num = generate_flight_number()
    while num in used_flight_nums:
        num = generate_flight_number()
    used_flight_nums.append(num)
    flight_data = {
        "flight_number" : num,
        "status" : status,
        "gate" : get_random_gate([]), # TODO: used gate numbers
        "runway" : None,
    }

    # TODO: planes landing
    if status == FlightStatus.REQUEST_TO_APPROACH:
        flight_data["gate"] = None

    return flight_data 

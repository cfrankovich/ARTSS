from utils.coms import CommunicationType 

AIRPORT = "DAB"

class Agent():
    def __init__(self):
        pass

    def send_com(self, com, plane):
        plane.receive_com(com)

    def receive_com(self, com, plane):
        com_to_send = self.check_request(plane, com) 
        if com_to_send is not None:
            self.send_com(com_to_send, plane)

    # Return command to send back to plane based on the checks
    def check_request(self, com, plane):
        fn = plane.flight_data["flight_number"]
        ct = com[1]
        if ct == CommunicationType.PUSHBACK_CLEARANCE:
            # TODO: check if clear to pushback 
            return (f"{fn}, {AIRPORT} Ground, cleared for pushback and engine start, advise ready to taxi.", CommunicationType.PUSHBACK_CLEARANCE)
        if ct == CommunicationType.TAXI_CLEARANCE:
            # TODO: check if taxiways are clear and assign a runway 
            runway_number = "" 
            taxiways = "" 
            return (f"{fn}, taxi to runway {runway_number}, via taxiways {taxiways}, hold short of runway {runway_number}.", CommunicationType.TAXI_CLEARANCE)
        if ct == CommunicationType.HOLDING_SHORT:
            # TODO: check if the assigned runway is clear to lineup if not, tell plane to continue holding and standby 
            #return (f"{fn}, hold short of runway {runway_number}, standby.", CommunicationType.HOLD_SHORT)
            runway_number = "" 
            return (f"{fn}, runway {runway_number}, line up and wait.", CommunicationType.LINE_UP)
        if ct == CommunicationType.TAKEOFF_CLEARANCE:
            # TODO: check if plane is clear for takeoff if not return None
            runway_number = ""
            return (f"{fn}, runway {runway_number}, cleared for takeoff.", CommunicationType.TAKEOFF_CLEARANCE)
        if ct == CommunicationType.DEPARTURE:
            desired_altitude = plane.flight_data["desired_altitude"] 
            return (f"{fn}, radar contact, climb to {desired_altitude}, proceed on course.", CommunicationType.DEPARTURE)
        return None 

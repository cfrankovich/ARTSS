from utils.coms import CommunicationType 
from utils.logger import logger
from utils.map_handler import TileType, find_taxiway_path, get_map, get_node_type, get_wind_info
from .plane_agent import DEPARTED_ALTITUDE, get_plane_queue

AIRPORT = "DAB"

class Agent():
    def send_com(self, com, plane):
        logger.log_atc_com(com[0])
        plane.receive_com(self, com)

    def receive_com(self, com, plane):
        com_to_send = self.check_request(plane, com) 
        if com_to_send is not None:
            self.send_com(com_to_send, plane)

    # returns the command to send back to plane based on the checks
    # TODO: clean this clutterfuck of a function
    def check_request(self, plane, com):
        fn = plane.flight_data["flight_number"]
        ct = com[1]
        if ct == CommunicationType.PUSHBACK_CLEARANCE:
            return (f"{fn}, {AIRPORT} Ground, cleared for pushback and engine start, advise ready to taxi.", CommunicationType.PUSHBACK_CLEARANCE)
        if ct == CommunicationType.TAXI_CLEARANCE:
            full_path = find_taxiway_path(plane, get_plane_queue())
            runway_node = full_path[-4]
            map = get_map()
            runway_number = map[runway_node[0]][runway_node[1]].info

            taxiways = [] 
            for node_pos in full_path:
                node = map[node_pos[0]][node_pos[1]] 
                if node.info not in taxiways and node.type is TileType.TAXIWAY:
                    taxiways.append(node.info)
            taxiways = ', '.join(taxiways)

            i = len(full_path) - 1
            while get_node_type(full_path[i]) is TileType.RUNWAY:
                i -= 1

            print(full_path)
            plane.runway_path = full_path[i+1:] 
            plane.current_path = full_path[:i+1]
            print(plane.current_path)
            print(plane.runway_path)
            print(f"ASSIGNED PLANE PATH: {plane.current_path}")

            return (f"{fn}, taxi to runway {runway_number}, via taxiways {taxiways}, hold short of runway {runway_number}.", CommunicationType.TAXI_CLEARANCE)
            return (f"", CommunicationType.NONE)
        if ct == CommunicationType.HOLDING_SHORT:
            runway_number = plane.flight_data["runway"] 
            clear = self.is_runway_clear_for_lineup(runway_number)
            if clear:
                return (f"{fn}, runway {runway_number}, line up and wait.", CommunicationType.LINE_UP)
            return (f"{fn}, hold short of runway {runway_number}, standby.", CommunicationType.HOLDING_SHORT)
        if ct == CommunicationType.TAKEOFF_CLEARANCE:
            runway_number = plane.flight_data["runway"] 
            wind = get_wind_info()
            return (f"{fn}, runway {runway_number}, cleared for takeoff, wind {wind[0]} degrees at {wind[1]} knots.", CommunicationType.TAKEOFF_CLEARANCE)
        if ct == CommunicationType.DEPARTURE:
            return (f"{fn}, radar contact, climb to {DEPARTED_ALTITUDE}, proceed on course.", CommunicationType.DEPARTURE)
        return None 

    def is_runway_clear_for_lineup(self, runway_number):
        pq = get_plane_queue()
        for plane in pq:
            if plane.flight_data["runway"] == runway_number:
                status_val = abs(plane.get_status().value)
                if status_val in range(7, 12): 
                    return False
        return True

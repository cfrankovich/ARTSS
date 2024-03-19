from utils.coms import CommunicationType 
from utils.logger import logger
from utils.map_handler import get_map, TileType, temp_add_fill 
from .plane_agent import DEPARTED_ALTITUDE

AIRPORT = "DAB"

class Agent():
    def __init__(self):
        pass

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
            runway_path = self.get_next_runway_path(plane.map_x, plane.map_y)
            runway_node = runway_path[-1]
            map = get_map()
            runway_number = map[runway_node[0]][runway_node[1]].info

            taxiways = [] 
            for node_pos in runway_path:
                node = map[node_pos[0]][node_pos[1]] 
                if node.info not in taxiways and node.type is TileType.TAXIWAY:
                    taxiways.append(node.info)
            taxiways = ', '.join(taxiways)

            plane.current_path = runway_path[:-1] # exclude runway 

            return (f"{fn}, taxi to runway {runway_number}, via taxiways {taxiways}, hold short of runway {runway_number}.", CommunicationType.TAXI_CLEARANCE)
        if ct == CommunicationType.HOLDING_SHORT:
            runway_number = plane.flight_data["runway"] 
            clear = True # TODO: check if the runway is clear
            if clear:
                return (f"{fn}, runway {runway_number}, line up and wait.", CommunicationType.LINE_UP)
            return (f"{fn}, hold short of runway {runway_number}, standby.", CommunicationType.HOLD_SHORT)
        if ct == CommunicationType.TAKEOFF_CLEARANCE:
            #return (f"{fn}, runway {runway_number}, cleared for takeoff, wind {wind_direction} at {wind_speed}.", CommunicationType.TAKEOFF_CLEARANCE)
            runway_number = plane.flight_data["runway"] 
            return (f"{fn}, runway {runway_number}, cleared for takeoff.", CommunicationType.TAKEOFF_CLEARANCE)
        if ct == CommunicationType.DEPARTURE:
            return (f"{fn}, radar contact, climb to {DEPARTED_ALTITUDE}, proceed on course.", CommunicationType.DEPARTURE)
        return None 

    def get_next_runway_path(self, mx, my):
        closest_runway_path = self.get_closest_runway(mx, my) 
        runway_loc = closest_runway_path[-1]
        temp_add_fill(runway_loc)
        map = get_map()
        return closest_runway_path 

    # breadth first search 
    def get_closest_runway(self, mx, my):
        map = get_map()
        queue = [(mx, my)]
        visited = [(mx, my)]
        parent_map = {}

        while queue:
            current_node = queue.pop(0) 

            if map[current_node[0]][current_node[1]].type == TileType.RUNWAY:
                path = []
                while current_node != (mx, my):
                    path.append(current_node)
                    current_node = parent_map[current_node]
                path.reverse()
                return path

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                next_node = (current_node[0] + dx, current_node[1] + dy)
                type = map[next_node[0]][next_node[1]].type
                if next_node not in visited and type is not TileType.NOTHING and type is not TileType.GATE:
                    visited.append(next_node)
                    queue.append(next_node)
                    parent_map[next_node] = current_node

        return None

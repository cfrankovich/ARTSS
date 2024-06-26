import pygame
from utils.flight_data_handler import generate_flight_data, FlightStatus, generate_aircraft_info 
from utils.coms import CommunicationType 
from utils.map_handler import gates, get_facing_direction_from_gate, Direction, get_adjacent_runway_pos
from utils.logger import logger
import matplotlib as plt
import numpy as np

AIRPORT = "DAB"
DEPARTURE_FREQUENCY = "125.800 MHz"
DEPARTED_ALTITUDE = 1000 # ft
gates_in_use = []
plane_queue = [] 
color_index = 0


def create_new_plane():
    global plane_queue
    plane_queue.append(Plane())


def is_next_node_occupied(node, p):
    for plane in plane_queue: 
        if plane.flight_data["flight_number"] == p.flight_data["flight_number"]:
            continue 
        if plane.get_map_pos() == node and plane.get_status() is not FlightStatus.DEPARTED:
            return True
    return False


def get_plane_queue():
    return plane_queue


def init_plane_queue(num_planes):
    global plane_queue
    for _ in range(num_planes):
        plane_queue.append(Plane())

def get_rainbow_color(amt, idx):
    global color_index
    rainbow_colors_red_to_violet = plt.cm.rainbow(np.linspace(1, 0, amt))
    rainbow_colors_red_to_violet_255 = [(int(color[0]*255), int(color[1]*255), int(color[2]*255)) for color in rainbow_colors_red_to_violet]
    color = rainbow_colors_red_to_violet_255[color_index]
    color_index = (color_index + 1) % 10
    color = (
        min(color[0] + 40, 255),
        min(color[1] + 40, 255),
        min(color[2] + 40, 255),
    )
    return color

class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.flight_data = generate_flight_data(gates_in_use) 
        self.aircraft_info = generate_aircraft_info() 
        gates_in_use.append(self.flight_data["gate"])
        self.map_x, self.map_y = self.get_initial_map_pos() 
        self.facing = get_facing_direction_from_gate(self.map_x, self.map_y) 
        self.facing = Direction((self.facing.value + 180) % 360) # opposite direction angle 
        self.current_path = [] 
        self.runway_path = []
        self.d_altitude = 1
        self.altitude = 0
        self.debug_paths = []
        self.debug_best_grade_path = []
        self.ticks = 0
        self.grades = []
        self.color = get_rainbow_color(10, 'lasdjfoasd8fu9as8df idc blajhablhahhhh')

        self.x = 0
        self.y = 0
        self.image = pygame.Surface((100,100))
        self.rect = self.image.get_rect()

    def get_grades(self):
        return self.grades

    def debug_set_grades(self, grades):
        sorted_grades = sorted(grades) 
        ranked_grades = [sorted_grades.index(grade) for grade in grades]
        self.grades = ranked_grades

    def get_grade_color(self, n):
        return self.grade_colors[n]

    def debug_set_best_grade_path(self, route):
        self.debug_best_grade_path = route

    def debug_get_best_grade_path(self):
        return self.debug_best_grade_path

    def get_debug_paths(self):
        return self.debug_paths

    def set_debug_paths(self, paths):
        self.debug_paths = paths

    def get_map_pos(self):
        return (self.map_x, self.map_y)

    def get_initial_map_pos(self):
        if self.get_status() == FlightStatus.AT_GATE:
            self.flight_data["status"] = FlightStatus.READY_FOR_PUSHBACK
            return gates[self.flight_data["gate"]]
        return (0, 0)

    def receive_com(self, atc, com):
        fn = self.flight_data["flight_number"]
        ct = com[1]

        if ct == CommunicationType.PUSHBACK_CLEARANCE:
            self.set_status(FlightStatus.PUSHBACK_IN_PROGRESS)
        elif ct == CommunicationType.TAXI_CLEARANCE:
            runway_number = self.extract_runway(com[0]) 
            self.flight_data["runway"] = runway_number
            taxiways = self.extract_taxiways(com[0])
            self.send_com(atc, (f"Taxi to runway {runway_number}, via taxiways {taxiways}, hold short of runway {runway_number}, {fn}.", CommunicationType.READ_BACK))
            gates_in_use.remove(self.flight_data["gate"])
            self.set_status(FlightStatus.TAXIING_TO_RUNWAY)
        elif ct == CommunicationType.LINE_UP:
            runway_number = self.flight_data["runway"] 
            self.set_status(FlightStatus.LINING_UP)
            self.current_path.append(get_adjacent_runway_pos(self.map_x, self.map_y))
            self.send_com(atc, (f"Runway {runway_number}, lining up and waiting, {fn}.", CommunicationType.LINE_UP))
        elif ct == CommunicationType.TAKEOFF_CLEARANCE:
            runway_number = self.flight_data["runway"] 
            self.current_path = self.runway_path
            self.aircraft_info["ticks_per_tile"] = 1 # speedy takeoff
            self.d_altitude = DEPARTED_ALTITUDE / len(self.current_path)
            self.set_status(FlightStatus.AIRBORNE)
            self.send_com(atc, (f"Runway {runway_number}, cleared for takeoff, {fn}.", CommunicationType.CONFIRM_TAKEOFF_CLEARANCE))

    def send_com(self, atc, com=None):
        fn = self.flight_data["flight_number"]
        if com is not None:
            logger.log_flight_com(fn, com[0])
            atc.receive_com(com, self)
            return
        status = self.flight_data["status"]
        com = ("", CommunicationType.NONE)

        if status == FlightStatus.READY_FOR_PUSHBACK:
            gate = self.flight_data["gate"]
            com = (f"{AIRPORT} Ground, {fn}, at gate {gate}, ready for pushback.", CommunicationType.PUSHBACK_CLEARANCE)
        elif status == FlightStatus.WAITING_FOR_TAXI_CLEARANCE:
            com = (f"{AIRPORT} Ground, {fn}, ready to taxi.", CommunicationType.TAXI_CLEARANCE)
            self.flight_data["status"] = FlightStatus.AT_GATE
        elif status == FlightStatus.HOLDING_SHORT:
            runway = self.flight_data["runway"]
            com = (f"Holding short of runway {runway}, {fn}.", CommunicationType.HOLDING_SHORT) 
        elif status == FlightStatus.AIRBORNE:
            com = (f"{fn}, climbing to {DEPARTED_ALTITUDE}.", CommunicationType.DEPARTURE)
            self.set_status(FlightStatus.CLIMBING)

        logger.log_flight_com(fn, com[0])
        atc.receive_com(com, self)

    def update(self):
        self.ticks += 1
        if self.ticks % self.aircraft_info["ticks_per_tile"] != 0:
            return
        status = self.flight_data["status"]
        if status == FlightStatus.PUSHBACK_IN_PROGRESS:
            self.facing = Direction((self.facing.value + 180) % 360)
            self.set_status(FlightStatus.WAITING_FOR_TAXI_CLEARANCE)
        elif status.value >= 5 and status.value < 12: # taxiing to departure
            #if status.value 
            try:
                self.move_on_path()
                if status == FlightStatus.CLIMBING:
                    self.altitude += self.d_altitude
                    if self.altitude >= DEPARTED_ALTITUDE:
                        create_new_plane()
                        if len(plane_queue) > 11:
                            plane_queue.pop(0)
                        self.set_status(FlightStatus.DEPARTED)
            except:
                new_status = self.get_next_status(status)
                if new_status == FlightStatus.DEPARTED:
                    create_new_plane()
                    if len(plane_queue) > 11:
                        plane_queue.pop(0)
                self.set_status(new_status)
        if status == FlightStatus.DEPARTED:
            pass
            #global plane_queue 
            #plane_queue.remove(self)

    def get_direction_of_next_node(self, node):
        dx = node[0] - self.map_x
        dy = node[1] - self.map_y
        if dx == 1:
            return Direction.EAST
        if dx == -1:
            return Direction.WEST
        if dy == 1:
            return Direction.SOUTH
        if dy == -1:
            return Direction.NORTH
        return None

    def get_facing_direction(self):
        return self.facing

    def get_status(self):
        return self.flight_data["status"]

    def set_status(self, new_status):
        self.flight_data["status"] = new_status

    def extract_taxiways(self, com):
        parts = com.split(", via taxiways ")
        if len(parts) > 1:
            taxiways_part = parts[1].split(", hold short of runway")[0]
            return taxiways_part.strip()
        return None 

    def extract_runway(self, com):
        parts = com.split("taxi to runway ")
        if len(parts) > 1:
            runway_number_part = parts[1].split(",")[0]
            return runway_number_part.strip()
        return None 

    def move_on_path(self):
        if is_next_node_occupied(self.current_path[0], self):
            return
        node = self.current_path.pop(0)
        self.map_x = node[0]
        self.map_y = node[1]
        next_face = self.get_direction_of_next_node(self.current_path[0])
        self.facing = self.facing if next_face is None else next_face 
        
    def get_next_status(self, status):
        try:
            return FlightStatus(status.value + 1) 
        except:
            return FlightStatus((status.value + 1) * -1)

    def get_aircraft_type(self):
        return self.aircraft_info["type"]

    def get_pos(self):
        return (self.map_x, self.map_y)

    def get_current_path(self):
        return self.current_path

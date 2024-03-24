from enum import Enum
import random
import numpy as np
import math 

MAP_PATH = "map.csv"
MAX_WIND_SPEED = 25
MIN_WIND_SPEED = 5

gates = {} 
map = [] 
runways = {}
debug_paths = []
winds = []
wind_direction = random.randrange(0, 360) # deg 
wind_speed = random.randrange(MIN_WIND_SPEED, MAX_WIND_SPEED + 1) # knots 
winds.append((wind_direction, wind_speed))


def get_wind_info():
    return (wind_direction, wind_speed)


def get_winds():
    return winds


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


def get_node_type_from_pos(pos):
    return map[pos[0]][pos[1]].type 


def get_map():
    global map
    return map


class Direction(Enum):
    NORTH = 0
    WEST = 90 
    SOUTH = 180 
    EAST = 270 


class TileType(Enum):
    NOTHING = 0
    RUNWAY = 1
    TAXIWAY = 2
    GATE = 3


class Tile():
    def __init__(self, x, y, t=TileType.NOTHING):
        self.x = x
        self.y = y
        self.label = ''
        self.color = (0, 0, 0)
        self.type = TileType.NOTHING 
        self.toggle(t)
        self.info = ""
        self.fill = 1

    def toggle(self, tool):
        if tool == TileType.RUNWAY: 
            self.color = (255, 0, 255)
            self.type = TileType.RUNWAY
        elif tool == TileType.TAXIWAY:
            self.color = (0, 255, 0)
            self.type = TileType.TAXIWAY
        elif tool == TileType.GATE:
            self.color = (255, 255, 0)
            self.type = TileType.GATE
        else: 
            self.color = (0, 0, 0)
            self.type = TileType.NOTHING 
    
    def set_info(self, i):
        self.info = i

    def get_pos(self):
        return (self.x, self.y)


def get_random_gate(gates_in_use, flight_num):
    gate = random.choice(list(gates.items()))[0]
    char_to_check = "A" if flight_num[:2] == "ER" else "B" # gates B-XX are exclusive to ERU flights 
    while gate in gates_in_use and gate[0] == char_to_check:
        gate = random.choice(list(gates.items()))[0]
    return gate


def load_map():
    global map
    f = open(MAP_PATH, "r")
    m = []
    for x, line in enumerate(f.readlines()):
        ml = []
        s = line.split(',')
        for y, tile in enumerate(s):
            tt = TileType(int(tile[0]))
            t = Tile(x, y, tt)
            try:
                info = tile.split('-')[1]
                t.set_info(info)
                if tt == TileType.GATE:
                    gates[info] = (t.x, t.y)
                elif tt == TileType.RUNWAY and info not in runways:
                    runways[info] = int(info[:2]) * 10  
            except:
                pass
            ml.append(t)
        m.append(ml)
    f.close()
    map = m


def get_facing_direction_from_gate(mx, my):
    if map[mx][my-1].type == TileType.TAXIWAY:
        return Direction.NORTH
    elif map[mx][my+1].type == TileType.TAXIWAY:
        return Direction.SOUTH
    elif map[mx+1][my].type == TileType.TAXIWAY:
        return Direction.EAST
    elif map[mx-1][my].type == TileType.TAXIWAY:
        return Direction.WEST
    return None
    

# for debugging 
def temp_add_fill(pos):
    global map
    map[pos[0]][pos[1]].fill = 0


def get_adjacent_runway_pos(x, y):
    if map[x][y-1].type == TileType.RUNWAY:
        return (x, y-1)
    elif map[x][y+1].type == TileType.RUNWAY:
        return (x, y+1)
    elif map[x+1][y].type == TileType.RUNWAY:
        return (x+1, y)
    elif map[x-1][y].type == TileType.RUNWAY:
        return (x-1, y)
    return None


def get_runway_paths(x, y):
    global map
    arp = get_adjacent_runway_pos(x, y)
    path1 = []
    path2 = []

    mx = x
    my = y
    dx = arp[0] - x 
    dy = arp[1] - y 
    node = map[x][y]

    while node.type == TileType.RUNWAY: 
        path1.append(node.get_pos())
        mx += dx
        my += dy
        node = map[mx][my]

    mx = x
    my = y
    dx *= -1
    dy *= -1
    node = map[x][y]

    while node.type == TileType.RUNWAY: 
        path2.append(node.get_pos())
        mx += dx
        my += dy
        node = map[mx][my]

    return (path1, path2) 


def find_taxiway_path(plane, queue):
    plane_ticks_per_tile = plane.aircraft_info["ticks_per_tile"]
    min_runway_required = plane.aircraft_info["required_runway_space"]
    routes = get_all_routes_no_wind(plane.get_pos(), min_runway_required)
    crosswinds = get_crosswinds(plane_ticks_per_tile, routes)
    grades = grade_routes(plane, routes, crosswinds, queue) 
    lowest_grade = min(grades)
    return routes[grades.index(lowest_grade)] 


def get_crosswinds(ticks_per_tile, routes):
    global winds
    crosswinds = []

    for route in routes:
        wind_index = 0
        avg_crosswind_arr = [] 
        runway_angle = get_runway_angle_from_route(route)
        for node in route:
            if get_node_type(node) is not TileType.RUNWAY: 
                wind_index += ticks_per_tile
                continue
            
            wind = winds[wind_index] 
            wind_dir = wind[0]
            wind_speed = wind[1]
            cw = wind_speed / (math.cos(abs(180 - abs(runway_angle - wind_dir))))
            avg_crosswind_arr.append(cw)
        
        avg_crosswind = sum(avg_crosswind_arr) / len(avg_crosswind_arr)
        crosswinds.append(avg_crosswind)

    return crosswinds 


def get_all_routes_no_wind(pos, min_runway_required):
    routes = []
    paths = get_all_runway_paths(pos[0], pos[1])
    for path in paths:
        runway_node = path[-1] 
        runway_paths = get_runway_paths(runway_node[0], runway_node[1])
        if len(runway_paths[0]) > min_runway_required:
            routes.append(path + runway_paths[0][:min_runway_required])
        if len(runway_paths[1]) > min_runway_required:
            routes.append(path + runway_paths[1][:min_runway_required])
    return routes[:-min_runway_required]


def get_all_runway_paths(mx, my):
    paths = []
    map = get_map()
    queue = [(mx, my)]
    visited = [(mx, my)]
    parent_map = {}

    while queue:
        current_node = queue.pop(0) 
        runway_flag = False 

        if map[current_node[0]][current_node[1]].type == TileType.RUNWAY: 
            runway_flag = True
            path = []
            temp_node = current_node
            while temp_node != (mx, my):
                path.append(temp_node)
                temp_node = parent_map[temp_node]
            path.reverse()
            paths.append(path)

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            next_node = (current_node[0] + dx, current_node[1] + dy)
            next_node_runway_flag = map[next_node[0]][next_node[1]].type == TileType.RUNWAY
            if next_node_runway_flag and runway_flag: 
                continue
            node = map[next_node[0]][next_node[1]]
            type_val = node.type.value

            if next_node not in visited and type_val % 3 != 0: # avoid nothing (0) and gate (3) tile types 
                visited.append(next_node)
                queue.append(next_node)
                parent_map[next_node] = current_node

    return paths 


def debug_get_paths():
    global debug_paths
    return debug_paths


def get_node_type(pos):
    global map
    return map[pos[0]][pos[1]].type


def get_runway_angle_from_route(route):
    for node in route: 
        if get_node_type(node) is TileType.RUNWAY:
            return int(map[node[0]][node[1]].info[:2]) * 10 
    return None


def get_other_routes(current_plane, queue):
    return [plane.current_path for plane in queue if current_plane != plane]


def grade_routes(plane, routes, crosswinds, queue):
    # lowest grade is best route
    grades = []

    # filter routes that have too much crosswind for plane  
    max_crosswind_limit = plane.aircraft_info["crosswind_limit"]
    for i in range(len(routes)-1, -1, -1):
        if crosswinds[i] > max_crosswind_limit:
            routes.pop(i)
            crosswinds.pop(i)

    # grade crosswinds (0 for least, len for max) 
    sorted_winds = sorted(crosswinds) 
    grades = [sorted_winds.index(cw) for cw in crosswinds]

    # intersections  
    intersections = [get_intersections(route, queue, plane) for route in routes]
    grades = [ grades[i] + intersections[i] for i in range(len(grades)) ]

    # distance (div by 3 for less of a penalty) 
    grades = [ grades[i] + (len(route) / 3) for i, route in enumerate(routes)]

    return grades 


def get_intersections(route, queue, plane):
    # TODO: cover your eyes
    plane_speed = plane.aircraft_info["ticks_per_tile"] 
    route_with_times = [(node, i * plane_speed) for i, node in enumerate(route)]
    other_routes_with_speed = [(p.aircraft_info["ticks_per_tile"], p.current_path) for p in queue if plane != p]
    intersections_count = 0 
    runway_lineup_node = get_runway_lineup_node(route) 

    for node_and_time in route_with_times:
        intersection_count = 0
        node = node_and_time[0] 
        time = node_and_time[1]

        for other_route_and_speed in other_routes_with_speed: 
            other_plane_landing = other_route[-1] is TileType.GATE
            other_runway_lineup_node = get_runway_lineup_node(other_route) 

            if other_plane_landing is False and runway_lineup_node == other_runway_lineup_node:
                return -1 # taxiing to same location  

            other_speed = other_route_and_speed[0] 
            other_route = other_route_and_speed[1]

            for i, other_node in enumerate(other_route):
                if node == other_node and time == other_speed * i:
                    intersection_count += 1 + other_plane_landing # penalize if intersecting with landing path 

    return intersection_count


def get_runway_lineup_node(route):
    for node in route:
        if get_node_type(node) is TileType.RUNWAY:
            return node
    return None

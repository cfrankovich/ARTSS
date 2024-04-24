from enum import Enum
import random
import numpy as np
import math 
from collections import Counter 

MAP_PATH = "map.csv"
MAX_WIND_SPEED = 25
MIN_WIND_SPEED = 5
OFF_MAP_DISTANCE = 50 
DAB_RUNWAY_INFO = [ 
    # (xpos, ypos, length, angle) #
    (4, 21, 46, 70),   # 07L/25R -> 07 east
    (50, 21, 46, 250), # 07L/25R -> 25 west 
    (32, 28, 15, 70),  # 07R/25L -> 07 east
    (47, 28, 15, 250), # 07R/25L -> 25 west
    (43, 7, 25, 160),  # 16/34   -> 16 south
    (43, 32, 25, 340), # 16/34   -> 34 north
]
RUNWAY_NAMES = [ "07L", "25R", "07R", "25L", "16", "34" ]

# arguments to pass to the path gen + rwa
LOOP_LENGTH      = 50
LOOP_WIDTH       = 40
DIAG_SIDE_LENGTH = 10 
ENTRY_SPACE      = 10
HOLD_POINTS_INFO = {
    "Alpha" : (43, 7, 2, 2, 160), 
    "Bravo" : (43, 7, 2, 1, 160), 
    "Charlie" : (50, 21, 1, 1, 250), 
    "Delta" : (50, 21, 1, 2, 250), 
    "Echo" : (47, 28, 1, 2, 250), 
    "Foxtrot" : (43, 32, 0, 2, 340), 
    "Golf" : (43, 32, 0, 1, 340), 
    "Hotel" : (32, 28, 3, 1, 70), 
    "India" : (4, 21, 3, 2, 70), 
    "Juliett" : (4, 21, 3, 1, 70)
}

gates = {} 
map = [] 
runways = {}
debug_paths = []
winds = []
#wind_direction = random.randrange(0, 360) # deg 
#wind_speed = random.randrange(MIN_WIND_SPEED, MAX_WIND_SPEED + 1) # knots 
wind_direction = 70 
wind_speed = 14 
winds.append((wind_direction, wind_speed))
debug_stuff_delete_me = []


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

    dir = int(np.random.normal(winds[-1][0], 5)) % 360 
    speed = int(np.random.normal(winds[-1][1], 2))
    speed = max(MIN_WIND_SPEED, min(MAX_WIND_SPEED, speed))
    winds.append((dir, speed))


def debug_init_winds(samples):
    global winds
    global wind_direction
    global wind_speed
    #winds = [(70, 12) for i in range(15)]
    #winds.extend([(340, 12) for i in range(samples)])
    winds = [(wind_direction, wind_speed) for i in range(samples)]


def init_winds(samples):
    global winds
    for i in range(1, samples):
        dir = int(np.random.normal(winds[i-1][0], 7)) % 360 
        speed = int(np.random.normal(winds[i-1][1], 3))
        speed = max(MIN_WIND_SPEED, min(MAX_WIND_SPEED, speed))
        winds.append((dir, speed))


def get_node_type_from_pos(pos):
    return map[pos[0]][pos[1]].type 


def get_map():
    global map
    return map


def get_cruising_pos(d):
    MAX_X = 65 
    MAX_Y = 45
    random_pos = random.randint(5, MAX_X) 
    if d == Direction.NORTH:
        return (Direction.SOUTH, random_pos, OFF_MAP_DISTANCE * -1)
    if d == Direction.WEST:
        return (Direction.EAST, OFF_MAP_DISTANCE * -1, random_pos % MAX_Y)
    if d == Direction.SOUTH:
        return (Direction.NORTH, random_pos, OFF_MAP_DISTANCE + MAX_Y)
    if d == Direction.EAST:
        return (Direction.WEST, OFF_MAP_DISTANCE + MAX_X, random_pos % MAX_Y)


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
    while gate in gates_in_use or gate[0] == char_to_check:
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
    node = map[x + dx][y + dy]

    while node.type == TileType.RUNWAY: 
        path1.append(node.get_pos())
        mx += dx
        my += dy
        node = map[mx][my]

    mx = x
    my = y
    dx *= -1
    dy *= -1
    node = map[x + dx][y + dy]

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
    crosswinds, headwinds, temp_rwa = get_winds(plane_ticks_per_tile, routes, queue)
    routes, grades = grade_routes(plane, routes, crosswinds, headwinds, queue, temp_rwa) 
    lowest_grade = min(grades) 
    plane.debug_set_grades(grades)
    #return routes
    return routes[grades.index(lowest_grade)]
    plane.debug_set_best_grade_path(routes[grades.index(lowest_grade)])


def calculate_crosswind(runway_angle_deg, wind_angle_deg, wind_speed):
    wind_direction_rad = math.radians(wind_angle_deg)
    runway_direction_rad = math.radians(runway_angle_deg)

    angle_diff_rad = wind_direction_rad - runway_direction_rad
    angle_diff_rad = (angle_diff_rad + math.pi) % (2 * math.pi) - math.pi
    
    return abs(wind_speed * math.sin(angle_diff_rad))


def calculate_headwind(runway_angle_deg, wind_angle_deg, wind_speed):
    wind_direction_rad = math.radians(wind_angle_deg)
    runway_direction_rad = math.radians(runway_angle_deg)

    angle_diff_rad = wind_direction_rad - runway_direction_rad
    angle_diff_rad = (angle_diff_rad + math.pi) % (2 * math.pi) - math.pi
    
    return wind_speed * math.cos(angle_diff_rad)


def get_winds(ticks_per_tile, routes, queue):
    global winds
    crosswinds = []
    headwinds = []
    temp_rwa = []

    for route in routes:
        wind_index = 0
        avg_crosswind_arr = [] 
        avg_headwind_arr = [] 
        runway_angle = get_runway_angle_from_route(route)
        temp_rwa.append(runway_angle)
        for i in range(len(route)):
            if is_runway_being_used_at_time(wind_index, queue):
                wind_index += 1
                i -= 1
                continue

            node = route[i] 
            wind_index += ticks_per_tile
            if get_node_type(node) is not TileType.RUNWAY: 
                continue
            
            wind = winds[wind_index] 
            wind_dir = wind[0]
            wind_speed = wind[1]
            cw = calculate_crosswind(runway_angle, wind_dir, wind_speed) 
            hw = calculate_headwind(runway_angle, wind_dir, wind_speed) 
            avg_crosswind_arr.append(cw)
            avg_headwind_arr.append(hw)
        
        avg_crosswind = sum(avg_crosswind_arr) // (len(avg_crosswind_arr) + 1)
        avg_headwind = sum(avg_headwind_arr) // (len(avg_headwind_arr) + 1)
        crosswinds.append(avg_crosswind)
        headwinds.append(avg_headwind)

    return crosswinds, headwinds, temp_rwa 


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
    return routes


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
    try:
        return map[pos[0]][pos[1]].type
    except:
        return TileType.NOTHING


def get_runway_angle_from_route(route):
    runway_nodes = [node for node in route if get_node_type(node) is TileType.RUNWAY]
    if len(runway_nodes) < 2:
        return None

    x1 = runway_nodes[-4][0] 
    y1 = runway_nodes[-4][1] 
    x2 = runway_nodes[-2][0]
    y2 = runway_nodes[-2][1]
    dx = x2 - x1
    dy = y2 - y1

    info = map[runway_nodes[-4][0]][runway_nodes[-4][1]].info
    first = int(info[:2]) * 10
    second = int(info.split('/')[1][:2]) * 10

    # N = 0, E = 90, S = 180, W = 270
    if dx < 0 and dy == 0:
        perfect_dir = 270 
    elif dx > 0 and dy == 0:
        perfect_dir = 90 
    elif dx == 0 and dy > 0:
        perfect_dir = 180
    else:
        perfect_dir = 360 

    if abs(perfect_dir - first) < abs(perfect_dir - second):
        return first 
    return second


def get_other_routes(current_plane, queue):
    return [plane.current_path for plane in queue if current_plane != plane]


def grade_routes(plane, routes, crosswinds, headwinds, queue, temp_angles):
    # lowest grade is best route
    grades = []

    # filter routes that have too much crosswind for plane  
    max_crosswind_limit = plane.aircraft_info["crosswind_limit"]
    for i in range(len(routes)-1, -1, -1):
        if crosswinds[i] > max_crosswind_limit:
            routes.pop(i)
            crosswinds.pop(i)
            headwinds.pop(i)

    # grade crosswinds (0 for least, len for max) 
    grades = [cw for cw in crosswinds]

    # grade headwinds 
    grades = [(grades[i] + (hw * 2)) for hw in headwinds]

    # intersections  
    intersections = [get_intersections(route, queue, plane) for route in routes]
    grades = [ grades[i] + intersections[i] * 20 for i in range(len(grades)) ]

    # distance (div for less of a penalty) 
    lengths = [len(route) for route in routes] 
    grades = [ grades[i] + lengths[i] for i in range(len(lengths))]

    #pretty_print_data(routes, crosswinds, headwinds, intersections, lengths, grades, temp_angles)

    return routes, grades 


def get_intersections(route, queue, plane):
    # TODO: cover your eyes
    plane_speed = plane.aircraft_info["ticks_per_tile"] 
    route_with_times = [(node, i * plane_speed) for i, node in enumerate(route)]
    other_routes_with_speed = [(p.aircraft_info["ticks_per_tile"], p.current_path) for p in queue if plane != p]
    intersection_count = 0 
    runway_lineup_node = get_runway_lineup_node(route) 

    for node_and_time in route_with_times:
        intersection_count = 0
        node = node_and_time[0] 
        time = node_and_time[1]

        for other_route_and_speed in other_routes_with_speed: 
            other_route = other_route_and_speed[1]
            if other_route == []:
                return 0 
            other_speed = other_route_and_speed[0] 
            other_plane_landing = other_route[-1] is TileType.GATE
            other_runway_lineup_node = get_runway_lineup_node(other_route) 

            if other_plane_landing is False and runway_lineup_node == other_runway_lineup_node:
                return -1 # taxiing to same location  

            for i, other_node in enumerate(other_route):
                if node == other_node and time == other_speed * i:
                    intersection_count += 3 + other_plane_landing # penalize if intersecting with landing path 

    return intersection_count


def get_runway_lineup_node(route):
    for node in route:
        if get_node_type(node) is TileType.RUNWAY:
            return node
    return None

def pretty_print_data(routes, cw, hw, inter, lengths, grades, temp_angles):
    for i in range(len(routes)):
        print(f"ROUTE #{i} :: ANG = {temp_angles[i]} :: CW = {cw[i]} :: HW = {hw[i]} :: INT = {inter[i]} :: LEN = {lengths[i]} :: G = {grades[i]}")

def is_runway_being_used_at_time(tick_num, queue):
    for plane in queue:
        ticks_per_tile = plane.aircraft_info["ticks_per_tile"]
        num_ticks = 0
        for node in plane.current_path:
            if get_node_type(node) == TileType.RUNWAY:
                if num_ticks >= tick_num:
                    return True
                num_ticks += 1
            else:
                num_ticks += ticks_per_tile
    return False


def bresenhams_line_algorithm(a, b, x, y):
    points = []
    dx = abs(x - a)
    dy = abs(y - b)
    sx = 1 if a < x else -1
    sy = 1 if b < y else -1
    err = dx - dy

    while True:
        points.append((a, b))
        if a == x and b == y:
            break
        e2 = 2 * err
        if e2 >= -dy:
            err -= dy
            a += sx
        if e2 <= dx:
            err += dx
            b += sy

    return points


def generate_cruising_path(runway_required, pos):
    # filter runways based on length
    runway_info_copy = DAB_RUNWAY_INFO.copy()
    for i in range(len(runway_info_copy) - 1, 0, -1):
        rwi = runway_info_copy[i]
        if rwi[2] < runway_required:
            runway_info_copy.pop(i)

    # now get closest one
    closest_runway_pos = None 
    score = 999999999999 
    for rwi in runway_info_copy:
        temp_score = math.sqrt(((pos[1] - rwi[0]) ** 2) + ((pos[2] - rwi[1]) ** 2)) 
        if temp_score < score:
            score = temp_score 
            closest_runway_pos = rwi 

    #print(pos[1], pos[2], closest_runway_pos[0], closest_runway_pos[1])

    # now generate closest path to it
    #return bresenhams_line_algorithm(pos[1], pos[2], closest_runway_pos[0], closest_runway_pos[1])
    return []


def is_plane_clear_to_land(plane, clock, queue):
    """
        1. check the wind conditions if the plane is on course to the runway at that time
            1a. keep in mind the direction the plane is coming from tell plane to hold at place with best wind 
            1b. keep in mind the tick...
        2. check the traffic congestion if the plane is to land asap
            2a. when the plane lands can they exit the runway immediately
        3. if these are both bad tell the plane to hold at a position and theyll fly around that path 
    """
    flight_ticks = plane.aircraft_info["flight_ticks_per_tile"]
    min_runway_req = plane.aircraft_info["required_runway_space"] + 3 # +3 since coming in fast
    crosswind_limit = plane.aircraft_info["crosswind_limit"]
    pos = plane.get_map_pos()
    clock_ticks = clock.ticks

    cw_and_hws = get_best_cws_and_hws(min_runway_req, crosswind_limit, pos, clock_ticks, flight_ticks)
    grades = [ abs(cwhw[0]) + cwhw[1] for cwhw in cw_and_hws ] 
    lowest_wind_grade = min(grades)    
    if lowest_wind_grade >= 199998: 
        hold_point = get_hold_point(plane) 
        return False, ("high crosswinds", hold_point)
    runway_best_wind = DAB_RUNWAY_INFO[grades.index(lowest_wind_grade)]

    debug_stuff_delete_me.append((runway_best_wind[0], runway_best_wind[1]))
    debug_stuff_delete_me.append(gates[plane.flight_data["gate"]])

    try:
        path = calculate_traffic_for_runway(runway_best_wind, plane, queue)
        plane.current_path = path 
    except:
        hold_point = get_hold_point(plane) 
        return False, ("traffic congestion", hold_point)

    fix_point = get_hold_point(plane) 
    return True, (fix_point, RUNWAY_NAMES[grades.index(lowest_wind_grade)]) 


def calculate_traffic_for_runway(runway_info, plane, plane_queue): 
    # return -1 if too congested (not a path to the gate) 
    # -2 if not available (plane is using it right now) 
    for plane in plane_queue:
        status_value = abs(plane.get_status().value)
        if status_value >= 9 and status_value <= 11: # flight status of taking off to climbing 
            route = plane.runway_path
            facing = plane.facing

            x_or_y_idx = 0 
            if facing.value % 180 != 0: # towards east or west 
                x_or_y_idx = 1 

            if runway_info[x_or_y_idx] == route[len(route) - 1][x_or_y_idx]:
                raise Exception

    path_to_gate = get_path_to_gate(runway_info, plane, plane_queue)

    if path_to_gate == []:
        raise Exception 

    plane.set_debug_paths([path_to_gate])

    return path_to_gate 


def delete_this_function():
    global debug_stuff_delete_me
    return debug_stuff_delete_me


def get_path_to_gate(runway_info, plane, plane_queue):
    gate_loc = gates[plane.flight_data["gate"]] 
    min_runway_req = plane.aircraft_info["required_runway_space"]
    runway_angle = runway_info[3]

    mx = runway_info[0] 
    my = runway_info[1]
    if runway_angle == 70:
        mx += min_runway_req 
    elif runway_angle == 250:
        mx -= min_runway_req
    elif runway_angle == 160:
        my += min_runway_req
    else:
        my -= min_runway_req

    debug_stuff_delete_me.append((mx, my))

    map = get_map()
    queue = [(mx, my)]
    visited = [(mx, my)]
    parent_map = {}
    other = get_other_taxi_paths(plane, plane_queue)
    other_taxi_paths = [node for path in other for node in path]

    while queue:
        current_node = queue.pop(0) 
        runway_flag = False 

        if current_node[0] == gate_loc[0] and current_node[1] == gate_loc[1]: 
            path = []
            temp_node = current_node
            while temp_node != (mx, my):
                path.append(temp_node)
                temp_node = parent_map[temp_node]
            path.reverse()
            return path

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            next_node = (current_node[0] + dx, current_node[1] + dy)
            next_node_gate_flag= map[next_node[0]][next_node[1]].type == TileType.GATE
            next_node_runway_flag= map[next_node[0]][next_node[1]].type == TileType.RUNWAY

            if next_node_runway_flag and \
                map[current_node[0]][current_node[1]].type == TileType.RUNWAY and \
                ((runway_angle == 70 and next_node[0] <= mx) or \
                    (runway_angle == 250 and next_node[0] >= mx) or \
                    (runway_angle == 160 and next_node[1] <= my) or \
                    (runway_angle == 350 and next_node[1] >= my)):
                continue

            if next_node_gate_flag and \
                (next_node[0] != gate_loc[0] or next_node[1] != gate_loc[1]): 
                continue

            if next_node in other_taxi_paths:
                continue

            node = map[next_node[0]][next_node[1]]
            type_val = node.type.value

            if next_node not in visited and type_val != 0: # avoid nothing (0) tile types 
                visited.append(next_node)
                queue.append(next_node)
                parent_map[next_node] = current_node

    return []  


def get_other_taxi_paths(filter_plane, queue):
    paths = []
    for plane in queue:
        if filter_plane is plane: 
            continue
        if plane.get_status().value != 5 and plane.get_status().value != -6 and plane.get_status().value != 0: 
            continue
        paths.append(plane.get_current_path())

    return paths


def get_hold_point(plane):
    TOTAL_LOOP_DIST = 294 
    distances = [TOTAL_LOOP_DIST for _ in range(len(HOLD_POINTS_INFO))]        
    min_runway_req = plane.aircraft_info["required_runway_space"] + 3 # +3 since coming in fast 
    crosswind_limit = plane.aircraft_info["crosswind_limit"]
    wind_grades = []
    names = []

    pos = plane.get_pos()
    for i, hp_name in enumerate(HOLD_POINTS_INFO):
        names.append(hp_name)
        info = HOLD_POINTS_INFO[hp_name]
        start = get_holdpoint_paths(info[0], info[1], info[2], info[3], just_start=True)
        distances[i] += int( math.sqrt(((start[0] - pos[0]) ** 2) + ((start[1] - pos[1]) ** 2)) ) 

        offset = distances[i]
        cws = []
        hws = []
        runway_angle = info[4]
        for j in range(min_runway_req):
            wind = winds[offset + j]
            cws.append(calculate_crosswind(runway_angle, wind[0], wind[1]))
            hws.append(calculate_headwind(runway_angle, wind[0], wind[1]))

        cw_avg = sum(cws) // (len(cws) + 1)
        if cw_avg >= crosswind_limit:
            wind_grades.append(99999)

        hw_avg = sum(hws) // (len(hws) + 1)
        wind_grades.append( abs(cw_avg) + hw_avg )

    lowest_wind_grade = min(wind_grades)    
    best_wind_index = wind_grades.index(lowest_wind_grade)

    return names[best_wind_index]

### 
    # end runway path -> (a, b) 
    # facing dir ->
    # N - 0 :: y :: ns = 1 
    # E - 3 :: x :: ew = 1
    # S - 2 :: y :: ns = -1
    # W - 1 :: x :: ew = -1
    # path variant -> path_num (1 for first path)
    # first paths: 
    # north - left 
    # south - right  
    # east - bottom 
    # west - top 
def get_holdpoint_paths(a, b, facing_dir, path_num, just_start=False): 
    ns = facing_dir % 2 == 0 
    ew = not ns 
    ns *= 1 if facing_dir % 3 == 0 else -1 
    ew *= -1 if facing_dir % 3 == 0 else 1 

    bx = a + ((LOOP_LENGTH + ENTRY_SPACE + DIAG_SIDE_LENGTH) * ew) 
    by = b + ((LOOP_LENGTH + ENTRY_SPACE + DIAG_SIDE_LENGTH) * ns) 

    path_1 = []
    x1 = bx - ((LOOP_WIDTH + DIAG_SIDE_LENGTH) * ns)
    y1 = by - ((LOOP_WIDTH + DIAG_SIDE_LENGTH) * ew)

    if just_start:
        if path_num == 1:
            return (x1, y1)
        else:
            if ew == 0:
                return ((2 * bx) - x1, y1)
            else:
                return(x1, (2 * by) - y1)

    for _ in range(LOOP_LENGTH + ENTRY_SPACE):
        path_1.append((x1, y1))
        x1 -= 1 * ew 
        y1 -= 1 * ns 

    for _ in range(LOOP_WIDTH):
        path_1.append((x1, y1))
        x1 += 1 * ns 
        y1 += 1 * ew 

    for _ in range(LOOP_LENGTH):
        path_1.append((x1, y1))
        x1 += 1 * ew
        y1 += 1 * ns 

    for _ in range(LOOP_WIDTH):
        path_1.append((x1, y1))
        x1 -= 1 * ns 
        y1 -= 1 * ew 

    for _ in range(LOOP_LENGTH):
        path_1.append((x1, y1))
        x1 -= 1 * ew 
        y1 -= 1 * ns 

    for _ in range(LOOP_WIDTH):
        path_1.append((x1, y1))
        x1 += 1 * ns 
        y1 += 1 * ew 
    
    for _ in range(ENTRY_SPACE):
        path_1.append((x1, y1))
        if ew == 0:
            x1 += 1 * ns
            y1 -= 1 * ns
        else:
            x1 -= 1 * ew
            y1 += 1 * ew

    if path_num == 1:
        return path_1

    if ew == 0:
        path_2 = [((2 * bx) - node[0], node[1]) for node in path_1]
    else:
        path_2 = [(node[0], (2 * by) - node[1]) for node in path_1]

    return path_2


def get_best_cws_and_hws(min_runway_req, crosswind_limit, pos, clock_ticks, flight_ticks): 
    cw_and_hws = []
    for runway in DAB_RUNWAY_INFO:
        if runway[2] < min_runway_req:
            cw_and_hws.append((99999, 99999))
            continue

        path = bresenhams_line_algorithm(pos[0], pos[1], runway[0], runway[1])
        ticks_until_runway = flight_ticks * len(path) 
        at_runway_tick_num = clock_ticks + ticks_until_runway # TODO: THIS IS WRONG IF ADJUST WIND BEING CALLED
        cws = []
        hws = []
        runway_angle = runway[3] 

        for i in range(min_runway_req):
            wind = winds[at_runway_tick_num + i] 
            cws.append(calculate_crosswind(runway_angle, wind[0], wind[1]))
            hws.append(calculate_headwind(runway_angle, wind[0], wind[1]))

        cw_avg = sum(cws) // (len(cws) + 1)
        if cw_avg >= crosswind_limit:
            cw_and_hws.append((99999, 99999))
            continue

        hw_avg = sum(hws) // (len(hws) + 1)
        cw_and_hws.append((cw_avg, hw_avg))

    return cw_and_hws

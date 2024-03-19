from enum import Enum
import random

MAP_PATH = "map.csv"
gates = {} 
map = [] 
runways = {}


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


# return the longest runway path go out both sides
# probably not the most efficient but it werks!!!!!!!!!!!!!!!!
def get_runway_path(x, y):
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

    return path1 if len(path1) > len(path2) else path2


def find_taxiway_path(plane, queue, winds):
    # TODO:
    # get the average wind speed during the predicted time range from takeoff to departed 
    # use this wind speed, max crosswind limit, required runway space, and distance to suggest a runway  
    # determine the shortest path to this runway while evaluating different entrance possibilities
    # evaluate the path comparing each step or node to other routes during the time

    # INFO:
    # a route can be shared no need to try and go around a plane going the same place
    # the best route is one where it is not blocking the terminal entrance or gates if
    # theres potentially a long queue, shortest path to runway, not crossing runways, not
    # intersecting with other routes that have different destinations, etc. 

    # TODO: 
    # experiment by generating all possibilities and then draw the lines for the possibilities
    # "grade" the possibilities and color them accordingly and take a screenshot would be good
    # to have in presentation 

    pass

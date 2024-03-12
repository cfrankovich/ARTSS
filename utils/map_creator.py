import pygame
import sys
from enum import Enum

# TYPE-INFO
def save_map():
    f = open("map.csv", "w")
    for line in map:
        s = ''
        for tile in line:
            if tile.type != TileType.NOTHING:
                s += f"{tile.type.value}-{tile.info}," 
            else:
                s += "0,"
        f.write(s + "\n")
    f.close()


def load_map():
    f = open("map.csv", "r")
    m = []
    for x, line in enumerate(f.readlines()):
        ml = []
        s = line.split(',')
        for y, tile in enumerate(s):
            t = Tile(x, y, TileType(int(tile[0])))
            try:
                t.set_info(tile.split('-')[1])
            except:
                pass
            ml.append(t)
        m.append(ml)
    f.close()
    return m


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
        self.info = "INFO"

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

    def get_fill(self):
        if self.info == "INFO":
            return 1
        else:
            return 0


pygame.init()
size = (width, height) = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('map creator')

image = pygame.image.load('graphics/DAB.png')
resized_image = pygame.transform.scale(image, (1280, 720))
rotated_image = pygame.transform.rotate(resized_image, -25)

grid_color = (0, 0, 0)  
GRID_SPACE_SIZE = 20
tool = TileType.NOTHING
map = load_map() 
num = 1
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos
            x, y = event.pos
            mx, my = (x // GRID_SPACE_SIZE, y // GRID_SPACE_SIZE)
            if tool == -1:
                map[mx][my].set_info(f"B{num}")
                num += 1
            else:
                map[mx][my].toggle(tool)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_0:
                tool = TileType.NOTHING
            elif event.key == pygame.K_1:
                tool = TileType.RUNWAY
            elif event.key == pygame.K_2:
                tool = TileType.TAXIWAY
            elif event.key == pygame.K_3:
                tool = TileType.GATE
            elif event.key == pygame.K_e:
                tool = -1 
            elif event.key == pygame.K_RETURN:
                save_map()
                print('saved!')

    screen.fill((0, 0, 0))

    #image_rect = rotated_image.get_rect(center=(width / 2, height / 2))
    #screen.blit(rotated_image, image_rect.topleft)

    for i, x in enumerate(map):
        for j, y in enumerate(x):
            pygame.draw.rect(screen, y.color, (i*GRID_SPACE_SIZE, j*GRID_SPACE_SIZE, 
                                               GRID_SPACE_SIZE, GRID_SPACE_SIZE), y.get_fill()) 

    pygame.display.flip()


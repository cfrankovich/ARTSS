import pygame
import ast
from utils.states import State, Event 
from utils.map_handler import TileType, get_map, get_node_type, get_wind_info, MIN_WIND_SPEED, MAX_WIND_SPEED
from .plane_agent import DEPARTED_ALTITUDE, plane_queue
import math
import numpy as np 
import matplotlib as plt
from utils.logger import ARTSSClock

FPS = 2 
WIDTH = 1280
HEIGHT = 720
GRID_SPACE_SIZE = 20
MAX_PLANE_SCALE = 4
#WIND_ARROW_COLOR = (255, 0, 85)
WIND_ARROW_COLOR = (255, 255, 255)
#COMPASS_BG_COLOR = (77, 77, 97)
COMPASS_BG_COLOR = (27, 27, 37)
#LOWER_COMPASS_BG_COLOR = (95, 95, 117)
LOWER_COMPASS_BG_COLOR = (0, 0, 0)
COMPASS_DIR_COLOR = (190, 180, 180)


def get_line_type(start, end):
    dx1 = start[0] - end[0]
    dx2 = end[0] - start[0]
    dy1 = start[1] - end[1]
    dy2 = end[1] - start[1]
    # lol
    if dx1 == 0: 
        return 1
    if dy1 == 0:
        return 2
    if dx1 < 1 and dy1 > 1 and dx2 > 1 and dy2 < 1:
        return 3
    if dx1 > 1 and dy1 > 1 and dx2 < 1 and dy2 < 1:
        return 4
    if dx1 > 1 and dy1 > 1 and dx2 < 1 and dy2 < 1:
        return 5
    if dx1 > 1 and dy1 < 1 and dx2 < 1 and dy2 > 1:
        return 6


def draw_dashed_line(surface, color, start_pos, end_pos, width):
    DASH_LENGTH = 10 
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    dash_count = int(distance / DASH_LENGTH)

    for i in range(dash_count):
        start = x1 + (dx * i / dash_count), y1 + (dy * i / dash_count)
        end = x1 + (dx * (i + 0.5) / dash_count), y1 + (dy * (i + 0.5) / dash_count)
        pygame.draw.line(surface, color, start, end, width)


def colorize_image(image, new_color):
    colored_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    colored_image.fill((0, 0, 0, 0)) 

    for x in range(image.get_width()):
        for y in range(image.get_height()):
            pixel = image.get_at((x, y))
            if pixel[3] > 0:
                colored_image.set_at((x, y), new_color + (pixel[3],))

    return colored_image


def get_rainbow_color(amt, idx):
    rainbow_colors_red_to_violet = plt.cm.rainbow(np.linspace(1, 0, amt))
    rainbow_colors_red_to_violet_255 = [(int(color[0]*255), int(color[1]*255), int(color[2]*255)) for color in rainbow_colors_red_to_violet]
    return rainbow_colors_red_to_violet_255[idx]


def to_screen_xy(node):
    return (node[0] * GRID_SPACE_SIZE, node[1] * GRID_SPACE_SIZE) 


def get_midpoint(a, b):
    return ( ((a[0] + b[0]) // 2), ((a[1] + b[1]) // 2) )


def draw_text_with_outline(surface, text, font, pos, text_color, outline_color, outline_width, center):
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()

    if center:
        x, y = pos
        pos = (x - text_rect.width // 2, y - text_rect.height // 2)
    else:
        x, y = pos

    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1)]:
        outline_surface = font.render(text, True, outline_color)
        surface.blit(outline_surface, (x + dx * outline_width - (text_rect.width // 2 if center else 0), \
                                       y + dy * outline_width - (text_rect.height // 2 if center else 0)))

    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, pos)


class Simulation():
    def __init__(self, ui):
        self.ui = ui
        airport_image = pygame.image.load("graphics/sim_bg_demo_no_labels.png")
        self.airport_background = pygame.transform.scale(airport_image, (WIDTH, HEIGHT))

        # grid for testing purposes
        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, x in enumerate(get_map()):
            for j, y in enumerate(x):
                if y.type == TileType.NOTHING: 
                    continue 
                pygame.draw.rect(grid_surface, y.color, (i*GRID_SPACE_SIZE, j*GRID_SPACE_SIZE, 
                                                GRID_SPACE_SIZE, GRID_SPACE_SIZE), 1)
        self.rot_grid_surface = pygame.transform.rotate(grid_surface, 25)

        large_plane_img = pygame.image.load("graphics/large_plane.png")
        default_plane_img = pygame.image.load("graphics/default_plane.png")
        small_plane_img = pygame.image.load("graphics/small_plane.png")
        self.plane_imgs = [large_plane_img, default_plane_img, small_plane_img]

        self.plane_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        self.wind_arrow = pygame.image.load("graphics/wind_arrow_white.png")
        self.font = pygame.font.Font(None, 34)
        self.smaller_font = pygame.font.Font(None, 30)

        self.debug_flag = False
        self.debug_path_num = -1

    def render(self):
        screen = self.ui.screen
        screen.fill((0, 0, 0))

        airport_background_rect = self.airport_background.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(self.airport_background, airport_background_rect.topleft)

        #screen.blit(self.rot_grid_surface, (WIDTH/2 - self.rot_grid_surface.get_width() / 2, HEIGHT / 2 - self.rot_grid_surface.get_height() / 2))

        self.plane_surface.fill((0, 0, 0, 0))
        for n, plane in enumerate(plane_queue):
            #color = get_rainbow_color(n) 
            plane_img = self.plane_imgs[plane.get_aircraft_type().value - 1] 
            plane_img = colorize_image(plane_img, WIND_ARROW_COLOR)
            facing_angle = plane.get_facing_direction().value
            mx, my = plane.get_map_pos()
            scale_factor = ((plane.altitude / DEPARTED_ALTITUDE) * (MAX_PLANE_SCALE - 1)) + 1 
            width = height = GRID_SPACE_SIZE * scale_factor
            offset = (width - GRID_SPACE_SIZE) // 2
            x, y = (mx * GRID_SPACE_SIZE - offset, my * GRID_SPACE_SIZE - offset) 
            plane_img_rot = pygame.transform.rotate(plane_img, facing_angle)
            plane_img_scaled = pygame.transform.scale(plane_img_rot, (width, height))
            self.plane_surface.blit(plane_img_scaled, (x, y))
            
        ps = pygame.transform.rotate(self.plane_surface, 25) 
        screen.blit(ps, (WIDTH/2 - ps.get_width() / 2, HEIGHT/2 - ps.get_height() / 2))

        CENTER_X = 550
        CENTER_Y = 200
        pygame.draw.rect(screen, (0, 0, 0), (CENTER_X-60, CENTER_Y, 120, 134), border_radius=10)
        pygame.draw.rect(screen, COMPASS_BG_COLOR, (CENTER_X-56, CENTER_Y, 112, 130), border_radius=8)
        pygame.draw.circle(screen, (0, 0, 0), (CENTER_X, CENTER_Y), 67) 
        pygame.draw.circle(screen, COMPASS_BG_COLOR, (CENTER_X, CENTER_Y), 63) 
        pygame.draw.circle(screen, (0, 0, 0), (CENTER_X, CENTER_Y), 38) 
        pygame.draw.circle(screen, LOWER_COMPASS_BG_COLOR, (CENTER_X, CENTER_Y), 34) 
        pygame.draw.circle(screen, (0, 0, 0), (CENTER_X, CENTER_Y), 10) 
        draw_text_with_outline(screen, "N", self.smaller_font, (CENTER_X-8, CENTER_Y-60), COMPASS_DIR_COLOR, (0, 0, 0), 2, False)
        draw_text_with_outline(screen, "S", self.smaller_font, (CENTER_X-6, CENTER_Y+42), COMPASS_DIR_COLOR, (0, 0, 0), 2, False)
        draw_text_with_outline(screen, "E", self.smaller_font, (CENTER_X+43, CENTER_Y-8), COMPASS_DIR_COLOR, (0, 0, 0), 2, False)
        draw_text_with_outline(screen, "W", self.smaller_font, (CENTER_X-60, CENTER_Y-8), COMPASS_DIR_COLOR, (0, 0, 0), 2, False)

        wind = get_wind_info()
        wind_arrow_size = self.wind_arrow.get_size()
        scale_factor = ((wind[1] - MIN_WIND_SPEED) / (MAX_WIND_SPEED - MIN_WIND_SPEED)) + 0.5
        width = wind_arrow_size[0] * scale_factor 
        height = wind_arrow_size[1] 
        wind_arrow_scaled = pygame.transform.scale(self.wind_arrow, (width, height)) 
        wind_arrow_rot = pygame.transform.rotate(wind_arrow_scaled, 180 - wind[0]) 
        rot_rect = wind_arrow_rot.get_rect()
        rot_rect.center = (CENTER_X, CENTER_Y)
        screen.blit(wind_arrow_rot, rot_rect.topleft)

        draw_text_with_outline(screen, f"{wind[1]} knots", self.font, (CENTER_X, CENTER_Y+82), WIND_ARROW_COLOR, (0, 0, 0), 2, True)

        the_time = str(ARTSSClock.ticks)
        draw_text_with_outline(screen, f"Tick #{the_time}", self.font, (CENTER_X, CENTER_Y+112), WIND_ARROW_COLOR, (0, 0, 0), 2, True)

        # draw paths 
        half_grid_space_size = GRID_SPACE_SIZE / 2
        path_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        line_width = 4
        for n, plane in enumerate(plane_queue):
            """
            if self.debug_flag:
                paths = [plane.debug_best_grade_path] 
            elif self.debug_path_num != -1:
                paths = [plane.get_debug_paths()[self.debug_path_num]]
            else:
                paths = plane.get_debug_paths()
            """
            paths = [plane.current_path]
            drawn = []
            for j, path in enumerate(paths):
                #color = get_rainbow_color(len(paths), j) 
                color = WIND_ARROW_COLOR 
                prev = plane.get_map_pos()
                for i, node in enumerate(path):
                    top_left = (node[0] * GRID_SPACE_SIZE, node[1] * GRID_SPACE_SIZE) 
                    center = (top_left[0] + half_grid_space_size, top_left[1] + half_grid_space_size) 

                    start = get_midpoint(to_screen_xy(prev), center) 
                    prev = node
                    try:
                        next = path[i + 1] 
                    except:
                        continue
                    end = get_midpoint(to_screen_xy(next), center)

                    new_start = start
                    new_end = end
                    """
                    line_info = (node, get_line_type(start, end))

                    if line_info in been_drawn:
                        dup_offset = line_width * been_drawn.count(line_info)
                        new_start = (start[0] + dup_offset, start[1] + dup_offset) 
                        new_end = (end[0] + dup_offset, end[1] + dup_offset) 

                    if get_node_type(node) == TileType.RUNWAY: 
                        if line_info not in temp_drawn and line_info not in been_drawn: 
                            draw_dashed_line(path_surface, color, new_start, new_end, line_width) 
                            temp_drawn.append(line_info)
                    else:
                        pygame.draw.line(path_surface, color, new_start, new_end, line_width)
                        temp_drawn.append(line_info)
                    """

                    line_info = f"{start}{end}"
                    if line_info in drawn:
                        offset = line_width * drawn.count(line_info)
                        new_start = (start[0] + offset, start[1] + offset)
                        new_end = (end[0] + offset, end[1] + offset)

                    if get_node_type(node) == TileType.RUNWAY: 
                        draw_dashed_line(path_surface, color, new_start, new_end, line_width) 
                    else:
                        pygame.draw.line(path_surface, color, new_start, new_end, line_width)

                    drawn.append(line_info)

                #been_drawn.extend(temp_drawn) 

        rot_path_surface = pygame.transform.rotate(path_surface, 25)
        screen.blit(rot_path_surface, (WIDTH/2 - rot_path_surface.get_width() / 2, HEIGHT / 2 - rot_path_surface.get_height() / 2))

        pygame.display.flip()
       
    def event_handler(self, pg_event, mouse_pos):
        if pg_event.type == pygame.KEYUP:
            try:
                value = int(pygame.key.name(pg_event.key).title())
            except:
                value = -1 
            if pg_event.key == pygame.K_RETURN:
                self.debug_flag = not self.debug_flag
                self.debug_path_num = -1
            elif value >= 0 and value <= 9: 
                self.debug_flag = False
                self.debug_path_num = value 
            elif pg_event.key == pygame.K_i:
                self.debug_flag = False
                self.debug_path_num += 1 
            elif pg_event.key == pygame.K_o:
                self.debug_flag = False
                self.debug_path_num -= 1 
            elif pg_event.key == pygame.K_r:
                self.debug_flag = False
                self.debug_path_num = -1
        return Event.NONE


class MainMenu():
    def __init__(self, ui):
        self.ui = ui

        menu_font = pygame.font.Font(None, 40)
        menu_titlefont = pygame.font.Font(None, 60)
        self.background = pygame.image.load("graphics/mainmenu.png")
        self.background = pygame.transform.smoothscale(self.background, ui.screen.get_size())
        self.menu_text = menu_titlefont.render("Air Runway and Taxiway Simulation System", True, "Black")
        self.menu_widget = self.menu_text.get_rect(midtop = (ui.screen_width/2, 0))

        self.start_text = menu_font.render("Start", True, "Black")
        self.start_button = self.start_text.get_rect(center = (ui.screen_width/2, ui.screen_height/4))

        self.settings_text = menu_font.render("Settings", True, "Black")
        self.settings_button = self.settings_text.get_rect(center = (ui.screen_width/2, ui.screen_height/2))

        self.exit_text = menu_font.render("Exit", True, "Black")
        self.exit_button = self.exit_text.get_rect(center = (ui.screen_width/2, ui.screen_height*3/4))

    def render(self):
        screen = self.ui.screen
        screen.blit(self.background, (0, 0)) 
        pygame.draw.rect(screen, "White", self.menu_widget)
        pygame.draw.rect(screen, "Black", self.menu_widget, 1, 3)
        screen.blit(self.menu_text, self.menu_widget)
        pygame.draw.rect(screen, "White", self.start_button) 
        pygame.draw.rect(screen, "Black", self.start_button, 1, 3)
        screen.blit(self.start_text, self.start_button)
        pygame.draw.rect(screen, "White", self.settings_button) 
        pygame.draw.rect(screen, "Black", self.settings_button, 1, 3)
        screen.blit(self.settings_text, self.settings_button)
        pygame.draw.rect(screen, "White", self.exit_button) 
        pygame.draw.rect(screen, "Black", self.exit_button, 1, 3)
        screen.blit(self.exit_text, self.exit_button)

    def event_handler(self, pg_event, mouse_pos):
        if pg_event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.GOTO_LOGIN
            elif self.settings_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.GOTO_SETTINGS
            elif self.exit_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.QUIT
        return Event.NONE


class Settings():
    def __init__(self, ui):
        self.ui = ui

        menu_font = pygame.font.Font(None, 40)
        menu_titlefont = pygame.font.Font(None, 60)
        self.background = pygame.image.load("graphics/settingsgear.png")
        self.background = pygame.transform.smoothscale(self.background, self.ui.screen.get_size())
        self.text = menu_titlefont.render("Settings", True, "Black")
        self.settings_widget = self.text.get_rect(midtop = (ui.screen_width/2, 0))

        self.fullscreen_text = menu_font.render("Toggle Fullscreen", True, "Black")
        self.fullscreen_button = self.fullscreen_text.get_rect(center = (ui.screen_width/2, ui.screen_height/2))

        self.return_text = menu_font.render("<--Return", True, "Black")
        self.return_button = self.return_text.get_rect(topleft = (0,0))

    def render(self):
        self.ui.screen.blit(self.background, (0,0))
        pygame.draw.rect(self.ui.screen, "White", self.settings_widget)
        pygame.draw.rect(self.ui.screen, "Black", self.settings_widget, 1, 3)
        self.ui.screen.blit(self.text, self.settings_widget)
        pygame.draw.rect(self.ui.screen, "White", self.fullscreen_button) 
        pygame.draw.rect(self.ui.screen, "Black", self.fullscreen_button, 1, 3)
        self.ui.screen.blit(self.fullscreen_text, self.fullscreen_button)
        pygame.draw.rect(self.ui.screen, "White", self.return_button) 
        pygame.draw.rect(self.ui.screen, "Black", self.return_button, 1, 3)
        self.ui.screen.blit(self.return_text, self.return_button)

    def event_handler(self, pg_event, mouse_pos):
        if pg_event.type == pygame.MOUSEBUTTONDOWN:
            if self.fullscreen_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.TOGGLE_FULLSCREEN
            elif self.return_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.GOTO_MAIN_MENU
        return Event.NONE


class Login():
    def __init__(self, ui):
        self.ui = ui

        self.menu_font = pygame.font.Font(None, 40)
        menu_titlefont = pygame.font.Font(None, 60)
        self.background = pygame.image.load("graphics/login.png")
        self.background = pygame.transform.smoothscale(self.background, ui.screen.get_size())
        self.text = menu_titlefont.render("Login", True, "Black")
        self.login_widget = self.text.get_rect(midtop = (ui.screen_width/2, 0))

        self.key_text = self.menu_font.render("Enter Key", True, "Black")
        self.key_input_box = pygame.Rect(100, 50, 540, 32)
        self.color_inactive = pygame.Color("White")
        self.color_active = pygame.Color("Light Gray")
        self.key_input_box_color = self.color_inactive
        self.input_active = False
        self.key_input_text = ''

        self.return_text = self.menu_font.render("<--Return", True, "Black")
        self.return_button = self.return_text.get_rect(topleft = (0,0))

    def render(self):
        self.ui.screen.blit(self.background, (0,0))
        pygame.draw.rect(self.ui.screen, "White", self.login_widget)
        pygame.draw.rect(self.ui.screen, "Black", self.login_widget, 1, 3)
        self.ui.screen.blit(self.text, self.login_widget)

        pygame.draw.rect(self.ui.screen, self.key_input_box_color, self.key_input_box)
        pygame.draw.rect(self.ui.screen, "Black", self.key_input_box, 1, 3)
        key_text_surface = self.menu_font.render(self.key_input_text, True, "Black")
        self.ui.screen.blit(key_text_surface, (self.key_input_box.x+5, self.key_input_box.y+5))

        pygame.draw.rect(self.ui.screen, "White", self.return_button) 
        pygame.draw.rect(self.ui.screen, "Black", self.return_button, 1, 3)
        self.ui.screen.blit(self.return_text, self.return_button)

    def event_handler(self, pg_event, mouse_pos):
        if pg_event.type == pygame.MOUSEBUTTONDOWN:
            if self.return_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.GOTO_MAIN_MENU
            elif self.key_input_box.collidepoint(mouse_pos):
                self.input_active = not self.input_active
            else:
                self.input_active = False
            self.key_input_box_color = self.color_active if self.input_active else self.color_inactive

        if pg_event.type == pygame.KEYDOWN:
            if self.input_active:
                if pg_event.key == pygame.K_RETURN:
                    return Event.CHECK_KEY
                elif pg_event.key == pygame.K_BACKSPACE:
                    self.key_input_text = self.key_input_text[:-1]
                else:
                    self.key_input_text += pg_event.unicode
        return Event.NONE


class UserInterface():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('ARTSS')

        pygame.mixer.init()
        self.button_sound = pygame.mixer.Sound("audio/click.wav")
        self.button_sound.set_volume(0.9)
        self.bg_music = pygame.mixer.Sound("audio/bgmusic.mp3")
        self.bg_music.set_volume(0.1)
        self.menu_channel = pygame.mixer.Channel(0)
        self.menu_channel.play(self.bg_music, loops = -1)

        
        with open('settings.txt', 'r') as f:
            settingsdata = f.read().strip()
        self.fullscreen_setting = ast.literal_eval(settingsdata.split('=')[1].strip())
        if self.fullscreen_setting:
            self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        self.current_ui = None 

    def render(self):
        self.current_ui.render()
        pygame.display.update()
        self.clock.tick(FPS)

    def event_handler(self):
        mouse_pos = pygame.mouse.get_pos()
        event = Event.NONE
        
        for pg_event in pygame.event.get():
            if pg_event.type == pygame.QUIT:
                return Event.QUIT
            event = self.current_ui.event_handler(pg_event, mouse_pos)
        return event 
    
    def transition_state(self, new_state):
        # python's garbage collector takes care of "unloading"
        if new_state == State.MAIN_MENU:
            self.menu_channel.set_volume(0.1)
            self.current_ui = MainMenu(self) 
        elif new_state == State.SETTINGS:
            self.menu_channel.set_volume(0.1)
            self.current_ui = Settings(self)
        elif new_state == State.LOGIN:
            self.menu_channel.set_volume(0.1)
            self.current_ui = Login(self)
        elif new_state == State.FULLSCREEN:
            if not self.fullscreen_setting:
                self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
                self.screen_width, self.screen_height = self.screen.get_size()
                self.fullscreen_setting = True
                settingline = "Fullscreen = True\n"
                with open("settings.txt","w+") as f:
                    f.write(settingline)
                self.current_ui = Settings(self)
            elif self.fullscreen_setting:
                self.screen = pygame.display.set_mode((1200, 800))
                self.screen_width, self.screen_height = self.screen.get_size()
                self.fullscreen_setting = False
                settingline = "Fullscreen = False\n"
                with open("settings.txt","w+") as f:
                    f.write(settingline)
                self.current_ui = Settings(self)
        elif new_state == State.SIMULATION:
            self.menu_channel.set_volume(0)
            self.current_ui = Simulation(self)

    def quit(self):
        pygame.mixer.quit()
        pygame.quit()  
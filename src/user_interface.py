import pygame
import ast
import math
from utils.states import State, Event 
from utils.map_handler import TileType, get_map, get_node_type, get_wind_info, MIN_WIND_SPEED, MAX_WIND_SPEED
from .plane_agent import DEPARTED_ALTITUDE, plane_queue
import numpy as np 
import matplotlib as plt
from utils.logger import ARTSSClock
from utils.flight_data_handler import FlightStatus
from .message_box import MessageBox
from utils.logger import Logger


FPS = 30
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


def get_status_text(plane):
    status = plane.get_status()
    if status == FlightStatus.AT_GATE: 
        return "At Gate" 
    elif status == FlightStatus.READY_FOR_PUSHBACK: 
        return "Ready for Pushback" 
    elif status == FlightStatus.PUSHBACK_IN_PROGRESS: 
        return "Pushback in Progress"
    elif status == FlightStatus.WAITING_FOR_TAXI_CLEARANCE: 
        return "Waiting for Taxi Clearance" 
    elif status == FlightStatus.TAXIING_TO_RUNWAY: 
        return "Taxiing to Runway" 
    elif status == FlightStatus.HOLDING_SHORT: 
        return "Holding Short" 
    elif status == FlightStatus.LINING_UP: 
        return "Lining Up" 
    elif status == FlightStatus.WAITING_FOR_TAKEOFF_CLEARANCE: 
        return "Waiting for Takeoff Clearance" 
    elif status == FlightStatus.TAKING_OFF: 
        return "Taking Off" 
    elif status == FlightStatus.AIRBORNE: 
        return "Airborne" 
    elif status == FlightStatus.CLIMBING: 
        return "Climbing" 
    elif status == FlightStatus.DEPARTED: 
        return "Departed" 
    else:
        return "None"


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


def get_red_green_color(amt, idx):
    if idx == 0: 
        return (255, 0, 255)
    colors = plt.cm.RdYlGn(np.linspace(1, 0, amt))
    rgb_colors = [(int(c[0]*255), int(c[1]*255), int(c[2]*255)) for c in colors]
    return rgb_colors[idx]


def get_rainbow_color(amt, idx):
    rainbow_colors_red_to_violet = plt.cm.rainbow(np.linspace(1, 0, amt))
    rainbow_colors_red_to_violet_255 = [(int(color[0]*255), int(color[1]*255), int(color[2]*255)) for color in rainbow_colors_red_to_violet]
    color =rainbow_colors_red_to_violet_255[idx]
    color = (
        min(color[0] + 40, 255),
        min(color[1] + 40, 255),
        min(color[2] + 40, 255),
    )
    return color


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


def draw_rect_alpha(surface, color, rect, borders=True, text=None):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    if borders:
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), 4, 4)
    else:
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    if text is not None:
        surface.blit(text, rect)
    surface.blit(shape_surf, rect)

def add_outline_to_image(image: pygame.Surface, thickness: int, color: tuple, color_key: tuple = (0, 0, 0)) -> pygame.Surface:
    mask = pygame.mask.from_surface(image)
    mask_surf = mask.to_surface(setcolor=color)
    mask_surf.set_colorkey((0, 0, 0))

    new_img = pygame.Surface((image.get_width() + 2, image.get_height() + 2))
    new_img.fill(color_key)
    new_img.set_colorkey(color_key)

    for i in -thickness, thickness:
        new_img.blit(mask_surf, (i + thickness, thickness))
        new_img.blit(mask_surf, (thickness, i + thickness))
    new_img.blit(image, (thickness, thickness))

    return new_img

class ARTSSCanvas():
    def __init__(self, ui):
        self.ui = ui
        airport_image = pygame.image.load("graphics/sim_bg_dark.png")
        self.airport_background = pygame.transform.scale(airport_image, (WIDTH, HEIGHT))

        # grid for testing purposes
        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, x in enumerate(get_map()):
            for j, y in enumerate(x):
                if y.type == TileType.NOTHING: 
                    continue 
                pygame.draw.rect(grid_surface, (255, 255, 255), (i*GRID_SPACE_SIZE, j*GRID_SPACE_SIZE, 
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
            
        ps = pygame.transform.rotate(self.plane_surface, 25) 
        screen.blit(ps, (WIDTH/2 - ps.get_width() / 2, HEIGHT/2 - ps.get_height() / 2))

        CENTER_X = 1180
        CENTER_Y = 100
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
        line_width = 3
        drawn = []
        for n, plane in enumerate(plane_queue):
            """
            status_text = get_status_text(plane)
            text_surface = self.font.render(status_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            pygame.draw.rect(screen, (0, 0, 0), (CENTER_X-60, CENTER_Y+150, text_rect[2]+18, 48), border_radius=10)
            pygame.draw.rect(screen, COMPASS_BG_COLOR, (CENTER_X-56, CENTER_Y+154, text_rect[2]+10, 40), border_radius=8)

            draw_text_with_outline(screen, f"{status_text}", self.font, (CENTER_X-51, CENTER_Y+164), WIND_ARROW_COLOR, (0, 0, 0), 2, False)
            if self.debug_flag:
                paths = [plane.debug_best_grade_path] 
            elif self.debug_path_num != -1:
                paths = [plane.get_debug_paths()[self.debug_path_num]]
            else:
                paths = plane.get_debug_paths()
            """
            #paths = plane.get_debug_paths()
            paths = [plane.current_path]
            color = plane.color
            #color = get_rainbow_color(len(plane_queue), n) 
            for j, path in enumerate(paths):
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

                    line_info = f"{start}{end}"
                    if line_info in drawn:
                        n = drawn.count(line_info)
                        offset = (round(n/2) * (-1 if n % 2 == 0 else 1)) + line_width
                        new_start = (start[0] + offset, start[1] + offset)
                        new_end = (end[0] + offset, end[1] + offset)
                    
                    if get_node_type(node) == TileType.RUNWAY: 
                        draw_dashed_line(path_surface, color, new_start, new_end, line_width) 
                    else:
                        pygame.draw.line(path_surface, color, new_start, new_end, line_width)

                    drawn.append(line_info)

        rot_path_surface = pygame.transform.rotate(path_surface, 25)
        screen.blit(rot_path_surface, (WIDTH/2 - rot_path_surface.get_width() / 2, HEIGHT / 2 - rot_path_surface.get_height() / 2))

        self.plane_surface.fill((0, 0, 0, 0))
        for n, plane in enumerate(plane_queue):
            if plane.get_status() == FlightStatus.DEPARTED:
                continue
            #color = get_rainbow_color(len(plane_queue), n) 
            color = plane.color
            plane_img = self.plane_imgs[plane.get_aircraft_type().value - 1] 
            plane_img = colorize_image(plane_img, color)
            facing_angle = plane.get_facing_direction().value
            mx, my = plane.get_map_pos()
            scale_factor = ((plane.altitude / DEPARTED_ALTITUDE) * (MAX_PLANE_SCALE - 1)) + 1 
            width = height = GRID_SPACE_SIZE * scale_factor
            offset = (width - GRID_SPACE_SIZE) // 2
            x, y = (mx * GRID_SPACE_SIZE - offset, my * GRID_SPACE_SIZE - offset) 
            plane_img_rot = pygame.transform.rotate(plane_img, facing_angle)
            plane_img_scaled = pygame.transform.scale(plane_img_rot, (width, height))
            self.plane_surface.blit(plane_img_scaled, (x, y))
            planefont = pygame.font.Font(None, 18)
            planetext = planefont.render(plane.flight_data["flight_number"], True, color)
            self.plane_surface.blit(planetext, (x - 8, y - 8))
            plane.x = x
            plane.y = y
            plane.image = plane_img_scaled
            plane.rect = plane.image.get_rect(topleft = (plane.x,plane.y))

class Simulation ():
    def __init__(self, ui):
        self.ui = ui
        self.artss_canvas = ARTSSCanvas(ui)

        self.message_font = pygame.font.Font(None, 25)
        self.menufont = pygame.font.SysFont("britannic", 35)
        self.titlefont= pygame.font.SysFont("britannic", 55)
        self.color_not_hovering = pygame.Color(255,255,255,215)
        self.color_hovering = pygame.Color(128,128,128,215)
        self.transparent = pygame.Color(0,0,0,0)
        self.return_box_color = self.color_not_hovering
        self.titletext = self.titlefont.render("Simulation", True, "White")
        self.titletext_widget = self.titletext.get_rect(midtop = (ui.screen_width/2, 0))
        self.return_text = self.menufont.render("<--Return", True, "Black")
        self.return_button = self.return_text.get_rect(topleft = (0,0))
        self.play_button = pygame.image.load("graphics/playbutton.png")
        self.play_button = pygame.transform.smoothscale(self.play_button, (ui.screen_width/30, ui.screen_height/20))
        self.pause_button = pygame.image.load("graphics/pausebutton.png")
        self.pause_button = pygame.transform.smoothscale(self.pause_button, (ui.screen_width/30, ui.screen_height/20))

        self.show_log = False
        self.show_manual_controls = False
        self.logheader_text = self.menufont.render("Log", True, "White")
        self.logheader_text = add_outline_to_image(self.logheader_text, 2, (0,0,0))
        self.logheader_button = self.logheader_text.get_rect(center = (ui.screen_width/15, 50)) 
        self.logheader_button_color = self.transparent

        self.controls_text = self.menufont.render("Manual Controls", True, "CYAN")
        self.controls_text = add_outline_to_image(self.controls_text, 2, (0,0,0))
        self.controls_button = self.controls_text.get_rect(center = (ui.screen_width/4.8, 50))
        self.controls_button_color = self.transparent
        
        self.logbox = pygame.Rect((0, 75), (ui.screen_width/3, ui.screen_height - 75))
        self.logoutgoing_text = self.menufont.render("Outgoing", True, "Blue")
        self.logoutgoing_text.set_alpha(127)
        self.logoutgoing_widget = self.logoutgoing_text.get_rect(center = (ui.screen_width/6 - 5, 95))
        self.logoutgoingbox = pygame.Rect((0, 115), (ui.screen_width/3, ui.screen_height/2 - 115))
        self.logincoming_text = self.menufont.render("Incoming", True, "Green")
        self.logoutgoing_text.set_alpha(127)
        self.logincoming_widget = self.logincoming_text.get_rect(center = (ui.screen_width/6 - 5, ui.screen_height/2 + 20))
        self.logincomingbox = pygame.Rect((0, ui.screen_height/2 + 40), (ui.screen_width/3, ui.screen_height/2 - 40))

        self.controlsbox = self.logbox = pygame.Rect((0, 75), (ui.screen_width/3, ui.screen_height - 75))
        
        self.outgoing_messages = pygame.sprite.Group()
        self.last_atc_message = ""
        self.incoming_messages = pygame.sprite.Group()
        self.last_flight_message = ""

        self.planes_info = pygame.sprite.Group()
    
    def change_button_color(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.return_button.collidepoint(mouse_pos):
            self.return_box_color = self.color_hovering
        else:
            self.return_box_color = self.color_not_hovering
        if self.logheader_button.collidepoint(mouse_pos):
            self.logheader_button_color = self.color_hovering
        else:
            self.logheader_button_color = self.transparent
        if self.controls_button.collidepoint(mouse_pos):
            self.controls_button_color = self.color_hovering
        else:
            self.controls_button_color = self.transparent

    def determine_boxheight(self, text, font, allowable_width):
        fw, fh = pygame.font.Font.size(font, text)
        num_row = math.ceil(fw/allowable_width)
        box_height = fh * num_row + 3
        return box_height

    def create_messagebox(self, text, font, color, allowable_width, screen, outgoing=True):
        box_height = self.determine_boxheight(text, font, allowable_width)
        if outgoing:
            if (len(self.outgoing_messages) == 0):
                current_y = self.logoutgoingbox.topleft[1] + 4
            else:
                current_y = self.outgoing_messages.sprites()[len(self.outgoing_messages) - 1].rect.bottom
            while not self.logoutgoingbox.collidepoint((self.logoutgoingbox.topleft[0], current_y + box_height)):
                dy = self.outgoing_messages.sprites()[0].rect.height
                self.outgoing_messages.sprites()[0].kill()
                self.outgoing_messages.update(-dy)
                current_y = self.outgoing_messages.sprites()[len(self.outgoing_messages) - 1].rect.bottom
            message = MessageBox(allowable_width -  10, box_height, self.logoutgoingbox.topleft[0] + 5, current_y, screen, text, color, 127)
            self.outgoing_messages.add(message)
        else:
            if (len(self.incoming_messages) == 0):
                current_y = self.logincomingbox.topleft[1] + 4
            else:
                current_y = self.incoming_messages.sprites()[len(self.incoming_messages) - 1].rect.bottom
            while not self.logincomingbox.collidepoint((self.logincomingbox.topleft[0], current_y + box_height)):
                dy = self.incoming_messages.sprites()[0].rect.height
                self.incoming_messages.sprites()[0].kill()
                self.incoming_messages.update(-dy)
                current_y = self.incoming_messages.sprites()[len(self.incoming_messages) - 1].rect.bottom
            message = MessageBox(allowable_width -  10, box_height, self.logincomingbox.topleft[0] + 5, current_y, screen, text, color,127)
            self.incoming_messages.add(message)

    def display_plane_info(self, font, plane):
        color = plane.color
        plane_info = plane.flight_data["flight_number"] + ": " + get_status_text(plane)
        box_height = self.determine_boxheight(plane_info, font, 100)
        plane_box = MessageBox(100, box_height, plane.x - 15, plane.y - box_height - 15, self.artss_canvas.plane_surface, plane_info, color, 175)
        self.planes_info.add(plane_box)
     
    def render(self):
        screen = self.ui.screen
        self.artss_canvas.render()
    
        self.change_button_color()
        draw_rect_alpha(screen, self.return_box_color, self.return_button, False)
        pygame.draw.rect(screen, "Black", self.return_button, 1, 3)
        screen.blit(self.return_text, self.return_button)
        screen.blit(self.play_button, (1125, 240))
        screen.blit(self.pause_button, (1190, 240))
        draw_rect_alpha(screen, self.logheader_button_color, self.logheader_button)
        screen.blit(self.logheader_text, self.logheader_button)
        draw_rect_alpha(screen, self.controls_button_color, self.controls_button)
        screen.blit(self.controls_text, self.controls_button)
        if self.show_log:
            draw_rect_alpha(screen, (255,255,255,127) , self.logbox)
            draw_rect_alpha(screen, (255,255,255,127), self.logoutgoingbox)
            screen.blit(self.logoutgoing_text, self.logoutgoing_widget)
            draw_rect_alpha(screen, (255,255,255,127), self.logincomingbox)
            screen.blit(self.logincoming_text, self.logincoming_widget)

            new_atc_message = Logger.last_atc_message
            atc_msg = new_atc_message.split("]")[1]
            atc_msg_without_time = atc_msg[1:len(atc_msg)]
            if atc_msg_without_time != self.last_atc_message:
                self.create_messagebox(new_atc_message,self.message_font,(0,0,255,127), self.logoutgoingbox.width, screen)
            self.last_atc_message = atc_msg_without_time

            new_flight_message = Logger.last_flight_message
            flight_msg = new_flight_message.split("]")[1]
            flight_msg_without_time = flight_msg[1:len(flight_msg)]
            if flight_msg_without_time != self.last_flight_message:
                self.create_messagebox(new_flight_message,self.message_font,(0,255,0,127), self.logincomingbox.width, screen, False)
            self.last_flight_message = flight_msg_without_time

            self.outgoing_messages.draw(screen)
            self.outgoing_messages.update(0)
            self.incoming_messages.draw(screen)
            self.incoming_messages.update(0)  
        elif self.show_manual_controls:
            draw_rect_alpha(screen, (0,255,255,127) , self.controlsbox)
        
        self.planes_info.draw(screen)
        self.planes_info.update(0)
        if ARTSSClock.Running:
            self.planes_info.empty()

    def event_handler(self, pg_event, mouse_pos):
        if pg_event.type == pygame.MOUSEBUTTONDOWN:
            if self.return_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.GOTO_MAIN_MENU
            elif self.play_button.get_rect(topleft = (1125, 240)).collidepoint(mouse_pos):
                self.ui.button_sound.play()
                ARTSSClock.setRunning(True)
            elif self.pause_button.get_rect(topleft = (1190, 240)).collidepoint(mouse_pos):
                self.ui.button_sound.play()
                ARTSSClock.setRunning(False)
            elif self.logheader_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                self.show_manual_controls = False
                self.show_log = not self.show_log
            elif self.controls_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                self.show_log = False
                self.show_manual_controls = not self.show_manual_controls
            if not ARTSSClock.Running:  
                for n, plane in enumerate(plane_queue):
                    center_x = WIDTH/2
                    center_y= HEIGHT/2
                    vec = pygame.math.Vector2(plane.x - center_x, plane.y - center_y)
                    rot_vec = vec.rotate(-25)
                    dif_x = rot_vec.x - vec.x
                    dif_y = rot_vec.y - vec.y
                    rot_rect = pygame.Rect(plane.x + dif_x, plane.y + dif_y, plane.rect.width, plane.rect.height)
                    if rot_rect.collidepoint(mouse_pos):
                        if len(self.planes_info) == 0:
                            self.display_plane_info(self.message_font, plane)
                        else:
                            self.planes_info.empty()
                            self.display_plane_info(self.message_font, plane)
        if pg_event.type == pygame.KEYDOWN:
            if pg_event.key == pygame.K_SPACE:
                self.ui.button_sound.play()
                ARTSSClock.setRunning(not ARTSSClock.Running)
        return Event.NONE


class MainMenu():
    def __init__(self, ui):
        self.ui = ui
        
        menu_font = pygame.font.SysFont("britannic", 40)
        menu_titlefont = pygame.font.SysFont("britannic", 55)
        self.color_not_hovering = pygame.Color(255,255,255,215)
        self.color_hovering = pygame.Color(128,128,128,215)
        self.start_box_color = self.color_not_hovering
        self.settings_box_color = self.color_not_hovering
        self.exit_box_color = self.color_not_hovering
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

    def change_button_color(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.start_button.collidepoint(mouse_pos):
            self.start_box_color = self.color_hovering
        else:
            self.start_box_color = self.color_not_hovering
        if self.settings_button.collidepoint(mouse_pos):
            self.settings_box_color = self.color_hovering
        else:
            self.settings_box_color = self.color_not_hovering
        if self.exit_button.collidepoint(mouse_pos):
            self.exit_box_color = self.color_hovering
        else:
            self.exit_box_color = self.color_not_hovering

    def render(self):
        screen = self.ui.screen

        screen.blit(self.background, (0, 0)) 
        draw_rect_alpha(screen,(255,255,255,225), self.menu_widget, False)
        pygame.draw.rect(screen, "Black", self.menu_widget, 1, 3)
        screen.blit(self.menu_text, self.menu_widget)
        self.change_button_color()
        draw_rect_alpha(screen, self.start_box_color, self.start_button, False)
        pygame.draw.rect(screen, "Black", self.start_button, 1, 3)
        screen.blit(self.start_text, self.start_button)
        draw_rect_alpha(screen, self.settings_box_color, self.settings_button, False)
        pygame.draw.rect(screen, "Black", self.settings_button, 1, 3)
        screen.blit(self.settings_text, self.settings_button)
        draw_rect_alpha(screen, self.exit_box_color, self.exit_button, False)
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

        menu_font = pygame.font.SysFont("britannic", 40)
        menu_titlefont = pygame.font.SysFont("britannic", 55)
        self.color_not_hovering = pygame.Color(255,255,255,215)
        self.color_hovering = pygame.Color(128,128,128,215)
        self.return_box_color = self.color_not_hovering
        self.toggle_box_color = self.color_not_hovering
        self.background = pygame.image.load("graphics/settingsgear.png")
        self.background = pygame.transform.smoothscale(self.background, self.ui.screen.get_size())
        self.text = menu_titlefont.render("Settings", True, "Black")
        self.settings_widget = self.text.get_rect(midtop = (ui.screen_width/2, 0))
        self.fullscreen_text = menu_font.render("Toggle Fullscreen", True, "Black")
        self.fullscreen_button = self.fullscreen_text.get_rect(center = (ui.screen_width/2, ui.screen_height/2))
        self.return_text = menu_font.render("<--Return", True, "Black")
        self.return_button = self.return_text.get_rect(topleft = (0,0))
    
    def change_button_color(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.return_button.collidepoint(mouse_pos):
            self.return_box_color = self.color_hovering
        else:
            self.return_box_color = self.color_not_hovering
        if self.fullscreen_button.collidepoint(mouse_pos):
            self.toggle_box_color = self.color_hovering
        else:
            self.toggle_box_color = self.color_not_hovering
    
    def render(self):
        screen = self.ui.screen

        screen.blit(self.background, (0,0))
        draw_rect_alpha(screen,(255,255,255,225), self.settings_widget, False)
        pygame.draw.rect(screen, "Black", self.settings_widget, 1, 3)
        screen.blit(self.text, self.settings_widget)
        self.change_button_color()
        draw_rect_alpha(screen, self.toggle_box_color, self.fullscreen_button, False)
        pygame.draw.rect(screen, "Black", self.fullscreen_button, 1, 3)
        screen.blit(self.fullscreen_text, self.fullscreen_button)
        draw_rect_alpha(screen, self.return_box_color, self.return_button, False)
        pygame.draw.rect(screen, "Black", self.return_button, 1, 3)
        screen.blit(self.return_text, self.return_button)

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

        self.menu_font = pygame.font.SysFont("britannic", 40)
        menu_titlefont = pygame.font.SysFont("britannic", 55)
        self.color_not_hovering = pygame.Color(255,255,255,215)
        self.color_hovering = pygame.Color(128,128,128,215)
        self.return_box_color = self.color_not_hovering
        self.background = pygame.image.load("graphics/login.png")
        self.background = pygame.transform.smoothscale(self.background, ui.screen.get_size())
        self.text = menu_titlefont.render("Login", True, "Black")
        self.login_widget = self.text.get_rect(midtop = (ui.screen_width/2, 0))
        self.key_text = self.menu_font.render("Enter Key", True, "Black")
        self.key_input_box = pygame.Rect(100, 75, 540, 45)
        self.color_inactive = pygame.Color("White")
        self.color_active = pygame.Color("Light Gray")
        self.key_input_box_color = self.color_inactive
        self.input_active = False
        self.key_input_text = ''
        self.return_text = self.menu_font.render("<--Return", True, "Black")
        self.return_button = self.return_text.get_rect(topleft = (0,0))
    
    def change_button_color(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.return_button.collidepoint(mouse_pos):
            self.return_box_color = self.color_hovering
        else:
            self.return_box_color = self.color_not_hovering

    def render(self):
        screen = self.ui.screen

        screen.blit(self.background, (0,0))
        draw_rect_alpha(screen,(255,255,255,225), self.login_widget, False)
        pygame.draw.rect(screen, "Black", self.login_widget, 1, 3)
        screen.blit(self.text, self.login_widget)
        pygame.draw.rect(screen, self.key_input_box_color, self.key_input_box)
        pygame.draw.rect(screen, "Black", self.key_input_box, 1, 3)
        key_text_surface = self.menu_font.render(self.key_input_text, True, "Black")
        screen.blit(key_text_surface, (self.key_input_box.x+5, self.key_input_box.y+5))
        self.change_button_color()
        draw_rect_alpha(screen, self.return_box_color, self.return_button, False)
        pygame.draw.rect(screen, "Black", self.return_button, 1, 3)
        screen.blit(self.return_text, self.return_button)

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
        self.explosion_sound = pygame.mixer.Sound("audio/explosion_sfx.wav")
        self.explosion_sound.set_volume(0.1)
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
            ARTSSClock.setRunning(False) 
        elif new_state == State.SETTINGS:
            self.menu_channel.set_volume(0.1)
            self.current_ui = Settings(self)
            ARTSSClock.setRunning(False) 
        elif new_state == State.LOGIN:
            self.menu_channel.set_volume(0.1)
            self.current_ui = Login(self)
            ARTSSClock.setRunning(False) 
        elif new_state == State.FULLSCREEN:
            if not self.fullscreen_setting:
                self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
                self.screen_width, self.screen_height = self.screen.get_size()
                self.fullscreen_setting = True
                with open("settings.txt","w+") as f:
                    f.write("Fullscreen = True\n")
                self.current_ui = Settings(self)
            elif self.fullscreen_setting:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                self.screen_width, self.screen_height = self.screen.get_size()
                self.fullscreen_setting = False
                with open("settings.txt","w+") as f:
                    f.write("Fullscreen = False\n")
                self.current_ui = Settings(self)
        elif new_state == State.SIMULATION:
            self.menu_channel.set_volume(0)
            self.current_ui = Simulation(self)
            ARTSSClock.setRunning(True)

    def quit(self):
        pygame.mixer.quit()
        pygame.quit()  
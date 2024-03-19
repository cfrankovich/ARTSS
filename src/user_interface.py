import pygame
import ast
from utils.states import State, Event 
from src.sim import ARTSS
from utils.map_handler import TileType, get_map 
from .plane_agent import DEPARTED_ALTITUDE 

FPS = 5 
WIDTH = 1280
HEIGHT = 720
GRID_SPACE_SIZE = 20
MAX_PLANE_SCALE = 4

class Simulation():
    def __init__(self, ui):
        self.ui = ui
        airport_image = pygame.image.load("graphics/sim_bg_blur.png")
        self.airport_background = pygame.transform.scale(airport_image, (WIDTH, HEIGHT))

        # grid for testing purposes
        """
        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, x in enumerate(get_map()):
            for j, y in enumerate(x):
                if y.type == TileType.NOTHING: 
                    continue 
                pygame.draw.rect(grid_surface, y.color, (i*GRID_SPACE_SIZE, j*GRID_SPACE_SIZE, 
                                                GRID_SPACE_SIZE, GRID_SPACE_SIZE), 1)
        self.rot_grid_surface = pygame.transform.rotate(grid_surface, 25)
        """

        plane_img = pygame.image.load("graphics/plane_blue.png")
        self.plane_img = pygame.transform.scale(plane_img, (20, 20))

        self.plane_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def render(self):
        screen = self.ui.screen
        screen.fill((0, 0, 0))

        airport_background_rect = self.airport_background.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(self.airport_background, airport_background_rect.topleft)

        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, x in enumerate(get_map()):
            for j, y in enumerate(x):
                if y.type == TileType.NOTHING: 
                    continue 
                pygame.draw.rect(grid_surface, y.color, (i*GRID_SPACE_SIZE, j*GRID_SPACE_SIZE, 
                                                GRID_SPACE_SIZE, GRID_SPACE_SIZE), y.fill)
        self.rot_grid_surface = pygame.transform.rotate(grid_surface, 25)
        screen.blit(self.rot_grid_surface, (WIDTH/2 - self.rot_grid_surface.get_width() / 2, HEIGHT/2 - self.rot_grid_surface.get_height() / 2))

        self.plane_surface.fill((0, 0, 0, 0))
        for plane in ARTSS.plane_queue:
            facing_angle = plane.get_facing_direction().value
            mx, my = plane.get_map_pos()
            scale_factor = ((plane.altitude / DEPARTED_ALTITUDE) * (MAX_PLANE_SCALE - 1)) + 1 
            size = self.plane_img.get_size()
            width = size[0] * scale_factor 
            height = size[1] * scale_factor 
            x_offset = width - size[0] 
            y_offset = height - size[1] 
            x, y = (mx * GRID_SPACE_SIZE - (x_offset // 2), my * GRID_SPACE_SIZE - (y_offset // 2)) 
            plane_img_rot = pygame.transform.rotate(self.plane_img, facing_angle)
            plane_img_scaled = pygame.transform.scale(plane_img_rot, (width, height))
            self.plane_surface.blit(plane_img_scaled, (x, y))
            
        ps = pygame.transform.rotate(self.plane_surface, 25) 
        screen.blit(ps, (WIDTH/2 - ps.get_width() / 2, HEIGHT/2 - ps.get_height() / 2))

        pygame.display.flip()
       
    def event_handler(self, pg_event, mouse_pos):
        if pg_event.type == pygame.MOUSEBUTTONDOWN:
            if self.return_button.collidepoint(mouse_pos):
                self.ui.button_sound.play()
                return Event.GOTO_MAIN_MENU
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
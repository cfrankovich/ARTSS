import pygame
import ast
import math
import random
from random import randint
from utils.states import State, Event 
from src.plane_agent import Plane
from src.message_box import MessageBox

class Simulation():
    def __init__(self, ui):
        self.ui = ui

        self.message_font = pygame.font.Font(None, 25)
        self.menufont = pygame.font.Font(None, 40)
        self.titlefont= pygame.font.Font(None, 60)

        self.titletext = self.titlefont.render("Simulation", True, "White")
        self.titletext_widget = self.titletext.get_rect(midtop = (ui.screen_width/2, 0))
        self.return_text = self.menufont.render("<--Return", True, "Black")
        self.return_button = self.return_text.get_rect(topleft = (0,0))
        self.logheader_text = self.menufont.render("Log", True, "White")
        self.logheader_widget = self.logheader_text.get_rect(center = (ui.screen_width/6, 50))
        self.logbox = pygame.Rect((0, 75), (ui.screen_width/3, ui.screen_height - 75))
        self.logoutgoing_text = self.menufont.render("Outgoing", True, "Blue")
        self.logoutgoing_widget = self.logoutgoing_text.get_rect(center = (ui.screen_width/6 - 5, 95))
        self.logoutgoingbox = pygame.Rect((0, 115), (ui.screen_width/3, ui.screen_height/2 - 115))
        self.logincoming_text = self.menufont.render("Incoming", True, "Green")
        self.logincoming_widget = self.logincoming_text.get_rect(center = (ui.screen_width/6 - 5, ui.screen_height/2 + 20))
        self.logincomingbox = pygame.Rect((0, ui.screen_height/2 + 40), (ui.screen_width/3, ui.screen_height - 75))
        
        self.outgoing_messages = pygame.sprite.Group()

        self.airport_text = self.menufont.render("Airport", True, "White")
        self.airport_widget = self.airport_text.get_rect(center = (ui.screen_width *2/3, 50))
        self.simbox = pygame.Rect((ui.screen_width/3, 75), (ui.screen_width * 2/3, ui.screen_height - 75))
        self.airport_surface = pygame.image.load("graphics/DAB.png")
        self.airport_surface = pygame.transform.smoothscale(self.airport_surface, (ui.screen_width * 2/3 - 10, ui.screen_height - 75 -10))

        self.testplane = Plane("White", 100, 100, "A67")
        self.explosion = pygame.image.load("graphics/explosion.png")
        self.explosion = pygame.transform.smoothscale(self.explosion, ui.screen.get_size())

    def determine_boxheight(self, text, font, allowable_width):
        fw, fh = pygame.font.Font.size(font, text)
        num_col = math.ceil(fw/allowable_width)
        box_height = fh * num_col
        return box_height

    def create_messagebox(self, text, font, allowable_width, screen):
        box_height = self.determine_boxheight(text, font, allowable_width)
        if (len(self.outgoing_messages) == 0):
            current_y = self.logoutgoingbox.topleft[1] + 4
        else:
            current_y = self.outgoing_messages.sprites()[len(self.outgoing_messages) - 1].rect.bottom
        while not self.logoutgoingbox.collidepoint((self.logoutgoingbox.topleft[0], current_y + box_height)):
            dy = self.outgoing_messages.sprites()[0].rect.height
            self.outgoing_messages.sprites()[0].kill()
            self.outgoing_messages.update(-dy)
            current_y = self.outgoing_messages.sprites()[len(self.outgoing_messages) - 1].rect.bottom
        message = MessageBox("Black", allowable_width -  10, box_height, self.logoutgoingbox.topleft[0] + 5, current_y, screen, text)
        self.outgoing_messages.add(message)

    def render(self):
        screen = self.ui.screen
        screen.fill((0, 0, 0))

        screen.blit(self.titletext, self.titletext_widget)
        pygame.draw.rect(screen, "White", self.return_button) 
        pygame.draw.rect(screen, "Black", self.return_button, 1, 3)
        screen.blit(self.return_text, self.return_button)
        screen.blit(self.logheader_text, self.logheader_widget)
        screen.blit(self.airport_text, self.airport_widget)
        pygame.draw.rect(screen, "White", self.logbox, 5, 5)
        pygame.draw.rect(screen, "White", self.simbox, 5, 5)
        screen.blit(self.airport_surface, (self.ui.screen_width/3 + 5, 80) )
        screen.blit(self.logoutgoing_text, self.logoutgoing_widget)
        pygame.draw.rect(screen, "White", self.logoutgoingbox, 3, 2)
        screen.blit(self.logincoming_text, self.logincoming_widget)
        pygame.draw.rect(screen, "White", self.logincomingbox, 3, 2)

        self.outgoing_messages.draw(screen)
        self.outgoing_messages.update(0)
        
        testplane = self.testplane
        simbox = self.simbox
        
        if not simbox.collidepoint(testplane.rect.topleft):
            rotated_plane = testplane.move(randint(9,12), randint(4,8))
        elif not simbox.collidepoint(testplane.rect.bottomright):
           rotated_plane = testplane.move(-randint(9,12), -randint(4,8))
        elif not simbox.collidepoint(testplane.rect.topright):
           rotated_plane = testplane.move(-randint(9,12), randint(4,8))
        elif not simbox.collidepoint(testplane.rect.bottomleft):
           rotated_plane = testplane.move(randint(9,12), -randint(6,8))
        else:
           rotated_plane = testplane.move(1, 1)
        screen.blit(rotated_plane, rotated_plane.get_rect(center = testplane.rect.center))
        testfont = pygame.font.Font(None, 25)
        planetext = testfont.render(testplane.flightnumber, True, "Blue")
        screen.blit(planetext, rotated_plane.get_rect(center = testplane.rect.center))

        pygame.display.update()
       
    def event_handler(self, pg_event, mouse_pos):
        if pg_event.type == pygame.MOUSEBUTTONDOWN:
            ##Click to simulate event that would display message in log box##
            textlist = ["This is some random test text to test the text wrapping ability of text for testing. The more the test text, the better the testing.", "The better the testing, the better the test. The better the test...", "Some more random test text for testing"]
            self.create_messagebox(random.choices(textlist)[0], self.message_font, self.logoutgoingbox.width, self.ui.screen)
            ##-------------------------------------------------------------##
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
            self.screen = pygame.display.set_mode((1200, 800))
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        self.current_ui = None 

    def render(self):
        self.current_ui.render()
        pygame.display.update()
        self.clock.tick(60)

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
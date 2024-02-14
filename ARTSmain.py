import pygame
import sys

pygame.init()
pygame.mixer.init()

# Window mode
windowmode = "Full"
if windowmode == "Fullscreen":
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
else:
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('ARTSS')
clock = pygame.time.Clock()

# Audio
button_sound = pygame.mixer.Sound("audio/click.wav")
button_sound.set_volume(0.9)
bg_music = pygame.mixer.Sound("audio/bgmusic.mp3")
bg_music.set_volume(0.1)
bg_music.play(loops = -1)

menu_font = pygame.font.Font(None, 40)
menu_titlefont = pygame.font.Font(None, 60)
# Main Menu
mainmenu_surface = pygame.image.load("graphics/mainmenu.png")
mainmenu_surface = pygame.transform.smoothscale(mainmenu_surface, screen.get_size())
mainmenu_text = menu_titlefont.render("Air Runway and Taxiway Simulation System", True, "Black")
mainmenu_widget = mainmenu_text.get_rect(midtop = (SCREEN_WIDTH/2 , 0))
menustart_text = menu_font.render("Start", True, "Black")
start_button = menustart_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
menusettings_text = menu_font.render("Settings", True, "Black")
settings_button = menusettings_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
menuexit_text = menu_font.render("Exit", True, "Black")
exit_button = menuexit_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT*3/4))
def showMainMenu():
    screen.blit(mainmenu_surface, (0, 0)) 
    pygame.draw.rect(screen, "White", mainmenu_widget)
    pygame.draw.rect(screen, "Black", mainmenu_widget, 1, 3)
    screen.blit(mainmenu_text, mainmenu_widget)
    pygame.draw.rect(screen, "White", start_button) 
    pygame.draw.rect(screen, "Black", start_button, 1, 3)
    screen.blit(menustart_text, start_button)
    pygame.draw.rect(screen, "White", settings_button) 
    pygame.draw.rect(screen, "Black", settings_button, 1, 3)
    screen.blit(menusettings_text, settings_button)
    pygame.draw.rect(screen, "White", exit_button) 
    pygame.draw.rect(screen, "Black", exit_button, 1, 3)
    screen.blit(menuexit_text, exit_button)

# Settings Menu
settingsmenu_surface = pygame.image.load("graphics/settingsgear.png")
settingsmenu_surface = pygame.transform.smoothscale(settingsmenu_surface, screen.get_size())
settings_text = menu_titlefont.render("Settings", True, "Black")
settings_widget = settings_text.get_rect(midtop = (SCREEN_WIDTH/2, 0))
fullscreen_text = menu_font.render("Toggle Fullscreen", True, "Black")
fullscreen_button = fullscreen_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
return_text = menu_font.render("<--Return", True, "Black")
return_button = return_text.get_rect(topleft = (0,0))
def showSettingsMenu():
    screen.blit(settingsmenu_surface, (0,0))
    pygame.draw.rect(screen, "White", settings_widget)
    pygame.draw.rect(screen, "Black", settings_widget, 1, 3)
    screen.blit(settings_text, settings_widget)
    pygame.draw.rect(screen, "White", fullscreen_button) 
    pygame.draw.rect(screen, "Black", fullscreen_button, 1, 3)
    screen.blit(fullscreen_text, fullscreen_button)
    pygame.draw.rect(screen, "White", return_button) 
    pygame.draw.rect(screen, "Black", return_button, 1, 3)
    screen.blit(return_text, return_button)

# Start/Login menu
startmenu_surface = pygame.image.load("graphics/login.png")
startmenu_surface = pygame.transform.smoothscale(startmenu_surface, screen.get_size())
start_text = menu_titlefont.render("Login/Signup", True, "Black")
start_widget = start_text.get_rect(midtop = (SCREEN_WIDTH/2, 0))
login_text = menu_font.render("Login", True, "Black")
login_button = login_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
signup_text = menu_font.render("Signup", True, "Black")
signup_button = signup_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
def showLoginMenu():
    screen.blit(startmenu_surface, (0,0))
    pygame.draw.rect(screen, "White", start_widget) 
    pygame.draw.rect(screen, "Black", start_widget, 1, 3)
    screen.blit(start_text, start_widget)
    pygame.draw.rect(screen, "White", login_button) 
    pygame.draw.rect(screen, "Black", login_button, 1, 3)
    screen.blit(login_text, login_button)
    pygame.draw.rect(screen, "White", signup_button) 
    pygame.draw.rect(screen, "Black", signup_button, 1, 3)
    screen.blit(signup_text, signup_button)
    pygame.draw.rect(screen, "White", return_button) 
    pygame.draw.rect(screen, "Black", return_button, 1, 3)
    screen.blit(return_text, return_button)

run = True
# 0 = main menu
# 1 = settings menu
# 2 = start/login menu
state = 0 
while run:

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if state == 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("START")
                    state = 2
                elif settings_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("SETTINGS")
                    state = 1
                elif exit_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("EXIT")
                    run = False
        if state == 1:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if fullscreen_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("FULLSCREEN")
                elif return_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("RETURN")
                    state = 0
        if state == 2:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("RETURN")
                    state = 0
                elif login_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("LOGIN")
                elif signup_button.collidepoint(mouse_pos):
                    button_sound.play()
                    print("SIGNUP")

    if state == 0:
        showMainMenu()
    elif state == 1:
        showSettingsMenu()
    elif state == 2:
        showLoginMenu()

    pygame.display.update()
    clock.tick(60)

pygame.quit()  
sys.exit()



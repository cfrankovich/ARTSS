import pygame
import os
#full_path = os.path.abspath("mainmenu.png")

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('ARTSS')
clock = pygame.time.Clock()

menu_font = pygame.font.Font(None, 40)
# Main Menu

mainmenu = pygame.image.load("graphics/mainmenu.png")
mainmenu_text = menu_font.render("Air Runway and Taxiway Simulation System", True, "Black")
menustart_text = menu_font.render("Start", True, "Black")
start_button = menustart_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
menusettings_text = menu_font.render("Settings", True, "Black")
settings_button = menusettings_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
menuexit_text = menu_font.render("Exit", True, "Black")
exit_button = menuexit_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT*3/4))
def showMainMenu():
    screen.blit(mainmenu, (0, 0)) 
    screen.blit(mainmenu_text, (SCREEN_WIDTH/5, 0))
    pygame.draw.rect(screen, "White", start_button) 
    pygame.draw.rect(screen, "Black", start_button, 1, 3)
    screen.blit(menustart_text, start_button)
    pygame.draw.rect(screen, "White", settings_button) 
    pygame.draw.rect(screen, "Black", settings_button, 1, 3)
    screen.blit(menusettings_text, settings_button)
    pygame.draw.rect(screen, "White", exit_button) 
    pygame.draw.rect(screen, "Black", exit_button, 1, 3)
    screen.blit(menuexit_text, exit_button)

# Settings
settingsmenu = pygame.image.load("graphics/settingsgear.png")
settings_text = menu_font.render("Settings", True, "Black")
fullscreen_text = menu_font.render("Toggle Fullscreen", True, "Black")
fullscreen_button = fullscreen_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
return_text = menu_font.render("<--Return", True, "Black")
return_button = return_text.get_rect(topleft = (0,0))
def showSettings():
    screen.blit(settingsmenu, (0,0))
    screen.blit(settings_text, (SCREEN_WIDTH/2.5, 0))
    pygame.draw.rect(screen, "White", fullscreen_button) 
    pygame.draw.rect(screen, "Black", fullscreen_button, 1, 3)
    screen.blit(fullscreen_text, fullscreen_button)
    pygame.draw.rect(screen, "White", return_button) 
    pygame.draw.rect(screen, "Black", return_button, 1, 3)
    screen.blit(return_text, return_button)

run = True

# 0 = main menu
# 1 = settings
state = 0 
while run:

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if state == 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse_pos):
                    print("START")
                elif settings_button.collidepoint(mouse_pos):
                    print("SETTINGS")
                    state = 1
                elif exit_button.collidepoint(mouse_pos):
                    print("EXIT")
                    run = False
        if state == 1:
            # main menu state stuff
            pass

    if state == 0:
        showMainMenu()
    elif state == 1:
        showSettings()
 
    pygame.display.update()
    clock.tick(60)

pygame.quit()  



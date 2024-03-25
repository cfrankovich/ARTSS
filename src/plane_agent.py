import pygame
import math

class Plane(pygame.sprite.Sprite):
    def __init__(self, flightnum, screen, x, y):
       super().__init__() 
       self.image = pygame.image.load("graphics/plane.png")
       self.rect = self.image.get_rect() 
       self.rect.x = x
       self.rect.y = y
       self.mask = pygame.mask.from_surface(self.image)

       self.screen = screen
       self.flightnumber = flightnum

    def move(self, dx, dy):

        self.rect.x += dx
        self.rect.y += dy
      
        rot_plane = self.rot_center(self.image, self.rot_direction(dx, dy))
        return rot_plane
    
    def rot_direction(self, dx, dy):
        new_angle = 0
        if (dx > 0):      
            new_angle = 0 + (math.atan(-dy/dx) * 180 / math.pi)
        elif(dx < 0):
            new_angle = 180 + (math.atan(-dy/dx) * 180 / math.pi)
        elif(dx == 0 and dy < 0):
            new_angle = 90
        elif(dx == 0 and dy > 0):
            new_angle = -90
        return new_angle
    
    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
       
    def update(self, dx, dy):
        planefont = pygame.font.Font(None, 25)
        planetext = planefont.render(self.flightnumber, True, "Blue")
        rotated_plane = self.move(dx, dy)
        self.screen.blit(rotated_plane, rotated_plane.get_rect(center = self.rect.center))
        self.screen.blit(planetext, rotated_plane.get_rect(center = self.rect.center))
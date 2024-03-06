import pygame
import math

class Plane(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
       super().__init__() 
       self.color = color
       self.image = pygame.Surface([width, height])
       self.image.fill(color)
       self.image = pygame.image.load("graphics/plane.png")
       self.rect = self.image.get_rect() 
       self.rect.x = 800
       self.rect.y = 400

    def move(self, dx, dy):

        self.rect.x += dx
        self.rect.y += dy
      
        rot_plane = self.rot_center(self.image, self.rot_direction(dx, dy))
        return rot_plane
    
    def rot_direction(self, dx, dy):
        new_angle = 0
        if (dy < 0 and dx > 0):      
            new_angle = 0 + (math.atan(dy/dx) * 180 / math.pi)
        elif (dy < 0 and dx < 0):
            new_angle = 0 + (math.atan(dy/dx) * 180 / math.pi)
        elif(dy > 0 and dx > 0):       
            new_angle = -90 - (math.atan(dy/dx) * 180 / math.pi)
        elif(dy > 0 and dx < 0):
            new_angle = 180 + (math.atan(dy/dx) * 180 / math.pi)
        return new_angle
    
    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
       
        
import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, screen, x, y):
       super().__init__() 
       self.image = pygame.image.load("graphics/explosion.png")
       screen_width, screen_height = screen.get_size()
       self.explosion = pygame.transform.smoothscale(self.image, (screen_width/12, screen_height/8))
       self.rect = self.image.get_rect() 
       self.rect.x = x
       self.rect.y = y
      
       self.screen = screen

    def update(self):
        pass

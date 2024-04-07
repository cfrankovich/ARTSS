import pygame

class MessageBox(pygame.sprite.Sprite):
    def __init__(self, width, height, top_x, top_y, screen, text, color):
       super().__init__() 

       self.image = pygame.Surface([width, height])
       self.image.set_alpha(0)
       self.rect = pygame.Rect((top_x, top_y), (width, height))

       self.text = text
       self.screen = screen
       self.color = color

    def draw_text(self, surface, text, rect, font, aa=False, bkg=None):
        rect = pygame.Rect(rect)
        y = rect.top
        lineSpacing = -2
        fontHeight = font.size("Tg")[1]

        while text:
            i = 1
            if y + fontHeight > rect.bottom:
                break

            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1
        
            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1
            if bkg:
                image = font.render(text[:i], 1, self.color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, self.color)
            image.set_alpha(127)
            surface.blit(image, (rect.left, y))
            y += fontHeight + lineSpacing
            text = text[i:]

        return text

    def draw_rect_alpha(self, surface, rect):
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, self.color, shape_surf.get_rect(), 3, 3)
        surface.blit(shape_surf, rect)

    def draw_borders_and_text(self):
        message_font = pygame.font.Font(None, 25)
        self.draw_rect_alpha(self.screen, self.rect)
        self.draw_text(self.screen, self.text, self.rect, message_font, True)

    def update(self, dy):
        self.rect = self.rect.move(0, dy)
        self.draw_borders_and_text()
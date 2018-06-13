import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self, x , y, width = 32, height = 32):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color(255, 0, 0)

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 1)

import pygame

class Block:
    def __init__(self, x , y, width = 32, height = 32):
        self.rect = (x, y, width, height)
        self.color = pygame.Color(50, 0, 0)

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

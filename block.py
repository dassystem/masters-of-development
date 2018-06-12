import pygame


class Block:
    def __init__(self, x , y):
        self.width=32
        self.height=32
        self.rect = (x, y, self.width, self.height)

    def render(self, window):
        pygame.draw.rect(window, (50,0,0), self.rect)

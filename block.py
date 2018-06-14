import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self, x , y, width = 32, height = 32):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        
        self.__rect = pygame.Rect(x, y, width, height)
        self.__color = pygame.Color(255, 0, 0)
    
    def get_rect(self):
        return self.__rect

    def render(self, surface):
        pygame.draw.rect(surface, self.__color, self.__rect, 1)

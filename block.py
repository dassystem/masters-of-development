import pygame


class Block(pygame.sprite.Sprite):
    BLOCK_WIDTH = 32
    BLOCK_HEIGHT = 32
    
    def __init__(self, level, x , y, width = BLOCK_WIDTH, height = BLOCK_HEIGHT):
        # call the parent class (Sprite) constructor
        super(Block, self).__init__()

        self.__level = level
        self.__rect = pygame.Rect(x, y, width, height)
        self.__color = pygame.Color(255, 0, 0)
    
    def get_rect(self):
        return self.__rect

    def get_level(self):
        return self.__level

    def render(self, surface):
        pygame.draw.rect(surface, self.__color, self.__rect, 1)

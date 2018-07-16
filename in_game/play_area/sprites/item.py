import pygame
import random

class Item(pygame.sprite.Sprite):
    def __init__(self, block):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Item, self).__init__()
        self.__block = block
        
        self.rect = self.image.get_rect()
        self.rect.bottom = self.__block.rect.top
        
        r = random.randint(0, 3)
        
        if r == 1:
            self.rect.left = self.__block.rect.left
        elif r == 2:
            self.rect.midbottom = self.__block.rect.midtop
        else:
            self.rect.right = self.__block.rect.right
        
        self.__block.add_item(self)
        
    def update(self):
        # items scroll with their block, get killed by their block
        self.rect = self.image.get_rect(bottom = self.__block.rect.top, x = self.rect.x)

    def on_collide(self, player, score):
        pass

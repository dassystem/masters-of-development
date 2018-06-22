import pygame

class Block(pygame.sprite.Sprite):
    """A sprite representing a block. Contains the block level."""
    BLOCK_WIDTH = 32
    BLOCK_HEIGHT = 32
    
    def __init__(self, level, x , y, width = BLOCK_WIDTH, height = BLOCK_HEIGHT):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Block, self).__init__()

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        self.image = pygame.Surface((width, height))
        self.image.fill(pygame.Color(255, 0, 0))
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect(x = x, y = y)
        self.__level = level
    
    def get_level(self):
        """Gets the level of this block. Used to calculate the score when a player reaches a higher block"""
        return self.__level

    def update(self, scroll_velocity, surface_height):
        """Updates the block for moving down while scrolling the play area.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        self.rect.y += scroll_velocity
        
        # delete blocks offscreen
        if self.rect.top >= surface_height:
            self.kill()

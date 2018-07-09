import pygame
import string
import random
from masters_of_development import MastersOfDevelopment

class Block(pygame.sprite.Sprite):
    """A sprite representing a block. Contains the block level."""
    BLOCK_WIDTH = 32
    BLOCK_HEIGHT = 32
    
    words = {
        2: ["&&", "||", "if", "in", "+=", "-=", "*=", "or"],
        3: ["abs", "and", "def", "END", "i++", "i--", "int", "for", "GET", "JMP", "LDA", "not", "sys", "REM", "RUN", "STA", "try", "val", "var"],
        4: ["char", "elif", "else", "from", "GOTO", "into", "join", "main", "LOAD", "LIST","long", "PEEK", "POKE", "SAVE", "self", "THEN", "this", "True", "None", "null"],
        5: ["begin", "break", "catch", "class", "False", "float", "GOSUB", "import", "INPUT", "print", "short", "super", "where", "while"],
        6: ["double", "import", "random", "public", "select", "static", "string", "switch"],
        7: ["boolean", "declare", "numeric", "private", "varchar"],
        8: ["__name__", "continue", "varchar2", "volatile"],
        9: ["exception", "interface", "protected", "transient"]
    }
    
    def __init__(self, font, level, x , y, width = BLOCK_WIDTH, height = BLOCK_HEIGHT):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Block, self).__init__()

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        #self.image = pygame.Surface((width, height))
        #self.image.fill(pygame.Color(255, 0, 0))
        
        letters = width // 25
        s = ""
        
        if letters >= 2 and letters <= 9:
            s = random.choice(Block.words[letters])
        else:
            for i in range(0, letters):
                s += random.choice(string.ascii_letters)
        
        self.image = font.render(s, True, MastersOfDevelopment.LIGHT_GRAY)
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect(x = x, y = y)
        self.__level = level
        self.__item = None
    
    def get_level(self):
        """Gets the level of this block. Used to calculate the score when a player reaches a higher block"""
        return self.__level

    def add_item(self, item):
        self.__item = item

    def update(self, scroll_velocity, surface_height):
        """Updates the block for moving down while scrolling the play area. Kills itself if moving out of surface.
           
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        self.rect.y += scroll_velocity
        
        # delete blocks offscreen
        if self.rect.top >= surface_height:
            self.kill()
                
    def kill(self):
        """Kills any score item.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.kill
        """
        if self.__item is not None:
            self.__item.kill()
            
        super().kill()
        
    def on_collide(self, player, score):
        uplevel = player.set_on_block(self)
            
        if uplevel > 0:
            score.add_platform_score(uplevel)
            player.set_score(score.get_score())

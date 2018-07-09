import pygame
import string
import random
from masters_of_development import MastersOfDevelopment

class Block(pygame.sprite.Sprite):
    """A sprite representing a block. Contains the block level."""
    BLOCK_WIDTH = 32
    BLOCK_HEIGHT = 32
    
    KEYWORD_COLOR = MastersOfDevelopment.LIGHT_GRAY
    #KEYWORD_COLOR = pygame.Color(81, 86, 88)
    # Eclipse Photon Dark Theme Comment Color
    #KEYWORD_COLOR = pygame.Color(88, 96, 92)
    
    words = {
        2: ["as", "if", "in", "is", "or"],
        3: ["and", "def", "del", "for", "not"],
        4: ["elif", "from", "pass", "None", "True", "try:", "with"],
        5: ["a % 2", "del b", "break", "class", "else:", "False", "raise", "while", "yield"],
        6: ["i += 1", "x == y", "s = \"\"", "len(d)", "import", "lambda", "return", "i = 42", "str(i)", "# TODO"],
        7: ["finally", "next(g)", "d = {}", "l  = []", "type(x)", "# FIXME", "except:"],
        8: ["continue", "nonlocal", "print(i)", "d.copy()", "d.clear()", "global a"],
        9 : ["self.rect", "d.clear()", "if x < 0:", "f.__doc__"],
        10: ["import sys", "print d[k]", "d.values()", "l2 = l1[:]", "f(*t, **d)", "@decorator", "f.__name__"],
        11: ["for k in d:", "print s[-1]", "import math", "a, b = 0, 1"],
        12: ["s.center(10)", "f.__module__", "@wraps(func)"],
        13: ["import random", "t = (1, 2, 3)", "while i <= n:", "pygame.init()", "pygame.quit()"],
        14: ["super().kill()", "def f(**args):"],
        15: ["# We are hiring", "# www.tarent.de"],
        16: ["lambda x: x + 42"],
        17: ["self.rect.x += dx", "self.rect.y += dy", "math.cos(math.pi)"],
        18: ["def __str__(self):", "s.format(\"0:d\", i)", "def f(): return 42", "f = 9 * c / 5 + 32"]
    }
    
    def __init__(self, font, level, x , y, width = BLOCK_WIDTH, height = BLOCK_HEIGHT):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Block, self).__init__()

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        #self.image = pygame.Surface((width, height))
        #self.image.fill(pygame.Color(255, 0, 0))
        
        letters = width // 25
        s = ""
        
        if letters in Block.words:
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

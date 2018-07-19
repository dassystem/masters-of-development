import keyword
import pygame
import random
import re
import string

from colors import DARKER_GRAY, LIGHT_GRAY, WHITE
from constants import PIXEL_PER_SECOND

class Block(pygame.sprite.Sprite):
    """A sprite representing a block. Contains the block level."""
    BLOCK_WIDTH = 32
    BLOCK_HEIGHT = 32

    KEYWORD_COLOR = pygame.Color(204, 108, 29)
    NAME_COLOR = pygame.Color(100, 220, 242)
    FUNCTION_COLOR = pygame.Color(164, 231, 33)
    #KEYWORD_COLOR = pygame.Color(81, 86, 88)
    # Eclipse Photon Dark Theme Comment Color
    #KEYWORD_COLOR = pygame.Color(88, 96, 92)

    words = {
        2: ["as", "if", "in", "is", "or"],
        3: ["and", "def", "del", "for", "not"],
        4: ["from", "pass", "None", "True", "try:", "with"],
        5: ["a % 2", "del b", "break", "class", "elif:", "else:", "False", "raise", "while", "yield"],
        6: ["i += 1", "x == y", "s = \"\"", "len(d)", "import", "lambda", "return", "i = 42", "str(i)", "# TODO"],
        7: ["finally", "next(g)", "d = {}", "l  = []", "type(x)", "# FIXME", "except:"],
        8: ["continue", "nonlocal", "print(i)", "d.copy()", "d.clear()", "global a"],
        9: ["self.rect", "d.clear()", "if x < 0:", "f.__doc__"],
        10: ["import sys", "print(d[k])", "d.values()", "l2 = l1[:]", "f(*t, **d)", "@decorator", "f.__name__"],
        11: ["for k in d:", "print(s[-1])", "import math", "a, b = 0, 1"],
        12: ["s.center(10)", "f.__module__", "@wraps(func)"],
        13: ["import random", "t = (1, 2, 3)", "while i <= n:", "pygame.init()", "pygame.quit()"],
        14: ["super().kill()", "def f(**args):"],
        15: ["# We are hiring", "# www.tarent.de"],
        16: ["lambda x: x + 42"],
        17: ["self.rect.x += dx", "self.rect.y += dy", "math.cos(math.pi)"],
        18: ["def __str__(self):", "s.format(\"0:d\", i)", "def f(): return 42", "f = 9 * c / 5 + 32"]
    }

    operators = ["=", "==", ">=", "<=", "+=", "-=", "*=", "%", "-", "+", "<", ">", "(", ")", "[", "]", "{", "}"]

    def __init__(self, font, level, x, y, width=BLOCK_WIDTH, height=BLOCK_HEIGHT):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Block, self).__init__()

        self.__font = font

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        #self.image = pygame.Surface((width, height))
        #self.image.fill(pygame.Color(255, 0, 0))

        letters = width // 25
        self.__line = ""

        if letters in Block.words:
            self.__line = random.choice(Block.words[letters])
        else:
            for i in range(0, letters):
                self.__line += random.choice(string.ascii_letters)

        color = WHITE
        split = True

        if self.__line.startswith("#"):
            color = LIGHT_GRAY
            split = False
        elif self.__line.startswith("@"):
            color = LIGHT_GRAY
            split = False
        elif self.__line in keyword.kwlist:
            color = Block.KEYWORD_COLOR
            split = False

        self.image = font.render(self.__line, True, color)

        if split:
            parts = []

            self.__inspect_line(self.__line, " ", parts, 0)

            self.image.fill(DARKER_GRAY)

            for part in parts:
                self.image.blit(part[1], part[0])

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect(x=x, y=y)
        #pygame.draw.rect(self.image, MastersOfDevelopment.WHITE, pygame.Rect(0, 0, self.rect.width, self.rect.height), 1)
        self.__level = level
        self.__item = None
        #print("new block level {0}, image {1}, rect {2}, line {3}".format(self.__level, self.image, self.rect, self.__line))

    def __inspect_line(self, line, separator, global_parts, x, override_color=None):
        split = line.split(separator)

        for i, s in enumerate(split):
            if s in keyword.kwlist:
                color = Block.KEYWORD_COLOR
            elif s in Block.operators:
                color = WHITE
            elif "." in s:
                x = self.__inspect_line(s, ".", global_parts, x)
                continue
            else:
                match = re.match(r"(.*?)([\(\[\{])(.*)([\)\]\}])", s)

                if match:
                    override_color = None
                    for j, group in enumerate(match.groups()):
                        if j == 0:
                            override_color = Block.FUNCTION_COLOR
                        else:
                            override_color = None

                        x = self.__inspect_line(group, " ", global_parts, x, override_color)

                    if len(split) > 1 and i < len(split):
                        separator_part = self.__render_part(separator, WHITE, x)
                        global_parts.append(separator_part)

                        x += separator_part[1].get_width()
                    continue
                elif override_color is not None:
                    color = override_color
                else:        
                    color = Block.NAME_COLOR

            part = self.__render_part(s, color, x)

            global_parts.append(part)

            x += part[1].get_width()

            if len(split) > 1 and i < len(split):
                separator_part = self.__render_part(separator, WHITE, x)
                global_parts.append(separator_part)

                x += separator_part[1].get_width()

        return x

    def __render_part(self, s, color, x):
        part_image = self.__font.render(s, True, color)
        part_rect = part_image.get_rect().copy()
        part_rect.x += x

        return (part_rect, part_image)

    def get_level(self):
        """Gets the level of this block. Used to calculate the score when a player reaches a higher block"""
        return self.__level

    def add_item(self, item):
        self.__item = item

    def update(self, scroll_velocity, surface_height, seconds):
        """Updates the block for moving down while scrolling the play area. Kills itself if moving out of surface.

           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        self.rect.y += scroll_velocity * round(PIXEL_PER_SECOND * seconds)

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

import pygame

from colors import LIGHT_GRAY
from constants import PIXEL_PER_SECOND
from pygame.font import Font
from pygame.sprite import Sprite
from typing import Dict


class LineNumber(Sprite):
    def __init__(self, number: int, y: int, right: int, fonts: Dict[str, Font]):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(LineNumber, self).__init__()

        self.__number = number
        self.__fonts = fonts

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        self.image = fonts["big"].render("{0:>3s}".format(str(number)), True, LIGHT_GRAY)

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect()
        self.rect.right = right
        self.rect.y = y

    def update(self, scroll_velocity: int, surface_height: int, seconds: int) -> None:
        """Updates the line number for moving down while scrolling the play area. Kills itself if moving out of surface.

           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        self.rect.y += scroll_velocity * round(PIXEL_PER_SECOND * seconds)

        # delete line number offscreen
        if self.rect.top >= surface_height:
            self.kill()

    def get_number(self) -> int:
        return self.__number

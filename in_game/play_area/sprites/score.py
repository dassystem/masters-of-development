import pygame

from colors import WHITE

class Score(pygame.sprite.Sprite):
    """A sprite representing the score display."""
    PLATFORM_LEVEL_SCORE = 100
    
    def __init__(self, font, sound):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Score, self).__init__()
        self.__font = font
        self.__sound = sound
        self.__score = 0
        self.__dirty = True

    def reset(self):
        self.__score = 0
        self.__dirty = True
        
    def update(self, target_surface):
        """Updates the score display. Does nothing if score hasn't changed..
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__dirty:
            return
        
        self.image = self.__font.render("{0:d}".format(self.__score), True, WHITE)

        self.rect = self.image.get_rect(topleft = (target_surface.get_width() // 2, 5))
        
        self.__dirty = False
    
    def add_platform_score(self, uplevel):
        """Adds a score for achiving a higher block."""
        self.add_score(uplevel * Score.PLATFORM_LEVEL_SCORE)
        
    def add_score(self, score):
        """Adds a score."""
        self.__score += score
        self.__dirty = True
        self.__sound.play()
    
    def get_score(self):
        """Gets the current score (number)."""
        return self.__score

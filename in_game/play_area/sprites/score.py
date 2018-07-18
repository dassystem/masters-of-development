from colors import WHITE
from commons.text_sprite import TextSprite

class Score(TextSprite):
    """A sprite representing the score display."""
    PLATFORM_LEVEL_SCORE = 100
    
    def __init__(self, initial_pos, font, sound):
        self.__sound = sound
        self.__score = 0
        super(Score, self).__init__(initial_pos, self. __get_score_text(), font, WHITE)

    def reset(self):
        self.__score = 0
        super().update(self.__get_score_text())
    
    def add_platform_score(self, uplevel):
        """Adds a score for achiving a higher block."""
        self.add_score(uplevel * Score.PLATFORM_LEVEL_SCORE)
        
    def add_score(self, score):
        """Adds a score."""
        self.__score += score
        super().update(self.__get_score_text())
        self.__sound.play()
    
    def get_score(self):
        """Gets the current score (number)."""
        return self.__score

    def __get_score_text(self):
        return "{0:d}".format(self.__score)

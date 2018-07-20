from colors import WHITE
from commons.text_sprite import TextSprite
from pygame.font import Font
from pygame.mixer import Sound
from typing import Tuple


class Score(TextSprite):
    """A sprite representing the score display."""
    PLATFORM_LEVEL_SCORE: int = 100

    def __init__(self, initial_pos: Tuple[int, int], font: Font, sound: Sound) -> None:
        self.__sound = sound
        self.__score = 0
        super(Score, self).__init__(initial_pos, self. __get_score_text(), font, WHITE)

    def reset(self) -> None:
        self.__score = 0
        super().update(self.__get_score_text())

    def add_platform_score(self, uplevel: int) -> None:
        """Adds a score for achiving a higher block."""
        self.add_score(uplevel * Score.PLATFORM_LEVEL_SCORE)

    def add_score(self, score: int) -> None:
        """Adds a score."""
        self.__score += score
        super().update(self.__get_score_text())
        self.__sound.play()

    def get_score(self) -> int:
        """Gets the current score (number)."""
        return self.__score

    def __get_score_text(self) -> str:
        return "{0:d}".format(self.__score)

from in_game.play_area.sprites.item import Item
from pygame import Surface
from typing import Dict


class Coin(Item):
    """A sprite representing a collectable extra score item."""

    def __init__(self, images: Dict[str, Surface], block: "in_game.play_area.sprites.block.Block"):
        self.image = images["coin"]

        self.__score = 500

        # IMPORTANT: call the parent class (Sprite) constructor
        super(Coin, self).__init__(block)

    def get_score(self) -> int:
        return self.__score

    def on_collide(
            self, player: "in_game.play_area.sprites.player.Player", score: "in_game.play_area.sprites.score.Score"):
        score.add_score(self.get_score())
        player.set_score(score.get_score())

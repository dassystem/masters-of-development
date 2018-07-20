from in_game.play_area.sprites.item import Item
from in_game.play_area.sprites.power_up_shield import PowerUpShield
from pygame import Surface
from typing import Dict


class Bug(Item):
    def __init__(self, images: Dict[str, Surface], block: "in_game.play_area.sprites.block.Block") -> None:
        self.image = images["bug"]
        self.__score = -500

        super(Bug, self).__init__(block)

    def get_score(self) -> int:
        return self.__score

    def on_collide(
            self,
            player: "in_game.play_area.sprites.player.Player",
            score: "in_game.play_area.sprites.score.Score") -> None:
        power_ups = player.get_power_ups()

        if PowerUpShield.NAME in power_ups:
            bug_resistant = power_ups[PowerUpShield.NAME]

            if len(bug_resistant) > 0:
                return

        score.add_score(self.get_score())
        player.set_score(score.get_score())

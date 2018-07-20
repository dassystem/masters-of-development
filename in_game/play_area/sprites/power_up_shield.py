from in_game.play_area.sprites.power_up import PowerUp
from pygame import Surface
from typing import Dict


class PowerUpShield(PowerUp):
    NAME = "power_up_shield"

    def __init__(
            self,
            images: Dict[str, Surface],
            block: "in_game.play_area.sprites.block.Block",
            block_area: "in_game.play_area.block_area.BlockArea") -> None:
        self.image = images[PowerUpShield.NAME]
        super(PowerUpShield, self).__init__(PowerUpShield.NAME, block, block_area)

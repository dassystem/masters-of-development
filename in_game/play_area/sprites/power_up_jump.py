from in_game.play_area.sprites.power_up import PowerUp
from pygame import Surface
from typing import Dict


class PowerUpJump(PowerUp):
    NAME = "power_up_jump"

    def __init__(
            self,
            images: Dict[str, Surface],
            block: "in_game.play_area.sprites.block.Block",
            block_area: "in_game.play_area.block_area.BlockArea"):
        self.image = images["power_up_jump_height"]
        super(PowerUpJump, self).__init__(PowerUpJump.NAME, block, block_area)

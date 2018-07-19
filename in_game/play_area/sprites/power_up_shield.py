from in_game.play_area.sprites.power_up import PowerUp


class PowerUpShield(PowerUp):
    NAME = "power_up_shield"

    def __init__(self, images, block, block_area):
        self.image = images[PowerUpShield.NAME]
        super(PowerUpShield, self).__init__(PowerUpShield.NAME, block, block_area)

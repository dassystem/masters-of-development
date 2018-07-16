from in_game.play_area.sprites.power_up import PowerUp

class PowerUpShield(PowerUp):
    def __init__(self, images, block, block_area):
        self.image = images["power_up_shield"]
        super(PowerUpShield, self).__init__("power_up_shield", block, block_area)

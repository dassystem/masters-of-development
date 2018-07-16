from in_game.play_area.sprites.power_up import PowerUp

class PowerUpJump(PowerUp):
    def __init__(self, images, block, block_area):
        self.image = images["power_up_jump_height"]
        super(PowerUpJump, self).__init__("power_up_jump", block, block_area)

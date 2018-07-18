from in_game.play_area.sprites.item import Item
from in_game.play_area.sprites.power_up_shield import PowerUpShield

class Bug(Item):
    def __init__(self, images, block):
        self.image = images["bug"]
        self.__score = -500
        
        super(Bug, self).__init__(block)

    def get_score(self):
        return self.__score

    def on_collide(self, player, score):
        power_ups = player.get_power_ups()
        
        if PowerUpShield.NAME in power_ups:
            bug_resistant = power_ups[PowerUpShield.NAME]
            
            if len(bug_resistant) > 0:
                return
        
        score.add_score(self.get_score())
        player.set_score(score.get_score())

from in_game.play_area.sprites.item import Item

class Coin(Item):
    """A sprite representing a collectable extra score item."""

    def __init__(self, images, block):
        self.image = images["coin"]

        self.__score = 500

        # IMPORTANT: call the parent class (Sprite) constructor
        super(Coin, self).__init__(block)

    def get_score(self):
        return self.__score

    def on_collide(self, player, score):
        score.add_score(self.get_score())
        player.set_score(score.get_score())

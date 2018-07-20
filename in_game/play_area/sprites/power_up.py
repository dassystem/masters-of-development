from in_game.play_area.event_handlers.power_up_timer_elapsed_event_handler import PowerUpTimerElapsedEventHandler
from in_game.play_area.sprites.item import Item
from in_game.play_area.sprites.score import Score
from utils.timer import Timer


class PowerUp(Item):
    def __init__(
            self,
            name: str,
            block: "in_game.play_area.sprites.block.Block",
            block_area: "in_game.play_area.block_area.BlockArea",
            active_seconds: int=5) -> None:
        self.__name = name
        self.__block_area = block_area
        self.__active_seconds = active_seconds

        self.__timer = None
        self.__event_handlers = []

        # IMPORTANT: call the parent class (Sprite) constructor
        super(PowerUp, self).__init__(block)

    def get_name(self) -> str:
        return self.__name

    def get_timer(self) -> Timer:
        return self.__timer

    def on_collide(self, player: "in_game.play_area.sprites.playerPlayer", score: Score) -> None:
        player.add_power_up(self)

        self.__timer = Timer("powerup", self.__active_seconds)

        self.__event_handlers = []
        self.__event_handlers.append(self.__timer.get_event_handler())

        screen = self.__block_area.get_play_area().get_screen()

        self.__event_handlers.append(
            PowerUpTimerElapsedEventHandler(screen, self))

        for event_handler in self.__event_handlers:
            screen.add_event_handler(event_handler)

        self.__timer.start()

    def deactivate(self) -> None:
        self.__block_area.get_play_area().get_player().remove_power_up(self)
        self.__timer.stop()
        self.__timer = None

        for event_handler in self.__event_handlers:
            self.__block_area.get_play_area().get_screen().remove_event_handler(event_handler)

        self.__event_handlers = []
        self.kill()

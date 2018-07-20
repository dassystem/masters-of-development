import utils.timer

from pygame.event import Event
from screens.base import BaseScreenEventHandler
from utils.timer import Timer

class InGameScreenTimerElapsedEventHandler(BaseScreenEventHandler):
    """Event handler that sets all players dead if a timer is elapsed."""
    def __init__(self, in_game_screen: "in_game.screen.screen.InGameScreen", timer: Timer):
        super(InGameScreenTimerElapsedEventHandler, self).__init__(in_game_screen)
        self.__timer = timer

    def can_handle(self, event: Event) -> bool:
        if not super().can_handle(event):
            return False

        return event.type == utils.timer.ELAPSED_EVENT and event.timer == self.__timer

    def handle_event(self, event: Event) -> None:
        for player in self.get_screen().get_players():
            player.set_dead()

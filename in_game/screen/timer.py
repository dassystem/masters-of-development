import utils.timer

from screens.base import BaseScreenEventHandler

class InGameScreenTimerElapsedEventHandler(BaseScreenEventHandler):
    """Event handler that sets all players dead if a timer is elapsed."""
    def __init__(self, in_game_screen, timer):
        super(InGameScreenTimerElapsedEventHandler, self).__init__(in_game_screen)
        self.__timer = timer

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        return event.type == utils.timer.ELAPSED_EVENT and event.timer == self.__timer

    def handle_event(self, event):
        for player in self.get_screen().get_players():
            player.set_dead()

import utils

from screens.base import BaseScreenEventHandler

class PowerUpTimerElapsedEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, power_up):
        super(PowerUpTimerElapsedEventHandler, self).__init__(in_game_screen)
        self.__power_up = power_up
        
    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == utils.timer.ELAPSED_EVENT and event.timer == self.__power_up.get_timer()
    
    def handle_event(self, event):
        self.__power_up.deactivate()

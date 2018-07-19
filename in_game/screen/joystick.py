import utils.joysticks

from screens.base import BaseScreenEventHandler

class ScreenJoystickEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, play_areas):
        super(ScreenJoystickEventHandler, self).__init__(in_game_screen)
        self.__play_areas = play_areas

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        if not utils.joysticks.is_button_down(event):
            return False

        active_keyboard = False
        for play_area in self.get_screen().get_play_areas():
            active_keyboard = active_keyboard or play_area.get_keyboard().is_active()

        return (self.get_screen().all_dead() or not self.get_screen().get_timer().is_started()) and not active_keyboard

    def handle_event(self, event):
        self.get_screen().set_active(False)

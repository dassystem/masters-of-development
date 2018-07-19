from screens.base import BaseJoystickEventHandler

class PlayerJoystickEventHandler(BaseJoystickEventHandler):
    """Joystick event handler for a player."""

    def __init__(self, in_game_screen, joystick, player):
        super(PlayerJoystickEventHandler, self).__init__(in_game_screen, joystick)
        self.__player = player

    def _on_up(self, event):
        self.__player.jump()

    def _on_left(self, event):
        self.__player.move_left()

    def _on_right(self, event):
        self.__player.move_right()

    def _on_horizontal_stop(self, event):
        self.__player.stop()

    def _on_button_down(self, event):
        active_keyboard = False
        for play_area in self.get_screen().get_play_areas():
            active_keyboard = active_keyboard or play_area.get_keyboard().is_active()

        if (self.get_screen().all_dead() or not self.get_screen().get_timer().is_started()) and not active_keyboard:
            self.get_screen().set_active(False)
        else:
            self.__player.jump()

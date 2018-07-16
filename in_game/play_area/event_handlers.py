import screens.base
import utils.keyboard

class PlayerJoystickEventHandler(screens.base.BaseJoystickEventHandler):
    """Joystick event handler for a player."""
    
    def __init__(self, in_game_screen, joystick):
        super(PlayerJoystickEventHandler, self).__init__(in_game_screen, joystick)

    def __get_player(self, event):
        """Get the player assigned to the joystick."""
        return utils.Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)
    
    def _on_up(self, event):
        self.__get_player(event).jump()

    def _on_left(self, event):
        self.__get_player(event).move_left()

    def _on_right(self, event):
        self.__get_player(event).move_right()

    def _on__horizontal_stop(self, event):
        self.__get_player(event).stop()

    def _on_button_down(self, event):
        active_keyboard = False
        for play_area in self.__screen.get_play_areas():
            active_keyboard = active_keyboard or play_area.get_keyboard().is_active()
        
        if (self.get_screen().all_dead() or not self.get_screen().get_timer().is_started()) and not active_keyboard:
            self.get_screen().set_active(False)
        else:
            self.__get_player().jump()

class PlayerKeyboardEventHandler(screens.base.BaseKeyboardEventHandler):
    def __init__(self, in_game_screen, key_mappings, player):
        super(PlayerKeyboardEventHandler, self).__init__(in_game_screen, key_mappings)
        self.__player = player

    def can_handle(self, event):
        return super().can_handle(event) and not self.__player.is_dead()

    def handle_event(self, event):
        if utils.keyboard.is_key_down(event):
            if self._key_mappings["up"] == event.key:
                self.__player.jump()
            elif self._key_mappings["left"] == event.key:
                self.__player.move_left()
            elif self._key_mappings["right"] == event.key:
                self.__player.move_right()
        elif utils.keyboard.is_key_up(event):
            if self._key_mappings["left"] == event.key or self._key_mappings["right"] == event.key: 
                self.__player.stop()

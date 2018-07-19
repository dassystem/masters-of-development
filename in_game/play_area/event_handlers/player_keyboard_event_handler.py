import utils.keyboard

from screens.base import BaseKeyboardEventHandler


class PlayerKeyboardEventHandler(BaseKeyboardEventHandler):
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

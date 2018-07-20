import utils.keyboard

from pygame.event import Event
from screens.base import BaseKeyboardEventHandler
from typing import Dict


class PlayerKeyboardEventHandler(BaseKeyboardEventHandler):
    def __init__(
            self,
            in_game_screen: "in_game.screen.screen.InGameScreen",
            key_mappings: Dict[str, int],
            player: "in_game.play_area.sprites.player.Player") -> None:
        super(PlayerKeyboardEventHandler, self).__init__(in_game_screen, key_mappings)
        self.__player = player

    def can_handle(self, event: Event) -> bool:
        return super().can_handle(event) and not self.__player.is_dead()

    def handle_event(self, event: Event) -> None:
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

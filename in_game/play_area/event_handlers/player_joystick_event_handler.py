from pygame.event import Event
from pygame.joystick import Joystick
from screens.base import BaseJoystickEventHandler


class PlayerJoystickEventHandler(BaseJoystickEventHandler):
    """Joystick event handler for a player."""

    def __init__(
            self,
            in_game_screen: "in_game.screen.screen.InGameScreen",
            joystick: Joystick,
            player: "in_game.play_area.sprites.playerPlayer") -> None:
        super(PlayerJoystickEventHandler, self).__init__(in_game_screen, joystick)
        self.__player = player

    def _on_up(self, event: Event) -> None:
        self.__player.jump()

    def _on_left(self, event: Event) -> None:
        self.__player.move_left()

    def _on_right(self, event: Event) -> None:
        self.__player.move_right()

    def _on_horizontal_stop(self, event: Event) -> None:
        self.__player.stop()

    def _on_button_down(self, event: Event) -> None:
        active_keyboard = False
        for play_area in self.get_screen().get_play_areas():
            active_keyboard = active_keyboard or play_area.get_keyboard().is_active()

        if (self.get_screen().all_dead() or not self.get_screen().get_timer().is_started()) and not active_keyboard:
            self.get_screen().set_active(False)
        else:
            self.__player.jump()

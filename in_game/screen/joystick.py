import utils.joysticks

from screens.base import BaseScreenEventHandler
from pygame.event import Event
from typing import List


class ScreenJoystickEventHandler(BaseScreenEventHandler):
    def __init__(
            self,
            in_game_screen: "in_game.screen.screen.InGameScreen",
            play_areas: List["in_game.play_area.play_area.PlayArea"]) -> None:
        super(ScreenJoystickEventHandler, self).__init__(in_game_screen)
        self.__play_areas = play_areas

    def can_handle(self, event: Event) -> bool:
        if not super().can_handle(event):
            return False

        if not utils.joysticks.is_button_down(event):
            return False

        active_keyboard = False
        for play_area in self.get_screen().get_play_areas():
            active_keyboard = active_keyboard or play_area.get_keyboard().is_active()

        return (self.get_screen().all_dead() or not self.get_screen().get_timer().is_started()) and not active_keyboard

    def handle_event(self, event: Event) -> None:
        self.get_screen().set_active(False)

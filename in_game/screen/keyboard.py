import pygame

from screens.base import BaseKeyboardEventHandler

class ScreenKeyboardEventHandler(BaseKeyboardEventHandler):
    def __init__(self, in_game_screen, play_areas):
        super(ScreenKeyboardEventHandler, self).__init__(
            in_game_screen, {"info": pygame.K_i, "next": pygame.K_RETURN}, [pygame.KEYDOWN])
        self.__play_areas = play_areas

    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        active_keyboard = False
        
        for play_area in self.__play_areas:
            active_keyboard = active_keyboard or play_area.get_keyboard().is_active()
        
        return (self.get_screen().all_dead() or not self.get_screen().get_timer().is_started()) and not active_keyboard

    def handle_event(self, event):
        if self._key_mappings["info"] == event.key: 
            for play_area in self.__play_areas:
                play_area.switch_debug()
        elif self._key_mappings["next"] == event.key:
            self.get_screen().set_active(False)

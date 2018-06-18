import pygame
from screens.base import BaseScreen

class GlobalBaseEventHandler:
    def __init__(self, tarent_jumper):
        self._tarent_jumper = tarent_jumper

class GlobalQuitEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper):
        GlobalBaseEventHandler.__init__(self, tarent_jumper)

    def can_handle(self, event):
        return event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def handle_event(self, event):
        if self.can_handle(event):
            self._tarent_jumper.shutdown()

class GlobalSwitchMusicEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper):
        GlobalBaseEventHandler.__init__(self, tarent_jumper)
        
    def can_handle(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_m
    
    def handle_event(self, event):
        if self.can_handle(event):
            self._tarent_jumper.switch_music()

class GlobalScreenDeactivateEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper):
        GlobalBaseEventHandler.__init__(self, tarent_jumper)

    def can_handle(self, event):
        return event.type == BaseScreen.DEACTIVE_SCREEN_EVENT

    def handle_event(self, event):
        self._tarent_jumper.change_screen(event.screen)
        
class GlobalEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper):
        GlobalBaseEventHandler.__init__(self, tarent_jumper)
        self.__handlers = []
        self.__handlers.append(GlobalQuitEventHandler(self._tarent_jumper))
        self.__handlers.append(GlobalSwitchMusicEventHandler(self._tarent_jumper))
        self.__handlers.append(GlobalScreenDeactivateEventHandler(self._tarent_jumper))
        
        for screen in tarent_jumper.get_screens():
            for event_handler in screen.get_event_handlers():
                self.__handlers.append(event_handler)

    def handle_event(self, event):
        handler = None

        for h in self.__handlers:
            if h.can_handle(event):
                handler = h
                break

        if handler is not None:
            handler.handle_event(event)

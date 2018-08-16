import pygame
from pygame.event import Event
from screens.base import BaseScreen
from typing import List


class GlobalBaseEventHandler(object):
    def __init__(self, tarent_jumper: "masters_of_development.MastersOfDevelopment") -> None:
        self._tarent_jumper = tarent_jumper


class GlobalQuitEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper: "masters_of_development.MastersOfDevelopment") -> None:
        super(GlobalQuitEventHandler, self).__init__(tarent_jumper)

    def can_handle(self, event: Event) -> bool:
        return event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def handle_event(self, event: Event) -> None:
        if self.can_handle(event):
            self._tarent_jumper.shutdown()


class GlobalSwitchMusicEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper: "masters_of_development.MastersOfDevelopment") -> None:
        super(GlobalSwitchMusicEventHandler, self).__init__(tarent_jumper)

    def can_handle(self, event: Event) -> bool:
        return (
            event.type == pygame.KEYDOWN and (
                event.key == pygame.K_m or event.key == pygame.K_b or event.key == pygame.K_n
            )
        )

    def handle_event(self, event: Event) -> None:
        if event.key == pygame.K_m:
            self._tarent_jumper.switch_music()
        elif event.key == pygame.K_b:
            self._tarent_jumper.prev_music()
        elif event.key == pygame.K_n:
            self._tarent_jumper.next_music()


class GlobalScreenDeactivateEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper: "masters_of_development.MastersOfDevelopment") -> None:
        super(GlobalScreenDeactivateEventHandler, self).__init__(tarent_jumper)

    def can_handle(self, event: Event) -> bool:
        return event.type == BaseScreen.DEACTIVATE_SCREEN_EVENT

    def handle_event(self, event: Event) -> None:
        self._tarent_jumper.change_screen(event.screen)


class GlobalEventHandler(GlobalBaseEventHandler):
    def __init__(self, tarent_jumper: "masters_of_development.MastersOfDevelopment"):
        super(GlobalEventHandler, self).__init__(tarent_jumper)

    def __get_event_handlers(self) -> List[GlobalBaseEventHandler]:
        event_handlers = [
            GlobalQuitEventHandler(self._tarent_jumper),
            GlobalSwitchMusicEventHandler(self._tarent_jumper),
            GlobalScreenDeactivateEventHandler(self._tarent_jumper)
        ]

        for screen in self._tarent_jumper.get_screens():
            for event_handler in screen.get_event_handlers():
                event_handlers.append(event_handler)

        return event_handlers

    def handle_event(self, event: Event) -> None:
        for handler in self.__get_event_handlers():
            if handler.can_handle(event):
                handler.handle_event(event)

import pygame

from handlers.base_event_handler import BaseEventHandler


class QuitEventHandler(BaseEventHandler):
    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)

    def can_handle(self, event):
        return event.type == pygame.QUIT

    def handle_event(self, event):
        self._tarent_jumper.shutdown()
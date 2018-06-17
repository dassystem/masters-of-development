import pygame

from handlers.base_event_handler import BaseEventHandler


class KeyboardEventHandler(BaseEventHandler):
    # TYPE = pygame.KEYDOWN

    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)

    def can_handle(self, event):
        return event.type == pygame.KEYDOWN or event.type == pygame.KEYUP

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.__handle_keydown_event(event)
        elif event.type == pygame.KEYUP:
            self.__handle_keyup_event(event)

    def __handle_keydown_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self._tarent_jumper.shutdown()
        elif event.key == pygame.K_w:
            self._tarent_jumper.get_players()[0].jump()
        elif event.key == pygame.K_a:
            self._tarent_jumper.get_players()[0].move_left()
        elif event.key == pygame.K_d:
            self._tarent_jumper.get_players()[0].move_right()
        elif event.key == pygame.K_RIGHT:
            self._tarent_jumper.get_players()[1].move_right()
        elif event.key == pygame.K_LEFT:
            self._tarent_jumper.get_players()[1].move_left()
        elif event.key == pygame.K_UP:
            self._tarent_jumper.get_players()[1].jump()
        elif event.key == pygame.K_i:
            for player in self._tarent_jumper.get_players():
                player.switch_debug()
        elif event.key == pygame.K_m:
            self._tarent_jumper.switch_music()

    def __handle_keyup_event(self, event):
        if event.key == pygame.K_a or event.key == pygame.K_d:
            self._tarent_jumper.get_players()[0].stop()
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            self._tarent_jumper.get_players()[1].stop()
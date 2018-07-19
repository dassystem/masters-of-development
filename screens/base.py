import pygame
import utils.joysticks

class BaseScreen(object):
    DEACTIVE_SCREEN_EVENT = pygame.USEREVENT + 1

    def __init__(self, surface, event_handlers, active = False):
        self._surface = surface
        self.__event_handlers = event_handlers
        self.__active = active

    def get_event_handlers(self):
        return self.__event_handlers

    def add_event_handler(self, event_handler):
        self.__event_handlers.append(event_handler)

    def remove_event_handler(self, event_handler):
        self.__event_handlers.remove(event_handler)

    def is_active(self):
        return self.__active

    def set_active(self, active):
        self.__active = active

        if not self.__active:
            pygame.event.post(pygame.event.Event(BaseScreen.DEACTIVE_SCREEN_EVENT, {"screen": self}))

    def get_next_screen(self):
        return self.__next_screen

    def set_next_screen(self, next_screen):
        self.__next_screen = next_screen

    def render(self, seconds):
        if not self.__active:
            return

class BaseScreenEventHandler(object):
    def __init__(self, screen):
        self.__screen = screen

    def get_screen(self):
        return self.__screen;

    def can_handle(self, event):
        return self.__screen.is_active()

    def handle_event(self, event):
        pass

class BaseJoystickEventHandler(BaseScreenEventHandler):
    def __init__(self, screen, joystick):
        super(BaseJoystickEventHandler, self).__init__(screen)

        assert joystick is not None

        self.__joystick = joystick

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        joystick_event = utils.joysticks.is_motion(event) or utils.joysticks.is_button_down(event)

        if not joystick_event:
            return False

        correct_joystick = utils.joysticks.get_joystick_id(event) == self.__joystick.get_id()

        return correct_joystick

    def handle_event(self, event):
        if not self.can_handle(event):
            return

        if utils.joysticks.is_up(event):
            self._on_up(event)
        elif utils.joysticks.is_down(event):
            self._on_down(event)
        elif utils.joysticks.is_left(event):
            self._on_left(event)
        elif utils.joysticks.is_right(event):
            self._on_right(event)
        elif utils.joysticks.is_horizontal_stop(event):
            self._on_horizontal_stop(event)
        elif utils.joysticks.is_button_down(event):
            self._on_button_down(event)

    def _on_up(self, event):
        pass

    def _on_down(self, event):
        pass

    def _on_left(self, event):
        pass

    def _on_right(self, event):
        pass

    def _on_horizontal_stop(self, event):
        pass

    def _on_button_down(self, event):
        pass

class BaseKeyboardEventHandler(BaseScreenEventHandler):
    def __init__(self, screen, key_mappings, supported_events = [pygame.KEYDOWN, pygame.KEYUP]):
        super(BaseKeyboardEventHandler, self).__init__(screen)
        self._key_mappings = key_mappings
        self.__supported_events = supported_events

    def can_handle(self, event):
        return super().can_handle(event) and event.type in self.__supported_events and event.key in self._key_mappings.values()

import pygame
import utils.joysticks

from abc import ABCMeta, abstractmethod
from pygame import Surface, USEREVENT
from pygame.event import Event, post
from pygame.joystick import Joystick
from typing import Dict, List


class BaseScreenEventHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, screen: "BaseScreen"):
        self.__screen = screen

    def get_screen(self) -> "BaseScreen":
        return self.__screen

    def can_handle(self, event: Event) -> bool:
        return self.__screen.is_active()

    @abstractmethod
    def handle_event(self, event: Event) -> None:
        pass


class BaseScreen(object):
    DEACTIVATE_SCREEN_EVENT: int = USEREVENT + 1

    def __init__(self, surface: Surface, event_handlers: List[BaseScreenEventHandler], active: bool=False) -> None:
        self._surface = surface
        self.__event_handlers = event_handlers
        self.__active = active

    def get_event_handlers(self) -> List[BaseScreenEventHandler]:
        return self.__event_handlers

    def add_event_handler(self, event_handler: BaseScreenEventHandler) -> None:
        self.__event_handlers.append(event_handler)

    def remove_event_handler(self, event_handler: BaseScreenEventHandler) -> None:
        self.__event_handlers.remove(event_handler)

    def is_active(self) -> bool:
        return self.__active

    def set_active(self, active: bool):
        self.__active = active

        if not self.__active:
            post(Event(BaseScreen.DEACTIVATE_SCREEN_EVENT, {"screen": self}))

    def get_next_screen(self) -> "BaseScreen":
        return self.__next_screen

    def set_next_screen(self, next_screen: "BaseScreen") -> None:
        self.__next_screen = next_screen

    def render(self, seconds: float) -> None:
        if not self.__active:
            return


class BaseJoystickEventHandler(BaseScreenEventHandler):
    def __init__(self, screen: BaseScreen, joystick: Joystick) -> None:
        super(BaseJoystickEventHandler, self).__init__(screen)

        assert joystick is not None

        self.__joystick = joystick

    def can_handle(self, event: Event) -> bool:
        if not super().can_handle(event):
            return False

        joystick_event = utils.joysticks.is_motion(event) or utils.joysticks.is_button_down(event)

        if not joystick_event:
            return False

        correct_joystick = utils.joysticks.get_joystick_id(event) == self.__joystick.get_id()

        return correct_joystick

    def handle_event(self, event: Event) -> None:
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

    def _on_up(self, event: Event) -> None:
        pass

    def _on_down(self, event: Event) -> None:
        pass

    def _on_left(self, event: Event) -> None:
        pass

    def _on_right(self, event: Event) -> None:
        pass

    def _on_horizontal_stop(self, event: Event) -> None:
        pass

    def _on_button_down(self, event: Event) -> None:
        pass


class BaseKeyboardEventHandler(BaseScreenEventHandler):
    __metaclass__ = ABCMeta

    def __init__(
            self,
            screen: BaseScreen,
            key_mappings: Dict[str, int],
            supported_events: List[int]=[pygame.KEYDOWN, pygame.KEYUP]) -> None:
        super(BaseKeyboardEventHandler, self).__init__(screen)
        self._key_mappings = key_mappings
        self.__supported_events = supported_events

    def can_handle(self, event: Event) -> bool:
        return (
            super().can_handle(event) and
            event.type in self.__supported_events and
            event.key in self._key_mappings.values()
        )

    @abstractmethod
    def handle_event(self, event: Event) -> None:
        pass

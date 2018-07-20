import pygame

from pygame.event import Event
from pygame.joystick import Joystick
from typing import List


VERTICAL_AXIS: int = 1
HORIZONTAL_AXIS: int = 0
UP: int = -1
DOWN: int = 1
LEFT: int = -1
RIGHT: int = 1
STOP: int = 0


def init_joysticks() -> List[Joystick]:
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    for joystick in joysticks:
        joystick.init()

    return joysticks


def round_event_value(event: Event) -> int:
    return round(event.value)


def is_motion(event: Event) -> bool:
    return event.type == pygame.JOYAXISMOTION


def is_vertical_motion(event: Event) -> bool:
    return is_motion(event) and event.axis == VERTICAL_AXIS


def is_horizontal_motion(event: Event) -> bool:
    return is_motion(event) and event.axis == HORIZONTAL_AXIS


def is_up(event: Event) -> bool:
    return is_vertical_motion(event) and round_event_value(event) == UP


def is_down(event: Event) -> bool:
    return is_vertical_motion(event) and round_event_value(event) == DOWN


def is_left(event: Event) -> bool:
    return is_horizontal_motion(event) and round_event_value(event) == LEFT


def is_right(event: Event) -> bool:
    return is_horizontal_motion(event) and round_event_value(event) == RIGHT


def is_horizontal_stop(event: Event) -> bool:
    return is_horizontal_motion(event) and round_event_value(event) == STOP


def is_button_down(event: Event) -> bool:
    return event.type == pygame.JOYBUTTONDOWN


def get_joystick_id(event: Event) -> int:
    return event.joy

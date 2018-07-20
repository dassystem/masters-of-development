import pygame


def is_key_down(event: pygame.event.Event) -> bool:
    return event.type == pygame.KEYDOWN


def is_key_up(event: pygame.event.Event) -> bool:
    return event.type == pygame.KEYUP

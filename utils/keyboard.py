import pygame


def is_key_down(event):
    return event.type == pygame.KEYDOWN


def is_key_up(event):
    return event.type == pygame.KEYUP

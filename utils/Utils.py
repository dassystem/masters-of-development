import pygame
from typing import List
from in_game.play_area.sprites.player import Player


def center(surface: pygame.Surface, target_surface: pygame.Surface) -> pygame.Rect:
    x = center_x(surface, target_surface)
    y = center_y(surface, target_surface)

    return pygame.Rect(x, y, surface.get_width(), surface.get_height())


def center_with_offset(
        surface: pygame.Surface, target_surface: pygame.Surface, offset_x: int, offset_y: int) -> pygame.Rect:
    x = center_x(surface, target_surface) - offset_x
    y = center_y(surface, target_surface) - offset_y

    return pygame.Rect(x, y, surface.get_width(), surface.get_height())


def center_x(surface: pygame.Surface, target_surface: pygame.Surface) -> int:
    return target_surface.get_rect().centerx - surface.get_width() // 2


def center_y(surface: pygame.Surface, target_surface: pygame.Surface) -> int:
    return target_surface.get_rect().centery - surface.get_height() // 2


def get_player_from_joystick_event(
        event: pygame.event.Event, joysticks: List[pygame.joystick.Joystick], players: List[Player]) -> Player:
    player = None

    for i in range(len(joysticks)):
        if joysticks[i] is not None and joysticks[i].get_id() == event.joy:
            player = players[i]
            break

    return player


def split_screen(surface: pygame.Surface) -> List[pygame.Surface]:
    half_width = surface.get_width() // 2
    height = surface.get_height()

    split = []

    for i in range(0, 2):
        player_rect = pygame.Rect(i * half_width, 0, half_width, height)
        # TODO: Vorsicht bei fullscreen
        split.append(surface.subsurface(player_rect))

    return split

import os
import pygame
import random
import sys

import utils.joysticks

from handlers.global_event_handler import GlobalEventHandler
from in_game.play_area.sprites.player import Player
from in_game.play_area.sprites.power_up_shield import PowerUpShield
from in_game.screen.screen import InGameScreen
from pygame import Surface
from pygame.font import Font
from pygame.joystick import Joystick
from pygame.mixer import Sound
from pygame.time import Clock
from screens.base import BaseScreen
from screens.start_screen import StartScreen
from typing import Dict, List, Iterable


class MastersOfDevelopment(object):
    # width and height = 0 -> current screen resolution
    def __init__(self, width: int=0, height: int=0, flags: int=0, fps: int=60) -> None:
        """Initialize pygame, window, background, ...
        """

        random.seed()

        # less laggy sound
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()

        # pygame.HWSURFACE only for fullscreen...
        self.__display: Surface = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("Masters of Development")

        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self._width: int = width
        self._height: int = height

        self.__loops: List[str] = os.listdir("assets/loops")
        self.__loops.sort()
        self.__current_loop: int = 0

        pygame.mixer.music.load("assets/loops/" + self.__loops[self.__current_loop])
        self.__music: bool = False
        self.switch_music()

        self.__init_fonts()
        self.__init_sounds()
        self.__init_images()

        self.__clock: Clock = Clock()
        self.__fps: int = fps

        self.__init_joysticks()
        self.__init_players()

        self.__screen_dict: Dict[str, BaseScreen] = {
            "start": StartScreen(
                self.__display,
                self.__fonts,
                self.__sounds,
                self.__images,
                self.__players),
            "ingame": InGameScreen(
                self.__display,
                self.__fonts,
                self.__sounds,
                self.__images,
                self.__players)
        }

        for item in self.__screen_dict.items():
            if item[0] == "start":
                item[1].set_next_screen(self.__screen_dict["ingame"])
            elif item[0] == "ingame":
                item[1].set_next_screen(self.__screen_dict["start"])

        self.__event_handler: GlobalEventHandler = GlobalEventHandler(self)
        self.__running: bool = True

    def get_screens(self) -> Iterable[BaseScreen]:
        return self.__screen_dict.values()

    def change_screen(self, old_screen: BaseScreen) -> None:
        next_screen = old_screen.get_next_screen()

        for screen in self.__screen_dict.values():
            if screen == next_screen:
                next_screen.set_active(True)
                break

    def __init_fonts(self) -> None:
        self.__fonts: Dict[str, Font] = {
            "big": Font("assets/fonts/PressStart2P.ttf", 29),
            "medium": Font("assets/fonts/PressStart2P.ttf", 24),
            "small": Font("assets/fonts/PressStart2P.ttf", 12),
            "micro": Font("assets/fonts/PressStart2P.ttf", 8)
        }

    def __init_sounds(self) -> None:
        self.__sounds: Dict[str, Sound] = {
            "start_game": Sound("assets/sounds/start_game.wav"),
            "jump": Sound("assets/sounds/jump.wav"),
            "score": Sound("assets/sounds/glass.ogg"),
            "player1wins": Sound("assets/sounds/Player_o-NEOKOLOR-7551_hifi.ogg"),
            "player2wins": Sound("assets/sounds/Player_t-Neokolor-7552_hifi.ogg")
        }

        for i in range(1, 11):
            self.__sounds[str(i)] = pygame.mixer.Sound("assets/sounds/82986__tim-kahn__countdown-{0:02d}.ogg".format(i))

    def __init_images(self) -> None:
        self.__images: Dict[str, Surface] = {
            "start_screen_bg": self.__load_image("assets/images/start_screen_bg.png"),
            "start_screen_player_1": self.__load_image("assets/images/player_1.png"),
            "start_screen_player_2": self.__load_image("assets/images/player_2.png"),
            "start_screen_start_normal": self.__load_image("assets/images/start_button_normal.png"),
            "start_screen_start_pushed": self.__load_image("assets/images/start_button_pushed.png"),
            "start_screen_countdown_bg": self.__load_image("assets/images/countdown_screen_bg.png"),
            "start_screen_countdown_3": self.__load_image("assets/images/countdown_3.png"),
            "start_screen_countdown_2": self.__load_image("assets/images/countdown_2.png"),
            "start_screen_countdown_1": self.__load_image("assets/images/countdown_1.png"),
            "start_screen_countdown_go": self.__load_image("assets/images/countdown_lets_code.png"),
            "in_game_screen_bg": self.__load_image("assets/images/game_screen_frame.png"),
            "in_game_screen_game_over_bg": self.__load_image("assets/images/inscreen_game_over.png"),
            "in_game_screen_win_bg": self.__load_image("assets/images/inscreen_you_win.png"),
            "in_game_screen_loose_bg": self.__load_image("assets/images/inscreen_you_lose.png"),
            "in_game_screen_player": self.__load_image("assets/images/game_figure.png"),
            "in_game_screen_player_jumping": self.__load_image("assets/images/game_figure_jump.png"),
            "coin": self.__load_image("assets/images/coin.png"),
            "power_up_jump_height": self.__load_image("assets/images/jump_power.png"),
            "bug": self.__load_image("assets/images/bug.png"),
            PowerUpShield.NAME: self.__load_image("assets/images/armor.png")
        }

    def __load_image(self, filename: str) -> Surface:
        return pygame.image.load(filename).convert_alpha()

    def __init_joysticks(self) -> None:
        self.__joysticks: List[Joystick] = utils.joysticks.init_joysticks()

    def __init_players(self) -> None:
        self.__players: List[Player] = []

        joystick_count = len(self.__joysticks)

        for i in range(0, 2):
            joystick = None

            if i < joystick_count:
                joystick = self.__joysticks[i]

            self.__players.append(
                self.__init_player(i + 1, self.__images, joystick, self.__sounds))

    def __init_player(
            self, number: int, images: Dict[str, Surface], joystick: Joystick, sounds: Dict[str, Sound]) -> Player:
        return Player(number, images, 1, joystick, sounds, self.__fonts, self.__fps)

    def switch_music(self) -> None:
        self.__music = not self.__music

        if self.__music:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()

    def next_music(self) -> None:
        if not self.__music:
            return

        if self.__current_loop + 1 == len(self.__loops):
            self.__current_loop = 0
        else:
            self.__current_loop += 1

        self.__change_loop()

    def prev_music(self) -> None:
        if not self.__music:
            return

        if self.__current_loop == 0:
            self.__current_loop = len(self.__loops) - 1
        else:
            self.__current_loop -= 1

        self.__change_loop()

    def __change_loop(self) -> None:
        pygame.mixer.music.load("assets/loops/" + self.__loops[self.__current_loop])
        pygame.mixer.music.play(-1)

    def shutdown(self) -> None:
        self.__running = False

    def get_players(self) -> List[Player]:
        return self.__players

    def run(self) -> None:
        """The mainloop
        """

        pygame.time.set_timer(utils.timer.COUNTDOWN_EVENT, 1000)

        while self.__running:
            milliseconds = self.__clock.tick(self.__fps)
            seconds = milliseconds / 1000

            for screen in self.__screen_dict.values():
                screen.render(seconds)

            for event in pygame.event.get():
                self.__event_handler.handle_event(event)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    width: int = 1920
    height: int = 1080
    flags: int = 0  # pygame.NOFRAME

    for i, arg in enumerate(sys.argv):
        if arg == "fullscreen":
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        elif i == 1:
            width = int(arg)
        elif i == 2:
            height = int(arg)

    MastersOfDevelopment(width, height, flags).run()

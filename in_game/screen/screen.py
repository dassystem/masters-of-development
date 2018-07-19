from colors import BLACK, GREEN, RED
from in_game.play_area.play_area import PlayArea
from in_game.screen import InGameScreenTimerElapsedEventHandler
from in_game.screen.joystick import ScreenJoystickEventHandler
from in_game.screen.keyboard import ScreenKeyboardEventHandler
from leaderboard import INSTANCE as LEADERBOARD, MAX_ENTRIES
from screens.base import BaseScreen
from utils.timer import FontSpriteTimer

import pygame


class InGameScreen(BaseScreen):
    def __init__(self, surface, fonts, sounds, images, players, seconds=100):
        super(InGameScreen, self).__init__(surface, [])

        self.__fonts = fonts
        self.__sounds = sounds
        self.__images = images

        self.__players = players

        self.__play_areas = []
        self.__init_play_areas(fonts, sounds, images)

        super().add_event_handler(ScreenJoystickEventHandler(self, self.__play_areas))
        super().add_event_handler(ScreenKeyboardEventHandler(self, self.__play_areas))

        timer = FontSpriteTimer(
            "ingame",
            seconds,
            {"center": (960, 77)},
            fonts["big"],
            GREEN,
            RED,
            sounds,
            10)

        self.__timer = pygame.sprite.GroupSingle(timer)

        super().add_event_handler(InGameScreenTimerElapsedEventHandler(self, self.get_timer()))

        self.__init_redraw_areas()

    def __init_play_areas(self, fonts, sounds, images):
        split_screen = []
        player_1_rect = pygame.Rect(55, 85, 850, 735)
        split_screen.append(self._surface.subsurface(player_1_rect))

        player_2_rect = pygame.Rect(1015, 85, 850, 735)
        split_screen.append(self._surface.subsurface(player_2_rect))

        for i, subsurface in enumerate(split_screen):
            play_area = PlayArea(
                self, subsurface, fonts, sounds, images, self.__players[i])
            self.__play_areas.append(play_area)

    def __init_redraw_areas(self):
        self.__redraw_areas = {}

        background = self.__images["in_game_screen_bg"]

        self.__redraw_areas["timer_1"] = (background.subsurface((870, 85, 35, 40)), (870, 85))
        self.__redraw_areas["timer_2"] = (background.subsurface((1015, 85, 35, 40)), (1015, 85))
        self.__redraw_areas["head_1"] = (background.subsurface((400, 795, 155, 25)), (400, 795))
        self.__redraw_areas["head_2"] = (background.subsurface((1360, 800, 120, 20)), (1360, 800))

    def render(self, seconds):
        if not self.is_active():
            return

        for play_area in self.__play_areas:
            play_area.update(seconds)

        self.__redraw()

        all_dead = True

        for player in self.__players:
            all_dead = all_dead and player.is_dead()

        if self.all_dead() and self.get_timer().is_started():
            self.get_timer().stop()

        self.__render_timer()

    def __redraw(self):
        for redraw_area in self.__redraw_areas.values():
            self._surface.blit(redraw_area[0], redraw_area[1])

    def all_dead(self):
        all_dead = True

        for player in self.__players:
            all_dead = all_dead and player.is_dead()

        return all_dead

    def set_keyboard_states(self):
        if not self.__keyboard_states_dirty:
            return

        if LEADERBOARD.get_count() + len(self.__players) <= MAX_ENTRIES:
            for play_area in self.__play_areas:
                play_area.get_keyboard().set_active(True)
        else:
            new_scores = self.__players.copy()
            new_scores.sort(key=lambda player: player.get_score(), reverse=True)

            new_entries = 0

            for new_score in new_scores:
                if LEADERBOARD.get_count() + new_entries < MAX_ENTRIES:
                    self.__play_areas[new_scores[0].get_number() - 1].get_keyboard().set_active(True)
                    new_entries += 1
                    continue
                else:
                    for entry in LEADERBOARD.get_entries():
                        if entry.get_score() < new_score.get_score():
                            self.__play_areas[new_scores[0].get_number() - 1].get_keyboard().set_active(True)
                            new_entries += 1

                            break

        self.__keyboard_states_dirty = False

    def __render_timer(self):
        self.__timer.clear(self._surface, fill_with_black)
        self.__timer.update()
        self.__timer.draw(self._surface)

    def set_active(self, active):
        super().set_active(active)

        if self.is_active():
            self.add_event_handler(self.get_timer().get_event_handler())
            self.get_timer().start()

            for play_area in self.__play_areas:
                play_area.reset()

            self._surface.blit(self.__images["in_game_screen_bg"], (0, 0))

            self.__ending_sound_played = False
            self.__keyboard_states_dirty = True
        else:
            self.get_timer().stop()
            self.remove_event_handler(self.get_timer().get_event_handler())

    def play_ending_sound(self, player):
        if not self.__ending_sound_played:
            self.__sounds["player{0:d}wins".format(player.get_number())].play()
            self.__ending_sound_played = True

    def set_ending_sound_played(self):
        self.__ending_sound_played = True

    def get_players(self):
        return self.__players

    def get_play_areas(self):
        return self.__play_areas

    def get_timer(self):
        """Get the timer out of the sprite group."""
        return self.__timer.sprite


def fill_with_black(surface, rect):
    surface.fill(BLACK, rect)

import os
import pygame
import sys

import handlers.global_event_handler
import player
import screens.start_screen
import screens.in_game_screen
import screens.game_over_screen
import screens.leaderboard_screen

class MastersOfDevelopment(object):
    # colors
    TARENT_RED = pygame.Color(204, 0, 0)
    TARENT_GREY = pygame.Color(180, 180, 180)
    WHITE = pygame.Color(255, 255, 255)
    BLACK = pygame.Color(0, 0, 0)
    BACKGROUND_COLOR = WHITE
    
    # width and height = 0 -> current screen resolution
    def __init__(self, width = 0, height = 0, flags = 0, fps = 60):
        """Initialie pygame, window, background, ...
        """
        
        # less laggy sound
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        
        # pygame.HWSURFACE only for fullscreen...
        self.__display = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("Masters of Development")

        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self._width = width
        self._height = height

        self.__loops = os.listdir("assets/loops")
        self.__loops.sort()
        self.__current_loop = 0

        pygame.mixer.music.load("assets/loops/" + self.__loops[self.__current_loop])
        self.__music = False
        self.switch_music()
        
        self.__init_fonts()
        
        self.__sounds = {}
        
        self.__clock = pygame.time.Clock()
        self.__fps = fps

        self.__init_joysticks()
        self.__init_players()
        self.__init_cursors()
        
        self.__screen_dict = {
            "start": screens.start_screen.StartScreen(self.__display, self.__fonts, self.__players),
            "ingame": screens.in_game_screen.InGameScreen(self.__display, self.__fonts, self.__sounds, self.__players, self.__joysticks),
            "gameover": screens.game_over_screen.GameOverScreen(
                self.__display, self.__players, self.__fonts, MastersOfDevelopment.TARENT_RED, MastersOfDevelopment.WHITE),
            "leaderboard" : screens.leaderboard_screen.LeaderboardScreen(
                self.__display, self.__players, self.__joysticks, self.__cursors, self.__fonts, MastersOfDevelopment.TARENT_RED,
                MastersOfDevelopment.WHITE)

        }
        
        for item in self.__screen_dict.items():
            if item[0] == "start":
                item[1].set_next_screen(self.__screen_dict["ingame"])
            elif item[0] == "ingame":
                item[1].set_next_screen(self.__screen_dict["gameover"])
            elif item[0] == "gameover":
                item[1].set_next_screen(self.__screen_dict["leaderboard"])
            elif item[0] == "leaderboard":
                item[1].set_next_screen(self.__screen_dict["start"])
        
        self.__event_handler = handlers.global_event_handler.GlobalEventHandler(self)
        self.__running = True

    def get_screens(self):
        return self.__screen_dict.values()

    def change_screen(self, old_screen):
        next_screen = old_screen.get_next_screen()
        
        for screen in self.__screen_dict.values():
            if screen == next_screen:
                next_screen.set_active(True)
                break;

    def __init_fonts(self):
        self.__fonts = {}
        
        self.__fonts["big"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 36)
        self.__fonts["medium"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 24)
        self.__fonts["small"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 12)
        self.__fonts["micro"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 8)

    def __init_joysticks(self):
        self.__joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        
        for joystick in self.__joysticks:
            joystick.init()

    def __init_players(self):
        self.__players = []
        
        self.__sounds['jump'] = pygame.mixer.Sound("assets/sounds/jump.wav")
        self.__sounds['score'] = pygame.mixer.Sound("assets/sounds/glass.ogg")
        
        joystick_count = len(self.__joysticks)

        for i in range(0, 2):
            joystick = None
            
            if i < joystick_count:
                joystick = self.__joysticks[i]

            self.__players.append(
                self.__init_player(i + 1, "assets/images/dev" + str(i + 1) + ".png", joystick, self.__sounds))

    def __init_cursors(self):
        self.__cursors = []

        for player in self.__players:
            self.__cursors.append(screens.leaderboard_screen.Cursor())

    def __init_player(self, number, image_file_name, joystick, sounds):
        return player.Player(number, image_file_name, 1, joystick, sounds, self.__fonts, self.__fps)

    def switch_music(self):
        self.__music = not self.__music
        
        if self.__music:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()

    def next_music(self):
        if not self.__music:
            return
        
        if self.__current_loop + 1 == len(self.__loops):
            self.__current_loop = 0
        else:
            self.__current_loop += 1
            
        self.__change_loop()

    def prev_music(self):
        if not self.__music:
            return
        
        if self.__current_loop == 0:
            self.__current_loop = len(self.__loops) - 1
        else:
            self.__current_loop -= 1

        self.__change_loop()
    
    def __change_loop(self):
        pygame.mixer.music.load("assets/loops/" + self.__loops[self.__current_loop])
        pygame.mixer.music.play(-1)

    def shutdown(self):
        self.__running = False

    def get_players(self):
        return self.__players

    def run(self):
        """The mainloop
        """

        while self.__running:
            for screen in self.__screen_dict.values():
                screen.render()
            
            for event in pygame.event.get():
                self.__event_handler.handle_event(event)
            
            self.__clock.tick(self.__fps)
            pygame.display.flip()
       
        pygame.quit()
    
if __name__ == "__main__":
    width = 1280 #1980
    height = 720 #1024
    flags = 0
    
    for i, arg in enumerate(sys.argv):
        if arg == "fullscreen":
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        elif i == 1:
            width = int(arg)
        elif i == 2:
            height = int(arg)
    
    MastersOfDevelopment(width, height, flags).run()

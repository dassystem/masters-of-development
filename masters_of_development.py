import os
import pygame
import random
import sys

import handlers.global_event_handler
import leaderboard
import screens.start_screen
import screens.in_game_screen
import utils.joysticks

from in_game.play_area.sprites.player import Player

PIXEL_PER_SECOND = 60

class MastersOfDevelopment(object):
    # colors
    TARENT_RED = pygame.Color(204, 0, 0)
    TARENT_GREY = pygame.Color(180, 180, 180)
    WHITE = pygame.Color(255, 255, 255)
    BLACK = pygame.Color(0, 0, 0)
    BACKGROUND_COLOR = WHITE
    GREEN = pygame.Color(93, 252, 172)
    RED = pygame.Color(255, 0, 0)
    LIGHT_GRAY = pygame.Color(131, 135, 135)
    DARK_GRAY = pygame.Color(58, 58, 58)
    DARKER_GRAY = pygame.Color(38, 38, 38)
    
    # width and height = 0 -> current screen resolution
    def __init__(self, width = 0, height = 0, flags = 0, fps = 60):
        """Initialie pygame, window, background, ...
        """
        
        random.seed()
        
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
        self.__init_sounds()
        self.__init_images()
        
        self.__clock = pygame.time.Clock()
        self.__fps = fps

        self.__init_joysticks()
        self.__init_players()
        
        self.__leaderboard = leaderboard.Leaderboard()
        
        self.__screen_dict = {
            "start": screens.start_screen.StartScreen(
                self.__display,
                self.__fonts,
                self.__sounds,
                self.__images,
                self.__players,
                self.__leaderboard),
            "ingame": screens.in_game_screen.InGameScreen(
                self.__display,
                self.__fonts,
                self.__sounds,
                self.__images,
                self.__players,
                self.__leaderboard)
        }
        
        for item in self.__screen_dict.items():
            if item[0] == "start":
                item[1].set_next_screen(self.__screen_dict["ingame"])
            elif item[0] == "ingame":
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
                break

    def __init_fonts(self):
        self.__fonts = {}
        
        self.__fonts["big"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 29)
        self.__fonts["medium"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 24)
        self.__fonts["small"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 12)
        self.__fonts["micro"] = pygame.font.Font("assets/fonts/PressStart2P.ttf", 8)

    def __init_sounds(self):
        self.__sounds = {}
        
        self.__sounds["start_game"] = pygame.mixer.Sound("assets/sounds/start_game.wav")
        
        self.__sounds["jump"] = pygame.mixer.Sound("assets/sounds/jump.wav")
        self.__sounds["score"] = pygame.mixer.Sound("assets/sounds/glass.ogg")
                
        self.__sounds["player1wins"] = pygame.mixer.Sound("assets/sounds/Player_o-NEOKOLOR-7551_hifi.ogg")
        self.__sounds["player2wins"] = pygame.mixer.Sound("assets/sounds/Player_t-Neokolor-7552_hifi.ogg")
        
        for i in range(1, 11):
            self.__sounds[str(i)] = pygame.mixer.Sound("assets/sounds/82986__tim-kahn__countdown-{0:02d}.ogg".format(i))

    def __init_images(self):
        self.__images = {}
        
        self.__images["start_screen_bg"] = pygame.image.load("assets/images/start_screen_bg.png").convert_alpha()
        self.__images["start_screen_player_1"] = pygame.image.load("assets/images/player_1.png").convert_alpha()
        self.__images["start_screen_player_2"] = pygame.image.load("assets/images/player_2.png").convert_alpha()
        self.__images["start_screen_start_normal"] = pygame.image.load("assets/images/start_button_normal.png").convert_alpha()
        self.__images["start_screen_start_pushed"] = pygame.image.load("assets/images/start_button_pushed.png").convert_alpha()
        
        self.__images["start_screen_countdown_bg"] = pygame.image.load("assets/images/countdown_screen_bg.png").convert_alpha()
        self.__images["start_screen_countdown_3"] = pygame.image.load("assets/images/countdown_3.png").convert_alpha()
        self.__images["start_screen_countdown_2"] = pygame.image.load("assets/images/countdown_2.png").convert_alpha()
        self.__images["start_screen_countdown_1"] = pygame.image.load("assets/images/countdown_1.png").convert_alpha()
        self.__images["start_screen_countdown_go"] = pygame.image.load("assets/images/countdown_lets_code.png").convert_alpha()
        
        self.__images["in_game_screen_bg"] = pygame.image.load("assets/images/game_screen_frame.png").convert_alpha()
        self.__images["in_game_screen_game_over_bg"] = pygame.image.load("assets/images/inscreen_game_over.png").convert_alpha()
        self.__images["in_game_screen_win_bg"] = pygame.image.load("assets/images/inscreen_you_win.png").convert_alpha()
        self.__images["in_game_screen_loose_bg"] = pygame.image.load("assets/images/inscreen_you_lose.png").convert_alpha()
        self.__images["in_game_screen_player"] = pygame.image.load("assets/images/game_figure.png").convert_alpha()
        self.__images["in_game_screen_player_jumping"] = pygame.image.load("assets/images/game_figure_jump.png").convert_alpha()        
        
        self.__images["coin"] = pygame.image.load("assets/images/coin.png").convert_alpha()
           
        self.__images["power_up_jump_height"] = pygame.image.load("assets/images/jump_power.png").convert_alpha()
        self.__images["bug"] = pygame.image.load("assets/images/bug.png").convert_alpha()
        self.__images["power_up_shield"] = pygame.image.load("assets/images/armor.png").convert_alpha()

    def __init_joysticks(self):
        self.__joysticks = utils.joysticks.init_joysticks()

    def __init_players(self):
        self.__players = []
        
        joystick_count = len(self.__joysticks)

        for i in range(0, 2):
            joystick = None
            
            if i < joystick_count:
                joystick = self.__joysticks[i]

            self.__players.append(
                self.__init_player(i + 1, self.__images, joystick, self.__sounds))

    def __init_player(self, number, images, joystick, sounds):
        return Player(number, images, 1, joystick, sounds, self.__fonts, self.__fps)

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
    width = 1920
    height = 1080
    flags = 0 #pygame.NOFRAME
    
    for i, arg in enumerate(sys.argv):
        if arg == "fullscreen":
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        elif i == 1:
            width = int(arg)
        elif i == 2:
            height = int(arg)
    
    MastersOfDevelopment(width, height, flags).run()

import pygame

import handlers.global_event_handler
import player

import screens.start_screen
import screens.get_ready_screen
import screens.countdown_screen
import screens.in_game_screen

class TarentJumper:
    # colors
    TARENT_RED = pygame.Color(204, 0, 0)
    TARENT_GREY = pygame.Color(180, 180, 180)
    WHITE = pygame.Color(255, 255, 255)
    BLACK = pygame.Color(0, 0, 0)
    BACKGROUND_COLOR = pygame.Color(50, 60, 200)
    
    # width and height = 0 -> current screen resolution
    def __init__(self, width = 0, height = 0, flags = 0, fps = 60):
        """Initialie pygame, window, background, ...
        """
        
        # less laggy sound
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        
        # pygame.HWSURFACE only for fullscreen...
        self.__display = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("tarent Jumper")
        #self._screens = []

        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self._width = width
        self._height = height

        pygame.mixer.music.load("assets/sounds/tetrisc.mid")
        self.__music = False
        self.switch_music()
        
        self.__init_fonts()
        
        self.__sounds = {}
        
        self.__clock = pygame.time.Clock()
        self.__fps = fps

        self.__init_joysticks()
        self.__init_players()
        
        self.__screen_dict = {
            "start": screens.start_screen.StartScreen(self.__display, self.__big_font, self.__small_font),
            "getready": screens.get_ready_screen.GetReadyScreen(
                self.__display, self.__joysticks, self.__players, self.__small_font),
            "countdown": screens.countdown_screen.CountdownScreen(self.__display, self.__big_font),
            "ingame": screens.in_game_screen.InGameScreen(self.__display, self.__players, self.__joysticks)
        }
        
        for item in self.__screen_dict.items():
            if item[0] == "start":
                item[1].set_next_screen(self.__screen_dict["getready"])
            elif item[0] == "getready":
                item[1].set_next_screen(self.__screen_dict["countdown"])
            elif item[0] == "countdown":
                item[1].set_next_screen(self.__screen_dict["ingame"])
            elif item[0] == "ingame":
                item[1].set_next_screen(self.__screen_dict["start"])
        
        for i, player_surface in enumerate(self.__screen_dict["ingame"].get_player_surfaces()):
            self.__players[i].set_surface(player_surface)

        
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
        self.__big_font = pygame.font.SysFont("sans", 72)
        self.__small_font = pygame.font.SysFont("sans", 24)

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

    def __init_player(self, number, image_file_name, joystick, sounds):
        return player.Player(number, image_file_name, 1, joystick, sounds, self.__fps)

    def switch_music(self):
        self.__music = not self.__music
        
        if self.__music:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()

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
    TarentJumper(800, 600).run()

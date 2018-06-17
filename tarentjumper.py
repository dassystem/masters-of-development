import pygame

from handlers.main_event_handler import EventHandler
from player import Player
from block import Block

level1 = [
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
    [1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0],
    [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
    [0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
    [1,1,0,0,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0]
]


class TarentJumper:
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
        self._screens = []

        # colors
        self._tarent_red = pygame.Color(204, 0, 0)
        self._tarent_grey = pygame.Color(180, 180, 180)
        self._white = pygame.Color(255, 255, 255)
        self.__background_color = pygame.Color(50, 60, 200)
        self._black = pygame.Color(0, 0, 0)

        self._width = width
        self._height = height

        pygame.mixer.music.load("assets/sounds/tetrisc.mid")
        self.__music = False
        self.switch_music()
        
        self.__clock = pygame.time.Clock()
        self.__fps = fps

        self.__fill_blocks()
        self.__init_joysticks()
        self.__init_players()
                
        self.level = Block(50, 50)
        self.__event_handler = EventHandler(self)
        self.__running = True

    def __start_screen(self):
        intro = True
        bigFont = pygame.font.SysFont("comicsansms", 72)
        smallFont = pygame.font.SysFont("comicsansms", 24)
        startTitle = bigFont.render("Tarent Jumper", True, self._tarent_red)
        startHint = smallFont.render("Press Enter to start the game", True, self._tarent_grey)
        startSound = pygame.mixer.Sound("assets/sounds/start_game.wav")

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                # TODO handle joystick / buttons
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        startSound.play(0)
                        pygame.time.wait(350)
                        intro = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()

            self.__display.fill(self._white)
            # tries to center the texts
            self.__display.blit(startTitle, (
                self._width // 2 - startTitle.get_width() // 2, self._height // 2 - startTitle.get_height() // 2 - 100))
            self.__display.blit(startHint, (
                self._width // 2 - startHint.get_width() // 2, self._height // 2 - startHint.get_height() // 2 + 50))
            pygame.display.flip()
            self.__clock.tick(self.__fps)

    def __ready_screen(self):
        player_one_ready = True
        player_two_ready = True


        self.__display.fill(self.__background_color)

        while player_one_ready or player_two_ready:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # TODO handle joystick / buttons
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        player_one_ready = False
                    if event.key == pygame.K_UP:
                        player_two_ready = False

            font = pygame.font.SysFont("sans", 20)

            #TODO change text to (Player X is ready!)
            for index ,screen in enumerate(self._screens):
                if index == 0:
                    text = "Player" + str(index + 1) + " are you ready?"
                    hint = "Press W to get ready!"
                else:
                    text = "Player" + str(index + 1) + " are you ready?"
                    hint = "Press UP to get ready!"
                text_surface = font.render(text, True, (255, 0, 0))
                text_rect = text_surface.get_rect()
                text_rect.x = screen.get_rect().centerx - text_surface.get_width() // 2
                text_rect.y = screen.get_rect().centery - text_surface.get_height() // 2

                text_surface_hint = font.render(hint, True , (255, 0 , 0))
                text_rect_hint = pygame.Rect.copy(text_rect)
                text_rect_hint.y += text_rect.height

                screen.blit(text_surface, text_rect)
                screen.blit(text_surface_hint, text_rect_hint)
                pygame.display.flip()
                self.__clock.tick(self.__fps)

    def __countdown_start(self):
        dt = 0
        '''
        timer is 6 seconds because ur not able to see the 6
        and for the user the countdown starts visible at 5
        '''
        timer = 6

        while timer > 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            timer -= dt
            bigFont = pygame.font.SysFont("comicsansms", 72)

            self.__display.fill(self.__background_color)

            time_txt = bigFont.render(str(int((timer))), True, self._black)
            self.__display.blit(time_txt, (self._width // 2 - time_txt.get_width() // 2, self._height // 2 - time_txt.get_height() // 2))

            pygame.display.flip()
            dt = self.__clock.tick(30) / 1000

    def __fill_blocks(self):
        self.__blocks = []

        for y in range(0, len(level1)):
            prev_line_block = None
            for x in range(0, len(level1[y])):
                if (level1[y][x] == 1):
                    new_x = x * 32
                    new_y = y * 32
                    new_width = 32
                    new_height = 32
                    
                    if prev_line_block:
                        if prev_line_block.get_rect().x / Block.BLOCK_WIDTH == x - 1:
                            self.__blocks.pop()
                            new_x = prev_line_block.get_rect().x
                            new_y = prev_line_block.get_rect().y
                            new_width = prev_line_block.get_rect().width + Block.BLOCK_WIDTH
                            new_height = Block.BLOCK_HEIGHT
                    
                    new_block = Block(new_x, new_y, new_width, new_height)
                    self.__blocks.append(new_block)
                    prev_line_block = new_block

    def __init_joysticks(self):
        self.__joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        
        for joystick in self.__joysticks:
            joystick.init()

    def __init_players(self):
        self.__players = []
        
        self.__jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
        
        # TODO: vorsicht bei width = 0 und/oder height = 0 (fullscreen)
        half_width = self.__display.get_width() // 2
        height = self.__display.get_height()

        joystick_count = len(self.__joysticks)

        for i in range(0, 2):
            joystick = None
            
            if i < joystick_count:
                joystick = self.__joysticks[i]

            self._screens.append(
                self.__init_screens(i * half_width, half_width, height))

            self.__players.append(
                self.__init_player(i + 1, i * half_width, half_width, height, "assets/images/dev" + str(i + 1) + ".png", joystick, self.__jump_sound))

    def __init_player(self, number, screen_x, screen_width, screen_height, image_file_name, joystick, jump_sound):
        player_rect = pygame.Rect(screen_x, 0, screen_width, screen_height)
        player_surface = self.__display.subsurface(player_rect)
        
        return Player(number, player_surface, image_file_name, self.__blocks, 1, joystick, jump_sound, self.__fps)

    def __init_screens(self, screen_x, screen_width, screen_height):
        player_rect = pygame.Rect(screen_x, 0, screen_width, screen_height)
        player_surface = self.__display.subsurface(player_rect)

        return player_surface

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

        self.__start_screen()
        self.__ready_screen()
        self.__countdown_start()
        while self.__running:
            self.__display.fill(self.__background_color)

            for block in self.__blocks:
                block.render(self.__display)
            
            for event in pygame.event.get():
                self.__event_handler.handle_event(event)
            
            for player in self.__players:
                player.update()
            
            self.__clock.tick(self.__fps)
            pygame.display.flip()
       
        pygame.quit()
    
if __name__ == "__main__":
    TarentJumper(800, 600).run()

import pygame
from player import Player
from block import Block

level1 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0],
    [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
    [0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,0]
]

class BaseEventHandler:
    def __init__(self, tarent_jumper):
        self._tarent_jumper = tarent_jumper

    def can_handle(self, event):
        return False

    def handle_event(self, event):
        print("handling event " + str(event))

class EventHandler(BaseEventHandler):
    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)
        self.__handlers = []
        self.__handlers.append(QuitEventHandler(self._tarent_jumper))
        self.__handlers.append(KeyboardEventHandler(self._tarent_jumper))
        self.__handlers.append(JoystickEventHandler(self._tarent_jumper))
        
    def handle_event(self, event):
        handler = None
        
        for i in range(len(self.__handlers)):
            if self.__handlers[i].can_handle(event):
                handler = self.__handlers[i]
                break
            
        if handler is not None:
            handler.handle_event(event)

class QuitEventHandler(BaseEventHandler):
    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)    

    def can_handle(self, event):
        return event.type == pygame.QUIT

    def handle_event(self, event):
        BaseEventHandler.handle_event(self, event)
        self._tarent_jumper.shutdown()

class KeyboardEventHandler(BaseEventHandler):
    TYPE = pygame.KEYDOWN
    
    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)

    def can_handle(self, event):
        return event.type == pygame.KEYDOWN

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.__handle_keydown_event(event)  

    def __handle_keydown_event(self, event):
        BaseEventHandler.handle_event(self, event)
         
        if event.key == pygame.K_ESCAPE:
            self._tarent_jumper.shutdown()
        elif event.key == pygame.K_w:
            self._tarent_jumper.get_players()[0].jump()
        elif event.key == pygame.K_a:
            self._tarent_jumper.get_players()[0].move_left()
        elif event.key == pygame.K_d:
            self._tarent_jumper.get_players()[0].move_right()
        elif event.key == pygame.K_RIGHT:
            self._tarent_jumper.get_players()[1].move_right()
        elif event.key == pygame.K_LEFT:
            self._tarent_jumper.get_players()[1].move_left()
        elif event.key == pygame.K_UP:
            self._tarent_jumper.get_players()[1].jump()
        elif event.key == pygame.K_i:
            for player in self._tarent_jumper.get_players():
                player.switch_debug()

class JoystickEventHandler(BaseEventHandler):
    VERTICAL_AXIS = 0
    HORIZONTAL_AXIS = 1
    UP = 1
    DOWN = -1
    LEFT = -1
    RIGHT = 1
    
    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)
        self.__joysticks = []
        
        for player in self._tarent_jumper.get_players():
            self.__joysticks.append(player.get_joystick())

    def can_handle(self, event):
        return event.type == pygame.JOYAXISMOTION
        
    def handle_event(self, event):
        if event.type == pygame.JOYAXISMOTION:
            self.__handle_axis_motion(event)
        else:
            print("Ignoring event " + str(event))
            
    def __handle_axis_motion(self, event):
        if event.axis > JoystickEventHandler.HORIZONTAL_AXIS:
            return
        
        BaseEventHandler.handle_event(self, event)
        
        player = self.__player_for_event(event)
                
        if player is None:
            return
        
        if event.axis == JoystickEventHandler.VERTICAL_AXIS:
            self.__handle_vertical_axis_motion(event, player)
        elif event.axis == JoystickEventHandler.HORIZONTAL_AXIS:
            self.__handle_horizontal_axis_motion(event, player)

    def __player_for_event(self, event):
        player = None
        
        for i in range(len(self.__joysticks)):
            if self.__joysticks[i] is not None and self.__joysticks[i].get_id() == event.joy:
                player = self._tarent_jumper.get_players()[i]
                break
            
        return player

    def __handle_vertical_axis_motion(self, event, player):
        if self.__round_event_value(event) == JoystickEventHandler.UP:
            player.jump()

    def __handle_horizontal_axis_motion(self, event, player):
        event_value = self.__round_event_value(event)
        
        if event_value == JoystickEventHandler.LEFT:
            player.move_left()
        elif event_value == JoystickEventHandler.RIGHT:
            player.move_right()

    def __round_event_value(self, event):
        return round(event.value, 0)

class TarentJumper:
    # width and height = 0 -> current screen resolution
    def __init__(self, width = 0, height = 0, flags = 0, fps = 30):
        """Initialie pygame, window, background, ...
        """
        pygame.init()
        
        # pygame.HWSURFACE only for fullscreen...
        self.__display = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("tarent Jumper")
        
        self.__background_color = pygame.Color(50, 60, 200)
        
        self.__clock = pygame.time.Clock()
        self.__fps = fps

        self.__fill_blocks()
        self.__init_joysticks()
        self.__init_players()
                
        self.level = Block(50, 50)
        self.__event_handler = EventHandler(self)
        self.__running = True

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
                        if prev_line_block.get_rect().x / 32 == x - 1:
                            self.__blocks.pop()
                            new_x = prev_line_block.get_rect().x
                            new_y = prev_line_block.get_rect().y
                            new_width = prev_line_block.get_rect().width + 32
                            new_height = 32
                    
                    new_block = Block(new_x, new_y, new_width, new_height)
                    self.__blocks.append(new_block)
                    prev_line_block = new_block

    def __init_joysticks(self):
        self.__joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        
        for joystick in self.__joysticks:
            joystick.init()
            print("found joystick #" + str(joystick.get_id()) + " " + joystick.get_name())

    def __init_players(self):
        self.__players = []
        
        # TODO: vorsicht bei width = 0 und/oder height = 0 (fullscreen)
        half_width = self.__display.get_width() // 2
        height = self.__display.get_height()

        self.__players.append(self.__init_player(1, 0, half_width, height, "dev1.png", self.__joysticks[0]))
        self.__players.append(self.__init_player(2, half_width, half_width, height, "dev2.png", None))

    def __init_player(self, number, screen_x, screen_width, screen_height, image_file_name, joystick):
        player_rect = pygame.Rect(screen_x, 0, screen_width, screen_height)
        player_surface = self.__display.subsurface(player_rect)
        
        return Player(number, player_surface, image_file_name, self.__blocks, 1, joystick)

    def shutdown(self):
        self.__running = False

    def get_players(self):
        return self.__players

    def run(self):
        """The mainloop
        """

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

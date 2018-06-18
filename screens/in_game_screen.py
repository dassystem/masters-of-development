from screens.base import BaseScreen, BaseScreenEventHandler
from utils import Utils
import pygame
import tarentjumper
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

class InGameScreen(BaseScreen):
    def __init__(self, surface, players, joysticks):
        BaseScreen.__init__(
            self,
            surface,
            [InGameScreenKeyboardEventHandler(self, players),
             InGameScreenJoystickEventHandler(self, players, joysticks)])
        
        self.__players = players
        self.__player_surfaces = []
        
        self.__init_player_surfaces()
        
        self.__fill_blocks()
        
        for player in self.__players:
            player.set_blocks(self.__blocks)
        
        self.level = Block(50, 50)

    def __init_player_surfaces(self):
        split_screen = Utils.split_screen(self._surface)
        
        for i, screen in enumerate(split_screen):
            self.__player_surfaces.append(screen)
            self.__players[i].set_surface(screen)

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

    def render(self):
        if not self.is_active():
            return
        
        self._surface.fill(tarentjumper.TarentJumper.BACKGROUND_COLOR)
        
        for block in self.__blocks:
            block.render(self._surface)

        for player in self.__players:
            player.update()

        all_dead = True

        for player in self.__players:
            all_dead = all_dead and player.is_dead()
            
        self.set_active(not all_dead)

    def set_active(self, active):
        BaseScreen.set_active(self, active)
        
        if not self.is_active():
            for player in self.__players:
                player.reset()
            self.__init_player_surfaces()

    def get_player_surfaces(self):
        return self.__player_surfaces

class InGameScreenKeyboardEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, players):
        BaseScreenEventHandler.__init__(self, in_game_screen)
        self.__players = players

    def can_handle(self, event):
        if not BaseScreenEventHandler.can_handle(self, event):
            return False
        
        return event.type == pygame.KEYDOWN or event.type == pygame.KEYUP

    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.KEYDOWN:
            self.__handle_keydown_event(event)
        elif event.type == pygame.KEYUP:
            self.__handle_keyup_event(event)

    def __handle_keydown_event(self, event):
        if event.key == pygame.K_w:
            self.__players[0].jump()
        elif event.key == pygame.K_a:
            self.__players[0].move_left()
        elif event.key == pygame.K_d:
            self.__players[0].move_right()
        elif event.key == pygame.K_RIGHT:
            self.__players[1].move_right()
        elif event.key == pygame.K_LEFT:
            self.__players[1].move_left()
        elif event.key == pygame.K_UP:
            self.__players[1].jump()
        elif event.key == pygame.K_i:
            for player in self.__players:
                player.switch_debug()

    def __handle_keyup_event(self, event):
        if event.key == pygame.K_a or event.key == pygame.K_d:
            self.__players[0].stop()
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            self.__players[1].stop()

class InGameScreenJoystickEventHandler(BaseScreenEventHandler):
    VERTICAL_AXIS = 1
    HORIZONTAL_AXIS = 0
    UP = -1
    DOWN = 1
    LEFT = -1
    RIGHT = 1
    STOP = 0

    def __init__(self, in_game_screen, players, joysticks):
        BaseScreenEventHandler.__init__(self, in_game_screen)
        self.__players = players
        self.__joysticks = joysticks

    def can_handle(self, event):
        if not BaseScreenEventHandler.can_handle(self, event):
            return False
        
        return event.type == pygame.JOYAXISMOTION

    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.JOYAXISMOTION:
            self.__handle_axis_motion(event)

    def __handle_axis_motion(self, event):
        if event.axis > InGameScreenJoystickEventHandler.VERTICAL_AXIS:
            return

        player = Utils.get_player_from_joystick_event(event, self.__joysticks, self._players)

        if player is None:
            return

        if event.axis == InGameScreenJoystickEventHandler.VERTICAL_AXIS:
            self.__handle_vertical_axis_motion(event, player)
        elif event.axis == InGameScreenJoystickEventHandler.HORIZONTAL_AXIS:
            self.__handle_horizontal_axis_motion(event, player)

    def __handle_vertical_axis_motion(self, event, player):
        if self.__round_event_value(event) == InGameScreenJoystickEventHandler.UP:
            player.jump()

    def __handle_horizontal_axis_motion(self, event, player):
        event_value = self.__round_event_value(event)

        if event_value == InGameScreenJoystickEventHandler.LEFT:
            player.move_left()
        elif event_value == InGameScreenJoystickEventHandler.RIGHT:
            player.move_right()
        elif event_value == InGameScreenJoystickEventHandler.STOP:
            player.stop()

    def __round_event_value(self, event):
        return round(event.value, 0)

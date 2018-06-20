from screens.base import BaseScreen, BaseScreenEventHandler
from utils import Utils
import pygame
import masters_of_development
from block import Block
from utils.timer import Timer

class InGameScreen(BaseScreen):
    def __init__(self, surface, fonts, players, joysticks, seconds = 100):
        super(InGameScreen, self).__init__(
            surface,
            [InGameScreenKeyboardEventHandler(self, players),
             InGameScreenJoystickEventHandler(self, players, joysticks),
             InGameScreenTimerElapsedEventHandler(self)])
        
        self.__font = fonts["small"]
        
        self.__players = players
        self.__player_surfaces = []
        
        self.__init_player_surfaces()
        #self.__init_level()

        self.__timer = Timer(seconds)

    def __init_player_surfaces(self):
        split_screen = Utils.split_screen(self._surface)
        
        for i, screen in enumerate(split_screen):
            self.__player_surfaces.append(screen)
            self.__players[i].set_surface(screen)

    def render(self):
        if not self.is_active():
            return
        
        self._surface.fill(masters_of_development.MastersOfDevelopment.BACKGROUND_COLOR)

        for player in self.__players:
            player.update()

        all_dead = True

        for player in self.__players:
            all_dead = all_dead and player.is_dead()
            
        if all_dead:
            self.set_active(False)
            
        self.__render_timer()

    def __render_timer(self):
        text_surface_1 = self.__font.render("Time", True, masters_of_development.MastersOfDevelopment.TARENT_RED)
        text_rect_1 = Utils.center(text_surface_1, self._surface)
        self._surface.blit(text_surface_1, text_rect_1)

        text_surface_2 = self.__font.render(
            "{0:d}s".format(self.__timer.get_seconds_left()), True , masters_of_development.MastersOfDevelopment.TARENT_RED)
        text_rect_2 = Utils.center(text_surface_2, self._surface)
        text_rect_2.move_ip(0, text_rect_1.height)
        self._surface.blit(text_surface_2, text_rect_2)

    def set_active(self, active):
        super().set_active(active)
        
        if self.is_active():
            self._add_event_handler(self.__timer.get_event_handler())
            self.__timer.start()
            
            for player in self.__players:
                player.reset()
        else:
            self.__timer.stop()
            self._remove_event_handler(self.__timer.get_event_handler())

    def get_player_surfaces(self):
        return self.__player_surfaces

class InGameScreenKeyboardEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, players):
        super(InGameScreenKeyboardEventHandler, self).__init__(in_game_screen)
        self.__players = players

    def can_handle(self, event):
        if not super().can_handle(event):
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
        super(InGameScreenJoystickEventHandler, self).__init__(in_game_screen)
        self.__players = players
        self.__joysticks = joysticks

    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYBUTTONDOWN

    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.JOYAXISMOTION:
            self.__handle_axis_motion(event)
        elif event.type == pygame.JOYBUTTONDOWN:
            self.__handle_button_down(event)

    def __handle_axis_motion(self, event):
        if event.axis > InGameScreenJoystickEventHandler.VERTICAL_AXIS:
            return

        player = Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)

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

    def __handle_button_down(self, event):
        player = Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)

        if player is None:
            return

        player.jump()

class InGameScreenTimerElapsedEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen):
        super(InGameScreenTimerElapsedEventHandler, self).__init__(in_game_screen)

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        return event.type == Timer.ELASPED_EVENT

    def handle_event(self, event):
        if not self.can_handle(event):
            return

        if event.type == Timer.ELASPED_EVENT:
            self.get_screen().set_active(False)

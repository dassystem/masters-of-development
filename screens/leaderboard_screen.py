import pygame
from screens.base import BaseScreen, BaseScreenEventHandler
import utils.Utils
import leaderboard

NAMEN = []

class LeaderboardScreen(BaseScreen):
    def __init__(self, surface, players, joysticks, fonts, font_color, background_color, leaderboard):
        super(LeaderboardScreen, self).__init__(surface, [])
        self.__players = players
        self.__fonts = fonts
        self.__font = fonts["medium"]
        self.__font_color = font_color
        self.__background_color = background_color
        self.__screens = utils.Utils.split_screen(self._surface)
        
        self.__leaderboard = leaderboard
        
        self.__init_keyboards()
        
        cursors = []
        
        for keyboard in self.__keyboards:
            cursors.append(keyboard.get_cursor())
        
        super().add_event_handler(LeaderboardScreenJoystickEventHandler(self, players , cursors, joysticks))
        super().add_event_handler(LeaderboardScreenEventHandler(self, cursors))

    def __init_keyboards(self):
        self.__keyboards = []

        for i, screen in enumerate(self.__screens):
            keyboard = leaderboard.Keyboard(screen, self.__players[i], self.__leaderboard, self.__fonts, self.__font_color)
            self.__keyboards.append(keyboard)
    
    def render(self, seconds):
        if not self.is_active():
            return

        self._surface.fill(self.__background_color)

        active = False

        for keyboard in self.__keyboards:
            active = active or keyboard.is_active()
        
            if keyboard.is_active():
                keyboard.render()

        if not active:
            self.end_screen()

    def end_screen(self):
        self.set_active(False)

    def set_active(self, active):
        super().set_active(active)
        
        if self.is_active():
            self.__reset()

    def __reset(self):
        for keyboard in self.__keyboards:
            keyboard.reset()
       
        if self.__leaderboard.get_count() + len(self.__players) <= leaderboard.MAX_ENTRIES:
            for i in range(len(self.__players)):
                self.__keyboards[i].set_active(True)
        else:
            new_scores = self.__players.copy()
            new_scores.sort(key = lambda player: player.get_score(), reverse = True)
            
            new_entries = 0
            
            for new_score in new_scores:
                if self.__leaderboard.get_count() + new_entries < leaderboard.MAX_ENTRIES:
                    self.__keyboards[new_scores[0].get_number() - 1].set_active(True)
                    new_entries += 1
                    continue
                else:
                    for entry in self.__leaderboard.get_entries():
                        if entry.get_score() < new_score.get_score():
                            self.__keyboards[new_scores[0].get_number() - 1].set_active(True)
                            new_entries += 1
                                
                            break

class LeaderboardScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, leaderboard_screen, cursor):
        super(LeaderboardScreenEventHandler, self).__init__(leaderboard_screen)
        self.cursor = cursor

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        return event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.cursor[0].enter_letter()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            self.cursor[0].delete_letter()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            self.cursor[0].move_cursor_left()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            self.cursor[0].move_cursor_right()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            self.cursor[0].move_cursor_up()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            self.cursor[0].move_cursor_down()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            self.cursor[1].move_cursor_left()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            self.cursor[1].move_cursor_right()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            self.cursor[1].move_cursor_up()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            self.cursor[1].move_cursor_down()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
            self.cursor[1].enter_letter()

class LeaderboardScreenJoystickEventHandler(BaseScreenEventHandler):
    VERTICAL_AXIS = 1
    HORIZONTAL_AXIS = 0
    UP = -1
    DOWN = 1
    LEFT = -1
    RIGHT = 1
    STOP = 0

    def __init__(self, leaderboard_screen, players, cursors,  joysticks):
        super(LeaderboardScreenJoystickEventHandler, self).__init__(leaderboard_screen)
        self.__players = players
        self.__cursors = cursors
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
        if event.axis > LeaderboardScreenJoystickEventHandler.VERTICAL_AXIS:
            return

        cursor = utils.Utils.get_cursor_from_joystick_event(event, self.__joysticks, self.__cursors)

        if cursor is None:
            return

        if event.axis == LeaderboardScreenJoystickEventHandler.VERTICAL_AXIS:
            self.__handle_vertical_axis_motion(event, cursor)
        elif event.axis == LeaderboardScreenJoystickEventHandler.HORIZONTAL_AXIS:
            self.__handle_horizontal_axis_motion(event, cursor)

    def __handle_vertical_axis_motion(self, event, cursor):
        if self.__round_event_value(event) == LeaderboardScreenJoystickEventHandler.UP:
            cursor.move_cursor_up()
        if self.__round_event_value(event) == LeaderboardScreenJoystickEventHandler.DOWN:
            cursor.move_cursor_down()
    def __handle_horizontal_axis_motion(self, event, cursor):
        event_value = self.__round_event_value(event)

        if event_value == LeaderboardScreenJoystickEventHandler.LEFT:
            cursor.move_cursor_left()
        elif event_value == LeaderboardScreenJoystickEventHandler.RIGHT:
            cursor.move_cursor_right()

    def __round_event_value(self, event):
        return round(event.value, 0)

    def __handle_button_down(self, event):
        cursor = utils.Utils.get_cursor_from_joystick_event(event, self.__joysticks, self.__cursors)

        if cursor is None:
            return

        cursor.enter_letter()

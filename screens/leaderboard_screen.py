import pygame
from screens.base import BaseScreen, BaseScreenEventHandler
import utils


class LeaderboardScreen(BaseScreen):
    def __init__(self, surface, players, joysticks,  cursors,  fonts, font_color, background_color):
        super(LeaderboardScreen, self).__init__(surface, [LeaderboardScreenJoystickEventHandler(self, players , cursors, joysticks)])
        self.__players = players
        self.__font = fonts["small"]
        self.__font_color = font_color
        self.__background_color = background_color
        self.screens = utils.Utils.split_screen(self._surface)
        self.__cursors = cursors
        self.init_cursor()
        super()._add_event_handler(LeaderboardScreenEventHandler(self, self.__cursors))

    def init_cursor(self):
        for index , screen in enumerate(self.screens):
            #a little trick to position the cursor where a letter would be
            text = self.__font.render("A", True, self.__font_color)
            rect_text = utils.Utils.center(text, screen)
            self.__cursors[index].set_x(rect_text.x)
            self.__cursors[index].set_y(rect_text.y + 10)

    def render(self):
        if not self.is_active():
            return

        self._surface.fill(self.__background_color)

        for index, screen in enumerate(self.screens):
            self.render_keyboard(screen)
            self.__cursors[index].render(screen)

    def render_keyboard(self, player_area):
        #TODO to get the "selected" status of a letter use coliderect
        #TODO catch movement out of bounds
        coords = [CoordLetter("A", 0), CoordLetter("B", 0), CoordLetter("C", 0), CoordLetter("D", 0), CoordLetter("E", 0), CoordLetter("F", 0), CoordLetter("G", 0),
                  CoordLetter("H", 0),CoordLetter("I", 0), CoordLetter("J", 0), CoordLetter("K", 1), CoordLetter("L", 1), CoordLetter("M", 1), CoordLetter("N", 1),
                  CoordLetter("O", 1), CoordLetter("P", 1), CoordLetter("Q", 1), CoordLetter("R", 1), CoordLetter("S", 1), CoordLetter("T", 1),
                  CoordLetter("U", 2), CoordLetter("V", 2), CoordLetter("W", 2), CoordLetter("X", 2), CoordLetter("Y", 2), CoordLetter("Z", 2), CoordLetter(":", 2),
                  CoordLetter(".", 2), CoordLetter("!", 2), CoordLetter("?", 2)]

        level = 0
        xoffset = 0
        for index, letter in enumerate(coords):
                if letter.level > level:
                    level = letter.level
                    xoffset = 0

                text = self.__font.render(letter.symbol, True, self.__font_color)
                rect_text = utils.Utils.center(text, player_area)
                rect_text.move_ip(xoffset, letter.level * 20)

                player_area.blit(text, rect_text)
                xoffset += 20



class LeaderboardScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, leaderboard_screen, cursor):
        super(LeaderboardScreenEventHandler, self).__init__(leaderboard_screen)
        self.cursor = cursor

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        return event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN

    def handle_event(self, event):
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.get_screen().set_active(False)

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
        # TODO select the letter not implemented yet
        test = 0




class CoordLetter():
    def __init__(self, symbol, level):
        self.level = level
        self.symbol = symbol

class Cursor():
    def __init__(self):
        self.image = pygame.Surface((10, 3))
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect(x = 0, y = 0)
        self.x_limit = 0
        self.y_limit = 0

    def render(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)

    def move_cursor_right(self):
        self.rect.x += 20

    def move_cursor_left(self):
        self.rect.x -= 20

    def move_cursor_up(self):
        self.rect.y -= 20

    def move_cursor_down(self):
        self.rect.y += 20

    def set_x(self, x):
        self.rect.x = x

    def set_y(self, y):
        self.rect.y = y
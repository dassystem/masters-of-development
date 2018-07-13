import pygame
from screens.base import BaseScreen, BaseScreenEventHandler
import utils.Utils
import leaderboard
import masters_of_development

NAMEN = []
TEXT_COLOR = pygame.Color(204, 0, 0)

class LeaderboardScreen(BaseScreen):
    def __init__(self, surface, players, joysticks, fonts, font_color, background_color, leaderboard):
        super(LeaderboardScreen, self).__init__(surface, [])
        self.__players = players
        self.__fonts = fonts
        self.__font = fonts["medium"]
        self.__font_color = font_color
        self.__background_color = background_color
        self.screens = utils.Utils.split_screen(self._surface)
        self.__leaderboard = leaderboard
        
        self.__init_cursors()
        
        super().add_event_handler(LeaderboardScreenJoystickEventHandler(self, players , self.__cursors.sprites(), joysticks))
        super().add_event_handler(LeaderboardScreenEventHandler(self, self.__cursors.sprites()))

    def __init_cursors(self):
        self.__cursors = pygame.sprite.OrderedUpdates()
        
        for index, screen in enumerate(self.screens):
            #a little trick to position the cursor where a letter would be
            text = self.__font.render("A", True, self.__font_color)
            rect_text = utils.Utils.center(text, screen)

            rect_text.x += index * screen.get_width()

            self.__cursors.add(
                leaderboard.Cursor(
                    self.__players[index],
                    self.__leaderboard,
                    rect_text.x - 100,
                    round(rect_text.y + leaderboard.LETTER_GAP / 1.5),
                    rect_text.width))

    def render(self, seconds):
        if not self.is_active():
            return

        self._surface.fill(self.__background_color)

        # if both players entered name switch to the "highscore" board
        if not self.__cursors.sprites()[0].get_active_status() and not self.__cursors.sprites()[1].get_active_status():
            for index, screen in enumerate(self.screens):
                self.render_leaderboard(screen, self.__players[index])
            return

        for index, screen in enumerate(self.screens):
            self.render_keyboard(screen, self.__cursors.sprites()[index])

        self.__cursors.draw(self._surface)

    def render_keyboard(self, player_area, cursor):
        coords = [CoordLetter("A", 0), CoordLetter("B", 0), CoordLetter("C", 0), CoordLetter("D", 0), CoordLetter("E", 0), CoordLetter("F", 0), CoordLetter("G", 0),
                  CoordLetter("H", 0),CoordLetter("I", 0), CoordLetter("J", 0), CoordLetter("K", 1), CoordLetter("L", 1), CoordLetter("M", 1), CoordLetter("N", 1),
                  CoordLetter("O", 1), CoordLetter("P", 1), CoordLetter("Q", 1), CoordLetter("R", 1), CoordLetter("S", 1), CoordLetter("T", 1),
                  CoordLetter("U", 2), CoordLetter("V", 2), CoordLetter("W", 2), CoordLetter("X", 2), CoordLetter("Y", 2), CoordLetter("Z", 2), CoordLetter(":", 2),
                  CoordLetter(".", 2), CoordLetter("←", 2), CoordLetter("→", 2)]

        level = 0
        xoffset = 0
        x_start, x_end, y_start , y_end = 0, 0, 0, 0
        start_rec = None

        for index, letter in enumerate(coords):
                if letter.level > level:
                    level = letter.level
                    xoffset = 0

                text = self.__font.render(letter.symbol, True, self.__font_color)
                rect_text = utils.Utils.center_with_offset(text, player_area, 100, 0)
                if index == 0:
                    x_start = rect_text.x
                    y_start = rect_text.y
                rect_text.move_ip(xoffset, letter.level * leaderboard.LETTER_GAP)

                if index == len(coords)-1:
                    x_end = rect_text.x
                    y_end = rect_text.y

                player_area.blit(text, rect_text)
                xoffset += leaderboard.LETTER_GAP

                if cursor.rect.colliderect(rect_text):
                    cursor.set_selected(letter.symbol)

                if index == 0:
                    # start_rec is used to position the enter name field
                    start_rec = rect_text

        name = ''.join(cursor.get_name())
        enter_name = self.__font.render("Your name: " + name, True, self.__font_color)
        player_area.blit(enter_name, (start_rec.x - 100, start_rec.y -100))

        hint = self.__fonts["small"].render("Use ← to delete a character ", True, self.__font_color)
        hint_rect = utils.Utils.center_with_offset(hint, player_area, 0, -150)

        hint_2 = self.__fonts["small"].render("or → to confirm your name", True, self.__font_color)
        hint_rect2 = hint_rect.copy()
        hint_rect2.y += hint_rect.height

        player_area.blit(hint,hint_rect)
        player_area.blit(hint_2, hint_rect2)

        #sets the horizontal and vertical limit where the cursor can move to select letters
        cursor.set_horizontal_limit(x_start, x_end)
        cursor.set_vertical_limit(y_start, y_end )

    def render_leaderboard(self, player_area, player):

        screen_height = player_area.get_rect().height
        screen_width = player_area.get_rect().width

        title = self.render_text("HIGH SCORES", "medium")
        title_position = utils.Utils.center_with_offset(title, player_area, 0, screen_height / 2.5)
        rank = self.render_text("RANK", "medium")

        rank_position = utils.Utils.center_with_offset(rank, player_area, screen_width / 3, screen_height / 3.5)

        score = self.render_text("SCORE", "medium")

        column_gap = round(player_area.get_rect().width / 50)
        score_postion = utils.Utils.center_with_offset(score, player_area, column_gap, screen_height / 3.5)
        name = self.render_text("NAME", "medium")
        name_postion = utils.Utils.center_with_offset(name, player_area, (column_gap - score_postion.x), screen_height / 3.5)

        player_area.blit(title, title_position)
        player_area.blit(rank, rank_position)
        player_area.blit(score, score_postion)
        player_area.blit(name, name_postion)

        self.fill_leaderboard(player_area, rank_position.x, score_postion.x, name_postion.x, rank_position.y, player)

    def fill_leaderboard(self, player_area, rankx, scorex, namex, height, player):
        level = 0
        for index, entry in enumerate(self.__leaderboard.get_entries()):
            if index == leaderboard.MAX_ENTRIES:
                break

            highlight = False
            number = index + 1
            level = height + number * 50

            #If the player is in the top leaderboard he gets highlighted
            if (entry.get_name(), entry.get_score()) == (player.get_player_name(), player.get_score()):
                highlight = True
                color = masters_of_development.MastersOfDevelopment.YELLOW
            else:
                color = masters_of_development.MastersOfDevelopment.TARENT_RED

            rank = self.render_text(str(number), "medium", color)
            rank_pos = pygame.Rect(rankx + 30, level, rank.get_width(), rank.get_height())

            score = self.render_text(str(entry.get_score()), "medium", color)
            score_pos = pygame.Rect(scorex, level, rank.get_width(), rank.get_height())

            name = self.render_text(entry.get_name(), "medium", color)
            name_pos = pygame.Rect(namex - 30, level, name.get_width(), name.get_height())

            if highlight == True:
                pygame.draw.line(player_area, color, (rank_pos.x, rank_pos.bottom), (name_pos.right, rank_pos.bottom), 5)

            player_area.blit(rank, rank_pos)
            player_area.blit(score, score_pos)
            player_area.blit(name, name_pos)

        #fetch the current rank the player achieved
        for index, entry in enumerate(self.__leaderboard.get_entries()):
            rank = 0
            if (entry.get_name(), entry.get_score()) == (player.get_player_name(), player.get_score()):
                rank = index + 1
                break

        player_text = self.render_text("Your placement " + player.get_player_name() + ": ", "medium")
        player_text_pos = utils.Utils.center_with_offset(player_text, player_area, 50, -100)
        player_rank = self.render_text("Rank " + str(rank), "medium")
        player_rank_pos = pygame.Rect(player_text_pos.x, player_text_pos.y + player_text_pos.height + 20, player_rank.get_width(), player_rank.get_height())
        player_points = self.render_text(" with a score of " + str(player.get_score()), "medium")
        player_points_pos = pygame.Rect(player_rank_pos.x + player_rank_pos.width, player_rank_pos.y, player_points.get_width(), player_points.get_height())

        player_area.blit(player_text, player_text_pos)
        player_area.blit(player_rank, player_rank_pos)
        player_area.blit(player_points, player_points_pos)

    def render_text(self, text, size, color=TEXT_COLOR):
        return self.__fonts[size].render(text, True, color)

    def end_screen(self):
        self.set_active(False)

    def set_active(self, active):
        super().set_active(active)
        
        if self.is_active():
            self.__reset()

    def __reset(self):
        for i in range(len(self.__players)):
            self.__cursors.sprites()[i].reset()
            self.__cursors.sprites()[i].set_active(False)


        for i in range(len(self.__players)):
            self.__cursors.sprites()[i].set_active(True)
                 
class CoordLetter(object):
    def __init__(self, symbol, level):
        self.level = level
        self.symbol = symbol

class LeaderboardScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, leaderboard_screen, cursor):
        super(LeaderboardScreenEventHandler, self).__init__(leaderboard_screen)
        self.cursor = cursor
        self.screen = leaderboard_screen

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        return event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:

            if not self.cursor[0].get_active_status() and not self.cursor[1].get_active_status():
                self.screen.set_active(False)

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
        self.__screen = leaderboard_screen

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


        if not self.__cursors[0].get_active_status() and not self.__cursors[1].get_active_status():
            self.__screen.set_active(False)

        cursor.enter_letter()


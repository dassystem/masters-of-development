import pygame
from screens.base import BaseScreen, BaseScreenEventHandler
import utils.Utils
import utils.db_connector

LETTER_GAP = 30
NAMEN = []

class LeaderboardScreen(BaseScreen):
    LEADERBOARD_SIZE = 5
    
    def __init__(self, surface, players, joysticks, fonts, font_color, background_color):
        super(LeaderboardScreen, self).__init__(surface, [])
        self.__players = players
        self.__fonts = fonts
        self.__font = fonts["medium"]
        self.__font_color = font_color
        self.__background_color = background_color
        self.screens = utils.Utils.split_screen(self._surface)
        self.__db_connector = utils.db_connector.DbConnector("assets/leaderboard.db")
        self.__db_connector.connect()

        self.__init_board()
        
        self.__init_cursors()
        
        super().add_event_handler(LeaderboardScreenJoystickEventHandler(self, players , self.__cursors, joysticks))
        super().add_event_handler(LeaderboardScreenEventHandler(self, self.__cursors))

    def __init_board(self):
        c = self.__db_connector.get_cursor()
        
        self.__board = []
                
        for row in c.execute("SELECT id, name, score FROM leaderboard ORDER BY score DESC"):
            self.__board.append(LeaderboardEntry(row[0], row[1], row[2]))
            
    def __init_cursors(self):
        self.__cursors = []
        
        for index, screen in enumerate(self.screens):
            #a little trick to position the cursor where a letter would be
            text = self.__font.render("A", True, self.__font_color)
            rect_text = utils.Utils.center(text, screen)

            self.__cursors.append(
                Cursor(
                    self.__players[index],
                    self.__db_connector,
                    self.__board,
                    rect_text.x - 100,
                    round(rect_text.y + LETTER_GAP / 1.5),
                    rect_text.width))

    def render(self):
        if not self.is_active():
            return

        if not self.__cursors[0].get_active_status() and not self.__cursors[1].get_active_status():
            self.end_screen()

        self._surface.fill(self.__background_color)

        for index, screen in enumerate(self.screens):
            self.render_keyboard(screen, self.__cursors[index])
            self.__cursors[index].render(screen)

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
                rect_text.move_ip(xoffset, letter.level * LETTER_GAP)

                if index == len(coords)-1:
                    x_end = rect_text.x
                    y_end = rect_text.y

                player_area.blit(text, rect_text)
                xoffset += LETTER_GAP

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

    def end_screen(self):
        self.set_active(False)

    def set_active(self, active):
        super().set_active(active)
        
        if self.is_active():
            self.__reset()

    def __reset(self):
        for i in range(len(self.__players)):
            self.__cursors[i].reset()
            self.__cursors[i].set_active(False)
        
        if len(self.__board) + len(self.__players) <= LeaderboardScreen.LEADERBOARD_SIZE:
            for i in range(len(self.__players)):
                self.__cursors[i].set_active(True)
        else:
            new_scores = self.__players.copy()
            new_scores.sort(key = lambda player: player.get_score(), reverse = True)
            
            new_entries = 0
            
            for new_score in new_scores:
                if len(self.__board) + new_entries < LeaderboardScreen.LEADERBOARD_SIZE:
                    self.__cursors[new_scores[0].get_number() - 1].set_active(True)
                    new_entries += 1
                    continue
                else:
                    for entry in self.__board.copy():
                        if entry.get_score() < new_score.get_score():
                            self.__cursors[new_scores[0].get_number() - 1].set_active(True)
                            new_entries += 1
                            
                            if len(self.__board) + new_entries > LeaderboardScreen.LEADERBOARD_SIZE:
                                last_entry = self.__board.pop()
                                c = self.__db_connector.get_cursor()
                                c.execute("DELETE FROM leaderboard WHERE id = :id", {"id": last_entry.get_id()})
                                self.__db_connector.commit()
                                
                            break
                 
class LeaderboardEntry(object):
    def __init__(self, identity, name, score):
        self.__id = identity
        self.__name = name
        self.__score = score
        
    def get_id(self):
        return self.__id
    
    def get_name(self):
        return self.__name
        
    def get_score(self):
        return self.__score

class CoordLetter(object):
    def __init__(self, symbol, level):
        self.level = level
        self.symbol = symbol

# TODO make Cursor a sprite
class Cursor(object):
    def __init__(self, player, db_connector, board, initial_x, initial_y, initial_width):
        self.image = pygame.Surface((10, 3))
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect(x = 0, y = 0)
        self.symbol = ""
        self.__initial_x = initial_x
        self.__initial_y = initial_y
        self.__initial_width = initial_width
        
        self.rect.x = initial_x
        self.rect.y = initial_y
        self.rect.width = initial_width
        
        self.__x_start_limit = 0
        self.__x_end_limit = 0
        self.__y_end_limit = 0
        self.__y_start_limit = 0
        self.__name = []
        self.__namelimit = 6
        self.__active = True
        self.__player = player
        self.__db_connector = db_connector
        self.__board = board

    def reset(self):
        self.rect = self.image.get_rect(x = 0, y = 0)
        self.rect.x = self.__initial_x
        self.rect.y = self.__initial_y
        self.rect.width = self.__initial_width
        self.symbol = ""
        self.__name = []        

    def __save(self):
        if self.__active == False:
            return

        self.__active = False
        player_info = (''.join(self.__name), self.__player.get_score())
        
        self.__db_connector.execute_with_parameter("INSERT INTO leaderboard (name, score) VALUES (?,?)", player_info)
        self.__db_connector.commit()
        pk = self.__db_connector.get_cursor().lastrowid
        self.__board.append(LeaderboardEntry(pk, player_info[0], player_info[1]))
        self.__board.sort(key = lambda entry: entry.get_score(), reverse = True)

    def render(self, surface):
        if self.__active == False:
            return
        pygame.draw.rect(surface, (0, 0, 0), self.rect)

    def move_cursor_right(self):
        if self.__active == False:
            return
        if self.rect.x < self.__x_end_limit:
            self.rect.x += LETTER_GAP

    def move_cursor_left(self):
        if self.__active == False:
            return
        if self.rect.x > self.__x_start_limit:
            self.rect.x -= LETTER_GAP

    def move_cursor_up(self):
        if self.__active == False:
            return
        if self.rect.y - LETTER_GAP > self.__y_start_limit:
            self.rect.y -= LETTER_GAP

    def move_cursor_down(self):
        if self.__active == False:
            return
        if self.rect.y < self.__y_end_limit:
            self.rect.y += LETTER_GAP

    def set_vertical_limit(self, starty, endy):
        self.__y_start_limit = starty
        self.__y_end_limit = endy

    def set_horizontal_limit(self, startx, endx):
        self.__x_start_limit = startx
        self.__x_end_limit = endx

    def set_selected(self, symbol):
        if self.__active == False:
            return
        self.symbol = symbol

    def enter_letter(self):
        if self.__active == False:
            return

        if self.symbol == "→":
            self.__save()
            return

        if self.symbol == "←":
            self.delete_letter()
            return

        if len(self.__name) < self.__namelimit:
            self.__name.append(self.symbol)

    def delete_letter(self):
        if self.__active == False:
            return
        if len(self.__name) > 0:
            self.__name.remove(self.__name[len(self.__name) - 1])

    def get_name(self):
        return self.__name

    def get_active_status(self):
        return self.__active
    
    def set_active(self, active):
        self.__active = active

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

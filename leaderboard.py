import screens.base
import pygame
import string
import utils.db_connector

from colors import DARKER_GRAY, WHITE
from commons.text_sprite import TextSprite
from pygame import Surface
from pygame.color import Color
from pygame.event import Event
from pygame.font import Font
from pygame.joystick import Joystick
from pygame.sprite import Sprite
from typing import Dict, List, Tuple


LETTER_GAP: int = 30
MAX_ENTRIES: int = 5


class Leaderboard(object):
    def __init__(self) -> None:
        self.__db_connector = utils.db_connector.DbConnector("assets/leaderboard.db")
        self.__db_connector.connect()

        self.__init_board()

    def __init_board(self) -> None:
        c = self.__db_connector.get_cursor()

        self.__board = []

        for row in c.execute("SELECT id, name, score FROM leaderboard ORDER BY score DESC"):
            self.__board.append(LeaderboardEntry(row[0], row[1], row[2]))

    def get_count(self) -> int:
        return len(self.__board)

    def get_entries(self) -> Tuple["LeaderboardEntry"]:
        return tuple(self.__board)

    def add_entry(self, player_info: Tuple[str, int]) -> None:
        if len(self.__board) >= MAX_ENTRIES:
            last_entry = self.__board[-1]

            if last_entry.get_score() > player_info[1]:
                return

            c = self.__db_connector.get_cursor()
            c.execute("DELETE FROM leaderboard WHERE id = :id", {"id": last_entry.get_id()})
            self.__db_connector.commit()

            self.__board.pop()

        self.__db_connector.execute_with_parameter("INSERT INTO leaderboard (name, score) VALUES (?,?)", player_info)
        self.__db_connector.commit()
        pk = self.__db_connector.get_cursor().lastrowid
        self.__board.append(LeaderboardEntry(pk, player_info[0], player_info[1]))
        self.__board.sort(key=lambda entry: entry.get_score(), reverse=True)


class LeaderboardEntry(object):
    def __init__(self, identity: int, name: str, score: int) -> None:
        self.__id = identity
        self.__name = name
        self.__score = score

    def get_id(self) -> int:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_score(self) -> int:
        return self.__score


INSTANCE: Leaderboard = Leaderboard()


class Keyboard(object):
    key_mappings_1 = {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,
        "delete": pygame.K_BACKSPACE,
        "enter": pygame.K_RETURN
    }

    key_mappings_2 = {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "delete": pygame.K_DELETE,
        "enter": pygame.K_KP_ENTER
    }

    def __init__(
            self,
            screen: "screens.base.BaseScreen",
            surface: Surface,
            player: "in_game.play_area.sprites.player.Player",
            fonts: Dict[str, Font],
            font_color: Color,
            columns: int=10) -> None:
        self.__screen = screen
        self.__surface = surface
        self.__player = player
        self.__fonts = fonts
        self.__font_color = font_color
        self.__columns = columns

        self.__name = ""
        self.__max_name_length = 6
        self.__active = False

        self.__init_letters()
        self.__init_cursor()
        self.__init_name_display()
        self.__init_hints()
        self.__init_event_listeners()

    def __init_letters(self) -> None:
        self.__letters = pygame.sprite.OrderedUpdates()

        letters = []
        letters.extend(string.ascii_uppercase)
        letters.extend([":", ".", "←", "→"])

        x = self.__surface.get_width() // 2 - LETTER_GAP * 5
        y = self.__surface.get_height() // 2 - LETTER_GAP

        for i, letter in enumerate(letters):
            row = i // self.__columns
            column = i % self.__columns
            coord_letter = CoordLetter(letter, row, column, (x, y), self.__fonts["medium"], self.__font_color)
            self.__letters.add(coord_letter)

    def __init_cursor(self) -> None:
        self.__cursor = pygame.sprite.GroupSingle()

        first_letter = self.get_letters()[0]

        rows = round(len(self.get_letters()) / self.__columns)

        cursor = Cursor(
            self, first_letter.rect.x, first_letter.rect.y - 5, first_letter.rect.width, rows, self.__columns
        )
        self.__cursor.add(cursor)

    def __init_name_display(self) -> None:
        self.__name_display = pygame.sprite.GroupSingle()

        first_letter = self.get_letters()[0]

        x = first_letter.rect.x
        y = first_letter.rect.y - 100

        name_display = NameDisplay((x, y), self.__fonts["medium"], self.__font_color)
        self.__name_display.add(name_display)

    def __init_hints(self) -> None:
        self.__hints = pygame.sprite.OrderedUpdates()

        first_letter = self.get_letters()[0]
        last_letter = self.get_letters()[-1]

        x = first_letter.rect.x
        y = last_letter.rect.bottom + 150

        hint_1 = TextSprite((x, y), "Use ← to delete a character", self.__fonts["small"], self.__font_color)
        self.__hints.add(hint_1)

        y += hint_1.rect.height

        hint_2 = TextSprite((x, y), "or → to confirm your name", self.__fonts["small"], self.__font_color)
        self.__hints.add(hint_2)

    def __init_event_listeners(self) -> None:
        self.__event_handlers = []

        if self.__player.get_joystick() is not None:
            self.__event_handlers.append(JoystickEventHandler(self.__screen, self, self.__player.get_joystick()))

        if self.__player.get_number() == 1:
            keyboard_event_handler = KeyboardEventHandler(self.__screen, self, Keyboard.key_mappings_1)
        else:
            keyboard_event_handler = KeyboardEventHandler(self.__screen, self, Keyboard.key_mappings_2)

        self.__event_handlers.append(keyboard_event_handler)

    def render(self) -> None:
        if not self.__active:
            return

        self.__name_display.draw(self.__surface)
        self.__letters.draw(self.__surface)
        self.__cursor.draw(self.__surface)
        self.__hints.draw(self.__surface)

    def reset(self) -> None:
        self.get_cursor().reset()
        self.get_name_display().reset()

    def enter_letter(self, row: int, column: int) -> None:
        index = row * self.__columns + column
        coord_letter = self.get_letters()[index]
        symbol = coord_letter.get_symbol()

        if symbol == "→":
            self.save()
            return

        if symbol == "←":
            self.delete_letter()
            return

        if len(self.get_name_display().get_name()) < self.__max_name_length:
            new_name = self.get_name_display().get_name() + symbol
            self.get_name_display().update(new_name)

    def delete_letter(self) -> None:
        current_name = self.get_name_display().get_name()

        if len(current_name) > 0:
            new_name = current_name[:-1]
            self.get_name_display().update(new_name)

    def save(self) -> None:
        self.__active = False
        self.get_cursor().set_active(False)

        player_info = (''.join(self.get_name_display().get_name()), self.__player.get_score())

        INSTANCE.add_entry(player_info)

    def get_name_display(self) -> Sprite:
        return self.__name_display.sprite

    def get_letters(self) -> List[Sprite]:
        return self.__letters.sprites()

    def get_cursor(self) -> Sprite:
        return self.__cursor.sprite

    def is_active(self) -> bool:
        return self.__active

    def set_active(self, active: bool) -> None:
        self.__active = active
        self.get_cursor().set_active(active)

    def get_event_handlers(self) -> List["screens.baseBaseScreenEventHandler"]:
        return self.__event_handlers


class CoordLetter(Sprite):
    def __init__(
            self,
            symbol: str,
            row: int,
            column: int,
            start_topleft: Tuple[int, int],
            font: Font,
            font_color: Color) -> None:
        # IMPORTANT: call the parent class (Sprite) constructor
        super(CoordLetter, self).__init__()

        self.__row = row
        self.__column = column
        self.__symbol = symbol
        self.__font = font
        self.__font_color = font_color

        self.image = self.__font.render(self.__symbol, True, self.__font_color)
        self.rect = self.image.get_rect(topleft=start_topleft)

        self.rect.move_ip(self.__column * LETTER_GAP, self.__row * LETTER_GAP)

    def get_symbol(self) -> str:
        return self.__symbol


class Cursor(Sprite):
    def __init__(
            self,
            keyboard: Keyboard,
            initial_x: int,
            initial_y: int,
            initial_width: int,
            rows: int,
            columns: int) -> None:
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Cursor, self).__init__()

        self.image = pygame.Surface((initial_width, 3))
        self.image.fill(WHITE)
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect(x=0, y=0)

        self.__initial_x = initial_x
        self.__initial_y = initial_y + LETTER_GAP

        self.rect.x = initial_x
        self.rect.y = initial_y

        self.__rows = rows
        self.__columns = columns

        self.__current_row = 0
        self.__current_column = 0

        self.__active = True
        self.__keyboard = keyboard
        self.__columns = columns
        self.symbol = None

    def reset(self) -> None:
        self.rect.x = self.__initial_x
        self.rect.y = self.__initial_y
        self.__current_row = 0
        self.__current_column = 0
        self.__active = False

    def move_cursor_right(self) -> None:
        if not self.__active:
            return

        if self.__current_column < self.__columns - 1:
            self.__current_column += 1
            self.rect.x = self.__initial_x + self.__current_column * LETTER_GAP

    def move_cursor_left(self) -> None:
        if not self.__active:
            return

        if self.__current_column > 0:
            self.__current_column -= 1
            self.rect.x = self.__initial_x + self.__current_column * LETTER_GAP

    def move_cursor_up(self) -> None:
        if not self.__active:
            return

        if self.__current_row > 0:
            self.__current_row -= 1
            self.rect.y = self.__initial_y + self.__current_row * LETTER_GAP

    def move_cursor_down(self) -> None:
        if not self.__active:
            return

        if self.__current_row < self.__rows - 1:
            self.__current_row += 1
            self.rect.y = self.__initial_y + self.__current_row * LETTER_GAP

    def set_selected(self, symbol: str) -> None:
        if not self.__active:
            return

        self.symbol = symbol

    def enter_letter(self) -> None:
        if not self.__active:
            return

        self.__keyboard.enter_letter(self.__current_row, self.__current_column)

    def get_active_status(self) -> bool:
        return self.__active

    def set_active(self, active: bool) -> None:
        self.__active = active

        if self.__active:
            self.image.fill(WHITE)
        else:
            self.image.fill(DARKER_GRAY)


class NameDisplay(TextSprite):
    def __init__(self, initial_pos: Tuple[int, int], font: Font, font_color: Color) -> None:
        self.__name = ""
        # IMPORTANT: call the parent class (Sprite) constructor
        super(NameDisplay, self).__init__(initial_pos, self.__name, font, font_color)

    def update(self, name: str) -> None:
        self.__name = name
        super().update("Your name: {0}".format(self.__name))

    def reset(self) -> None:
        self.update("")

    def get_name(self) -> str:
        return self.__name


class JoystickEventHandler(screens.base.BaseJoystickEventHandler):
    def __init__(self, screen: "screens.base.BaseScreen", keyboard: Keyboard, joystick: Joystick) -> None:
        super(JoystickEventHandler, self).__init__(screen, joystick)
        self.__keyboard = keyboard

    def can_handle(self, event: Event) -> bool:
        return super().can_handle(event) and self.__keyboard.is_active()

    def _on_up(self, event: Event) -> None:
        self.__keyboard.get_cursor().move_cursor_up()

    def _on_down(self, event: Event) -> None:
        self.__keyboard.get_cursor().move_cursor_down()

    def _on_left(self, event: Event) -> None:
        self.__keyboard.get_cursor().move_cursor_left()

    def _on_right(self, event: Event) -> None:
        self.__keyboard.get_cursor().move_cursor_right()

    def _on_button_down(self, event: Event) -> None:
        self.__keyboard.get_cursor().enter_letter()


class KeyboardEventHandler(screens.base.BaseKeyboardEventHandler):
    def __init__(self, screen: "screens.base.BaseScreen", keyboard: Keyboard, key_mappings: Dict[str, int]) -> None:
        super(KeyboardEventHandler, self).__init__(screen, key_mappings, [pygame.KEYDOWN])
        self.__keyboard = keyboard

    def can_handle(self, event: Event) -> bool:
        return super().can_handle(event) and self.__keyboard.is_active()

    def handle_event(self, event: Event) -> None:
        if self._key_mappings["up"] == event.key:
            self.__keyboard.get_cursor().move_cursor_up()
        elif self._key_mappings["down"] == event.key:
            self.__keyboard.get_cursor().move_cursor_down()
        elif self._key_mappings["left"] == event.key:
            self.__keyboard.get_cursor().move_cursor_left()
        elif self._key_mappings["right"] == event.key:
            self.__keyboard.get_cursor().move_cursor_right()
        elif self._key_mappings["delete"] == event.key:
            self.__keyboard.delete_letter()
        elif self._key_mappings["enter"] == event.key:
            self.__keyboard.get_cursor().enter_letter()

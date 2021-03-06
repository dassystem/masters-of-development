from constants import PIXEL_PER_SECOND
from in_game.play_area.sprites.block import Block
from in_game.play_area.sprites.power_up import PowerUp
from in_game.play_area.sprites.power_up_jump import PowerUpJump
from pygame import Rect, Surface
from pygame.font import Font
from pygame.joystick import Joystick
from pygame.mixer import Sound
from pygame.sprite import Sprite
from typing import Dict, List


class Player(Sprite):
    """A sprite representing a player."""
    NORMAL_JUMP_HEIGHT: int = 10
    SPEED: int = 5
    VELOCITY: int = 5

    def __init__(
            self,
            number: int,
            images: Dict[str, Surface],
            gravity: int,
            joystick: Joystick,
            sounds: Dict[str, Sound],
            fonts: Dict[str, Font],
            fps: int) -> None:
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Player, self).__init__()

        self.__number = number
        self.__images = images

        self.__fps = fps
        self.__gravity = gravity
        self.__joystick = joystick
        self.__sounds = sounds
        self.__font = fonts["small"]
        self.__dead = False
        self.__velocity = 0
        self.__falling = False
        self.__jumping = False
        self.__on_block = None
        self.__speed = Player.SPEED
        self.__initial_jump_height = Player.NORMAL_JUMP_HEIGHT
        self.__jump_height = self.__initial_jump_height
        self.__move = None
        self.__ready = False
        self.__highest_block_level = 0
        self.__level = 0
        self.__score = 0
        self.__power_ups = {}
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        self.image = None
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = None
        self.__surface_rect = None

    def reset(self) -> None:
        """Resets the player state so that the player can be reused in a new game round."""
        self.__dead = False
        self.__velocity = 0
        self.__falling = False
        self.__jumping = False
        self.__on_block = None
        self.__speed = Player.SPEED
        self.__initial_jump_height = Player.NORMAL_JUMP_HEIGHT
        self.__jump_height = self.__initial_jump_height
        self.__move = None
        self.__ready = False
        self.__highest_block_level = 0
        self.__level = 0
        self.__score = 0
        self.__power_ups = {}
        self.image = self.__images["in_game_screen_player"]
        self.rect = self.image.get_rect()

    def update(self, seconds: int) -> None:
        """Updates the player state. Does nothing if player is dead.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__dead:
            self.__update_alive(seconds)

    def __update_alive(self, seconds: int) -> None:
        """Updates the player state while he is stil alive."""
        if self.__jumping:
            self.__jump_height = self.__jump_height - 2

            if self.__jump_height <= 0:
                self.__jump_height = self.__initial_jump_height
                self.__jumping = False
                self.__falling = True
                self.__velocity = Player.VELOCITY
                self.image = self.__images["in_game_screen_player"]
                self.rect = self.image.get_rect(topleft=self.rect.topleft)

        if self.__on_block is not None:
            self.__check_still_on_block()

        if self.__falling:
            self.__move_down(seconds)
        elif self.__jumping:
            self.__move_up(seconds)

        if self.__move is not None:
            if self.__move == "left":
                self.__move_left(seconds)
            elif self.__move == "right":
                self.__move_right(seconds)

        self.__dead = self.__falling and self.rect.top > self.__surface_rect.bottom

    def __move_down(self, seconds: int) -> None:
        """Updates the player state to reflect a down move (aka falling)."""
        self.rect.move_ip(0, self.__velocity * round(PIXEL_PER_SECOND * seconds))
        self.__velocity += self.__gravity

    def __move_up(self, seconds: int) -> None:
        """Updates the player state to reflect a up move (aka jumping)."""
        self.rect.move_ip(0, self.__velocity * round(PIXEL_PER_SECOND * seconds) * -1)
        self.__jump_height = self.__jump_height - 2

    def __move_left(self, seconds: int) -> None:
        """Updates the player state to reflect a move to the left.
           Stops movement if player is on the left edge of the play area.
        """
        if self.__check_left_edge(seconds):
            self.rect.move_ip(self.__speed * round(PIXEL_PER_SECOND * seconds) * -1, 0)
        else:
            # stop movement at the left edge
            self.stop()

    def __check_left_edge(self, seconds: int) -> None:
        """Checks if the player is not beyond the left edge of the play area."""
        return self.rect.x - self.__speed * round(PIXEL_PER_SECOND * seconds) >= 0

    def __move_right(self, seconds: int) -> None:
        """Updates the player state to reflect a move to the right.
           Stops movement if player is on the right edge of the play area.
        """
        if self.__check_right_edge(seconds):
            self.rect.move_ip(self.__speed * round(PIXEL_PER_SECOND * seconds), 0)
        else:
            # stop movement at the right edge
            self.stop()

    def __check_right_edge(self, seconds: int) -> bool:
        """Checks is the player is not beyond the right edge of the play area."""
        new_x = self.__surface_rect.width - self.rect.width - self.__speed * round(PIXEL_PER_SECOND * seconds)
        return self.rect.x <= new_x

    def __check_still_on_block(self) -> None:
        """Checks if the player is still on a block. If not player begins to fall."""
        if self.__on_block is not None:
            if self.rect.left > self.__on_block.rect.right or self.rect.right < self.__on_block.rect.left:
                self.__on_block = None
                self.__falling = True
                self.__jumping = False
                self.__velocity = Player.VELOCITY

    def set_on_block(self, block: Block) -> int:
        """Sets the block on which the player is standing. Stops falling or jumping.
           Returns the block level improvement needed for score calculation.
        """
        uplevel = 0
        self.__on_block = block
        self.rect.bottom = block.rect.y

        if self.__on_block.get_level() > self.__highest_block_level:
            uplevel = self.__on_block.get_level() - self.__highest_block_level
            self.__highest_block_level = self.__on_block.get_level()

        self.__falling = False
        self.__jumping = False
        self.__velocity = 0

        return uplevel

    def move_right(self) -> None:
        """Marks the player as moving to the right. Update method will apply state changes."""
        if self.__dead:
            return

        self.__move = "right"

    def move_left(self) -> None:
        """Marks the player as moving to the left. Update method will apply state changes."""
        if self.__dead:
            return

        self.__move = "left"

    def stop(self) -> None:
        """Stops player movement to left or right.  Update method will apply state changes."""
        if self.__dead:
            return

        self.__move = None

    def jump(self) -> None:
        # TODO fix jumping, jumping right now is "teleporting" up then falling, looks/feels bad
        """Marks the player as jumping. Update method will apply state changes."""
        if self.__dead:
            return

        # jump only possible if standing on a block
        if self.__on_block is not None:
            self.image = self.__images["in_game_screen_player_jumping"]
            self.rect = self.image.get_rect(topleft=self.rect.topleft)

            self.__sounds["jump"].play()

            self.__on_block = None
            self.__falling = False
            self.__jumping = True
            self.__velocity = 6

            power_ups = self.__power_ups.get(PowerUpJump.NAME)

            go_up = Block.BLOCK_HEIGHT * 3

            if power_ups is not None:
                if len(power_ups) > 0:
                    go_up = go_up * 2

            # go up 3 block heights
            self.rect.y = self.rect.y - go_up

    def set_surface_rect(self, surface_rect: Rect) -> None:
        """Sets the rect of the play area surface. Needed for calculations of player state.
           Player MUST NOT update the play area surface!
        """
        self.__surface_rect = surface_rect

    def get_joystick(self) -> Joystick:
        """Gets the joystick assigned to the player, if any."""
        return self.__joystick

    def is_falling(self) -> bool:
        """Checks if player is falling."""
        return self.__falling

    def is_jumping(self) -> bool:
        """Checks if player is jumping."""
        return self.__jumping

    def get_jump_height(self) -> int:
        return self.__jump_height

    def get_speed(self) -> int:
        """Gets the current player speed (left or right direction)."""
        return self.__speed

    def get_velocity(self) -> int:
        """Gets the current player velocity (falling speed?)."""
        return self.__velocity

    def is_ready(self) -> bool:
        """Checks if the player is ready to begin a new game round."""
        return self.__ready

    def set_ready(self, ready: bool) -> None:
        """Marks if the player is ready to begin a new game round."""
        self.__ready = ready

    def is_dead(self) -> bool:
        """Checks if the player is dead (game over for him, sorry)."""
        return self.__dead

    def set_dead(self) -> None:
        self.__dead = True

    def get_number(self) -> int:
        """Gets the player numer (1 or 2)."""
        return self.__number

    def get_score(self) -> int:
        """Gets the current player score (number)."""
        return self.__score

    def set_score(self, score: int) -> None:
        """Sets the current player score (number)."""
        self.__score = score

    def add_power_up(self, power_up: PowerUp) -> None:
        same_name = None

        if power_up.get_name() in self.__power_ups:
            same_name = self.__power_ups[power_up.get_name()]
        else:
            same_name = []
            self.__power_ups[power_up.get_name()] = same_name

        same_name.append(power_up)

    def remove_power_up(self, power_up: PowerUp) -> None:
        same_name = self.__power_ups[power_up.get_name()]

        same_name.remove(power_up)

    def get_power_ups(self) -> Dict[str, List[PowerUp]]:
        return self.__power_ups

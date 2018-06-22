import pygame
import block

class Player(pygame.sprite.Sprite):
    """A sprite representing a player."""
    SPEED_TO_FPS_RATIO = 1 / 8
    
    def __init__(self, number, image_file_name, gravity, joystick, sounds, fonts, fps):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Player, self).__init__()
        
        self.__number = number
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        self.image = pygame.image.load(image_file_name).convert_alpha()
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect()

        self.__level = 0
        self.__fps = fps
        self.__gravity = gravity
        self.__joystick = joystick
        self.__sounds = sounds
        self.__font = fonts["small"]
        self.reset()

    def reset(self):
        """Resets the player state so that the player can be reused in a new game round."""
        self.__dead = False
        self.__velocity = 0
        self.__falling = False
        self.__jumping = False
        self.__on_block = None
        self.__speed = round(Player.SPEED_TO_FPS_RATIO * self.__fps)
        self.__jump_height = 15
        self.__move = None
        self.__ready = False
        self.__highest_block_level = 0
        self.__level = 0
        self.__score = 0
    
    def update(self):
        """Updates the player state. Does nothing if player is dead.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__dead:
            self.__update_alive()

    def __update_alive(self):
        """Updates the player state while he is stil alive."""
        if self.__jumping:
            self.__jump_height = self.__jump_height - 2
                    
            if self.__jump_height <= 0:
                self.__jump_height = 10
                self.__jumping = False
                self.__falling = True
                self.__velocity = 6

        if self.__on_block is not None:
            self.__check_still_on_block()

        if self.__falling:
            self.__move_down()
        elif self.__jumping:
            self.__move_up()
    
        if self.__move is not None:
            if self.__move == "left":
                self.__move_left()
            elif self.__move == "right":
                self.__move_right()

        self.__dead = self.__falling and self.rect.top > self.__surface_rect.bottom

    def __move_down(self):
        """Updates the player state to reflect a down move (aka falling)."""
        self.rect.move_ip(0, self.__velocity)
        self.__velocity += self.__gravity

    def __move_up(self):
        """Updates the player state to reflect a up move (aka jumping)."""
        self.rect.move_ip(0, self.__velocity * -1)
        self.__jump_height = self.__jump_height - 2

    def __move_left(self):
        """Updates the player state to reflect a move to the left.
           Stops movement if player is on the left edge of the play area.
        """        
        if self.__check_left_edge():
            self.rect.move_ip(self.__speed * -1, 0)
        else:
            # stop movement at the left edge
            self.stop()

    def __check_left_edge(self):
        """Checks if the player is not beyond the left edge of the play area."""
        return self.rect.x - self.__speed >= 0

    def __move_right(self):
        """Updates the player state to reflect a move to the right.
           Stops movement if player is on the right edge of the play area.       
        """
        if self.__check_right_edge():
            self.rect.move_ip(self.__speed, 0)
        else:
            # stop movement at the right edge
            self.stop()

    def __check_right_edge(self):
        """Checks is the player is not beyond the right edge of the play area."""
        return self.rect.x <= self.__surface_rect.width - self.rect.width - self.__speed

    def __check_still_on_block(self):
        """Checks if the player is still on a block. If not player begins to fall."""
        if self.__on_block is not None:
            if self.rect.left > self.__on_block.rect.right or self.rect.right < self.__on_block.rect.left:
                self.__on_block = None
                self.__falling = True
                self.__jumping = False
                self.__velocity = 6

    def set_on_block(self, block):
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
    
    def move_right(self):
        """Marks the player as moving to the right. Update method will apply state changes."""
        if self.__dead:
            return

        self.__move = "right"

    def move_left(self):
        """Marks the player as moving to the left. Update method will apply state changes."""
        if self.__dead:
            return
        
        self.__move = "left"

    def stop(self):
        """Stops player movement to left or right.  Update method will apply state changes."""
        if self.__dead:
            return
        
        self.__move = None

    def jump(self):
        # TODO fix jumping, jumping right now is "teleporting" up then falling, looks/feels bad
        """Marks the player as jumping. Update method will apply state changes."""
        if self.__dead:
            return
       
        # jump only possible if standing on a block
        if self.__on_block is not None:
            self.__sounds["jump"].play()
            self.__on_block = None
            self.__falling = False
            self.__jumping = True
            self.__velocity = 6
            # go up 3 block heights
            self.rect.y = self.rect.y - block.Block.BLOCK_HEIGHT * 3
           
    def set_surface_rect(self, surface_rect):
        """Sets the rect of the play area surface. Needed for calculations of player state.
           Player MUST NOT update the play area surface!
        """
        self.__surface_rect = surface_rect
        
    def get_joystick(self):
        """Gets the joystick assigned to the player, if any."""
        return self.__joystick
        
    def is_falling(self):
        """Checks if player is falling."""
        return self.__falling
    
    def is_jumping(self):
        """Checks if player is jumping."""
        return self.__jumping

    def get_speed(self):
        """Gets the current player speed (left or right direction)."""
        return self.__speed
    
    def get_velocity(self):
        """Gets the current player velocity (falling speed?)."""
        return self.__velocity

    def is_ready(self):
        """Checks if the player is ready to begin a new game round."""
        return self.__ready
    
    def set_ready(self, ready):
        """Marks if the player is ready to begin a new game round."""
        self.__ready = ready
    
    def is_dead(self):
        """Checks if the player is dead (game over for him, sorry)."""
        return self.__dead
    
    def get_number(self):
        """Gets the player numer (1 or 2)."""
        return self.__number

    def get_score(self):
        """Gets the current player score (number)."""
        return self.__score
    
    def set_score(self, score):
        """Sets the current player score (number)."""
        self.__score = score

import pygame
import random
from block import Block
import masters_of_development

class DebugInfo(object):
    def __init__(self, player):
        self.__player = player
        self.__visible = False

        self.__font = pygame.font.SysFont("mono", 14)
        self.__color = pygame.Color(0, 255, 0)    
        
    def update(self):
        if not self.__visible:
            return
        
        player_rect = self.__player.get_rect()
        
        debug_info = "player left {0:3d} right {1:3d} top {2:3d} bottom {3:3d}".format(
            player_rect.left, player_rect.right, player_rect.top, player_rect.bottom)
        
        self.__render_debug_info(debug_info, 0, 0)
       
        debug_info = "falling: {0:s} jumping: {1:s}".format(
            str(self.__player.is_falling()), str(self.__player.is_jumping()))
        
        self.__render_debug_info(debug_info, 0, 16)

        debug_info = "speed: {0:d} velocity: {1:d}".format(
            self.__player.get_speed(), self.__player.get_velocity())
        
        self.__render_debug_info(debug_info, 0, 32)
        
        debug_info = "screen width {0:d} height {0:d}".format(
            self.__player.get_surface().get_width(), self.__player.get_surface().get_height())
        
        self.__render_debug_info(debug_info, 0, 48)
        
        joystick = self.__player.get_joystick()
        
        if joystick != None:
            debug_info = "joystick: {0:s} {1:s}".format(
                str(joystick.get_id()), self.__remove_whitespace(joystick.get_name()))
        
            self.__render_debug_info(debug_info, 0, 64)
    
    def __remove_whitespace(self, name):
        whitespaces = 0
        new_name = ""
        
        for char in name:
            if char.isspace():
                whitespaces += 1
            else:
                whitespaces = 0
            
            if whitespaces <= 1:
                new_name += char

        return new_name
    
    def __render_debug_info(self, debug_info, x, y):
        debug_surface = self.__font.render(debug_info, False, self.__color)
        debug_rect = debug_surface.get_rect()
        debug_rect.x = x
        debug_rect.y = y

        self.__player.get_surface().blit(debug_surface, debug_rect)
        
    def switch_visibility(self):
        self.__visible = not self.__visible

class Player(pygame.sprite.Sprite):
    SPEED_TO_FPS_RATIO = 1 / 8
    
    def __init__(self, number, image_file_name, gravity, joystick, sounds, fps):
        # call the parent class (Sprite) constructor
        super(Player, self).__init__()
        
        self.__number = number
        self.__image = pygame.image.load(image_file_name).convert_alpha()
        self.__rect = self.__image.get_rect()
        self.__level = 0
        self.__fps = fps
        self._scroll_velocity = 8
        self.__gravity = gravity
        self.__debug_info = DebugInfo(self)
        self.__font = pygame.font.SysFont("sans", 20)
        self.__joystick = joystick
        self.__sounds = sounds
        self.__score = Score((0, 0), self.__font, self.__sounds["score"])
        self.__all_sprites = pygame.sprite.Group(self.__score)
        self.__blocks = []
        self.__reset_vars()

    def reset(self):
        self.__reset_vars()
        self.__reset_blocks()
        self.__generate_blocks()
        # set player on base block
        self.__set_on_block(self.__blocks[0])

    def __reset_vars(self):
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
        self.__score.reset()

    def __reset_blocks(self):
        for block in self.__blocks:
            block.kill()
            
        self.__blocks = []

    def __generate_blocks(self):
        if len(self.__blocks) == 0:
            self.__generate_base_block()
        
        # only generate as much new blocks as needed
        while len(self.__blocks) < 13:
            self.__level += 1
            ygaps = random.randrange(50, 100)
            xgaps = random.randrange(100, 150)
            block_width = random.randrange(80, 160)
            side_space = 30
            last_block = self.__blocks[len(self.__blocks)-1]

            last_block_top = last_block.get_rect().top
            random_y_position = last_block_top - ygaps
            random_x_position = last_block.get_rect().centerx

            # random if the platform spawns left or right to last one
            if random.randint(0,1) == 1:
                random_x_position += xgaps
            else:
                random_x_position -=  xgaps

            b = Block(self.__level,
                       random_x_position,
                      random_y_position,
                      block_width,
                      Block.BLOCK_HEIGHT)
            # make sure that the block is not out of screen bounds
            while b.get_rect().right > self.__screen_surface.get_rect().right:
                b.get_rect().right -= xgaps

            while b.get_rect().left < self.__screen_surface.get_rect().left:
                b.get_rect().right += xgaps

            self.__blocks.append(b)

    def __generate_base_block(self):
        baseBlock = Block(
            0,
            self.__screen_surface.get_rect().x,
            self.__screen_surface.get_height() - Block.BLOCK_HEIGHT,
            self.__screen_surface.get_width(), Block.BLOCK_HEIGHT
        )
        
        self.__blocks.append(baseBlock) 
    
    def update(self):
        if self.__dead:
            self.__render_game_over()
        else:
            self.__update_alive()
        
        self.__debug_info.update()

        self.__screen_surface.blit(self.__image, self.__rect)

    def __render_game_over(self):
        font_surface = self.__font.render("GAME OVER", True, (255, 0, 0))
        font_rect = font_surface.get_rect()
        font_rect.x = self.__screen_surface.get_rect().centerx - font_surface.get_width() // 2
        font_rect.y = self.__screen_surface.get_rect().centery - font_surface.get_height() // 2
        
        self.__screen_surface.blit(font_surface, font_rect)

    def __update_alive(self):
        self.__all_sprites.update()
        self.__all_sprites.draw(self.__screen_surface)

        self.__scroll_screen()
        # generate new blocks after scrolling if necessary
        self.__generate_blocks()

        for block in self.__blocks:
            block.render(self.get_surface())

        if self.__jumping:
            self.__jump_height = self.__jump_height - 2
                    
            if self.__jump_height <= 0:
                self.__jump_height = 10
                self.__jumping = False
                self.__falling = True
                self.__velocity = 6

        if self.__on_block is None:
            self.__detect_block_collision()
        else:
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

        self.__dead = self.__falling and self.__rect.top > self.__screen_surface.get_rect().bottom

    def __scroll_screen(self):
        if self.__rect.top <= self.__screen_surface.get_height() / 2:
            self.__rect.y += self._scroll_velocity
            for block in self.__blocks:
                block.get_rect().y += self._scroll_velocity
                # delete blocks offscreen
                if block.get_rect().top >= self.__screen_surface.get_height():
                    self.__blocks.remove(block)
                    block.kill()

    def __move_down(self):
        self.__rect.move_ip(0, self.__velocity)
        self.__velocity += self.__gravity

    def __move_up(self):
        self.__rect.move_ip(0, self.__velocity * -1)
        self.__jump_height = self.__jump_height - 2

    def __move_left(self):
        if self.__check_left_edge():
            self.__rect.move_ip(self.__speed * -1, 0)
        else:
            # stop movement at the left edge
            self.stop()

    def __check_left_edge(self):
        return self.__rect.x - self.__speed >= 0

    def __move_right(self):
        if self.__check_right_edge():
            self.__rect.move_ip(self.__speed, 0)
        else:
            # stop movement at the right edge
            self.stop()

    def __check_right_edge(self):
        return self.__rect.x <= self.__screen_surface.get_width() - self.__rect.width - self.__speed

    def __check_still_on_block(self):
        if self.__on_block is not None:
            if self.__rect.left > self.__on_block.get_rect().right or self.__rect.right < self.__on_block.get_rect().left:
                self.__on_block = None
                self.__falling = True
                self.__jumping = False
                self.__velocity = 6

    def __detect_block_collision(self):
        #Überprüft die Kollision mit allen vorhanden blöcken
        for block in self.__blocks:
            if self.__rect.colliderect(block.get_rect()):
                falled_on = self.__falling and self.__rect.bottom >= block.get_rect().top and self.__rect.bottom <= block.get_rect().centery
                jumped_on = self.__jumping and self.__rect.bottom == block.get_rect().top
                
                if falled_on or jumped_on:
                    self.__set_on_block(block)
                    
                    if self.__on_block.get_level() > self.__highest_block_level:
                        self.__score.add_platform_score(self.__on_block.get_level() - self.__highest_block_level)
                        self.__highest_block_level = self.__on_block.get_level()
                    
                    self.__falling = False
                    self.__jumping = False
                    self.__velocity = 0
                    break
    
    def __set_on_block(self, block):
        self.__on_block = block
        self.__rect.bottom = block.get_rect().y
    
    def move_right(self):
        """Marks the player as moving to the right.
        """
        if self.__dead:
            return

        self.__move = "right"

    def move_left(self):
        """Marks the player as moving to the left.
        """
        if self.__dead:
            return
        
        self.__move = "left"

    def stop(self):
        """Stops player movement to left or right.
        """
        
        if self.__dead:
            return
        
        self.__move = None

    def jump(self):
        # TODO fix jumping, jumping right now is "teleporting" up then falling, looks/feels bad
        """Marks the player as jumping.
        """
        if self.__dead:
            return
       
        # jump only possible if standing on a block
        if self.__on_block is not None:
            self.__sounds["jump"].play()
            self.__on_block = None
            self.__falling = False
            self.__jumping = True
            self.__velocity = 6
            # go up 10 pixel
            self.__rect.y = self.__rect.y - Block.BLOCK_HEIGHT * 3
            
    def switch_debug(self):
        """Switches the debug information on/off.
        """
        self.__debug_info.switch_visibility()

    def get_surface(self):
        return self.__screen_surface

    def set_surface(self, surface):
        self.__screen_surface = surface
        self.__init_player_position()
        self.__init_score_display()
        
    def __init_player_position(self):
        self.__rect.left = self.__screen_surface.get_width() // 2 - self.__image.get_width() // 2
        self.__rect.bottom = self.__screen_surface.get_height() - 44

    def __init_score_display(self):
        self.__score_display = Score((0, 0), self.__font, self.__sounds["score"])

    def get_rect(self):
        return self.__rect

    def get_joystick(self):
        return self.__joystick
        
    def is_falling(self):
        return self.__falling
    
    def is_jumping(self):
        return self.__jumping

    def get_speed(self):
        return self.__speed
    
    def get_velocity(self):
        return self.__velocity

    def is_ready(self):
        return self.__ready
    
    def set_ready(self, ready):
        self.__ready = ready
    
    def is_dead(self):
        return self.__dead
    
    def get_number(self):
        return self.__number

    def get_score(self):
        return self.__score

class Score(pygame.sprite.Sprite):
    PLATFORM_LEVEL_SCORE = 100
    
    def __init__(self, pos, font, sound):
        super(Score, self).__init__()
        self.__font = font
        self.__sound = sound
        self.rect = pygame.Rect(pos, (1, 1))
        self.reset()

    def reset(self):
        self.__score = 0
        self.__update_image()
        
    def __update_image(self):
        height = self.__font.get_height()
        text_surfaces = []
        
        for txt in ("SCORE", "{0:d}".format(self.__score)):
            text_surfaces.append(self.__font.render(txt, True, masters_of_development.MastersOfDevelopment.BLACK))
        
        width = max(txt_surface.get_width() for txt_surface in text_surfaces)
        
        self.image = pygame.Surface((width, height * len(text_surfaces)), pygame.SRCALPHA)
        
        for y, txt_surface in enumerate(text_surfaces):
            self.image.blit(txt_surface, (0, y * height))
        
        self.rect = self.image.get_rect(topleft = self.rect.topleft)
    
    def add_platform_score(self, uplevel):
        self.add_score(uplevel * Score.PLATFORM_LEVEL_SCORE)
        
    def add_score(self, score):
        self.__score += score
        self.__update_image()
        self.__sound.play()
    
    def get_score(self):
        return self.__score

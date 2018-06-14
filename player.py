import pygame
from block import Block

class DebugInfo:
    def __init__(self, player):
        self.__player = player
        self.__visible = False

        self.__font = pygame.font.SysFont("mono", 14)
        self.__color = pygame.Color(0, 255, 0)    
        
    def update(self):
        if not self.__visible:
            return
        
        player_rect = self.__player.get_surface().get_rect()
        
        debug_info = "left {0:3d} right {1:3d} top {2:3d} bottom {3:3d}".format(
            player_rect.left, player_rect.right, player_rect.top, player_rect.bottom)
        
        self.__render_debug_info(debug_info, 0, 0)
       
        debug_info = "falling: {0:s} jumping: {1:s}".format(
            str(self.__player.is_falling()), str(self.__player.is_jumping()))
        
        self.__render_debug_info(debug_info, 0, 16)
        
        joystick = self.__player.get_joystick()
        
        if joystick != None:
            debug_info = "joystick: {0:s} {1:s}".format(
                str(joystick.get_id()), self.__remove_whitespace(joystick.get_name()))
        
            self.__render_debug_info(debug_info, 0, 32)
    
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
    def __init__(self, number, screen_surface, image_file_name, blocks, gravity, joystick):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        
        self.__number = number
        self.__screen_surface = screen_surface
        
        self.__image = pygame.image.load(image_file_name).convert_alpha()
        self.__rect = self.__image.get_rect()

        self.__rect.left = screen_surface.get_width() // 2 - self.__image.get_width() // 2
        self.__rect.bottom = screen_surface.get_height() - 44
       
        self.__blocks = blocks
        self.__gravity = gravity
        self.__velocity = 0
        self.__falling = True
        self.__jumping = False
        self.__on_block = None
        self.__speed = 10
        self.__jump_height = 15
        self.__dead = False
        self.__debug_info = DebugInfo(self)
        self.__font = pygame.font.SysFont("sans", 20)
        self.__joystick = joystick
        self.__move = None

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
        if self.__jumping:
            self.__jump_height = self.__jump_height - 2
                    
            if self.__jump_height <= 0:
                self.__jump_height = 15
                self.__jumping = False
                self.__falling = True
                self.__velocity = 6

        if self.__on_block == None:
            self.__detect_block_collision()
        else:
            self.__check_still_on_block()

        if self.__falling:
            self.__rect.y += self.__velocity
            self.__velocity += self.__gravity
        elif self.__jumping:
            self.__rect.y -= self.__velocity
            self.__jump_height = self.__jump_height - 2
    
        if self.__move is not None:
            if self.__move == "left":
                self.__move_left()
            elif self.__move == "right":
                self.__move_right()
    
        self.__dead = self.__falling and self.__rect.top > self.__screen_surface.get_rect().bottom        

    def __move_left(self):
        if self.__rect.x - self.__speed >= 0:
            self.__rect.x = self.__rect.x - self.__speed
        else:
            # stop movement at the left edge
            self.stop()

    def __move_right(self):
        if self.__rect.x <= self.__screen_surface.get_width() - self.__rect.width - self.__speed:
            self.__rect.x = self.__rect.x + self.__speed
        else:
            # stop movement at the right edge
            self.stop()

    def __check_still_on_block(self):
        if self.__on_block:
            if self.__rect.left > self.__on_block.get_rect().right or self.__rect.right < self.__on_block.get_rect().left:
                print("player #" + str(self.__number) + ": " + str(self.__rect) + " fell off the block: " + str(self.__on_block.get_rect()))
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
                    self.__on_block = block
                    self.__falling = False
                    self.__jumping = False
                    self.__velocity = 0
                    old_rect = self.__rect
                    self.__rect.bottom = block.get_rect().y
                    print("Collision detected of player #" + str(self.__number) + " pos " + str(old_rect) + " with block pos "+ str(block.get_rect()) + "  new pos now " + str(self.__rect))
                    break
    
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
        """Marks the player as jumping.
        """
        if self.__dead:
            return
        
        # jump only possible if standing on a block
        if self.__on_block:
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

    def get_joystick(self):
        return self.__joystick
        
    def is_falling(self):
        return self.__falling
    
    def is_jumping(self):
        return self.__jumping

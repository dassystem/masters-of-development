import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, number, screen_surface, image_file_name, blocks, gravity):
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
        
        self.__debug = False
        self.__debug_font = pygame.font.SysFont("mono", 14)
        self.__debug_color = pygame.Color(0, 255, 0)

    def move_right(self):
        """Moves the player to the right. If on the right edge, the player won't move further right.
        """
        if self.__rect.x <= self.__screen_surface.get_width() - self.__rect.width - self.__speed:
            self.__rect.x = self.__rect.x + self.__speed

    def move_left(self):
        """Moves the player to the left. If on the left edge, the player won't move further left.
        """
        if self.__rect.x - self.__speed >= 0:
            self.__rect.x = self.__rect.x - self.__speed

    def jump(self):
        # jump only possible if standing on a block
        if self.__on_block:
            self.__on_block = None
            self.__falling = False
            self.__jumping = True
            self.__velocity = 6
            # go up 10 pixel
            self.__rect.y = self.__rect.y - 10

    def update(self):
        if self.__jumping:
            self.__jump_height = self.__jump_height - 2
                    
            if self.__jump_height <= 0:
                self.__jump_height = 15
                self.__jumping = False
                self.__falling = True
                self.__velocity = 6

        self.__check_on_block()

        if self.__on_block == None:
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

        if self.__falling:
            self.__rect.y += self.__velocity
            self.__velocity += self.__gravity
        elif self.__jumping:
            self.__rect.y -= self.__velocity
            self.__jump_height = self.__jump_height - 2
        
        self.__render_debug_info()
                
        self.__screen_surface.blit(self.__image, self.__rect)

    def __check_on_block(self):
        if self.__on_block:
            if self.__rect.left > self.__on_block.get_rect().right or self.__rect.right < self.__on_block.get_rect().left:
                print("player #" + str(self.__number) + ": " + str(self.__rect) + " fell off the block: " + str(self.__on_block.get_rect()))
                self.__on_block = None
                self.__falling = True
                self.__jumping = False
                self.__velocity = 6

    def __render_debug_info(self):
        if not self.__debug:
            return
        
        debug_info = "left {0:3d} right {1:3d} top {2:3d} bottom {3:3d}".format(
            self.__rect.left, self.__rect.right, self.__rect.top, self.__rect.bottom)
        
        self.__render_debug_surface(debug_info, 0, 0)
       
        debug_info = "falling: {0:s} jumping: {1:s}".format(str(self.__falling), str(self.__jumping))
        
        self.__render_debug_surface(debug_info, 0, 16)
    
    def __render_debug_surface(self, debug_info, x, y):
        debug_surface = self.__debug_font.render(debug_info, False, self.__debug_color)
        debug_rect = debug_surface.get_rect()
        debug_rect.x = x
        debug_rect.y = y
        self.__screen_surface.blit(debug_surface, debug_rect)
        
    def switch_debug(self):
        self.__debug = not self.__debug

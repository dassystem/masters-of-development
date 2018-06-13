import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, number, screen_surface, image_file_name, blocks, gravity):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        
        self.number = number
        
        self.screen_surface = screen_surface
        
        # TODO: use sprite?
        self.image = pygame.image.load(image_file_name).convert_alpha()
        self.rect = self.image.get_rect()

        self.rect.left = screen_surface.get_width() // 2 - self.image.get_width() // 2
        self.rect.bottom = screen_surface.get_height() - 44
       
        self.blocks = blocks
        self.gravity = gravity

        self.velocity = 0
        self.player_img = None
        self.falling = True
        self.is_jump = False
        self.on_block = None
        self.speed = 10
        self.jump_height = 15
        
        self.debug_font = pygame.font.SysFont("mono", 14)
        self.debug_color = pygame.Color(0, 255, 0)

    def move_right(self):
        """Moves the player to the right. If on the right edge, the player won't move further right.
        """
        if self.rect.x <= self.screen_surface.get_width() - self.rect.width - self.speed:
            self.rect.x = self.rect.x + self.speed

    def move_left(self):
        """Moves the player to the left. If on the left edge, the player won't move further left.
        """
        if self.rect.x - self.speed >= 0:
            self.rect.x = self.rect.x - self.speed

    def jump(self):
        # jump only possible if standing on a block
        if self.on_block:
            self.on_block = None
            self.falling = False
            self.is_jump = True
            self.velocity = 6
            # go up 10 pixel
            self.rect.y = self.rect.y - 10

    def update(self):
        if self.is_jump:
            self.jump_height = self.jump_height - 2
                    
            if self.jump_height <= 0:
                self.jump_height = 15
                self.is_jump = False
                self.falling = True
                self.velocity = 6

        self.__check_on_block()

        if self.on_block == None:
            #Überprüft die Kollision mit allen vorhanden blöcken
            for block in self.blocks:
                if self.rect.colliderect(block.rect):
                    falled_on = self.falling and self.rect.bottom >= block.rect.top and self.rect.bottom <= block.rect.centery
                    jumped_on = self.is_jump and self.rect.bottom == block.rect.top
                    
                    if falled_on or jumped_on:
                        self.on_block = block
                        self.falling = False
                        self.is_jump = False
                        self.velocity = 0
                        old_rect = self.rect
                        self.rect.bottom = block.rect.y
                        print("Collision detected of player #" + str(self.number) + " pos " + str(old_rect) + " with block pos "+ str(block.rect) + "  new pos now " + str(self.rect))
                        break

        if self.falling:
            self.rect.y += self.velocity
            self.velocity += self.gravity
        elif self.is_jump:
            self.rect.y -= self.velocity
            self.jump_height = self.jump_height - 2
        
        self.__render_debug_info()
                
        self.screen_surface.blit(self.image, self.rect)

    def __check_on_block(self):
        if self.on_block:
            if self.rect.left > self.on_block.rect.right or self.rect.right < self.on_block.rect.left:
                print("player #" + str(self.number) + ": " + str(self.rect) + " fell off the block: " + str(self.on_block.rect))
                self.on_block = None
                self.falling = True
                self.is_jump = False
                self.velocity = 6

    def __render_debug_info(self):
        debug_info = "left {0:3d} right {1:3d} top {2:3d} bottom {3:3d}".format(
            self.rect.left, self.rect.right, self.rect.top, self.rect.bottom)
        
        self.__render_debug_surface(debug_info, 0, 0)
       
        debug_info = "falling: {0:s} jumping: {1:s}".format(str(self.falling), str(self.is_jump))
        
        self.__render_debug_surface(debug_info, 0, 16)
    
    def __render_debug_surface(self, debug_info, x, y):
        debug_surface = self.debug_font.render(debug_info, False, self.debug_color)
        debug_rect = debug_surface.get_rect()
        debug_rect.x = x
        debug_rect.y = y
        self.screen_surface.blit(debug_surface, debug_rect)
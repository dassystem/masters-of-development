import pygame

class Player:
    def __init__(self, screen_surface, x, y):
        self.screen_surface = screen_surface
        self.velocity = 0
        self.player_img = None
        self.falling = True
        self.is_jump = 0
        self.on_ground = False
        self.speed = 10
        self.jump_height = 15
        
        # TODO: use sprite?
        self.image_surface = pygame.image.load("smile.png")
        self.rect = self.image_surface.get_rect(x = x, y = y)

    def update(self, gravity, blocklist):
        if self.is_jump == 0:
            self.velocity += gravity
        elif self.is_jump == 1:
            self.jump_height = self.jump_height - 2

        if self.jump_height <= 0:
            self.jump_height = 15
            self.is_jump = 0

        #Überprüft die Kollision mit allen vorhanden blöcken
        for block in blocklist:
            if self.rect.colliderect(block.rect):
                self.on_ground = True
                self.falling = False
                self.is_jump = 0
                self.velocity = 0

        if self.on_ground == True:
            self.rect.y = self.rect.y
        elif self.on_ground ==False:
            self.rect.y -= self.velocity

    def render(self):
        self.screen_surface.blit(self.image_surface, self.rect)

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
        if self.on_ground == True:
            self.falling = True
            self.is_jump = 1
            self.rect.y = self.rect.y - 10
            self.velocity = 6
            self.on_ground = False

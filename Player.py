import pygame
from time import sleep


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.velocity=0
        self.player_img = None
        self.falling=True
        self.isjump = 0
        self.onGround=False
        self.rect = None
        self.speed = 10
        self.jumpHeight = 15

    def update(self, gravity, blocklist):
        if self.isjump == 0:
            self.velocity += gravity
        elif self.isjump == 1:
            self.jumpHeight = self.jumpHeight - 2

        if self.jumpHeight <= 0:
            self.jumpHeight = 15
            self.isjump = 0

        #Überprüft die Kollision mit allen vorhanden blöcken
        for block in blocklist:
            if self.rect.colliderect(block.rect):
                self.onGround = True
                self.falling = False
                self.isjump = 0
                self.velocity=0

        if self.onGround == True:
            self.rect.y = self.rect.y
        elif self.onGround ==False:
            self.rect.y -= self.velocity

    def loadPlayerImage(self):
        image = pygame.image.load("smile.png")
        self.player_img = image.convert()
        self.height = image.get_height
        self.width = image.get_width
        self.rect = image.get_rect(x = self.x, y = self.y)

    def render(self, window):
        window.blit(self.player_img, self.rect)
        sleep(0.03)

    def moveRight(self):
        self.rect.x = self.rect.x + self.speed

    def moveLeft(self):
        self.rect.x = self.rect.x - self.speed

    def jump(self):
        if self.onGround == True:
            self.falling = True
            self.isjump = 1
            self.rect.y = self.rect.y-10
            self.velocity = 6
            self.onGround = False



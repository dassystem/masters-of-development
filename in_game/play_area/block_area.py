import pygame
import random

from colors import DARKER_GRAY
from constants import PIXEL_PER_SECOND
from in_game.play_area.sprites.block import Block
from in_game.play_area.sprites.bug import Bug
from in_game.play_area.sprites.coin import Coin
from in_game.play_area.sprites.power_up_jump import PowerUpJump
from in_game.play_area.sprites.power_up_shield import PowerUpShield


class BlockArea(object):
    def __init__(self, play_area, surface, fonts, images, sounds, player):
        self.__play_area = play_area
        self.__surface = surface
        self.__fonts = fonts
        self.__images = images
        self.__sounds = sounds

        self.__player = pygame.sprite.GroupSingle(player)
        self.__blocks = pygame.sprite.OrderedUpdates()
        self.__block_items = pygame.sprite.Group()

        self.__level = 0

        # pass a copy of the surface rect to the player so that the player can't mess up with the surface
        player.set_surface_rect(surface.get_rect().copy())

    def reset(self):
        self.__level = 0

        self.get_player().reset()
        self.__blocks.empty()
        self.__block_items.empty()
        self.__generate_blocks()

        self.get_player().set_on_block(self.__blocks.sprites()[0])
        self.get_player().rect.centerx = (self.__surface.get_rect().centerx)

        self.__surface.fill(DARKER_GRAY)

    def __generate_blocks(self):
        if len(self.__blocks) == 0:
            self.__generate_base_block()

        max_gap = 2 * Block.BLOCK_WIDTH

        # only generate as much new blocks as needed
        while len(self.__blocks) < 13:
            self.__level += 1

            ygaps = random.randint(2, 3) * Block.BLOCK_HEIGHT

            block_width = random.randrange(80, 400)
            last_block = self.__blocks.sprites()[-1]

            last_block_top = last_block.rect.top
            random_y = last_block_top - ygaps

            prev_left = last_block.rect.left
            prev_right = last_block.rect.right

            max_right = self.__surface.get_width()

            possible_x = set()

            if not (prev_left == 0 and prev_right == max_right):
                min_x_left = max(0, prev_left - max_gap - block_width)
                max_x_left = min(max_right - block_width, prev_left + Block.BLOCK_WIDTH)

                possible_x_left = set(range(min_x_left, max_x_left + 1))

                min_x_right = min(max_right - block_width, prev_right - Block.BLOCK_WIDTH)
                max_x_right = min(max_right - block_width, prev_right + max_gap)

                possible_x_right = set(range(min_x_right, max_x_right + 1))

                possible_x = possible_x_left.union(possible_x_right)
            else:
                pass
            if len(possible_x) == 0:
                possible_x = set(range(0, max_right - block_width + 1))

            random_x = random.choice(list(possible_x))

            new_block = Block(
                self.__fonts["big"],
                self.__level,
                random_x,
                random_y,
                block_width,
                Block.BLOCK_HEIGHT)

            if new_block.rect.right > max_right:
                new_block.rect.move_ip((new_block.rect.right - max_right) * -1, 0)

#            if last_block.rect.left - new_block.rect.right > 2 * block.Block.BLOCK_WIDTH:
#                pass

            self.__blocks.add(new_block)

            r = random.randint(0, 10)

            if r == 1:
                coin = Coin(self.__images, new_block)
                self.__block_items.add(coin)
            elif r == 2:
                power_up = PowerUpJump(self.__images, new_block, self)
                self.__block_items.add(power_up)
            elif r == 3:
                bug = Bug(self.__images, new_block)
                self.__block_items.add(bug)
            elif r == 4:
                power_up = PowerUpShield(self.__images, new_block, self)
                self.__block_items.add(power_up)

    def __generate_base_block(self):
        baseBlock = Block(
            self.__fonts["big"],
            0,  # level
            0,  # x
            self.__surface.get_height() - 1 - Block.BLOCK_HEIGHT,  # y
            self.__surface.get_width(),  # width
            self.__surface.get_height() - 1 - Block.BLOCK_HEIGHT  # height
        )

        baseBlock.rect.x = 0
        baseBlock.rect.width = self.__surface.get_width()

        self.__blocks.add(baseBlock)

    def update(self, seconds):
        self.__blocks.clear(self.__surface, clear_callback)
        self.__block_items.clear(self.__surface, clear_callback)
        self.__player.clear(self.__surface, clear_callback)

        self.__scroll_screen(seconds)

        # generate new blocks after scrolling if necessary
        self.__generate_blocks()

        self.__player.update(seconds)

        self.__detect_block_collision()
        self.__detect_block_item_collision()

        self.__blocks.draw(self.__surface)
        self.__block_items.draw(self.__surface)
        self.__player.draw(self.__surface)

    def __scroll_screen(self, seconds):
        player_rect = self.__player.sprite.rect

        if player_rect.top <= self.__surface.get_height() // 2:
            player_rect.y += self.__play_area.get_scroll_velocity() * round(PIXEL_PER_SECOND * seconds)

            self.__blocks.update(self.__play_area.get_scroll_velocity(), self.__surface.get_height(), seconds)
            self.__block_items.update()
            self.get_play_area().scroll(seconds)

    def __detect_block_collision(self):
        collided_blocks = pygame.sprite.spritecollide(self.get_player(), self.__blocks, False, detect_player_block_collide)

        for block in collided_blocks:
            block.on_collide(self.get_player(), self.__play_area.get_score())

    def __detect_block_item_collision(self):
        collided_items = pygame.sprite.spritecollide(self.get_player(), self.__block_items, True)

        for collided_item in collided_items:
            collided_item.on_collide(self.get_player(), self.__play_area.get_score())

    def get_player(self):
        return self.__player.sprite

    def get_play_area(self):
        return self.__play_area

    def __render_debug_info(self, debug_info):
        return self.__font.render(debug_info, False, self.__color)


def detect_player_block_collide(player, block):
    collided = False

    if player.rect.colliderect(block.rect):
        if player.is_falling():
            collided = player.rect.bottom >= block.rect.top
        elif player.is_jumping():
            collided = player.rect.bottom == block.rect.top

    return collided


def clear_callback(surface, rect):
    """see https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.clear"""
    surface.fill(DARKER_GRAY, rect)
